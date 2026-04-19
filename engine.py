from datetime import datetime, timedelta


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



def build_rank_map(ranking):
    return {identifier: i + 1 for i, (identifier, _) in enumerate(ranking)}



def item_stats(data, identifier, key_type="song"):
    stats = {}

    data_all = data
    data_4w = filter_by_period(data, "4weeks")
    data_3m = filter_by_period(data, "3months")
    data_6m = filter_by_period(data, "6months")
    data_1y = filter_by_period(data, "1year")

    rank_all = build_rank_map(rank(data_all, key_type))
    rank_4w = build_rank_map(rank(data_4w, key_type))
    rank_3m = build_rank_map(rank(data_3m, key_type))
    rank_6m = build_rank_map(rank(data_6m, key_type))
    rank_1y = build_rank_map(rank(data_1y, key_type))

    if key_type == "song":
        item_data = [l for l in data if (l["track"], l["artist"]) == identifier]
    elif key_type == "album":
        item_data = [l for l in data if (l["album"], l["artist"]) == identifier]
    else:
        item_data = [l for l in data if l["artist"] == identifier]

    if not item_data:
        return {}

    listenings = []
    track_counts = {}
    album_counts = {}
    unique_tracks = set()
    unique_albums = set()

    for ligne in item_data:
        ts = ligne["ts"]
        track = ligne["track"]
        album = ligne["album"]

        listenings.append(ts)

        stats["count"] = stats.get("count", 0) + 1
        stats["min_played"] = stats.get("min_played", 0) + ligne["min_played"]

        track_counts[track] = track_counts.get(track, 0) + 1
        album_counts[album] = album_counts.get(album, 0) + 1

        unique_tracks.add(track)
        unique_albums.add(album)

        stats["artist"] = ligne["artist"]

        if key_type == "song":
            stats["track"] = track
            stats["album"] = album
        elif key_type == "album":
            stats["album"] = album

    stats["first_listening"] = min(listenings)
    stats["last_listening"] = max(listenings)

    stats["rank_alltime"] = rank_all.get(identifier)
    stats["rank_4weeks"] = rank_4w.get(identifier)
    stats["rank_3months"] = rank_3m.get(identifier)
    stats["rank_6months"] = rank_6m.get(identifier)
    stats["rank_1year"] = rank_1y.get(identifier)

    if key_type == "song":
        return stats

    elif key_type == "album":
        stats["tracklist"] = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)
        return stats

    else:
        stats["number_of_songs"] = len(unique_tracks)
        stats["number_of_albums"] = len(unique_albums)

        stats["top_tracks"] = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)
        stats["top_albums"] = sorted(album_counts.items(), key=lambda x: x[1], reverse=True)

        rank_all_songs = rank(data_all, key_type="song")
        top_100 = rank_all_songs[:100]

        stats["songs_in_top_100"] = sum(
            1 for item in top_100
            if item[0][1] == identifier
        )

        return stats
 
