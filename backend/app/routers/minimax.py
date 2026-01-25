"""
Minimax API 代理路由
- 转发所有请求到 https://api.minimaxi.com
- 自动注入 API Key
"""
from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import logging

from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_minimax(path: str, request: Request):
    """
    代理所有 Minimax API 请求
    
    - **path**: API 路径
    """
    target_url = f"https://api.minimaxi.com/{path}"
    
    if not settings.minimax_api_key:
        logger.warning("[Proxy Minimax] MINIMAX_API_KEY not configured")
    
    headers = {
        "Authorization": f"Bearer {settings.minimax_api_key}",
        "Content-Type": "application/json",
    }
    
    logger.info(f"[Proxy Minimax] {request.method} {path} -> {target_url}")
    
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
        
        # 过滤需要移除的响应头
        # httpx 会自动解压缩 gzip 响应，但 response.headers 仍包含原始 Content-Encoding
        # 如果原样转发，客户端会尝试再次解压缩已解压的数据，导致 zlib 错误
        excluded_headers = {"content-encoding", "content-length", "transfer-encoding"}
        filtered_headers = {
            k: v for k, v in response.headers.items()
            if k.lower() not in excluded_headers
        }
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=filtered_headers,
        )
    
    except httpx.RequestError as e:
        logger.error(f"[Proxy Minimax] Request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy request failed: {str(e)}")
