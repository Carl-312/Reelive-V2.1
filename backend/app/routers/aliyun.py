"""
阿里云 DashScope API 代理路由
- 转发所有请求到 https://dashscope.aliyuncs.com
- 自动注入 API Key 到 Authorization header
- 转发 X-DashScope-* 自定义头部
"""
from fastapi import APIRouter, Request, Response, HTTPException
import httpx
import logging

from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_aliyun(path: str, request: Request):
    """
    代理所有 DashScope API 请求
    
    - **path**: API 路径 (例如: services/aigc/text-generation/generation)
    """
    target_url = f"https://dashscope.aliyuncs.com/{path}"
    
    # 检查 API Key
    if not settings.dashscope_api_key:
        logger.warning("[Proxy Aliyun] DASHSCOPE_API_KEY not configured")
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key}",
        "Content-Type": request.headers.get("Content-Type", "application/json"),
    }
    
    # 转发 X-DashScope-* 自定义头部
    for key, value in request.headers.items():
        if key.lower().startswith("x-dashscope"):
            headers[key] = value
    
    # 移除空值头部
    headers = {k: v for k, v in headers.items() if v}
    
    logger.info(f"[Proxy Aliyun] {request.method} {path} -> {target_url}")
    
    try:
        # 读取请求体
        body = await request.body()
        
        # 使用 httpx 发送异步请求
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
        
        # 返回原始响应
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=filtered_headers,
        )
    
    except httpx.RequestError as e:
        logger.error(f"[Proxy Aliyun] Request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy request failed: {str(e)}")
