"""
Nivose scripting
"""
import aiohttp
import asyncio
import datetime
from datetime import datetime, timezone, timedelta
import urllib.parse
import logging
import csv
import yaml
from io import StringIO


# Documentation
# https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/overview?homepageId=222265642
# https://portail-api.meteofrance.fr/web/fr/


error_command_file = { "202":"requette acceptée", 
                       "400":"contrôle de paramètres en erreur", 
                       "401":"non autorisé - informations d'identification non valides", 
                       "403":"accès interdit", 
                       "404":"la station demandée n'existe pas", 
                       "429":"seuil de requête atteint", 
                       "500":"erreur interne au serveur", 
                       "502":"erreur de passerelle",
                       "503":"service indisponible",
                       "504":"temps d'attente de la passerelle dépassé"
                       }

error_get_file = { "201":"Fichier envoyé",
                   "204":"production encore en attente ou en cours",
                   "401":"non autorisé - informations d'identification non valides",
                   "403":"accès interdit",
                   "404":"le numero de commande n'existait pas",
                   "410":"production déja delivrée",
                   "429":"seuil de requête atteint",
                   "500":"production terminée : echec",
                   "507":"production rejetée par le systeme (trop volumineuse)"
                    }


#----------------------------------------------------------------
#Requete WEB API
#----------------------------------------------------------------
async def fetch(session, url, headers, err):
    try:
        async with session.get(url,headers=headers) as response:
            if response.status == 201 or response.status == 202:
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    return await response.json()
                else:
                    return await response.text()
                    
            else:
                log.error(f"Erreur lors de la requette HTTP: {response.status} : {err.get(str(response.status))}")
                return None
    except Exception as e:
        log.error(f"Erreur lors de la requette: {e} : {err.get(str(e))} ")
        pass
        return None


#----------------------------------------------------------------
# Genere les fichiers climat pour le nivose
#----------------------------------------------------------------
def command_file(list_stations_nivose : dict, token : str):
    async with aiohttp.ClientSession() as session:
        #file_dict = {}
        for station in list_stations_nivose:
            time_delta = 5  # demande datas 30 minutes avant l'heure actuelle 
            datage = (datetime.now(timezone.utc) - timedelta(minutes=time_delta)).strftime("%Y-%m-%dT%H:%M:%SZ")
            serveur = 'https://public-api.meteofrance.fr/public/DPClim/v1'
            service = '/commande-station/horaire'
            url = serveur + service + "?id-station=" + station['id'] + "&date-deb-periode=" + urllib.parse.quote(datage) + "&date-fin-periode=" + urllib.parse.quote(datage)
            headers = {
                "accept": "*/*",
                "apikey": token  # Replace with your full API key
            }
            err = error_command_file
            #log.error(url)
            response = await fetch(session, url, headers, err) 
            # si pas de reponse on passe a la station suivante
            if not response:
                log.error(f" Echec commande fichier : Station {station['alias']} ")
                state.set(station['file_helper'], 0)
                # Mise à jour du numéro de fichier dans la liste des stations 
            else:
                #log.error(f" commande fichier ok: Station {station['alias']}  : {int(response['elaboreProduitAvecDemandeResponse']['return'])}")
                # mise a jour du helper dans HASS avec le numero du fichier a récupérer
                state.set(station['file_helper'],int(response['elaboreProduitAvecDemandeResponse']['return']))

#----------------------------------------------------------------
# Récupère les données nivose
#----------------------------------------------------------------
def get_file(list_stations_nivose : dict, token : str):

    async with aiohttp.ClientSession() as session:

        serveur = 'https://public-api.meteofrance.fr/public/DPClim/v1'
        service = '/commande/fichier'
        headers = {
            "accept": "*/*",
            "apikey": token  # Replace with your full API key
        }

        for station in list_stations_nivose:
            if state.get(station['file_helper']) == 0:
                continue
          
            url = serveur + service  + '?id-cmde=' + state.get(station['file_helper'])
            #log.error(url)
            err = error_get_file
            response = await fetch(session, url, headers, err) 
            if not response:
                continue
            csv_file = StringIO(response)
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            rows = list(csv_reader)
            #log.error(rows)
            
            wind = rows[0]['FF']
            wind = round(float(wind.replace(',', '.')) *3.6)
            
            temperature = rows[0]['T']
            temperature = temperature.replace(',', '.')
            temperature = round(float(temperature),1)
            
            u = rows[0]['U']
            humidity = int(u)
            
            windgust = rows[0]['FXI']
            windgust = round(float(windgust.replace(',', '.')) *3.6)
            #log.error(f"windgust : {windgust} km/h")
            
            snow = rows[0]['NEIGETOT']
            snow = snow.replace(',', '.')
            snow = round(float(snow))
            
            windchill = calcul_windchill(temperature,wind)
            #log.error(f"windchill : {windchill} °C")
            
            state.set(station['entities']['temp'],temperature)
            state.set(station['entities']['hum'],humidity)
            state.set(station['entities']['chill'],windchill)
            state.set(station['entities']['snow'],snow)
            state.set(station['entities']['gust'],windgust)
            state.set(station['entities']['wind'],wind)



def calcul_windchill(temperature_celsius, vitesse_vent_kmh):
    """
    Calcule la température ressentie (windchill) selon la formule officielle.
    
    Paramètres :
    - temperature_celsius : Température de l'air en degrés Celsius
    - vitesse_vent_kmh : Vitesse du vent en kilomètres par heure
    
    Retour :
    - Température ressentie en degrés Celsius
    """
    if temperature_celsius > 10 or vitesse_vent_kmh < 4.8:
        return temperature_celsius  # La formule ne s'applique pas dans ce cas

    windchill = (
        13.12 +
        0.6215 * temperature_celsius -
        11.37 * (vitesse_vent_kmh ** 0.16) +
        0.3965 * temperature_celsius * (vitesse_vent_kmh ** 0.16)
    )
    return round(windchill, 1)


@pyscript_executor                
def read_yaml_file(file_name):

    with open(file_name,'r',encoding='utf-8') as file_desc:
        content = yaml.safe_load(file_desc)
    return content
    
@service
def command_file_nivose():
    #log.error(f"Get File Nivose")
    liste = read_yaml_file("pyscript/liste_stations_nivose.yaml")
    token = read_yaml_file("secrets.yaml")
    await command_file(liste, token["nivose"])

    
    
@service
def get_data_nivose():
    #log.error(f"Get Data Nivose")
    liste = read_yaml_file("pyscript/liste_stations_nivose.yaml")
    token = read_yaml_file("secrets.yaml")
    await get_file(liste, token["nivose"])

        
