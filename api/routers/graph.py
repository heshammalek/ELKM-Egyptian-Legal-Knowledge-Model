
from fastapi import APIRouter, HTTPException
from api.services.graph_service import get_related_documents

router = APIRouter()

@router.get("/{doc_id}")
def get_document_graph(doc_id: str):
    """جلب بيانات الجراف لمستند معين (للفرونت إند)"""
    try:
        # هنا هنستخدم دالة البحث بس بالـ doc_id
        results = get_related_documents(doc_id)
        return {"doc_id": doc_id, "graph_data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
