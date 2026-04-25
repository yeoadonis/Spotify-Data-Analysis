from datetime import datetime, timedelta
from collections import defaultdict


def simplifier_list(orig_list):
    simp_list = []
    for ligne in orig_list:
        if ligne.get("master_metadata_track_name") is None or ligne.get("ms_played", 0) < 30000:
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
    if not data: return []
    last_date = max(ligne["ts"] for ligne in data)

    if period == "all": return data
    
    if period == "4weeks": limit = last_date - timedelta(days=28)
    elif period == "3months": limit = last_date - timedelta(days=90)
    elif period == "6months": limit = last_date - timedelta(days=182)
    elif period == "1year": limit = last_date - timedelta(days=365)
    elif period == "this year": limit = datetime(last_date.year, 1, 1)
    elif period == "last year":
        start = datetime(last_date.year - 1, 1, 1)
        end = datetime(last_date.year - 1, 12, 31)
        return [l for l in data if start <= l["ts"] <= end]
    else: return data

    return [l for l in data if l["ts"] >= limit]


from collections import defaultdict
from datetime import datetime

class ListeningContext:
    def __init__(self, data):
        self.data = data
        self.songs = {}
        self.artists = {}
        self.albums = {}
        self.rank_maps = {"count": {}, "time": {}}
        
        self._build_indices()
        self._generate_all_rankings()

    def _build_indices(self):
        for ligne in self.data:
            s_id = (ligne["track"], ligne["artist"])
            ar_id = ligne["artist"]
            al_id = (ligne["album"], ligne["artist"])
            ts = ligne["ts"]
            
            duration = ligne["min_played"]
            
            if s_id not in self.songs:
                self.songs[s_id] = {"count": 0, "min_played": 0, "first": ts, "last": ts, "album": ligne["album"]}
            self.songs[s_id]["count"] += 1
            self.songs[s_id]["min_played"] += duration
            self.songs[s_id]["last"] = max(self.songs[s_id]["last"], ts)

            if ar_id not in self.artists:
                self.artists[ar_id] = {"count": 0, "min_played": 0, "tracks": defaultdict(int), "albums": defaultdict(int), "first": ts, "last": ts}
            self.artists[ar_id]["count"] += 1
            self.artists[ar_id]["min_played"] += duration
            self.artists[ar_id]["tracks"][ligne["track"]] += 1
            self.artists[ar_id]["albums"][ligne["album"]] += 1
            self.artists[ar_id]["last"] = max(self.artists[ar_id]["last"], ts)

            if al_id not in self.albums:
                self.albums[al_id] = {"count": 0, "min_played": 0, "tracks": defaultdict(int), "first": ts, "last": ts}
            self.albums[al_id]["count"] += 1
            self.albums[al_id]["min_played"] += duration
            self.albums[al_id]["tracks"][ligne["track"]] += 1
            self.albums[al_id]["last"] = max(self.albums[al_id]["last"], ts)

    def _generate_all_rankings(self):
        from engine import filter_by_period 
        periods = ["all", "4weeks", "3months", "6months", "1year", "this_year"]
        
        for p in periods:
            p_data = filter_by_period(self.data, p)
            for mode in ["count", "time"]:
                self.rank_maps[mode][p] = {
                    "song": self._build_rank_map(p_data, "song", mode),
                    "artist": self._build_rank_map(p_data, "artist", mode),
                    "album": self._build_rank_map(p_data, "album", mode)
                }

    def _build_rank_map(self, data, key_type, mode):
        counts = defaultdict(int)
        for l in data:
            if key_type == "song": id_ = (l["track"], l["artist"])
            elif key_type == "album": id_ = (l["album"], l["artist"])
            else: id_ = l["artist"]
            
            counts[id_] += 1 if mode == "count" else l["min_played"]
        
        sorted_list = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return {item[0]: (i + 1, item[1]) for i, item in enumerate(sorted_list)}

    def get_item_stats(self, identifier, key_type, mode="count"):
        res = {}
        
        if key_type == "song":
            base = self.songs.get(identifier)
            if not base: return {}
            res = {
                "track": identifier[0], "artist": identifier[1], "album": base["album"],
                "count": base["count"], "min_played": base["min_played"],
                "first_listening": base["first"], "last_listening": base["last"]
            }
        elif key_type == "artist":
            base = self.artists.get(identifier)
            if not base: return {}
            res = {
                "artist": identifier, "count": base["count"], "min_played": base["min_played"],
                "first_listening": base["first"], "last_listening": base["last"],
                "number_of_songs": len(base["tracks"]), "number_of_albums": len(base["albums"]),
                "top_tracks": sorted(base["tracks"].items(), key=lambda x: x[1], reverse=True),
                "top_albums": sorted(base["albums"].items(), key=lambda x: x[1], reverse=True),
                "songs_in_top_100": self._count_top_100_songs(identifier, mode)
            }
        elif key_type == "album":
            base = self.albums.get(identifier)
            if not base: return {}
            res = {
                "album": identifier[0], "artist": identifier[1],
                "count": base["count"], "min_played": base["min_played"],
                "first_listening": base["first"], "last_listening": base["last"],
                "tracklist": sorted(base["tracks"].items(), key=lambda x: x[1], reverse=True)
            }

        mapping = {
            "all": "rank_alltime", "4weeks": "rank_4weeks",
            "3months": "rank_3months", "6months": "rank_6months", "1year": "rank_1year"
        }

        for p_key, js_key in mapping.items():
            rank_info = self.rank_maps[mode].get(p_key, {}).get(key_type, {}).get(identifier)
            res[js_key] = rank_info[0] if rank_info else "N/A"
            
        return res

    def _count_top_100_songs(self, artist_name, mode):
        top_100_map = self.rank_maps[mode]["all"]["song"]
        count = 0
        for (track, artist), (rank, val) in top_100_map.items():
            if rank <= 100 and artist == artist_name:
                count += 1
        return count
