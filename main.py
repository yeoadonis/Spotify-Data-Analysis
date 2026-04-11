
from fastapi import FastAPI, UploadFile, File
import json
from engine import simplifier_list() rank()


app = FastApi()

DATA = []

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
  


@app.post("/upload")
async def upload(file: UploadFile (...)):
    content = await file.read()
    orig_list = json.loads(content)

    global DATA
    DATA = simplifier_list(orig_list)

    return {"message": "data loaded"}

@app.get("/top-songs")
def top_songs(mode: str = "count", period: str = "all"):
    filtered = filter_by_period(DATA, period)
    return rank(filtered, key_type="song", mode=mode)[:250]


@app.get("/top-artists")
def top_artists(mode: str = "count", period: str = "all"):
    filtered = filter_by_period(DATA, period)
    return rank(filtered, key_type="artist", mode=mode)[:250]


@app.get("/top-albums")
def top_albums(mode: str = "count", period: str = "all"):
    filtered = filter_by_period(DATA, period)
    return rank(filtered, key_type="album", mode=mode)[:250]
  
