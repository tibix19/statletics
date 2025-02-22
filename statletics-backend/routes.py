import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from scraper import scrape_results_for_gender  # Import absolu
from chart import build_chart_data
from datetime import datetime
from db import store_results, get_athlete_gender, normalize_name, get_db  # Ajout get_db import

router = APIRouter()

@router.post("/api/results")
async def get_results(request: Request):
    """
    Route principale de recherche qui :
     1. Récupère les résultats pour hommes et femmes.
     2. Si un seul athlète est trouvé, renvoie ses résultats et les données du graphique.
     3. Si plusieurs athlètes sont trouvés, renvoie la liste des athlètes uniques.
     
     En plus, pour chaque athlète, les résultats sont enregistrés dans MongoDB
     par discipline ("100").
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
    
    search_term = data.get("search_term")
    discipline = data.get("discipline")  # Assurez-vous que discipline est présent
    selected_person = data.get("selected_person")  # Optionnel
    
    if not search_term or not discipline:
        return JSONResponse(status_code=400, content={"error": "search_term and discipline are required"})
    
    # Appeler les fonctions de scraping en parallèle pour "MAN" et "WOM"
    man_results, wom_results = await asyncio.gather(
        scrape_results_for_gender(request.app, search_term, "MAN", discipline),
        scrape_results_for_gender(request.app, search_term, "WOM", discipline)
    )
    combined_results = man_results + wom_results
    print(f"[DEBUG] Total results pour '{search_term}' et discipline '{discipline}': {len(combined_results)}")

    # Enregistrer par athlète dans la base de données pour la discipline "100"
    unique_persons = sorted({entry["name"] for entry in combined_results})
    for athlete in unique_persons:
        athlete_results = [entry for entry in combined_results if entry["name"] == athlete]
        print(f"[DEBUG] Athlète '{athlete}' a {len(athlete_results)} résultats")
        try:
            store_results(athlete, discipline, athlete_results)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement pour {athlete}: {e}")

    if selected_person:
        # Filtrer les résultats pour la personne sélectionnée
        filtered_results = [entry for entry in combined_results if entry["name"] == selected_person]
        try:
            filtered_results.sort(key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"))
        except Exception:
            pass
        chart_data = build_chart_data(filtered_results)
        return {
            "search_term": search_term,
            "selected_person": selected_person,
            "results": filtered_results,
            "chart_data": chart_data,
            "discipline": discipline
        }
    else:
        # S'il y a plusieurs athlètes, renvoyer la liste des athlètes uniques et tous les résultats.
        return {
            "search_term": search_term,
            "unique_persons": unique_persons,
            "results": combined_results,
            "discipline": discipline
        }

@router.post("/api/athlete-results")
async def get_athlete_results(request: Request):
    """
    Route secondaire pour obtenir les résultats d'un athlète donné.
    Si l'athlète existe déjà dans la DB, on récupère son genre et on effectue le scraping
    uniquement pour l'année 2025 avec le genre enregistré.
    Sinon, on fait le scraping pour les deux genres.
    Ensuite, on recharge les résultats stockés dans la DB pour éviter d'avoir à cliquer deux fois.
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
    
    athlete_name = data.get("athlete_name")
    search_term = data.get("search_term")
    discipline = data.get("discipline")  # Passage de discipline
    if not athlete_name or not search_term or not discipline:
        return JSONResponse(status_code=400, content={"error": "athlete_name, search_term and discipline are required"})
    
    stored_gender = get_athlete_gender(athlete_name)
    if stored_gender:
        print(f"[DEBUG] Athlète '{athlete_name}' déjà enregistré avec genre '{stored_gender}'")
        # Scraper uniquement pour le genre enregistré avec filtre pour l'année 2025
        results = await scrape_results_for_gender(request.app, search_term, stored_gender, discipline, filter_year=True)
        combined_results = results
    else:
        # Scraper pour les deux genres comme actuellement
        man_results, wom_results = await asyncio.gather(
            scrape_results_for_gender(request.app, search_term, "MAN", discipline),
            scrape_results_for_gender(request.app, search_term, "WOM", discipline)
        )
        combined_results = man_results + wom_results
    
    print(f"[DEBUG] Athlète '{athlete_name}' > résultats récupérés: {len(combined_results)}")
    # Filtrer en comparant les noms normalisés
    athlete_results = [r for r in combined_results if normalize_name(r["name"]) == normalize_name(athlete_name)]
    print(f"[DEBUG] Athlète '{athlete_name}' > résultats filtrés: {len(athlete_results)}")
    
    try:
        store_results(athlete_name, discipline, athlete_results)
    except Exception as e:
        print(f"[DEBUG] Erreur lors de l'enregistrement pour {athlete_name}: {e}")
    
    # Recharger le document de l'athlète depuis la DB pour récupérer les résultats stockés
    db = get_db()
    doc = db["results"].find_one({"normalized_name": normalize_name(athlete_name)})
    # Extraire les résultats pour la discipline "100"
    stored_results = doc.get("results", {}).get(discipline, []) if doc else []
    try:
        stored_results.sort(key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"))
    except Exception:
        pass
    
    chart_data = build_chart_data(stored_results)
    
    return {
        "athlete_name": athlete_name,
        "results": stored_results,
        "chart_data": chart_data,
        "discipline": discipline
    }