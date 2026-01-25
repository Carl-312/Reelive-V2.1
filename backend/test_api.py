"""
API 代理测试脚本
测试 FastAPI 后端代理功能 + 性能 Metrics 收集
"""
import httpx
import asyncio
import json
import time
import argparse
from typing import Dict, Any

BASE_URL = "http://localhost:7860"

# 性能 Metrics 存储
performance_metrics: Dict[str, Dict[str, Any]] = {}


async def test_health():
    """测试健康检查"""
    start_time = time.time()
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/health")
        elapsed = time.time() - start_time
        
        print("=== /health ===")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        print(f"TTFB: {elapsed:.3f}s")
        
        performance_metrics["health"] = {
            "status": resp.status_code,
            "ttfb": elapsed,
            "success": resp.status_code == 200
        }
        
        return resp.status_code == 200

async def test_dashscope():
    """测试 DashScope (qwen-max) 代理"""
    start_time = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{BASE_URL}/api/aliyun/compatible-mode/v1/chat/completions",
            json={
                "model": "qwen-max",
                "messages": [{"role": "user", "content": "say hi in one word"}],
                "max_tokens": 20
            }
        )
        elapsed = time.time() - start_time
        
        print("\n=== DashScope (qwen-max) ===")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        
        success = False
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            print(f"Response: {content}")
            print(f"TTFB: {elapsed:.3f}s")
            success = True
        else:
            print(f"Error: {json.dumps(data, indent=2)}")
        
        performance_metrics["dashscope"] = {
            "status": resp.status_code,
            "ttfb": elapsed,
            "success": success
        }
        
        return success

async def test_modelscope():
    """测试 ModelScope (GLM-4.7) 代理"""
    start_time = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{BASE_URL}/api/modelscope/chat/completions",
            json={
                "model": "ZhipuAI/GLM-4.7",
                "messages": [{"role": "user", "content": "say hi in one word"}],
                "max_tokens": 20
            }
        )
        elapsed = time.time() - start_time
        
        print("\n=== ModelScope (GLM-4.7) ===")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        
        success = False
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            print(f"Response: {content}")
            print(f"TTFB: {elapsed:.3f}s")
            success = True
        else:
            print(f"Error: {json.dumps(data, indent=2)}")
        
        performance_metrics["modelscope"] = {
            "status": resp.status_code,
            "ttfb": elapsed,
            "success": success
        }
        
        return success

async def test_minimax():
    """测试 Minimax (image-01) 代理"""
    start_time = time.time()
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{BASE_URL}/api/minimax/v1/image_generation",
            json={
                "prompt": "a cute cat",
                "model": "image-01",
                "n": 1
            }
        )
        elapsed = time.time() - start_time
        
        print("\n=== Minimax (image-01) ===")
        print(f"Status: {resp.status_code}")
        data = resp.json()
        
        success = False
        if "data" in data and "image_urls" in data.get("data", {}):
            url = data["data"]["image_urls"][0]
            print(f"Image URL: {url[:80]}...")
            print(f"TTFB: {elapsed:.3f}s")
            success = True
        else:
            print(f"Response: {json.dumps(data, indent=2)[:200]}")
            success = "error" not in str(data).lower()
        
        performance_metrics["minimax"] = {
            "status": resp.status_code,
            "ttfb": elapsed,
            "success": success
        }
        
        return success


def print_performance_table():
    """打印性能 Metrics 表格"""
    print("\n" + "=" * 70)
    print("性能 Metrics 汇总")
    print("=" * 70)
    print(f"{'API':<20} {'状态':<10} {'TTFB (s)':<12} {'结果':<10}")
    print("-" * 70)
    
    for api_name, metrics in performance_metrics.items():
        status_icon = "✅" if metrics["success"] else "❌"
        ttfb_str = f"{metrics['ttfb']:.3f}" if metrics["ttfb"] < 10 else f"{metrics['ttfb']:.1f}"
        status_code = metrics.get("status", "N/A")
        
        print(f"{api_name:<20} {status_code:<10} {ttfb_str:<12} {status_icon:<10}")
    
    # 计算平均 TTFB
    successful_ttfbs = [m["ttfb"] for m in performance_metrics.values() if m["success"]]
    if successful_ttfbs:
        avg_ttfb = sum(successful_ttfbs) / len(successful_ttfbs)
        print("-" * 70)
        print(f"{'Average TTFB':<20} {'':<10} {avg_ttfb:.3f}s")


async def main(benchmark_mode=False):
    print("=" * 50)
    print("API 代理测试 - FastAPI Backend")
    if benchmark_mode:
        print("🚀 Benchmark Mode: 性能监控已启用")
    print("=" * 50)
    
    results = {}
    
    # Test health
    results["health"] = await test_health()
    
    # Test DashScope
    try:
        results["dashscope"] = await test_dashscope()
    except Exception as e:
        print(f"\n=== DashScope Error: {e} ===")
        results["dashscope"] = False
        performance_metrics["dashscope"] = {"status": "Error", "ttfb": 0, "success": False}
    
    # Test ModelScope
    try:
        results["modelscope"] = await test_modelscope()
    except Exception as e:
        print(f"\n=== ModelScope Error: {e} ===")
        results["modelscope"] = False
        performance_metrics["modelscope"] = {"status": "Error", "ttfb": 0, "success": False}
    
    # Test Minimax
    try:
        results["minimax"] = await test_minimax()
    except Exception as e:
        print(f"\n=== Minimax Error: {e} ===")
        results["minimax"] = False
        performance_metrics["minimax"] = {"status": "Error", "ttfb": 0, "success": False}
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    # 打印性能表格（仅在 benchmark 模式）
    if benchmark_mode:
        print_performance_table()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API 代理测试工具")
    parser.add_argument("--benchmark", action="store_true", help="启用性能基准测试模式")
    args = parser.parse_args()
    
    asyncio.run(main(benchmark_mode=args.benchmark))
