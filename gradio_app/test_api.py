#!/usr/bin/env python3
"""
API 测试脚本
测试 DeepSeek-OCR Agent API 的所有接口
"""

import requests
import base64
import json
import time
from pathlib import Path

# API 基础 URL
BASE_URL = "http://localhost:8000"


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_root():
    """测试根路径"""
    print_section("测试 1: 根路径")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        assert response.status_code == 200
        print("✅ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_health():
    """测试健康检查"""
    print_section("测试 2: 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        print("✅ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_get_tasks():
    """测试获取任务列表"""
    print_section("测试 3: 获取任务列表")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tasks")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert len(data['data']['tasks']) > 0
        print("✅ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_get_resolutions():
    """测试获取分辨率列表"""
    print_section("测试 4: 获取分辨率列表")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/resolutions")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert len(data['data']['resolutions']) > 0
        print("✅ 测试通过")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def create_test_image():
    """创建测试图像"""
    from PIL import Image, ImageDraw, ImageFont
    import os

    # 创建白色背景图像
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)

    # 绘制文本
    text = "DeepSeek-OCR API Test"

    # 使用默认字体
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # 如果失败，使用默认字体
        font = ImageFont.load_default()

    # 绘制黑色文本
    draw.text((50, 80), text, fill='black', font=font)

    # 保存图像到当前目录
    test_image_path = Path("test_image.jpg")
    img.save(test_image_path, format='JPEG')

    return test_image_path


def test_ocr_file_upload():
    """测试 OCR 文件上传接口"""
    print_section("测试 5: OCR 文件上传接口")
    
    try:
        # 创建测试图像
        test_image_path = create_test_image()
        print(f"测试图像: {test_image_path}")
        
        # 准备请求
        with open(test_image_path, 'rb') as f:
            files = {'image': ('test.jpg', f, 'image/jpeg')}
            data = {
                'task': '通用OCR',
                'resolution_mode': 'Tiny (512×512) - 快速',
                'save_visualization': False
            }
            
            print("发送 OCR 请求...")
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/api/v1/ocr", files=files, data=data)
            elapsed_time = time.time() - start_time
            
            print(f"状态码: {response.status_code}")
            print(f"请求耗时: {elapsed_time:.2f}s")
            
            result = response.json()
            print(f"成功: {result.get('success')}")
            print(f"消息: {result.get('message')}")
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"识别文本: {data.get('text', '')[:100]}...")
                print(f"边界框数量: {data.get('bounding_box_count', 0)}")
                print(f"推理时间: {data.get('inference_time', 0)}s")
                print(f"总时间: {data.get('total_time', 0)}s")
                print(f"Token 数: {data.get('num_tokens', 0)}")
            else:
                print(f"错误: {result.get('error')}")
            
            assert response.status_code == 200
            assert result['success'] == True
            print("✅ 测试通过")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ocr_base64():
    """测试 OCR Base64 接口"""
    print_section("测试 6: OCR Base64 接口")
    
    try:
        # 创建测试图像
        test_image_path = create_test_image()
        
        # 读取并编码为 Base64
        with open(test_image_path, 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"Base64 长度: {len(image_base64)}")
        
        # 准备请求
        data = {
            'image_base64': image_base64,
            'task': '纯文本提取',
            'resolution_mode': 'Tiny (512×512) - 快速',
            'save_visualization': False
        }
        
        print("发送 OCR 请求...")
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/ocr/base64", data=data)
        elapsed_time = time.time() - start_time
        
        print(f"状态码: {response.status_code}")
        print(f"请求耗时: {elapsed_time:.2f}s")
        
        result = response.json()
        print(f"成功: {result.get('success')}")
        print(f"消息: {result.get('message')}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"识别文本: {data.get('text', '')[:100]}...")
            print(f"推理时间: {data.get('inference_time', 0)}s")
        else:
            print(f"错误: {result.get('error')}")
        
        assert response.status_code == 200
        assert result['success'] == True
        print("✅ 测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  DeepSeek-OCR Agent API 测试套件")
    print("=" * 60)
    print(f"API 地址: {BASE_URL}")
    print("=" * 60)
    
    # 等待服务启动
    print("\n等待 API 服务启动...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                print("✅ API 服务已就绪")
                break
        except:
            pass
        
        if i < max_retries - 1:
            print(f"等待中... ({i+1}/{max_retries})")
            time.sleep(1)
        else:
            print("❌ API 服务未启动，请先启动服务")
            return
    
    # 运行测试
    results = []
    
    results.append(("根路径", test_root()))
    results.append(("健康检查", test_health()))
    results.append(("获取任务列表", test_get_tasks()))
    results.append(("获取分辨率列表", test_get_resolutions()))
    results.append(("OCR 文件上传", test_ocr_file_upload()))
    results.append(("OCR Base64", test_ocr_base64()))
    
    # 打印测试结果
    print_section("测试结果汇总")
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")


if __name__ == "__main__":
    run_all_tests()

