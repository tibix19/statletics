import asyncio
import time
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from scraper import scrape_results_for_gender  # Import absolu
from chart import build_chart_data
from datetime import datetime
from db import store_results, get_athlete_gender, normalize_name, get_db, is_data_recent, store_search_history, check_search_history, update_search_history
from performance_logs import performance_logger  # Import du logger de performance

router = APIRouter()

# Fonction d'arrière-plan pour stocker les résultats dans la base de données
async def store_results_background(unique_persons, all_results):
    """Fonction exécutée en arrière-plan pour stocker les résultats dans la base de données"""
    for athlete in unique_persons:
        athlete_results_by_discipline = {}
        # Regrouper les résultats par discipline
        for result in [r for r in all_results if r["name"] == athlete]:
            disc = result["discipline"]
            if disc not in athlete_results_by_discipline:
                athlete_results_by_discipline[disc] = []
            athlete_results_by_discipline[disc].append(result)
        
        # Stocker les résultats pour chaque discipline
        for disc, results in athlete_results_by_discipline.items():
            print(f"[DEBUG] Athlète '{athlete}' a {len(results)} résultats pour discipline '{disc}'")
            try:
                store_results(athlete, disc, results)
            except Exception as e:
                print(f"Erreur lors de l'enregistrement pour {athlete} (discipline {disc}): {e}")

@router.post("/api/results")
async def get_results(request: Request, background_tasks: BackgroundTasks):
    start_time = time.perf_counter()
    
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
    
    search_term = data.get("search_term")
    selected_person = data.get("selected_person")  # Optionnel
    
    if not search_term:
        return JSONResponse(status_code=400, content={"error": "search_term is required"})
    
    # Vérifier l'historique des recherches
    search_history = check_search_history(search_term)
    print(f"[DEBUG] Historique de recherche pour '{search_term}': {search_history}")
    
    # Liste des disciplines à rechercher
    disciplines = ["100", "200", "300", "400", "600", "800", "HJ"]
    all_results = []
    
    # Si la recherche date de moins de 3 jours, on récupère directement les athlètes depuis la DB
    if search_history["recent"]:
        print(f"[DEBUG] Recherche récente pour '{search_term}', utilisation directe de la DB")
        db = get_db()
        # Rechercher tous les athlètes dont le nom contient le terme de recherche
        query = {"athlete_name": {"$regex": search_term, "$options": "i"}}
        athletes = list(db["results"].find(query, {"athlete_name": 1, "_id": 0}))
        unique_persons = sorted([athlete["athlete_name"] for athlete in athletes])
        
        # Mettre à jour le timestamp dans l'historique
        update_search_history(search_term, "/api/results")
        
        if not unique_persons:
            # Si aucun athlète n'est trouvé, on fait une recherche complète
            print(f"[DEBUG] Aucun athlète trouvé en DB pour '{search_term}', recherche complète")
        else:
            # Retourner directement la liste des athlètes
            return {
                "search_term": search_term,
                "unique_persons": unique_persons,
                "all_disciplines": True
            }
    
    # Si la recherche date de cette année mais pas des 3 derniers jours, on fait une recherche pour l'année en cours
    filter_year = search_history["same_year"] and not search_history["recent"]
    
    # Préparer toutes les tâches de scraping pour toutes les disciplines
    scraping_tasks = []
    for disc in disciplines:
        scraping_tasks.extend([
            scrape_results_for_gender(request.app, search_term, "MAN", disc, filter_year=filter_year),
            scrape_results_for_gender(request.app, search_term, "WOM", disc, filter_year=filter_year)
        ])
    
    # Exécuter toutes les requêtes en parallèle
    all_scraped_results = await asyncio.gather(*scraping_tasks)
    
    # Traiter les résultats
    for i in range(0, len(all_scraped_results), 2):
        disc = disciplines[i // 2]
        man_results = all_scraped_results[i]
        wom_results = all_scraped_results[i + 1]
        combined_results = man_results + wom_results
        for result in combined_results:
            result["discipline"] = disc
        all_results.extend(combined_results)
        print(f"[DEBUG] Total results pour '{search_term}' et discipline '{disc}': {len(combined_results)}")

    # Identifier les personnes uniques
    unique_persons = sorted({entry["name"] for entry in all_results})
    
    # Planifier le stockage des résultats en arrière-plan
    background_tasks.add_task(store_results_background, unique_persons, all_results)
    
    # Mettre à jour le timestamp dans l'historique
    update_search_history(search_term, "/api/results")

    if selected_person:
        # Filtrer les résultats pour la personne sélectionnée
        filtered_results = [entry for entry in all_results if entry["name"] == selected_person]
        try:
            filtered_results.sort(key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"))
        except Exception:
            pass
        chart_data = build_chart_data(filtered_results)
        
        # Calculer le temps écoulé et logger la performance
        elapsed_time = time.perf_counter() - start_time
        performance_logger.log_search_performance(search_term, elapsed_time, "/api/results")
        
        return {
            "search_term": search_term,
            "selected_person": selected_person,
            "results": filtered_results,
            "chart_data": chart_data,
            "all_disciplines": True
        }
    else:
        # S'il y a plusieurs athlètes, renvoyer la liste des athlètes uniques et tous les résultats.
        
        # Calculer le temps écoulé et logger la performance
        elapsed_time = time.perf_counter() - start_time
        performance_logger.log_search_performance(search_term, elapsed_time, "/api/results")
        
        return {
            "search_term": search_term,
            "unique_persons": unique_persons,
            "results": all_results,
            "all_disciplines": True
        }

@router.post("/api/athlete-results")
async def get_athlete_results(request: Request, background_tasks: BackgroundTasks):
    start_time = time.perf_counter()
    
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
    
    athlete_name = data.get("athlete_name")
    search_term = data.get("search_term")
    discipline = data.get("discipline")  # Optionnel, pour filtrer par discipline
    if not athlete_name or not search_term:
        return JSONResponse(status_code=400, content={"error": "athlete_name and search_term are required"})
        
    # Enregistrer le terme de recherche dans l'historique
    update_search_history(search_term, "/api/athlete-results")
    
    # Vérifier si les données sont récentes (moins de 2 jours)
    if is_data_recent(athlete_name):
        print(f"[DEBUG] Athlète '{athlete_name}' a des données récentes, utilisation directe de la DB")
        # Utiliser directement les données stockées sans faire de scraping
        db = get_db()
        doc = db["results"].find_one({"normalized_name": normalize_name(athlete_name)})
        
        # Récupérer tous les résultats pour toutes les disciplines
        all_results = []
        if doc and "results" in doc:
            for disc, results in doc["results"].items():
                # Ajouter la discipline à chaque résultat
                for result in results:
                    result_with_discipline = result.copy()
                    result_with_discipline["discipline"] = disc
                    all_results.append(result_with_discipline)
        
        try:
            all_results.sort(key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"))
        except Exception:
            pass
        
        chart_data = build_chart_data(all_results)
        
        return {
            "athlete_name": athlete_name,
            "results": all_results,
            "chart_data": chart_data,
            "all_disciplines": True
        }
    
    # Si les données ne sont pas récentes, faire le scraping pour toutes les disciplines
    disciplines = ["100", "200", "300", "400", "600", "800", "HJ"]
    all_results = []
    stored_gender = get_athlete_gender(athlete_name)
    
    # Préparer toutes les tâches de scraping
    scraping_tasks = []
    for disc in disciplines:
        if stored_gender:
            print(f"[DEBUG] Athlète '{athlete_name}' déjà enregistré avec genre '{stored_gender}' pour discipline '{disc}'")
            scraping_tasks.append(scrape_results_for_gender(request.app, search_term, stored_gender, disc, filter_year=True))
        else:
            scraping_tasks.extend([
                scrape_results_for_gender(request.app, search_term, "MAN", disc),
                scrape_results_for_gender(request.app, search_term, "WOM", disc)
            ])
    
    # Exécuter toutes les requêtes en parallèle
    all_scraped_results = await asyncio.gather(*scraping_tasks)
    
    # Traiter les résultats et préparer la réponse immédiate
    athlete_results_by_discipline = {}
    
    for i, results in enumerate(all_scraped_results):
        disc = disciplines[i if stored_gender else i // 2]
        combined_results = results if stored_gender else (results + all_scraped_results[i + 1] if i % 2 == 0 else [])
        
        # Ajouter la discipline aux résultats
        for result in combined_results:
            result["discipline"] = disc
        
        # Filtrer en comparant les noms normalisés
        athlete_results = [r for r in combined_results if normalize_name(r["name"]) == normalize_name(athlete_name)]
        print(f"[DEBUG] Athlète '{athlete_name}' > résultats récupérés pour discipline '{disc}': {len(athlete_results)}")
        
        # Stocker pour traitement en arrière-plan
        if athlete_results:
            athlete_results_by_discipline[disc] = athlete_results
            all_results.extend(athlete_results)
    
    # Planifier le stockage en arrière-plan
    async def store_athlete_results_background():
        for disc, results in athlete_results_by_discipline.items():
            try:
                store_results(athlete_name, disc, results)
            except Exception as e:
                print(f"[DEBUG] Erreur lors de l'enregistrement pour {athlete_name} (discipline {disc}): {e}")
    
    background_tasks.add_task(store_athlete_results_background)
    
    # Trier tous les résultats par date
    try:
        all_results.sort(key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"))
    except Exception:
        pass
    
    chart_data = build_chart_data(all_results)
    
    # Calculer le temps écoulé et logger la performance
    elapsed_time = time.perf_counter() - start_time
    performance_logger.log_search_performance(search_term, elapsed_time, "/api/athlete-results")
    
    return {
        "athlete_name": athlete_name,
        "results": all_results,
        "chart_data": chart_data,
        "all_disciplines": True
    }