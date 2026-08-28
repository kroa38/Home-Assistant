from sqlalchemy import text
# On importe la fonction officielle pour récupérer l'instance du Recorder
from homeassistant.components.recorder import get_instance

@pyscript_executor
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

