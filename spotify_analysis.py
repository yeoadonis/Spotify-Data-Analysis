
#turn the list in the file into a simplier one
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
            "ms_played": ligne["ms_played"],
            "timestamp": ligne["ts"]
        }

        simp_list.append(new_dict)

    return simp_list

def rank(data, key_type="song", mode="count"):
    counts = {}

    for ligne in data:

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
            value = ligne["ms_played"]

        counts[key] = counts.get(key, 0) + value

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_counts

from fastapi import FastAPI, UploadFile, File
import json


@app.post("/upload")
async def upload(file: UploadFile = File(engine.py)):
    content = await file.read()
    orig_list = json.loads(content)

    global DATA
    DATA = simplifier_list(orig_list)

    return {"message": "data loaded"}

@app.get("/top-songs")
def top_songs():
    return rank(DATA, key_type="song", mode="count")[:100]

@app.get("/top-artists")
def top_artists():
    return rank(DATA, key_type="artist", mode="count")[:100]
  
  
