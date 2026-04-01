
#turn the list in the file into a simplier one
def simplifier_list(orig_list) 
 for ligne in orig_list:
     new_dict = {}

     new_dict["track"] = ligne["master_metadata_track_name"]
     new_dict["artist"] = ligne["master_metadata_album_artist_name"]
     new_dict["album"] = ligne["master_metadata_album_album_name"]
     new_dict["ms_played"] = ligne["ms_played"]
     new_dict["timestamp"] = ligne["ts"]

     simp_list.append(new_dict) 

     return simp_list

#Range les titres par nombre d'écoutes
def rank_songs(data):
    counts = {}

    for ligne in data:
        key = (ligne["track"], ligne["artist"])
        counts[key] = counts.get(key, 0) + 1

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_counts


#Range les titres par durée d'écoute.
def rank_songsbis(data):
    counts = {}

    for ligne in data:
        key = (ligne["track"], ligne["artist"])
        counts[key] = counts.get(key, 0) +  ligne["timestamp"]

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_counts

#Range les albums par nombre d'écoutes 
def rank_albums(data):
    counts = {}

    for ligne in data:
        key = (ligne["album"], ligne["artist"])
        counts[key] = counts.get(key, 0) + 1

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_counts

#Range les albums par temps d'écoutes
def rank_albumsbis(data):
    counts = {}

    for ligne in data:
        key = (ligne["album"], ligne["artist"])
        counts[key] = counts.get(key, 0) + ligne["timestamp"]

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_counts
 #Range les artistes par nombre d'écoutes
 def rank_artist(data):
    counts = {}

    for ligne in data:
        key =  (ligne["artist"] )
        counts[key] = counts.get(key, 0) + 1
   

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_counts

  #Range les artistes par temps écoutés
  def rank_artistbis(data):
    counts = {}

    for ligne in data:
        key =  (ligne["artist"] )
        counts[key] = counts.get(key, 0) + ligne["timestamp"]
   

    sorted_counts = sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_counts
  
  
