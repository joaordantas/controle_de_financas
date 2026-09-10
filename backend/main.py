from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.auth import router as auth_router
from backend.routers.accounts import router as accounts_router
from backend.routers.categories import router as categories_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.sales import router as sales_router
from backend.routers.transactions import router as transactions_router
from database.schema import criar_banco

criar_banco()

app = FastAPI(
    title="Controle de Financas API",
    version="0.1.0",
    description="API do assistente financeiro pessoal.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(accounts_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(sales_router, prefix="/api")


@app.get("/api/health", include_in_schema=False)
def health_check() -> dict:
    return {
        "message": "API do Controle de Financas online.",
        "docs": "/docs",
    }


frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_dist.is_dir():
    app.frontend("/", directory=frontend_dist, fallback="index.html")
