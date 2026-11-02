import os
import sys

# إضافة مسار الجذر
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from scripts.utils.db import get_driver

def get_related_documents(keyword: str):
    """بيجيب المستندات والعلاقات المرتبطة بالكلمة المفتاحية"""
    driver = get_driver()
    try:
        with driver.session() as session:
            # 1. البحث عن المستندات
            query = "MATCH (d:Document) WHERE d.title_ar CONTAINS $kw OR d.doc_id CONTAINS $kw RETURN d.doc_id, d.title_ar"
            result = session.run(query, kw=keyword)
            docs = [{"doc_id": r["d.doc_id"], "title": r["d.title_ar"]} for r in result]

            if not docs:
                return []

            # 2. جلب العلاقات
            final_results = []
            for doc in docs:
                doc_id = doc["doc_id"]
                query_rel = """
                MATCH (src:Article)-[r:RELATION]->(tgt)
                WHERE (src.doc_id = $doc_id OR tgt.doc_id = $doc_id)
                RETURN 
                    CASE WHEN src.doc_id = $doc_id THEN 'Source' ELSE 'Target' END AS direction,
                    src.doc_id AS src_doc, src.article_number AS src_art,
                    r.type_name AS rel_type,
                    tgt.doc_id AS tgt_doc, tgt.article_number AS tgt_art,
                    r.reference_text AS ref_text
                """
                result_rel = session.run(query_rel, doc_id=doc_id)
                relations = [r.data() for r in result_rel]

                final_results.append({
                    "document": doc,
                    "relations": relations
                })

            return final_results
    finally:
        driver.close()

def execute_cypher_query(cypher: str):
    """بينفذ أي Cypher Query ويرجع النتيجة"""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(cypher)
            return [r.data() for r in result]
    finally:
        driver.close()
