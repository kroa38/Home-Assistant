"""
Meteo scripting
"""
import aiohttp
import datetime
from datetime import datetime, timezone
import urllib.parse
import yaml
import logging
from aiofile import async_open

# Documentation
# https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/overview?homepageId=222265642

#Requete API
async def fetch(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                #log.info(f"Requette HTTP OK")
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    #log.info(f"Requette HTTP JSON OK")
                    return await response.json()
                else:
                    #log.info(f"Requette HTTP TEXT OK")
                    return await response.text()
                    
            else:
                #log.error(f"Erreur lors de la requette HTTP: {response.status}")
                return None
    except Exception as e:
        #log.error(f"Erreur lors de la requette: {e}")
        return None
        
# function qui retourne les données de l'api meteofrance
def meteo(stations_list: dict, token : str):
    async with aiohttp.ClientSession() as session:
        serveur = 'https://public-api.meteofrance.fr/public/DPObs/v1'
        service = '/station/infrahoraire-6m'
        datage = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")     # en UTC
    
        for station in stations_list:
            url = serveur + service + '?id_station=' + station['id'] + '&date=' + urllib.parse.quote(datage) + '&format=json&apikey=' + urllib.parse.quote(token)
            #log.error(url)
            result = await fetch(session, url)   
            if not result:
                service = '/station/horaire'
                url = serveur + service + '?id_station=' + station['id'] + '&date=' + urllib.parse.quote(datage) + '&format=json&apikey=' + urllib.parse.quote(token)
                result = await fetch(session, url)   
            #log.error(station['alias'])    
            t = float(result[0]['t'] -273.15)
            t = round(t,1) 
            #log.error(f"Temperature {t} °C") 
            state.set(station['entities']['temperature'],t)
            u = float(result[0]['u'])
            u = round(u)
            #log.error(f"Humidité {u} %") 
            state.set(station['entities']['humidity'],u)

@pyscript_executor                
def read_yaml_file(file_name):
    with open(file_name,'r',encoding='utf-8') as file_desc:
        content = yaml.safe_load(file_desc)
    return content

async def read_async_yaml_file(file_name):
    async with async_open(file_name,'r') as file_desc:
        data = await file_desc.read()
        content = yaml.safe_load(data)
    return content
    
@service
def meteofrance():
    #log.error(f"Get MeteoFrance data") 
    liste = read_yaml_file("pyscript/liste_stations_meteo.yaml")
    token = read_yaml_file("secrets.yaml")
    await meteo(liste, token["meteo"]) 
        

