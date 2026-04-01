
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
  
