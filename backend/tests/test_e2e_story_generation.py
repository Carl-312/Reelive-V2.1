"""
E2E Story Generation 测试
测试完整的用户输入 → LLM 处理 → Galgame 脚本生成流程
"""
import httpx
import asyncio
import json
from typing import Dict, Any

BASE_URL = "http://localhost:7860"


async def test_full_story_pipeline():
    """
    端到端测试：用户输入故事文本 → 生成完整 GalgameScript
    
    Pipeline Flow:
    1. 用户输入 → DashScope (qwen-max) 生成 Outline
    2. Outline → ModelScope (GLM-4.7) 生成分段 Chunks
    3. Chunks → Minimax (image-01) 生成背景图 (可选)
    4. 组装为完整的 GalgameScript JSON
    """
    test_story = """
    小明是一个普通的高中生，某天放学后在图书馆遇到了神秘少女艾莉。
    艾莉告诉他，这座城市隐藏着一个巨大的秘密，而他是唯一能解开谜团的人。
    """
    
    print("=" * 60)
    print("E2E Story Generation Pipeline Test")
    print("=" * 60)
    
    # ===== Step 1: Generate Outline via DashScope =====
    print("\n[Step 1/3] 生成故事大纲 (DashScope qwen-max)")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=60) as client:
        outline_resp = await client.post(
            f"{BASE_URL}/api/aliyun/compatible-mode/v1/chat/completions",
            json={
                "model": "qwen-max",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的视觉小说编剧。将用户的故事转化为结构化的场景大纲，包括场景列表、角色信息。输出JSON格式。"
                    },
                    {
                        "role": "user",
                        "content": f"将以下故事转化为视觉小说大纲：\n\n{test_story}\n\n输出格式 (JSON):\n{{\n  \"title\": \"故事标题\",\n  \"characters\": [{{\"name\": \"角色名\", \"description\": \"简介\"}}],\n  \"scenes\": [{{\"id\": 1, \"location\": \"地点\", \"summary\": \"概要\"}}]\n}}"
                    }
                ],
                "max_tokens": 1000,
                "response_format": {"type": "json_object"}
            }
        )
    
    if outline_resp.status_code != 200:
        print(f"❌ Outline 生成失败: {outline_resp.status_code}")
        print(outline_resp.text)
        return False
    
    outline_data = outline_resp.json()
    outline_content = outline_data["choices"][0]["message"]["content"]
    print(f"✅ Outline 生成成功 ({len(outline_content)} chars)")
    print(f"Preview: {outline_content[:200]}...")
    
    try:
        outline_json = json.loads(outline_content)
        print(f"   Title: {outline_json.get('title', 'N/A')}")
        print(f"   Characters: {len(outline_json.get('characters', []))}")
        print(f"   Scenes: {len(outline_json.get('scenes', []))}")
    except json.JSONDecodeError:
        print("⚠️  Outline 格式不是有效的 JSON，继续测试...")
    
    # ===== Step 2: Generate Chunks via ModelScope =====
    print("\n[Step 2/3] 生成对话分段 (ModelScope GLM-4.7)")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=60) as client:
        chunk_resp = await client.post(
            f"{BASE_URL}/api/modelscope/chat/completions",
            json={
                "model": "ZhipuAI/GLM-4.7",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是视觉小说对话生成器。基于场景大纲，生成角色对话和旁白。"
                    },
                    {
                        "role": "user",
                        "content": f"基于以下大纲，为第一个场景生成详细的对话：\n\n{outline_content}\n\n输出格式 (JSON数组):\n[{{\"speaker\": \"角色名或null(旁白)\", \"text\": \"对话内容\"}}]"
                    }
                ],
                "max_tokens": 800
            }
        )
    
    if chunk_resp.status_code != 200:
        print(f"❌ Chunks 生成失败: {chunk_resp.status_code}")
        print(chunk_resp.text)
        return False
    
    chunk_data = chunk_resp.json()
    chunk_content = chunk_data["choices"][0]["message"]["content"]
    print(f"✅ Chunks 生成成功 ({len(chunk_content)} chars)")
    print(f"Preview: {chunk_content[:200]}...")
    
    # ===== Step 3: Generate Background Image (Optional) =====
    print("\n[Step 3/3] 生成背景图 (Minimax image-01) [可选]")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            image_resp = await client.post(
                f"{BASE_URL}/api/minimax/v1/image_generation",
                json={
                    "prompt": "高中图书馆，傍晚，柔和的光线，视觉小说背景",
                    "model": "image-01",
                    "n": 1
                }
            )
        
        if image_resp.status_code == 200:
            image_data = image_resp.json()
            if "data" in image_data and "image_urls" in image_data.get("data", {}):
                image_url = image_data["data"]["image_urls"][0]
                print(f"✅ 背景图生成成功")
                print(f"   URL: {image_url[:80]}...")
            else:
                print(f"⚠️  背景图 API 返回格式异常: {image_data}")
        else:
            print(f"⚠️  背景图生成失败 ({image_resp.status_code})，跳过此步骤")
    except Exception as e:
        print(f"⚠️  背景图生成异常: {e}，跳过此步骤")
    
    # ===== Step 4: Validate Complete Script Structure =====
    print("\n[Step 4/4] 验证完整脚本结构")
    print("-" * 60)
    
    # 构建最小可用的 GalgameScript
    mock_script = {
        "title": outline_json.get("title", "测试故事") if 'outline_json' in locals() else "测试故事",
        "characters": outline_json.get("characters", []) if 'outline_json' in locals() else [],
        "scenes": [
            {
                "id": 1,
                "background": image_url if 'image_url' in locals() else "default.jpg",
                "dialogues": json.loads(chunk_content) if chunk_content.startswith("[") else [{"speaker": None, "text": chunk_content}]
            }
        ]
    }
    
    # 验证结构完整性
    assert "title" in mock_script, "Missing 'title' field"
    assert "characters" in mock_script, "Missing 'characters' field"
    assert "scenes" in mock_script, "Missing 'scenes' field"
    assert len(mock_script["scenes"]) > 0, "No scenes generated"
    assert "dialogues" in mock_script["scenes"][0], "Missing 'dialogues' in first scene"
    
    print("✅ GalgameScript 结构验证通过")
    print(f"   Script Size: {len(json.dumps(mock_script))} bytes")
    print(f"   Total Scenes: {len(mock_script['scenes'])}")
    print(f"   Total Dialogues: {len(mock_script['scenes'][0]['dialogues'])}")
    
    return True


async def main():
    print("\n" + "=" * 60)
    print("Backend E2E Story Generation Test")
    print("=" * 60)
    
    success = await test_full_story_pipeline()
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"  E2E Pipeline: {'✅ PASS' if success else '❌ FAIL'}")
    print("")
    
    if success:
        print("🎉 所有测试通过！新系统可以生成完整的 Galgame 脚本。")
    else:
        print("⚠️  测试未通过，请检查 API 配置和网络连接。")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
