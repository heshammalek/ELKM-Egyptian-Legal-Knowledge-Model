import json
import os
import glob
from scripts.utils.db import get_driver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RELATIONS_DIR = os.path.join(BASE_DIR, "corpus", "relations", "by_document")

def import_relations():
    driver = get_driver()
    
    with driver.session() as session:
        files = glob.glob(os.path.join(RELATIONS_DIR, "*.json"))
        if not files:
            print("⚠️ مفيش ملفات علاقات.")
            return

        print(f"🔄 جاري معالجة {len(files)} ملف علاقات...")
        success_count = 0
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    rel = json.load(f)
                    
                    instance_id = rel.get("instance_id")
                    category = rel.get("category_id")
                    type_name = rel.get("type_name")
                    source = rel.get("source", {})
                    target = rel.get("target", {})
                    ref_text = rel.get("reference_text", "")
                    
                    if not instance_id or not category or not type_name:
                        continue

                    # تحديد نوع المصدر (Source)
                    src_doc = source.get("doc_id")
                    src_art = source.get("article_number")
                    src_section = source.get("section")

                    # الحالة الاستثنائية للأحكام (منطوق الحكم)
                    if src_art is None and src_section == "منطوق":
                        # هنا بنتعامل مع الأحكام كمصدر (بنفترض إن عندك Nodes للأحكام)
                        source_match = "MATCH (src:Judgment {doc_id: $src_doc})"
                        src_params = {"src_doc": src_doc}
                    else:
                        # الحالة العادية: المصدر مادة (Article)
                        source_match = "MATCH (src:Article {doc_id: $src_doc, article_number: $src_art})"
                        src_params = {"src_doc": src_doc, "src_art": str(src_art)}

                    # بناء الـ Cypher بناءً على الـ Target
                    query = ""
                    params = {**src_params, "inst_id": instance_id, "type_id": rel.get("type_id"), 
                              "type_name": type_name, "eff_date": rel.get("effective_date"), "ref_text": ref_text}

                    if category == "DOC-DOC":
                        if target.get("scope") == "whole_document":
                            query = f"{source_match} MATCH (tgt:Document {{doc_id: $tgt_doc}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.effective_date = $eff_date, r.reference_text = $ref_text"
                            params["tgt_doc"] = target.get("doc_id")
                        else:
                            query = f"{source_match} MATCH (tgt:Article {{doc_id: $tgt_doc, article_number: $tgt_art}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.effective_date = $eff_date, r.reference_text = $ref_text"
                            params["tgt_doc"] = target.get("doc_id")
                            params["tgt_art"] = str(target.get("article_number"))

                    elif category == "DOC-ENT":
                        # التعامل مع الكيانات (لو الـ entity_id موجود، لو مش موجود بنعمله)
                        ent_id = target.get("entity_id")
                        if not ent_id:
                            # لو السكريبت لاقى كيان جديد، بيعمله Node (مؤقتاً)
                            query = f"{source_match} MERGE (tgt:Entity {{name_ar: $ref_text}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.effective_date = $eff_date, r.reference_text = $ref_text"
                        else:
                            query = f"{source_match} MATCH (tgt:Entity {{entity_id: $tgt_entity}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.effective_date = $eff_date, r.reference_text = $ref_text"
                            params["tgt_entity"] = ent_id

                    elif category == "DOC-POS":
                        pos_id = target.get("position_id")
                        if not pos_id:
                            query = f"{source_match} MERGE (tgt:Position {{name_ar: $ref_text}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.effective_date = $eff_date, r.reference_text = $ref_text"
                        else:
                            query = f"{source_match} MATCH (tgt:Position {{position_id: $tgt_pos}}) MERGE (src)-[r:RELATION {{instance_id: $inst_id}}]->(tgt) SET r.type_id = $type_id, r.type_name = $type_name, r.effective_date = $eff_date, r.reference_text = $ref_text"
                            params["tgt_pos"] = pos_id

                    if query:
                        session.run(query, **params)
                        success_count += 1

            except Exception as e:
                print(f"❌ خطأ في معالجة {os.path.basename(filepath)}: {e}")

    driver.close()
    print(f"✅ تمت معالجة {success_count} علاقة بنجاح (من إجمالي {len(files)}).")

if __name__ == "__main__":
    import_relations()
