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
            "timestamp": ligne["ts"],
             
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

    elif period == "This year":
        limit = datetime.now().replace(year=datetime.now().year, month=1, day=1)
    
    elif period == "last year":
        limit = datetime.now().replace(year=datetime.now().year-1, month=1, day=1)       
        limit_end = datetime.now().replace(year=datetime.now().year-1, month=12, day=31)             
    filtered = []
    for ligne in data:
        if ligne["ts"] >= limit and (period != "last year" or ligne["ts"] <= limit_end):
            filtered.append(ligne)

    return filtered

# Fonction pour classer les données selon le mode choisi
def rank(data, key_type="song", mode="count", period="4weeks"):
    counts = {}

    for ligne in data  :
        

        # définir l'identifiant selon le type
        if key_type == "song":
            identifier = (ligne["track"], ligne["artist"])
        elif key_type == "album":
           identifier = (ligne["album"], ligne["artist"])
        elif key_type == "artist":
            identifier = ligne["artist"]
        
        for ligne in filter_by_period(data, period):
            if mode == "count":
                counts[identifier] = count_item(data, identifier, key_type)
            elif mode == "time":
                counts[identifier] = time_item(data, identifier, key_type)
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_counts

def count_item(data, identifier, key_type="song"):
    count = 0
    for ligne in data:
        if key_type == "song":
            if (ligne["track"], ligne["artist"]) == identifier:
                count += 1
        elif key_type == "album":
            if (ligne["album"], ligne["artist"]) == identifier:
                count += 1
        elif key_type == "artist":
            if ligne["artist"] == identifier:
                count += 1
    return count
def time_item(data, identifier, key_type="song"):
    total_time = 0
    for ligne in data:
        if key_type == "song":
            if (ligne["track"], ligne["artist"]) == identifier:
                total_time += ligne["min_played"]
        elif key_type == "album":
            if (ligne["album"], ligne["artist"]) == identifier:
                total_time += ligne["min_played"]
        elif key_type == "artist":
            if ligne["artist"] == identifier:
                total_time += ligne["min_played"]
    return total_time

# Fonction pour calculer le nombre total d'écoutes ou le temps total d'écoute
def total_listenings(data, mode="count"):
    
    hours = sum(ligne["min_played"] for ligne in data) / 60

    if mode == "count":
        return len(data)
    elif mode == "time":
        return sum(ligne["min_played"] for ligne in data)
   

def item_stats(data, identifier, key_type="song",):
    stats = {}
    all_listenings = []
    
    if key_type == "song":
        for ligne in data:
            
            if (ligne["track"], ligne["artist"]) == identifier:
                
                
                all_listenings.append(ligne["ts"])
                stats["first_listening"] = min(all_listenings)
                stats["last_listening"] = max(all_listenings)
                stats["track"] = ligne["track"]
                stats["artist"] = ligne["artist"]
                stats["album title"] = ligne["album"]
                stats["min_played"] = stats.get("min_played", 0) + ligne["min_played"]
                stats["count"] = stats.get("count", 0) + 1
                stats["rank_alltime"] = rank(data, key_type="song", mode="count", period="all").index(((ligne["track"], ligne["artist"]), stats["count"])) + 1
                stats["rank_4weeks"] = rank(filter_by_period(data, "4weeks"), key_type="song", mode="count", period="4weeks").index(((ligne["track"], ligne["artist"]), stats["count"])) + 1
                stats["rank_3months"] = rank(filter_by_period(data, "3months"), key_type="song", mode="count", period="3months").index(((ligne["track"], ligne["artist"]), stats["count"])) + 1
                stats["rank_6months"] = rank(filter_by_period(data, "6months"), key_type="song", mode="count", period="6months").index(((ligne["track"], ligne["artist"]), stats["count"])) + 1
                stats["rank_1year"] = rank(filter_by_period(data, "1year"), key_type="song", mode="count", period="1year").index(((ligne["track"], ligne["artist"]), stats["count"])) + 1
    
    if key_type == "album":
        tracknames =  {}
        for ligne in data:
            
            if (ligne["album"], ligne["artist"]) == identifier:
                all_listenings = stats.get("listenings", [])
                all_listenings.append(ligne["ts"])
                stats["listenings"] = all_listenings
                stats["first_listening"] = min(all_listenings)
                stats["last_listening"] = max(all_listenings)
                stats["album title"] = ligne["album"]
                stats["artist"] = ligne["artist"]
                stats["min_played"] = stats.get("min_played", 0) + ligne["min_played"]
                stats["count"] = stats.get("count", 0) + 1
                stats["rank_alltime"] = rank(data, key_type="album", mode="count", period="all").index(((ligne["album"], ligne["artist"]), stats["count"])) + 1
                stats["rank_4weeks"] = rank(filter_by_period(data, "4weeks"), key_type="album", mode="count", period="4weeks").index(((ligne["album"], ligne["artist"]), stats["count"])) + 1
                stats["rank_3months"] = rank(filter_by_period(data, "3months"), key_type="album", mode="count", period="3months").index(((ligne["album"], ligne["artist"]), stats["count"])) + 1
                stats["rank_6months"] = rank(filter_by_period(data, "6months"), key_type="album", mode="count", period="6months").index(((ligne["album"], ligne["artist"]), stats["count"])) + 1
                stats["rank_1year"] = rank(filter_by_period(data, "1year"), key_type="album", mode="count", period="1year").index(((ligne["album"], ligne["artist"]), stats["count"])) + 1
                tracknames[ligne["track"]] = count_item(data, (ligne["track"], ligne["artist"]), key_type="song")
                stats["tracklist"] = sorted(tracknames.items(), key=lambda x: x[1], reverse=True)
                
    if key_type == "artist":
        tracknames =  {}
        albumnames = {}
        for ligne in data:
            
            if ligne["artist"] == identifier:
                
                all_listenings = stats.get("listenings", [])
                all_listenings.append(ligne["ts"])
                stats["listenings"] = all_listenings
                stats["first_listening"] = min(all_listenings)
                stats["last_listening"] = max(all_listenings)
                stats["artist"] = ligne["artist"]
                stats["min_played"] = stats.get("min_played", 0) + ligne["min_played"]
                stats["count"] = stats.get("count", 0) + 1
                stats["rank_alltime"] = rank(data, key_type="artist", mode="count", period="all").index((ligne["artist"], stats["count"])) + 1
                stats["rank_4weeks"] = rank(filter_by_period(data, "4weeks"), key_type="artist", mode="count", period="4weeks").index((ligne["artist"], stats["count"])) + 1
                stats["rank_3months"] = rank(filter_by_period(data, "3months"), key_type="artist", mode="count", period="3months").index((ligne["artist"], stats["count"])) + 1
                stats["rank_6months"] = rank(filter_by_period(data, "6months"), key_type="artist", mode="count", period="6months").index((ligne["artist"], stats["count"])) + 1
                stats["rank_1year"] = rank(filter_by_period(data, "1year"), key_type="artist", mode="count", period="1year").index((ligne["artist"], stats["count"])) + 1
                tracknames[ligne["track"]] = count_item(data, (ligne["track"], ligne["artist"]), key_type="song")
                stats["top tracks"] = sorted(tracknames.items(), key=lambda x: x[1], reverse=True)
                albumnames[ligne["album"]] = count_item(data, (ligne["album"], ligne["artist"]), key_type="album")
                stats["top albums"] = sorted(albumnames.items(), key=lambda x: x[1], reverse=True)
                stats["number_of_songs_in_top_250_AOT"] = 0
               
                for songs in rank(data, key_type="song", mode="count", period="all"):
                    if songs[0][1] == identifier:
                        stats["number_of_songs_in_top_250_AOT"] += 1
                
                
                for songs in rank(data, key_type="song", mode="count", period="4weeks"):
                    if songs[0][1] == identifier:
                        stats["number_of_songs_in_top_250_AOT"] += 1
                        
                
                for songs in rank(data, key_type="song", mode="count", period="3months"):
                    if songs[0][1] == identifier:
                        stats["number_of_songs_in_top_250_AOT"] += 1
                    
                for songs in rank(data, key_type="song", mode="count", period="6months"):
                    if songs[0][1] == identifier:
                        stats["number_of_songs_in_top_250_AOT"] += 1
                
                for songs in rank(data, key_type="song", mode="count", period="1year"):
                    if songs[0][1] == identifier:
                        stats["number_of_songs_in_top_250_AOT"] += 1
                
    return stats
 
