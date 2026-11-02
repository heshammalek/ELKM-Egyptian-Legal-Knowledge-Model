from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

# إضافة مسار الجذر
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scripts.utils.db import get_driver

# تحميل المتغيرات
load_dotenv()

app = FastAPI(title="ELKM API")

# إعداد CORS عشان الـ Frontend يقدر يتكلم مع الـ API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to ELKM API"}

@app.post("/search")
def search_graph(request: QueryRequest):
    """يبحث في الجراف بناءً على السؤال"""
    keyword = request.question.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="السؤال فاضي")

    driver = get_driver()
    try:
        with driver.session() as session:
            # 1. ندور على المستندات اللي اسمها فيه الكلمة المفتاحية
            query = "MATCH (d:Document) WHERE d.title_ar CONTAINS $kw OR d.doc_id CONTAINS $kw RETURN d.doc_id, d.title_ar"
            result = session.run(query, kw=keyword)
            docs = [{"doc_id": r["d.doc_id"], "title": r["d.title_ar"]} for r in result]

            if not docs:
                return {"results": [], "message": "مفيش نتايج"}

            # 2. نجيب العلاقات لكل مستند
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

            return {"results": final_results, "message": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
