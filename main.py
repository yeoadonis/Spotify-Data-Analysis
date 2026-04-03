
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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
  
  
