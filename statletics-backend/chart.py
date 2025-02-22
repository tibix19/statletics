from datetime import datetime

def convert_time_to_seconds(time_str):
    """
    Convertit une chaîne de temps au format "SS.xx" ou "M:SS.xx" en secondes.
    """
    try:
        if ':' in time_str:
            minutes, seconds = time_str.split(':')
            return float(minutes) * 60 + float(seconds)
        else:
            return float(time_str)
    except Exception as e:
        print(f"Erreur de conversion de temps ({time_str}):", e)
        return None

def build_chart_data(results):
    """
    Construit les données pour le graphique d'évolution des performances.
    
    Processus:
    1. Convertit les dates du format 'DD.MM.YYYY' en objets datetime
    2. Convertit les résultats en nombres flottants (gère les virgules)
    3. Trie les résultats par date croissante
    4. Prépare deux listes parallèles: dates et valeurs
    
    Retourne:
    - Un dictionnaire avec:
        * labels: Liste des dates triées
        * values: Liste des performances correspondantes
    """
    try:
        sorted_results = sorted(results, key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"))
    except Exception as e:
        print("Erreur de tri des résultats:", e)
        sorted_results = results

    labels = []
    values = []
    for result in sorted_results:
        labels.append(result["date"])
        seconds = convert_time_to_seconds(result["result"])
        if seconds is not None:
            values.append(seconds)
    return {"labels": labels, "values": values}
