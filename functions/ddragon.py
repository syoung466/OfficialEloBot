import urllib.request
import json

dragon_url = "https://ddragon.leagueoflegends.com/api/versions.json"

def dragonVersion():

    ddragon_verion = urllib.request.urlopen(dragon_url).read().decode()
    ddragon_json = json.loads(ddragon_verion)
    version = ddragon_json[0]
    
    return version
   