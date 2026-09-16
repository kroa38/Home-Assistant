from sqlalchemy import text
from datetime import datetime, timedelta
# On importe la fonction officielle pour récupérer l'instance du Recorder
from homeassistant.components.recorder import get_instance


def query_db_record_count(entity_id):
    # Récupération propre de l'instance du Recorder, puis de son moteur SQL
    recorder_instance = get_instance(hass)
    engine = recorder_instance.engine
    
    # Le reste de la requête reste identique
    sql_query = text("""
        SELECT COUNT(*) 
        FROM states s
        JOIN states_meta m ON s.metadata_id = m.metadata_id
        WHERE m.entity_id = :entity_id;
    """)

    with engine.connect() as connection:
        result = connection.execute(sql_query, {"entity_id": entity_id})
        count = result.scalar()
        
    return count


def query_max_temp_by_day(entity_id, start_date, end_date):
    """Récupère la température maximale par jour pour une période donnée.
    
    Args:
        entity_id: L'ID de l'entité (ex: "sensor.th_outside_temperature")
        start_date: Date de début (format: "2026-07-01" ou datetime object)
        end_date: Date de fin (format: "2026-07-31" ou datetime object)
    
    Returns:
        Liste de dictionnaires avec la date et la température max de chaque jour
    """
    # Conversion des strings en datetime si nécessaire
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Ajouter 1 jour à la date de fin pour inclure le dernier jour
    end_date = end_date + timedelta(days=1)
    
    # Convertir les dates en strings ISO pour éviter les problèmes de fuseau horaire
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    recorder_instance = get_instance(hass)
    engine = recorder_instance.engine


    sql_query = text("""
        SELECT 
            DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED))) as jour,
            MAX(CAST(s.state AS FLOAT)) as temp_max
        FROM states s
        JOIN states_meta m ON s.metadata_id = m.metadata_id
        WHERE m.entity_id = :entity_id
            AND DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED))) >= :start_date
            AND DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED))) < :end_date
            AND s.state NOT IN ('unknown', 'unavailable')
            AND s.state IS NOT NULL
            AND s.state != ''
        GROUP BY DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED)))
        ORDER BY jour ASC
    """)

    with engine.connect() as connection:
        result = connection.execute(sql_query, {
            "entity_id": entity_id,
            "start_date": start_date_str,
            "end_date": end_date_str
        })
        rows = result.fetchall()
    # Conversion en liste de dictionnaires
    temperatures = []
    for row in rows:
        temperatures.append({
            "date": row[0],
            "temp_max": round(float(row[1]), 2)
        })

    return temperatures

def query_min_temp_by_day(entity_id, start_date, end_date):
    """Récupère la température minimale par jour pour une période donnée.
    
    Args:
        entity_id: L'ID de l'entité (ex: "sensor.th_outside_temperature")
        start_date: Date de début (format: "2026-07-01" ou datetime object)
        end_date: Date de fin (format: "2026-07-31" ou datetime object)
    
    Returns:
        Liste de dictionnaires avec la date et la température max de chaque jour
    """
    # Conversion des strings en datetime si nécessaire
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Ajouter 1 jour à la date de fin pour inclure le dernier jour
    end_date = end_date + timedelta(days=1)
    
    # Convertir les dates en strings ISO pour éviter les problèmes de fuseau horaire
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    recorder_instance = get_instance(hass)
    engine = recorder_instance.engine


    sql_query = text("""
        SELECT 
            DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED))) as jour,
            MIN(CAST(s.state AS FLOAT)) as temp_min
        FROM states s
        JOIN states_meta m ON s.metadata_id = m.metadata_id
        WHERE m.entity_id = :entity_id
            AND DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED))) >= :start_date
            AND DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED))) < :end_date
            AND s.state NOT IN ('unknown', 'unavailable')
            AND s.state IS NOT NULL
            AND s.state != ''
        GROUP BY DATE(FROM_UNIXTIME(CAST(s.last_updated_ts AS UNSIGNED)))
        ORDER BY jour ASC
    """)

    with engine.connect() as connection:
        result = connection.execute(sql_query, {
            "entity_id": entity_id,
            "start_date": start_date_str,
            "end_date": end_date_str
        })
        rows = result.fetchall()
    # Conversion en liste de dictionnaires
    temperatures = []
    for row in rows:
        temperatures.append({
            "date": row[0],
            "temp_min": round(float(row[1]), 2)
        })

    return temperatures

@service
def max_records_th_outside(entity_id="sensor.th_outside_temperature"):
    """Service pour compter le nombre de points enregistrés pour un capteur."""
    log.error(f"Calcul du nombre de records pour l'entité {entity_id}...")
    
    try:
        total_records = query_db_record_count(entity_id)
        
        log.error(f"--- RÉSULTAT ---")
        log.error(f"L'entité '{entity_id}' possède actuellement {total_records} enregistrements dans la table 'states'.")
        
#        state.set(
#            "sensor.pyscript_outside_temp_records_count",
#            value=total_records,
#            new_attributes={
#                "target_entity": entity_id,
#                "friendly_name": "Nombre de records température",
#                "unit_of_measurement": "enregistrements"
#            }
#        )
        
    except Exception as e:
        log.error(f"Erreur lors du comptage des enregistrements : {e}")

@service
def max_temp_period(start_date="2026-05-23", end_date="2026-08-25", entity_id="sensor.th_outside_temperature"):
    """Service pour obtenir la température maximale par jour sur une période donnée.
    """
    try:
        temperatures = query_max_temp_by_day(entity_id, start_date, end_date)
        
        log.error(f"--- Températures maximales du {start_date} au {end_date} ---")
        for day_data in temperatures:
            log.error(f"{day_data['date']} : {day_data['temp_max']}°C")
        
        if temperatures:
            max_temp = max([d['temp_max'] for d in temperatures])
            # min_temp = min([d['temp_max'] for d in temperatures])
            # avg_temp = sum([d['temp_max'] for d in temperatures]) / len(temperatures)
            log.error(f"--- Statistiques sur la période---")
            log.error(f"Max : {max_temp}°C")
            # log.error(f"Min : {min_temp}°C")
            # log.error(f"Moyenne : {round(avg_temp, 2)}°C")
        
    except Exception as e:
        log.error(f"Erreur lors de la récupération des températures : {e}")


@service
def min_temp_period(start_date="2026-05-23", end_date="2026-08-25", entity_id="sensor.th_outside_temperature"):
    """Service pour obtenir la température minimale par jour sur une période donnée.
    """
    try:
        temperatures = query_min_temp_by_day(entity_id, start_date, end_date)
        
        log.error(f"--- Températures minimales du {start_date} au {end_date} ---")
        for day_data in temperatures:
            log.error(f"{day_data['date']} : {day_data['temp_min']}°C")
        
        if temperatures:
            min_temp = min([d['temp_min'] for d in temperatures])
            # max_temp = max([d['temp_min'] for d in temperatures])
            # avg_temp = sum([d['temp_min'] for d in temperatures]) / len(temperatures)
            log.error(f"--- Statistiques sur la période---")
            log.error(f"Min : {min_temp}°C")
            # log.error(f"Max : {max_temp}°C")
            # log.error(f"Moyenne : {round(avg_temp, 2)}°C")
        
    except Exception as e:
        log.error(f"Erreur lors de la récupération des températures : {e}")

