"""
健康检查路由
- 返回服务状态
- 显示环境变量配置状态
"""
from fastapi import APIRouter
from pydantic import BaseModel

from ..config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    env_vars: dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查端点
    
    返回服务状态和环境变量配置状态
    """
    return HealthResponse(
        status="ok",
        env_vars={
            "DASHSCOPE_API_KEY": "***" if settings.dashscope_api_key else "NOT SET",
            "MODELSCOPE_API_KEY": "***" if settings.modelscope_api_key else "NOT SET",
            "MINIMAX_API_KEY": "***" if settings.minimax_api_key else "NOT SET",
        }
    )
