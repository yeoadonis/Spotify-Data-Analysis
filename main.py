from fastapi import FastAPI, UploadFile, File
import json
import zipfile
import io
from engine import simplifier_list, rank, filter_by_period



app = FastAPI()

DATA = []

from fastapi.middleware.cors import CORSMiddleware
# Autoriser les requêtes de n'importe quelle origine 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
  
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()

    global DATA

    
    if file.filename.endswith(".json"):
        orig_list = json.loads(content)


    elif file.filename.endswith(".zip"):
        orig_list = []

        zip_file = zipfile.ZipFile(io.BytesIO(content))

        for name in zip_file.namelist():
            if name.endswith(".json"):
                with zip_file.open(name) as f:
                    file_content = f.read().decode("utf-8")
                    data = json.loads(file_content)
                    orig_list.extend(data)

    DATA = simplifier_list(orig_list)

    global CONTEXT
    CONTEXT = ListeningContext(DATA) 
    return {"message": "data loaded"}
@app.get("/top-songs")
def top_songs(period: str = "all", mode: str = "count"):
    
    ranks = CONTEXT.rank_maps[mode].get(period, CONTEXT.rank_maps[mode]["all"])["song"]
    return [[x[0], x[1][1]] for x in sorted(ranks.items(), key=lambda x: x[1][0])][:250]
@app.get("/top-artists")
def top_artists(period: str = "all", mode: str = "count"):
    ranks = CONTEXT.rank_maps[mode].get(period, CONTEXT.rank_maps[mode]["all"])["artist"]
    return [[x[0], x[1][1]] for x in sorted(ranks.items(), key=lambda x: x[1][0])][:250]

@app.get("/top-albums")
def top_albums(period: str = "all", mode: str = "count"):
    ranks = CONTEXT.rank_maps[mode].get(period, CONTEXT.rank_maps[mode]["all"])["album"]
    return [[x[0], x[1][1]] for x in sorted(ranks.items(), key=lambda x: x[1][0])][:250]

@app.get("/get-item")
def get_item(type: str, name: str, artist: str = None, mode: str = "count"):
    identifier = (name, artist) if type in ["song", "album"] else name
    
    return CONTEXT.get_item_stats(identifier, type, mode)
