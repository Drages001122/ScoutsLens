from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.lineups import router as lineups_router
from app.api.players import router as players_router
from app.api.rules import router as rules_router
from app.api.stats import router as stats_router
from app.core.config import settings
from app.core.logger import logger
from app.db.session import init_db

app = FastAPI(
    title="ScoutsLens API",
    description="NBA球探数据分析平台后端API",
    version="2.0.0",
)

frontend_domains = settings.frontend_domains

if frontend_domains:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=frontend_domains,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_event():
    logger.info("Starting ScoutsLens API...")
    init_db()
    logger.info("Database initialized successfully")


@app.get("/", tags=["根路径"])
async def root():
    return {"message": "Welcome to ScoutsLens API", "docs": "/docs", "redoc": "/redoc"}


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}


app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(players_router, prefix="/api/basic_information", tags=["基础信息"])
app.include_router(lineups_router, prefix="/api/lineup", tags=["阵容"])
app.include_router(rules_router, prefix="/api/rule", tags=["规则"])
app.include_router(stats_router, prefix="/api/stats", tags=["统计数据"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.env == "dev",
    )
