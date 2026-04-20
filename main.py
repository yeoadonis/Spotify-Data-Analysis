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
  

# Endpoint pour l'upload du fichier
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

    return {"message": "data loaded"}

# Endpoint pour les chansons
@app.get("/top-songs")
def top_songs(mode: str = "count", period: str = "all"):
    filtered = filter_by_period(DATA, period)
    return rank(filtered, key_type="song", mode=mode)[:100]

# Endpoint pour les artistes
@app.get("/top-artists")
def top_artists(mode: str = "count", period: str = "all"):
    filtered = filter_by_period(DATA, period)
    return rank(filtered, key_type="artist", mode=mode)[:100]

# Endpoint pour les albums
@app.get("/top-albums")
def top_albums(mode: str = "count", period: str = "all"):
    filtered = filter_by_period(DATA, period)
    return rank(filtered, key_type="album", mode=mode)[:100]

#Endpoint pour les stats d'un item
@app.get("/get-item")
def stats(type, name, period, artist : str = None):
    
    if type == "song":
        identifier = (name, artist)
    elif type == "album":
        identifier = (name, artist)
    else:
        identifier = name

    return item_stats(DATA, identifier, period, key_type=type)
