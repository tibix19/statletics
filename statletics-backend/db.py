import os
from pymongo import MongoClient
from pymongo import UpdateOne
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# Load .env from parent directory
load_dotenv(Path(__file__).parent.parent / '.env')

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
    
    host = os.getenv("MONGO_HOST")
    port = os.getenv("MONGO_PORT")
    connection_string = f"mongodb://{host}:{port}"
    print(f"Connection string: {connection_string}")
    
    # client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017"))
    client = MongoClient(connection_string)
    return client.get_database("results_swiss_athletics")

def get_athlete_gender(athlete_name):
    normalized = normalize_name(athlete_name)
    db = get_db()
    collection = db["results"]
    doc = collection.find_one({"normalized_name": normalized}, {"gender": 1})
    return doc.get("gender") if doc and "gender" in doc else None

def is_data_recent(athlete_name, max_days=2):
    """
    Vérifie si les données d'un athlète ont été mises à jour récemment.
    Retourne True si les données ont été mises à jour dans les derniers 'max_days' jours,
    False sinon ou si l'athlète n'existe pas dans la base de données.
    """
    normalized = normalize_name(athlete_name)
    db = get_db()
    collection = db["results"]
    
    # Récupérer uniquement le champ last_updated
    doc = collection.find_one({"normalized_name": normalized}, {"last_updated": 1})
    
    if not doc or "last_updated" not in doc:
        return False
        
    last_updated = doc["last_updated"]
    current_time = datetime.now()
    time_difference = current_time - last_updated
    
    # Vérifier si la mise à jour date de moins de max_days jours
    return time_difference.days < max_days

def store_results(athlete_name, discipline, new_results):
    """
    Met à jour (ou insère) le document de l'athlète avec les résultats pour une discipline donnée.
    Si le document existe déjà, fusionne les résultats existants pour la discipline :
      - Mise à jour (remplacement) des résultats existants pour l'année 2025 (basée sur le champ "year")
      - Ajout des nouveaux résultats si non présents
    Le champ "gender" est retiré des sous-documents et stocké uniquement au niveau du document principal.
    Ajoute également un champ "last_updated" avec la date/heure actuelle.
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

    # Ajout de la date de dernière mise à jour
    current_time = datetime.now()
    
    update_doc = {
        "$set": {
            "athlete_name": athlete_name,
            "gender": gender,
            "normalized_name": normalized,
            f"results.{discipline}": merged,
            "last_updated": current_time
        }
    }
    result = collection.update_one({"normalized_name": normalized}, update_doc, upsert=True)
    print(f"[DEBUG] store_results pour {athlete_name} mise à jour, matched: {result.matched_count}, modified: {result.modified_count}")
    return result.raw_result

def check_search_history(search_term: str):
    """
    Vérifie si un terme de recherche existe dans l'historique et retourne des informations sur sa fraîcheur.
    
    Args:
        search_term (str): Le terme de recherche à vérifier
        
    Returns:
        dict: Un dictionnaire contenant:
            - 'exists' (bool): True si le terme existe dans l'historique
            - 'age_days' (int): Nombre de jours depuis la dernière recherche
            - 'same_year' (bool): True si la recherche date de l'année en cours
            - 'recent' (bool): True si la recherche date de moins de 3 jours
    """
    try:
        db = get_db()
        collection = db["search_history"]
        
        # Rechercher le terme dans l'historique, trié par date décroissante
        result = collection.find_one(
            {"search_term": search_term},
            sort=[("timestamp", -1)]  # -1 pour ordre décroissant (le plus récent d'abord)
        )
        
        current_time = datetime.now()
        current_year = current_time.year
        
        if not result:
            return {"exists": False, "age_days": None, "same_year": False, "recent": False}
        
        last_search_time = result["timestamp"]
        time_difference = current_time - last_search_time
        age_days = time_difference.days
        
        return {
            "exists": True,
            "age_days": age_days,
            "same_year": last_search_time.year == current_year,
            "recent": age_days < 3
        }
    except Exception as e:
        print(f"Erreur lors de la vérification de l'historique de recherche: {e}")
        return {"exists": False, "age_days": None, "same_year": False, "recent": False}

def update_search_history(search_term: str, endpoint: str):
    """
    Met à jour l'historique de recherche pour un terme donné.
    Si le terme existe déjà, met à jour son timestamp, sinon crée une nouvelle entrée.
    
    Args:
        search_term (str): Le terme de recherche utilisé
        endpoint (str): L'endpoint API qui a été appelé
    """
    try:
        db = get_db()
        collection = db["search_history"]
        
        # Mettre à jour le document s'il existe, sinon en créer un nouveau
        result = collection.update_one(
            {"search_term": search_term},
            {"$set": {"timestamp": datetime.now(), "endpoint": endpoint}},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"[DEBUG] Nouveau terme de recherche '{search_term}' enregistré dans search_history, id: {result.upserted_id}")
        else:
            print(f"[DEBUG] Terme de recherche '{search_term}' mis à jour dans search_history")
            
        return result.upserted_id or True
    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'historique de recherche: {e}")
        return None

def store_search_history(search_term: str, endpoint: str):
    """
    Enregistre un terme de recherche dans la collection 'search_history'.
    Cette fonction est maintenue pour compatibilité, mais update_search_history est préférable.
    
    Args:
        search_term (str): Le terme de recherche utilisé
        endpoint (str): L'endpoint API qui a été appelé
    """
    return update_search_history(search_term, endpoint)