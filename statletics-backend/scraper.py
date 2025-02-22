import time
import urllib.parse
from bs4 import BeautifulSoup
# Désactivez temporairement le cache pour le debugging
# from fastapi_cache.decorator import cache


def extract_unique_results_by_rank(soup, gender):
    """
    Extrait les performances en éliminant les doublons selon la valeur du rank.
    Retourne une liste de dictionnaires avec les informations extraites.
    """
    seen_ranks = set()
    unique_results = []
    results = soup.find_all("div", class_="entryline")
    for result in results:
        rank = result.find("div", class_="col-5").get_text(strip=True)
        if rank in seen_ranks:
            continue
        seen_ranks.add(rank)
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


# Désactivez temporairement le cache (remplacez @cache par rien)
async def scrape_results_for_gender(app, search_term: str, gender: str, discipline: str, filter_year: bool=False):
    """
    Effectue le scraping pour un genre donné et une discipline donnée en injectant le terme de recherche dans l'URL.
    Si filter_year est True, la requête est faite pour l'année 2025.
    """
    encoded_term = urllib.parse.quote_plus(search_term)
    year_param = "2025" if filter_year else "0"
    url = (
        "https://perfdb.prod.seltec-sports.net/Performances?"
        f"performanceList=4dcbe987-8109-4406-b19c-149205e08405&eventcode={discipline}"
        f"&classcode={gender}&environment=1&year={year_param}&showForeigners=0&windFilter=0"
        "&allResults=true&thisclassonly=false&allowInofficial=false&culture=de-CH&search=" + encoded_term
    )
    print(f"{url}")
    client = app.state.http_client
    start_time = time.perf_counter()
    response = await client.get(url)
    elapsed = time.perf_counter() - start_time
    print(
        f"Temps de réponse pour {gender} (search='{search_term}') : {elapsed:.2f} secondes")
    soup = BeautifulSoup(response.content, "html.parser")
    return extract_unique_results_by_rank(soup, gender)
