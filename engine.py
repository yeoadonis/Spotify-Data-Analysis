from datetime import datetime, timedelta


# ========================
# SIMPLIFICATION DES DONNÉES
# ========================

def simplifier_list(orig_list):
    simp_list = []

    for ligne in orig_list:
        if ligne["master_metadata_track_name"] is None:
            continue

        if ligne["ms_played"] < 30000:
            continue

        simp_list.append({
            "track": ligne["master_metadata_track_name"],
            "artist": ligne["master_metadata_album_artist_name"],
            "album": ligne["master_metadata_album_album_name"],
            "min_played": round(ligne["ms_played"] / 60000),
            "ts": datetime.fromisoformat(ligne["ts"].replace("Z", ""))
        })

    return simp_list


# ========================
# FILTRAGE PAR PÉRIODE
# ========================

def filter_by_period(data, period):
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
        limit = datetime(last_date.year, 1, 1)
    elif period == "last year":
        start = datetime(last_date.year - 1, 1, 1)
        end = datetime(last_date.year - 1, 12, 31)
        return [l for l in data if start <= l["ts"] <= end]

    return [l for l in data if l["ts"] >= limit]


# ========================
# RANK (OPTIMISÉ)
# ========================

def rank(data, key_type="song", mode="count"):
    counts = {}

    for ligne in data:
        if key_type == "song":
            identifier = (ligne["track"], ligne["artist"])
        elif key_type == "album":
            identifier = (ligne["album"], ligne["artist"])
        else:
            identifier = ligne["artist"]

        if identifier not in counts:
            counts[identifier] = 0

        if mode == "count":
            counts[identifier] += 1
        else:
            counts[identifier] += ligne["min_played"]

    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


# ========================
# BUILD RANK MAP (O(1))
# ========================

def build_rank_map(ranking):
    return {identifier: i + 1 for i, (identifier, _) in enumerate(ranking)}


# ========================
# ITEM STATS
# ========================

def item_stats(data, identifier, key_type="song"):
    stats = {}

    # --- Pré-calcul des datasets ---
    data_all = data
    data_4w = filter_by_period(data, "4weeks")
    data_3m = filter_by_period(data, "3months")
    data_6m = filter_by_period(data, "6months")
    data_1y = filter_by_period(data, "1year")

    # --- Rankings + maps ---
    rank_all = build_rank_map(rank(data_all, key_type))
    rank_4w = build_rank_map(rank(data_4w, key_type))
    rank_3m = build_rank_map(rank(data_3m, key_type))
    rank_6m = build_rank_map(rank(data_6m, key_type))
    rank_1y = build_rank_map(rank(data_1y, key_type))

    # --- Stats principales ---
    listenings = []
    track_counts = {}
    album_counts = {}

    for ligne in data:
        match = False

        if key_type == "song":
            match = (ligne["track"], ligne["artist"]) == identifier
        elif key_type == "album":
            match = (ligne["album"], ligne["artist"]) == identifier
        else:
            match = ligne["artist"] == identifier

        if not match:
            continue

        # Dates
        listenings.append(ligne["ts"])

        # Count + time
        stats["count"] = stats.get("count", 0) + 1
        stats["min_played"] = stats.get("min_played", 0) + ligne["min_played"]

        # Metadata
        stats["artist"] = ligne["artist"]

        if key_type == "song":
            stats["track"] = ligne["track"]
            stats["album"] = ligne["album"]

        elif key_type == "album":
            stats["album"] = ligne["album"]

            
            track = ligne["track"]
            if track not in track_counts:
                track_counts[track] = 0
            track_counts[track] += 1

        elif key_type == "artist":

            
            track = ligne["track"]
            if track not in track_counts:
                track_counts[track] = 0
            track_counts[track] += 1
           
            
            album = ligne["album"]
            if album not in album_counts:
                album_counts[album] = 0
            album_counts[album] += 1
            stats["songs_top_of_alltime"]= sum(1 for item in rank_all if identifier == item[1] )
            stats["songs_top_of_4weeks"]= sum(1 for item in rank_4w if identifier == item[1] )
            stats["songs_top_of_3months"]= sum(1 for item in rank_3m if identifier == item[1] )
            stats["songs_top_of_6months"]= sum(1 for item in rank_6m if identifier == item[1] )
            stats["songs_top_of_1year"]= sum(1 for item in rank_1y if identifier == item[1] )
    


    stats["first_listening"] = min(listenings)
    stats["last_listening"] = max(listenings)

    
    stats["rank_alltime"] = rank_all.get(identifier)
    stats["rank_4weeks"] = rank_4w.get(identifier)
    stats["rank_3months"] = rank_3m.get(identifier)
    stats["rank_6months"] = rank_6m.get(identifier)
    stats["rank_1year"] = rank_1y.get(identifier)

    
    if key_type == "album":
        stats["tracklist"] = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)

    if key_type == "artist":
        stats["top_tracks"] = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)
        stats["top_albums"] = sorted(album_counts.items(), key=lambda x: x[1], reverse=True)

    return stats
 
