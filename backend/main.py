from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import init_db
from api.routes import leads, enrichment, generation

app = FastAPI(title="OSINT Cold Call Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(leads.router)
app.include_router(enrichment.router)
app.include_router(generation.router)


@app.get("/health")
def health():
    return {"status": "ok"}
