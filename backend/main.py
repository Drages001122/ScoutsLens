from api.auth import router as auth_router
from api.basic_information import router as basic_information_router
from api.lineup import router as lineup_router
from api.rule import router as rule_router
from api.stats import router as stats_router
from config import get_current_config, init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ScoutsLens API",
    description="NBA球探数据分析平台后端API",
    version="1.0.0",
)

config = get_current_config()
frontend_domains = config.get("frontend_domains", [])

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
    init_db()


@app.get("/", tags=["根路径"])
async def root():
    return {"message": "Welcome to ScoutsLens API", "docs": "/docs", "redoc": "/redoc"}


@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "healthy"}


app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(
    basic_information_router, prefix="/api/basic_information", tags=["基础信息"]
)
app.include_router(lineup_router, prefix="/api/lineup", tags=["阵容"])
app.include_router(rule_router, prefix="/api/rule", tags=["规则"])
app.include_router(stats_router, prefix="/api/stats", tags=["统计数据"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=config["env"] == "dev",
    )
