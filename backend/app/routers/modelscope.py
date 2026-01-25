"""
ModelScope API 代理路由
- 转发所有请求到 https://api-inference.modelscope.cn/v1
- 自动注入 API Key
"""
from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import logging

from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_modelscope(path: str, request: Request):
    """
    代理所有 ModelScope API 请求
    
    - **path**: API 路径
    """
    target_url = f"https://api-inference.modelscope.cn/v1/{path}"
    
    if not settings.modelscope_api_key:
        logger.warning("[Proxy ModelScope] MODELSCOPE_API_KEY not configured")
    
    headers = {
        "Authorization": f"Bearer {settings.modelscope_api_key}",
        "Content-Type": "application/json",
    }
    
    logger.info(f"[Proxy ModelScope] {request.method} {path} -> {target_url}")
    
    try:
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=settings.proxy_timeout) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body if body else None,
                params=request.query_params,
            )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    
    except httpx.RequestError as e:
        logger.error(f"[Proxy ModelScope] Request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy request failed: {str(e)}")
