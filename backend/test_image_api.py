"""
测试图像生成 API 的后端代理路由
测试两个服务：Minimax 和 Wanx
"""
import requests
import json

BASE_URL = 'http://localhost:7860'

def test_minimax():
    """测试 Minimax 图像生成 API"""
    print("\n" + "="*60)
    print("Testing Minimax Image Generation API")
    print("="*60)
    
    endpoint = f'{BASE_URL}/api/minimax/v1/image_generation'
    payload = {
        'model': 'image-01',
        'prompt': 'A beautiful sunset over the ocean',
        'aspect_ratio': '16:9',
        'response_format': 'url'
    }
    
    print(f"POST {endpoint}")
    print(f"Request Body: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.ok:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 验证返回格式
            if 'data' in data and 'image_urls' in data.get('data', {}):
                print("\n✅ Minimax API 测试成功")
                return True
            else:
                print("\n⚠️ 返回格式不符合预期")
                return False
        else:
            print(f"Response Body: {response.text}")
            print(f"\n❌ Minimax API 测试失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        return False

def test_wanx():
    """测试 Wanx 图像生成 API"""
    print("\n" + "="*60)
    print("Testing Wanx (Aliyun) Image Generation API")
    print("="*60)
    
    endpoint = f'{BASE_URL}/api/aliyun/services/aigc/text2image/image-synthesis'
    payload = {
        'model': 'wanx2.1-t2i-turbo',
        'input': {
            'prompt': 'A beautiful sunset over the ocean'
        },
        'parameters': {
            'style': '<auto>',
            'size': '1280*720',
            'n': 1
        }
    }
    
    print(f"POST {endpoint}")
    print(f"Request Body: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.ok:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 验证返回格式
            if 'output' in data and 'results' in data.get('output', {}):
                print("\n✅ Wanx API 测试成功")
                return True
            else:
                print("\n⚠️ 返回格式不符合预期")
                return False
        else:
            print(f"Response Body: {response.text}")
            print(f"\n❌ Wanx API 测试失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        return False

if __name__ == '__main__':
    print("开始测试图像生成 API...")
    print(f"后端服务地址: {BASE_URL}")
    
    # 测试 Minimax
    minimax_ok = test_minimax()
    
    # 测试 Wanx
    wanx_ok = test_wanx()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"Minimax: {'✅ 通过' if minimax_ok else '❌ 失败'}")
    print(f"Wanx:    {'✅ 通过' if wanx_ok else '❌ 失败'}")
    
    if minimax_ok or wanx_ok:
        print("\n至少有一个服务可用，前端应该能够正常工作")
    else:
        print("\n⚠️ 所有服务都失败了，需要检查后端配置和 API Keys")
