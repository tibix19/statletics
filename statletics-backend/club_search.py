import asyncio
import csv
import sys
import os

import httpx
from config import init_http_client, init_cache
from scraper import scrape_results_for_gender, log_worker
from db import store_results, normalize_name
from routes import disciplines_all  # pour récupérer la liste des disciplines

# DummyApp pour l'initialisation d'un state http_client
class DummyApp:
    pass

async def main():
    # Remove sys.argv check because on recherche sur tous les clubs
    csv_path = os.path.join(os.path.dirname(__file__), "clubs_athletisme_suisse.csv")
    clubs = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            clubs.append(row["Nom du Club"])
            
    print(f"Recherche sur {len(clubs)} clubs depuis le fichier CSV")
    
    # Initialiser l'application "dummy"
    app = DummyApp()
    app.state = type("State", (), {})()
    client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=30.0, write=10.0, pool=10.0))
    app.state.http_client = client
    init_cache()
    asyncio.create_task(log_worker())
    
    club_count = 0
    for club_name in clubs:
        club_count += 1
        print(f"{club_count} Club sélectionné : {club_name}")
        print(f"Début du scraping pour {club_name} sur {len(disciplines_all)*2} combinaisons")
        
        # Créer et lancer en parallèle toutes les tâches de scraping pour ce club
        club_tasks = []
        for disc_obj in disciplines_all:
            disc = disc_obj["code"]
            for gender in ["MAN", "WOM"]:
                print(f"Lancement du scraping {club_name} - discipline: {disc}, gender: {gender}")
                club_tasks.append(scrape_results_for_gender(app, club_name, gender, disc))
        club_results_list = await asyncio.gather(*club_tasks)
        
        # Regrouper les résultats par athlète et discipline
        grouped = {}  # {(athlete, discipline): [results, ...]}
        for results in club_results_list:
            for res in results:
                key = (res.get("name"), res.get("discipline"))
                grouped.setdefault(key, []).append(res)
        
        print(f"Scraping terminé pour {club_name}")
        for (athlete, discipline), results_group in grouped.items():
            store_results(athlete, discipline, results_group)
            print(f"Stocké {len(results_group)} résultat(s) pour {athlete} ({discipline})")
        print(f"Traitement complet du club {club_name}.\n")
    
    await client.aclose()
    print("Script terminé avec succès.")

if __name__ == "__main__":
    asyncio.run(main())
