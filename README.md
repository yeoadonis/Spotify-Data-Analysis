# Spotify-Data-Analysis
An android app and website destinated to have 2 functions : 

Give the top songs, artists and albums of a spotify account based of the spotify API and/or the extented streaming history.
Being a music player and spotify client

## Features

- Upload Spotify Extended Streaming History (JSON)
- Ranking by:
  - Songs
  - Artists
  - Albums
- Two modes:
  - Count (number of streams)
  - Time (minutes listened)
- Time filters:
  - Last 4 weeks
  - Last 6 months
  - Last 1 year
  - All time
-Listening from prenium spotify account
-Navigate and edit playlists

## Installation

1. Clone the repository

2. Install dependencies:
py -m pip install fastapi uvicorn python-multipart

3. Run the server:
py -m uvicorn main:app --reload

4. Open the app:
- Frontend: open site.html

## Languages used

- Python (FastAPI)
- JavaScript 
- HTML/CSS

## Notes

- Extended history must be requested from Spotify
- Real-time features require Spotify account connection
- Playback features require Spotify Premium
  

