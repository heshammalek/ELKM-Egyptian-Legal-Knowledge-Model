from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.ai_service import analyze_question

router = APIRouter()

class SearchRequest(BaseModel):
    question: str

class SearchResponse(BaseModel):
    results: list
    message: str
    source: str
    answer: str  # الإجابة المنسقة
    cypher: str | None = None

@router.post("/", response_model=SearchResponse)
def search_legal(query: SearchRequest):
    keyword = query.question.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="السؤال فاضي")

    try:
        result = analyze_question(keyword)
        data = result.get("data", [])
        
        return SearchResponse(
            results=data, 
            message="success",
            source=result.get("source"),
            answer=result.get("answer"),
            cypher=result.get("cypher")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
