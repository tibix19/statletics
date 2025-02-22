import os
from pymongo import MongoClient
from pymongo import UpdateOne

def normalize_name(name: str) -> str:
    """
    Normalise le nom en minuscules et en supprimant les espaces superflus.
    """
    return " ".join(name.lower().split())

def get_db():
    """
    Initialise et retourne l'instance de la base de données MongoDB.
    Le connection string est récupéré via l'environnement (MONGO_URI) ou en fallback sur localhost.
    """
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017"))
    return client.get_database("results_swiss_athletics")

def get_athlete_gender(athlete_name):
    normalized = normalize_name(athlete_name)
    db = get_db()
    collection = db["results"]
    doc = collection.find_one({"normalized_name": normalized}, {"gender": 1})
    return doc.get("gender") if doc and "gender" in doc else None

def store_results(athlete_name, discipline, new_results):
    """
    Met à jour (ou insère) le document de l’athlète avec les résultats pour une discipline donnée.
    Si le document existe déjà, fusionne les résultats existants pour la discipline :
      - Mise à jour (remplacement) des résultats existants pour l’année 2025 (basée sur le champ "year")
      - Ajout des nouveaux résultats si non présents
    Le champ "gender" est retiré des sous-documents et stocké uniquement au niveau du document principal.
    """
    normalized = normalize_name(athlete_name)
    db = get_db()
    collection = db["results"]

    # Extraction du genre à partir du premier résultat, si disponible
    gender = new_results[0].get("gender") if new_results and "gender" in new_results[0] else None

    # Nettoyer les résultats pour retirer le champ "gender"
    clean_results = [{k: v for k, v in result.items() if k != "gender"} for result in new_results]

    # Recherche du document pour l'athlète
    doc = collection.find_one({"normalized_name": normalized})
    if doc:
        existing = doc.get("results", {}).get(discipline, [])
        merged = existing.copy()
        for new in clean_results:
            found = False
            for i, exist in enumerate(merged):
                if exist.get("date") == new.get("date"):
                    # Si le nouveau résultat concerne l'année 2025, on le met à jour
                    if new.get("year") and "2025" in new["year"]:
                        merged[i] = new
                    found = True
                    break
            if not found:
                merged.append(new)
    else:
        merged = clean_results

    update_doc = {
        "$set": {
            "athlete_name": athlete_name,
            "gender": gender,
            "normalized_name": normalized,
            f"results.{discipline}": merged
        }
    }
    result = collection.update_one({"normalized_name": normalized}, update_doc, upsert=True)
    print(f"[DEBUG] store_results pour {athlete_name} mise à jour, matched: {result.matched_count}, modified: {result.modified_count}")
    return result.raw_result
