import json
import os
from utils.db import get_driver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METADATA_DIR = os.path.join(BASE_DIR, "corpus", "metadata")

def import_entities_and_positions():
    driver = get_driver()
    
    with driver.session() as session:
        # 1. استيراد الكيانات (Entities)
        entities_path = os.path.join(METADATA_DIR, "entities.json")
        if os.path.exists(entities_path):
            with open(entities_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ent in data.get("entities", []):
                    session.run("""
                        MERGE (e:Entity {entity_id: $entity_id})
                        SET e.name_ar = $name_ar,
                            e.name_en = $name_en
                    """, entity_id=ent.get("entity_id"), name_ar=ent.get("name_ar"), name_en=ent.get("name_en"))
            print("✅ تم استيراد الكيانات (Entities) بنجاح.")
        
        # 2. استيراد المناصب (Positions)
        positions_path = os.path.join(METADATA_DIR, "positions.json")
        if os.path.exists(positions_path):
            with open(positions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for pos in data.get("positions", []):
                    session.run("""
                        MERGE (p:Position {position_id: $position_id})
                        SET p.name_ar = $name_ar,
                            p.name_en = $name_en
                    """, position_id=pos.get("position_id"), name_ar=pos.get("name_ar"), name_en=pos.get("name_en"))
            print("✅ تم استيراد المناصب (Positions) بنجاح.")

    driver.close()

if __name__ == "__main__":
    import_entities_and_positions()
