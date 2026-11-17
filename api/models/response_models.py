from pydantic import BaseModel
from typing import List, Optional, Any

class SearchResponse(BaseModel):
    results: List[Any]
    message: str
    source: str
    answer: str
    cypher: Optional[str] = None

class ConflictResponse(BaseModel):
    status: str
    message: str
    findings: List[Any]
