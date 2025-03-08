import time
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
import httpx
from fastapi_cache.decorator import cache
from asyncio import Queue

# Queue globale pour les logs
log_queue = Queue()

async def log_worker():
    """Worker asynchrone pour traiter les messages de log"""
    while True:
        message = await log_queue.get()
        print(message)
        log_queue.task_done()

async def async_print(message):
    """Fonction asynchrone pour envoyer les messages au worker de log"""
    await log_queue.put(message)


def extract_unique_results_by_rank(soup, gender):
    """
    Extrait les performances en éliminant les doublons selon la valeur du rank et le nom de l'athlète.
    Retourne une liste de dictionnaires avec les informations extraites.
    """
    seen_rank_names = set()
    unique_results = []
    results = soup.find_all("div", class_="entryline")
    for result in results:
        rank = result.find("div", class_="col-5").get_text(strip=True)
        name_block = result.find("div", class_="col-last")
        name = name_block.find("div", class_="firstline").get_text(strip=True)
        rank_name = f"{rank}-{name}"
        if rank_name in seen_rank_names:
            continue
        seen_rank_names.add(rank_name)
        result_value = result.find(
            "div", class_="col-4").find("div", class_="firstline").get_text(strip=True)
        name_block = result.find("div", class_="col-last")
        name = name_block.find("div", class_="firstline").get_text(strip=True)
        club = name_block.find("div", class_="secondline").get_text(strip=True)
        nat_block = result.find("div", class_="col-3")
        nat = nat_block.find("div", class_="firstline").get_text(strip=True)
        year = nat_block.find("div", class_="secondline").get_text(strip=True)
        date_block = result.find("div", class_="col-95p")
        date = date_block.find("div").get_text(strip=True)
        lieu_tag = date_block.find("div", class_="secondline")
        lieu = lieu_tag.get_text(strip=True) if lieu_tag else ""
        unique_results.append({
            "rank": rank,
            "result": result_value,
            "name": name,
            "club": club,
            "nat": nat,
            "year": year,
            "date": date,
            "lieu": lieu,
            "gender": gender
        })
    return unique_results


@cache(expire=24*60*60)  # Cache for 7 days (168 hours)
async def scrape_results_for_gender(app, search_term: str, gender: str, discipline: str, filter_year: bool=False):
    """
    Effectue le scraping pour un genre donné et une discipline donnée en injectant le terme de recherche dans l'URL.
    Si filter_year est True, la requête est faite pour l'année 2025.
    Inclut une logique de retry et de pagination pour récupérer tous les résultats disponibles.
    """
    encoded_term = urllib.parse.quote_plus(search_term)
    year_param = "2025" if filter_year else "0"
    base_url = (
        "https://perfdb.prod.seltec-sports.net/Performances?"
        f"performanceList=4dcbe987-8109-4406-b19c-149205e08405&eventcode={discipline}"
        f"&classcode={gender}&environment=1&year={year_param}&showForeigners=null&windFilter=0"
        "&allResults=true&thisclassonly=false&allowInofficial=true&culture=de-CH&search=" + encoded_term
    )
    
    client = app.state.http_client
    max_retries = 3
    retry_delay = 2  # secondes
    all_results = []
    page_number = 1
    
    while True:
        url = f"{base_url}&pageNumber={page_number}"
        await async_print(f"Fetching page {page_number} for {gender} {discipline}")
        
        for attempt in range(max_retries):
            try:
                start_time = time.perf_counter()
                response = await client.get(url)
                elapsed = time.perf_counter() - start_time
                await async_print(f"Temps de réponse pour {gender} {discipline} page {page_number} (search='{search_term}') : {elapsed:.2f} secondes")
                
                soup = BeautifulSoup(response.content, "html.parser")
                page_results = extract_unique_results_by_rank(soup, gender)
                
                if not page_results:  # Si la page ne retourne aucun résultat, on a atteint la fin
                    return all_results
                
                all_results.extend(page_results)
                page_number += 1
                break  # Sortir de la boucle de retry si la requête a réussi
                
            except httpx.ReadTimeout:
                if attempt < max_retries - 1:
                    retry_wait = retry_delay * (attempt + 1)  # Backoff exponentiel
                    await async_print(f"ReadTimeout pour {gender} {discipline} page {page_number}. Retry {attempt+1}/{max_retries} dans {retry_wait}s...")
                    await asyncio.sleep(retry_wait)
                else:
                    await async_print(f"Échec après {max_retries} tentatives pour {gender} {discipline} page {page_number}. Passage à la page suivante.")
                    return all_results  # Retourner les résultats déjà collectés en cas d'échec
                    
            except Exception as e:
                await async_print(f"Erreur inattendue pour {gender} {discipline} page {page_number}: {str(e)}")
                return all_results  # Retourner les résultats déjà collectés en cas d'erreur
    return []  # Retourne une liste vide en cas d'erreur inattendue