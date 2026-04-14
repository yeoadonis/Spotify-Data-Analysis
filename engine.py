from datetime import datetime, timedelta

# Fonction pour transformer les données brutes en données exploitables
def simplifier_list(orig_list):
    simp_list = []

    for ligne in orig_list:
        # filtre minimum
        if ligne["master_metadata_track_name"] is None:
            continue

        if ligne["ms_played"] < 30000:
            continue

        new_dict = {
            "track": ligne["master_metadata_track_name"],
            "artist": ligne["master_metadata_album_artist_name"],
            "album": ligne["master_metadata_album_album_name"],
            "min_played": round(ligne["ms_played"]/60000),
            "timestamp": ligne["ts"]
        }

        simp_list.append(new_dict)

    return simp_list

# Fonction pour filtrer les données selon la période choisie
def filter_by_period(data, period):

    for ligne in data:
        ligne["ts"] = datetime.fromisoformat(ligne["timestamp"].replace("Z", ""))
        
    last_date = max(ligne["ts"] for ligne in data)
    
    if period == "all":
        return data

    
    if period == "4weeks":
        limit = last_date - timedelta(days=28)

    elif period == "3months":
        limit = last_date - timedelta(days=90)

    elif period == "6months":
        limit = last_date - timedelta(days=182)

    elif period == "1year":
        limit = last_date - timedelta(days=365)

    
    filtered = []
    for ligne in data:
        if ligne["ts"] >= limit:
            filtered.append(ligne)

    return filtered

# Fonction pour classer les données selon le mode choisi
def rank(data, key_type="song", mode="count", period="4weeks"):
    counts = {}

    for ligne in data  :
        

        # définir la clé selon le type
        if key_type == "song":
            key = (ligne["track"], ligne["artist"])
        elif key_type == "album":
            key = (ligne["album"], ligne["artist"])
        elif key_type == "artist":
            key = ligne["artist"]

        # définir la valeur selon le mode
        if mode == "count":
            value = 1
        elif mode == "time":
            value = ligne["min_played"]

        counts[key] = counts.get(key, 0) + value

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_counts

 
