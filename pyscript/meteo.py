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

# API KEY
# Generate your apikey for 1 year at: https://portail-api.meteofrance.fr/web/fr/
# and save it in secrets.yaml

#Requete API
async def fetch(session, url, headers=None):
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            content_type = response.headers.get('Content-Type', '')
            #log.error(f"Requette https meteofrance ok")
            if 'application/json' in content_type:
                return await response.json()
            else:
                return await response.text()
        else:
            log.error(f"Meteofrance Erreur lors de la requette HTTP: {response.status}")
            return None
        
# function qui retourne les données de l'api meteofrance
def meteo(stations_list: dict, token : str):
    async with aiohttp.ClientSession() as session:
        """
        https://public-api.meteofrance.fr/public/DPObs/v2/station/infrahoraire-6m?id_station=38185012&format=json
        """
        serveur = 'https://public-api.meteofrance.fr/public/DPObs/v2'
        service = '/station/infrahoraire-6m'
        headers = {'apikey': f'{token}'}
        
        for station in stations_list:
            url = serveur + service + '?id_station=' + station['id'] + '&format=json'
            result = await fetch(session, url, headers=headers)   
            if not result:
                continue
            try:
                #log.error(station['alias'])    
                t = float(result[0]['t'] -273.15)
                t = round(t,1) 
                #log.error(f"Temperature {t} °C") 
                state.set(station['entities']['temperature'],t)
                u = float(result[0]['u'])
                u = round(u)
                #log.error(f"Humidité {u} %") 
                state.set(station['entities']['humidity'],u)
            except Exception as e:
                log.error(f" in parsing meteofrance data for station: {station=}")

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
        