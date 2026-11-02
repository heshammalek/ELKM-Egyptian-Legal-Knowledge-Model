from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import search, analysis

app = FastAPI(
    title="ELKM API",
    description="Egyptian Legal Knowledge Model - API",
    version="1.0.0"
)

# إعداد CORS (عشان الـ Frontend يقدر يتصل)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط الـ Routers
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ELKM API", "status": "running"}
