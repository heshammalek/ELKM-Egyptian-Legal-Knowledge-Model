import json
import os
from utils.db import get_driver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RELATIONS_DIR = os.path.join(BASE_DIR, "corpus", "relations", "by_document")

def import_relations():
    driver = get_driver()
    
    with driver.session() as session:
        for file in os.listdir(RELATIONS_DIR):
            if file.endswith('.json'):
                filepath = os.path.join(RELATIONS_DIR, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        rel = json.load(f)
                        
                        instance_id = rel.get("instance_id")
                        category = rel.get("category_id")
                        source = rel.get("source", {})
                        target = rel.get("target", {})
                        
                        if not instance_id or not category:
                            continue

                        # العلاقات بين المستندات (DOC-DOC)
                        if category == "DOC-DOC":
                            # لو الهدف مستند كامل
                            if target.get("scope") == "whole_document":
                                session.run("""
                                    MATCH (src:Article {doc_id: $src_doc, article_number: $src_art})
                                    MATCH (tgt:Document {doc_id: $tgt_doc})
                                    MERGE (src)-[r:RELATION {instance_id: $inst_id}]->(tgt)
                                    SET r.type_id = $type_id, r.type_name = $type_name,
                                        r.effective_date = $eff_date, r.reference_text = $ref_text
                                """, src_doc=source.get("doc_id"), src_art=source.get("article_number"),
                                     tgt_doc=target.get("doc_id"), inst_id=instance_id,
                                     type_id=rel.get("type_id"), type_name=rel.get("type_name"),
                                     eff_date=rel.get("effective_date"), ref_text=rel.get("reference_text"))
                            else:
                                # لو الهدف مادة محددة
                                session.run("""
                                    MATCH (src:Article {doc_id: $src_doc, article_number: $src_art})
                                    MATCH (tgt:Article {doc_id: $tgt_doc, article_number: $tgt_art})
                                    MERGE (src)-[r:RELATION {instance_id: $inst_id}]->(tgt)
                                    SET r.type_id = $type_id, r.type_name = $type_name,
                                        r.effective_date = $eff_date, r.reference_text = $ref_text
                                """, src_doc=source.get("doc_id"), src_art=source.get("article_number"),
                                     tgt_doc=target.get("doc_id"), tgt_art=target.get("article_number"),
                                     inst_id=instance_id, type_id=rel.get("type_id"), type_name=rel.get("type_name"),
                                     eff_date=rel.get("effective_date"), ref_text=rel.get("reference_text"))

                        # العلاقات مع الكيانات (DOC-ENT)
                        elif category == "DOC-ENT":
                            session.run("""
                                MATCH (src:Article {doc_id: $src_doc, article_number: $src_art})
                                MATCH (tgt:Entity {entity_id: $tgt_entity})
                                MERGE (src)-[r:RELATION {instance_id: $inst_id}]->(tgt)
                                SET r.type_id = $type_id, r.type_name = $type_name,
                                    r.effective_date = $eff_date, r.reference_text = $ref_text
                            """, src_doc=source.get("doc_id"), src_art=source.get("article_number"),
                                 tgt_entity=target.get("entity_id"), inst_id=instance_id,
                                 type_id=rel.get("type_id"), type_name=rel.get("type_name"),
                                 eff_date=rel.get("effective_date"), ref_text=rel.get("reference_text"))

                        # العلاقات مع المناصب (DOC-POS)
                        elif category == "DOC-POS":
                            session.run("""
                                MATCH (src:Article {doc_id: $src_doc, article_number: $src_art})
                                MATCH (tgt:Position {position_id: $tgt_pos})
                                MERGE (src)-[r:RELATION {instance_id: $inst_id}]->(tgt)
                                SET r.type_id = $type_id, r.type_name = $type_name,
                                    r.effective_date = $eff_date, r.reference_text = $ref_text
                            """, src_doc=source.get("doc_id"), src_art=source.get("article_number"),
                                 tgt_pos=target.get("position_id"), inst_id=instance_id,
                                 type_id=rel.get("type_id"), type_name=rel.get("type_name"),
                                 eff_date=rel.get("effective_date"), ref_text=rel.get("reference_text"))

                        print(f"✅ تم استيراد العلاقة: {instance_id}")
                        
                except Exception as e:
                    print(f"❌ خطأ في معالجة {file}: {e}")

    driver.close()

if __name__ == "__main__":
    import_relations()
