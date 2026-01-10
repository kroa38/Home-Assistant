"""
Atmo scripting
"""
import aiohttp
import logging
import yaml

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
                log.error(f"Erreur lors de la requette HTTP: {response.status}")
                return None
    except Exception as e:
        log.error(f"Erreur lors de la requette: {e}")
        return None
        
@pyscript_executor                
def read_yaml_file(file_name):

    with open(file_name,'r',encoding='utf-8') as file_desc:
        content = yaml.safe_load(file_desc)
    return content

async def get_atmo(token : str):
        async with aiohttp.ClientSession() as session:
            #log.info(f"Get Atmo data")  
            detail_communal = "https://api.atmo-aura.fr/api/v1/communes/38485/indices/atmo?commune_insee=38485&date_echeance="
            api_token = token
            url = "%s%s%s" % (detail_communal, 'now', "&api_token=")
            url = "%s%s" % (url, api_token)
            result = await fetch(session, url)
            if not result:
                log.error("api.atmo-aura.fr return null")
                return
            #log.error(result)
            indice = result['data'][0]['indice']
            state.set('input_number.air_quality',round(indice))
            # log.error(f"Indice global: {indice}")
            qualificatif = result['data'][0]['qualificatif']
            #log.error(f"Indice global: {indice}, Qualificatif: {qualificatif}")    

@service
def air_quality():
    token = read_yaml_file("secrets.yaml")
    await get_atmo(token["atmo"])
