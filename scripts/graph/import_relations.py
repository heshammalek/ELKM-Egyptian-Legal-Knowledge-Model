import json
import os
import glob
from scripts.utils.db import get_driver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RELATIONS_DIR = os.path.join(BASE_DIR, "corpus", "relations", "by_document")
ENTITIES_FILE = os.path.join(BASE_DIR, "corpus", "metadata", "entities.json")
POSITIONS_FILE = os.path.join(BASE_DIR, "corpus", "metadata", "positions.json")

def preload_metadata(session):
    print("🔄 جاري تحميل الكيانات والمناصب...")
    if os.path.exists(ENTITIES_FILE):
        with open(ENTITIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ent in data.get("entities", []):
                session.run("MERGE (e:Entity {entity_id: $id}) SET e.name_ar = $name", 
                            id=ent.get("entity_id"), name=ent.get("name_ar"))
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for pos in data.get("positions", []):
                session.run("MERGE (p:Position {position_id: $id}) SET p.name_ar = $name", 
                            id=pos.get("position_id"), name=pos.get("name_ar"))

def import_relations():
    driver = get_driver()
    with driver.session() as session:
        preload_metadata(session)
        
        files = glob.glob(os.path.join(RELATIONS_DIR, "*.json"))
        success_count = 0
        placeholder_count = 0
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    rel = json.load(f)
                    instance_id = rel.get("instance_id")
                    category = rel.get("category_id")
                    source = rel.get("source", {})
                    target = rel.get("target", {})
                    ref_text = rel.get("reference_text", "")
                    
                    if not instance_id or not category: continue

                    # --- 1. تحديد المصدر ---
                    src_doc = source.get("doc_id")
                    src_art = source.get("article_number")
                    
                    if src_doc is not None and src_art is not None:
                        # المصدر عادي (مادة)
                        session.run("MERGE (src:Article {doc_id: $doc, article_number: $art})", 
                                    doc=src_doc, art=str(src_art))
                        source_match = "MATCH (src:Article {doc_id: $src_doc, article_number: $src_art})"
                        params = {"src_doc": src_doc, "src_art": str(src_art)}
                    elif src_doc is not None:
                        # المصدر مستند (بدون مادة)
                        session.run("MERGE (src:Document {doc_id: $doc})", doc=src_doc)
                        source_match = "MATCH (src:Document {doc_id: $src_doc})"
                        params = {"src_doc": src_doc}
                    else:
                        # Source فيه null (مشكلة في ملف العلاقة) -> نعمل Placeholder
                        placeholder_id = f"UNKNOWN-{instance_id}"
                        session.run("MERGE (src:UnknownEntity {instance_id: $id}) SET src.reference_text = $ref", 
                                    id=placeholder_id, ref=ref_text)
                        source_match = "MATCH (src:UnknownEntity {instance_id: $id})"
                        params = {"id": placeholder_id}
                        placeholder_count += 1

                    params.update({"inst_id": instance_id, "type_id": rel.get("type_id"), "type_name": rel.get("type_name"), "ref_text": ref_text})

                    # --- 2. تحديد الهدف ---
                    query = ""
                    if category == "DOC-DOC":
                        if target.get("scope") == "whole_document":
                            tgt_doc = target.get("doc_id")
                            if tgt_doc:
                                session.run("MERGE (tgt:Document {doc_id: $doc})", doc=tgt_doc)
                                query = f"{source_match} MATCH (tgt:Document {{doc_id: $tgt_doc}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.reference_text = $ref_text"
                                params["tgt_doc"] = tgt_doc
                            else:
                                continue # تخطي لو الهدف مش موجود
                        else:
                            tgt_doc = target.get("doc_id")
                            tgt_art = target.get("article_number")
                            if tgt_doc and tgt_art:
                                session.run("MERGE (tgt:Article {doc_id: $doc, article_number: $art})", doc=tgt_doc, art=str(tgt_art))
                                query = f"{source_match} MATCH (tgt:Article {{doc_id: $tgt_doc, article_number: $tgt_art}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.reference_text = $ref_text"
                                params["tgt_doc"] = tgt_doc
                                params["tgt_art"] = str(tgt_art)
                            else:
                                continue # تخطي لو الهدف مش موجود

                    elif category == "DOC-ENT":
                        ent_id = target.get("entity_id")
                        if ent_id:
                            session.run("MERGE (tgt:Entity {entity_id: $id})", id=ent_id)
                            query = f"{source_match} MATCH (tgt:Entity {{entity_id: $tgt_entity}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.reference_text = $ref_text"
                            params["tgt_entity"] = ent_id
                        else:
                            query = f"{source_match} MERGE (tgt:Entity {{name_ar: $ref_text}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.reference_text = $ref_text"

                    elif category == "DOC-POS":
                        pos_id = target.get("position_id")
                        if pos_id:
                            session.run("MERGE (tgt:Position {position_id: $id})", id=pos_id)
                            query = f"{source_match} MATCH (tgt:Position {{position_id: $tgt_pos}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.reference_text = $ref_text"
                            params["tgt_pos"] = pos_id
                        else:
                            query = f"{source_match} MERGE (tgt:Position {{name_ar: $ref_text}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.reference_text = $ref_text"

                    if query:
                        session.run(query, **params)
                        success_count += 1

            except Exception as e:
                print(f"❌ خطأ في {os.path.basename(filepath)}: {e}")

    driver.close()
    print(f"✅ تمت معالجة {success_count} علاقة.")
    print(f"⚠️ تم استخدام Placeholder Node في {placeholder_count} علاقة.")

if __name__ == "__main__":
    import_relations()
