from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.graph_service import get_related_documents

router = APIRouter()

class SearchRequest(BaseModel):
    question: str

class SearchResponse(BaseModel):
    results: list
    message: str

@router.post("/", response_model=SearchResponse)
def search_legal(query: SearchRequest):
    """البحث في الجراف القانوني"""
    keyword = query.question.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="السؤال فاضي")

    try:
        results = get_related_documents(keyword)
        if not results:
            return SearchResponse(results=[], message="مفيش نتايج مطابقة.")
        
        return SearchResponse(results=results, message="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
