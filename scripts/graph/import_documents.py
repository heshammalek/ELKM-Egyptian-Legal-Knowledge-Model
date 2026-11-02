import json
import os
from scripts.utils.db import get_driver

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NORMALIZED_DIR = os.path.join(BASE_DIR, "corpus", "normalized")

def import_documents():
    driver = get_driver()
    
    with driver.session() as session:
        # المشي في كل مجلدات الـ normalized
        for root, dirs, files in os.walk(NORMALIZED_DIR):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            doc = json.load(f)
                            
                            doc_id = doc.get("doc_id")
                            if not doc_id:
                                continue

                            # 1. إنشاء Node للمستند (Document)
                            session.run("""
                                MERGE (d:Document {doc_id: $doc_id})
                                SET d.title_ar = $title_ar,
                                    d.doc_type = $doc_type,
                                    d.year = $year,
                                    d.issuing_authority = $issuing_authority,
                                    d.subjects = $subjects
                            """, doc_id=doc_id, title_ar=doc.get("title_ar"), doc_type=doc.get("doc_type"),
                                 year=doc.get("year"), issuing_authority=doc.get("issuing_authority"),
                                 subjects=doc.get("subjects", []))

                            # 2. إنشاء Nodes للمواد (Articles) وربطها بالمستند
                            articles = doc.get("articles", [])
                            for art in articles:
                                art_num = art.get("article_number")
                                if art_num is None:
                                    continue
                                
                                session.run("""
                                    MATCH (d:Document {doc_id: $doc_id})
                                    MERGE (a:Article {doc_id: $doc_id, article_number: $art_num})
                                    SET a.text_normalized = $text,
                                        a.order = $order,
                                        a.section = $section,
                                        a.chapter = $chapter
                                    MERGE (d)-[:HAS_ARTICLE]->(a)
                                """, doc_id=doc_id, art_num=art_num, text=art.get("text_normalized", ""),
                                     order=art.get("order", 0), section=art.get("section"), chapter=art.get("chapter"))
                            
                            print(f"✅ تم استيراد المستند: {doc_id} ({len(articles)} مادة).")
                            
                    except Exception as e:
                        print(f"❌ خطأ في معالجة {file}: {e}")

    driver.close()

if __name__ == "__main__":
    import_documents()
