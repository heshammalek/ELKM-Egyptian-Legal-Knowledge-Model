from pydantic import BaseModel

class SearchRequest(BaseModel):
    question: str

class ConflictRequest(BaseModel):
    law_a: str
    law_b: str
