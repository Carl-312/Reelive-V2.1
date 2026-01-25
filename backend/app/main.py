"""
FastAPI 主应用入口
- 注册所有路由模块
- 配置 CORS 中间件
- 服务静态文件
- 自动生成 OpenAPI 文档
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from .config import settings
from .routers import aliyun, modelscope, minimax, health

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="叙事引擎 API",
    description="AI 驱动的叙事音频选择服务 - 支持多 LLM 代理",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# CORS 中间件配置
# ============================================
import os

# 从环境变量读取允许的前端域名（逗号分隔）
# 默认允许本地开发环境
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 白名单模式（生产环境需配置 Vercel 域名）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 注册路由模块
# ============================================
app.include_router(aliyun.router, prefix="/api/aliyun", tags=["Aliyun DashScope"])
app.include_router(modelscope.router, prefix="/api/modelscope", tags=["ModelScope"])
app.include_router(minimax.router, prefix="/api/minimax", tags=["Minimax"])
app.include_router(health.router, tags=["Health Check"])

# ============================================
# 静态文件服务 (生产环境)
# ============================================
try:
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")
    logger.info("Static files mounted from 'dist/' directory")
except RuntimeError:
    logger.warning("Static files directory 'dist' not found - frontend not available")


# ============================================
# 应用生命周期事件
# ============================================
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"🚀 Starting server on {settings.host}:{settings.port}")
    logger.info(f"📚 API Documentation: http://localhost:{settings.port}/docs")
    logger.info("🔑 Environment variables status:")
    logger.info(f"  DASHSCOPE_API_KEY: {'✅ SET' if settings.dashscope_api_key else '❌ NOT SET'}")
    logger.info(f"  MODELSCOPE_API_KEY: {'✅ SET' if settings.modelscope_api_key else '❌ NOT SET'}")
    logger.info(f"  MINIMAX_API_KEY: {'✅ SET' if settings.minimax_api_key else '❌ NOT SET'}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("🛑 Shutting down server...")
