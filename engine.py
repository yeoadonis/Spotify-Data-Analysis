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
    elif period == "thisyear": limit = datetime(last_date.year, 1, 1)
    elif period == "lastyear":
        start = datetime(last_date.year - 1, 1, 1)
        end = datetime(last_date.year - 1, 12, 31)
        return [l for l in data if start <= l["ts"] and l["ts"] <= end]
    else: return data

    return [l for l in data if l["ts"] >= limit]

class ListeningContext:
    def __init__(self, data):
        self.data = data
        self.songs = {}
        self.artists = {}
        self.albums = {}
        self.rank_maps = {"count": {}, "time": {}}
        
        self._build_indices()
        self._generate_all_rankings()
        self.general_stats()

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
        
        periods = ["all", "4weeks", "3months", "6months", "1year", "thisyear", "lastyear"]
        
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
                "songs_in_top_100 All Time": self._count_top_100_songs_alltime(identifier, mode),
                "songs_in_top_100 Last Year": self._count_top_100_songs_1year(identifier, mode),
                "songs_in_top_100 Last 4 Weeks": self._count_top_100_songs_4weeks(identifier, mode)
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
            "3months": "rank_3months", "6months": "rank_6months", "1year": "rank_1year",
            "thisyear": "rank_thisyear", "lastyear": "rank_lastyear"
        }

        for p_key, js_key in mapping.items():
            rank_info = self.rank_maps[mode].get(p_key, {}).get(key_type, {}).get(identifier)
            res[js_key] = rank_info[0] if rank_info else "N/A"
                

        return res

    def _count_top_100_songs_alltime(self, artist_name, mode):
        top_100_map = self.rank_maps[mode]["all"]["song"]
        count = 0
        for (track, artist), (rank, val) in top_100_map.items():
            if rank <= 100 and artist == artist_name:
                count += 1
        return count
    
    def _count_top_100_songs_1year(self, artist_name, mode):
        top_100_map = self.rank_maps[mode]["1year"]["song"]
        count = 0
        for (track, artist), (rank, val) in top_100_map.items():
            if rank <= 100 and artist == artist_name:
                count += 1
        return count

    def _count_top_100_songs_4weeks(self, artist_name, mode):
        top_100_map = self.rank_maps[mode]["4weeks"]["song"]
        count = 0
        for (track, artist), (rank, val) in top_100_map.items():
            if rank <= 100 and artist == artist_name:
                count += 1
        return count

    def listening_per_year(self):
        yearly_counts = defaultdict(int)
        for s in self.data:
            year = s["ts"].year
            yearly_counts[year] += s["min_played"]
        return dict(yearly_counts)

    def get_weekly_profile(self):
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_counts = {d: 0 for d in days}
        for ligne in self.data:
            if "ts" in ligne and ligne["ts"]:
                jour_index = ligne["ts"].weekday() 
                weekly_counts[days[jour_index]] += 1
        return weekly_counts

    def get_hourly_profile(self):
        
        hourly_counts = {str(h): 0 for h in range(24)}
        for ligne in self.data:
            if "ts" in ligne and ligne["ts"]:
                heure = str(ligne["ts"].hour)
                hourly_counts[heure] += 1
        return hourly_counts

    def get_monthly_profile(self):
        
        monthly_counts = {str(m): 0 for m in range(1, 13)}
        for ligne in self.data:
            if "ts" in ligne and ligne["ts"]:
                mois = str(ligne["ts"].month)
                monthly_counts[mois] += 1
        return monthly_counts


        
    
    def general_stats(self):
        return {
            "total_songs": len(self.songs),
            "total_artists": len(self.artists),
            "total_albums": len(self.albums),
            "total_listening_time": sum(s["min_played"] for s in self.songs.values()),
            "total_listening_count": sum(s["count"] for s in self.songs.values()),
            "first_listening": min(s["first"] for s in self.songs.values()) if self.songs else None,
            "date_of_first_listening": min(s["first"] for s in self.songs.values()) if self.songs else None,
            "date_of_last_listening": max(s["last"] for s in self.songs.values()) if self.songs else None, 
            "listening_per_day": sum(s["min_played"] for s in self.songs.values()) / (max(s["last"] for s in self.songs.values()) - min(s["first"] for s in self.songs.values())).days if self.songs else None,
        
        }

    def listening_profiles(self):
        return {
            "weekly": self.get_weekly_profile(),
            "hourly": self.get_hourly_profile(),
            "monthly": self.get_monthly_profile(),
        }
