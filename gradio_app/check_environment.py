#!/usr/bin/env python3
"""
环境检查脚本
检查所有必要的依赖是否已安装
"""

import sys
import os

def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (需要 3.12+)")
        return False


def check_package(package_name, import_name=None):
    """检查 Python 包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"  ✅ {package_name}")
        return True
    except ImportError:
        print(f"  ❌ {package_name} (未安装)")
        return False


def check_packages():
    """检查所有必要的包"""
    print("\n检查 Python 包...")
    
    packages = [
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("gradio", "gradio"),
        ("PIL", "PIL"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
    ]
    
    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    
    return all(results)


def check_torch_device():
    """检查 PyTorch 可用设备"""
    print("\n检查 PyTorch 设备...")
    
    try:
        import torch
        
        # 检查 MPS
        if torch.backends.mps.is_available():
            print("  ✅ MPS (Apple Silicon GPU) 可用")
            return True
        
        # 检查 CUDA
        if torch.cuda.is_available():
            print(f"  ✅ CUDA 可用 (设备数: {torch.cuda.device_count()})")
            return True
        
        # 只有 CPU
        print("  ⚠️  仅 CPU 可用 (推理速度较慢)")
        return True
        
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False


def check_modules():
    """检查自定义模块"""
    print("\n检查自定义模块...")
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    modules = [
        "modules.model_manager",
        "modules.image_processor",
        "modules.prompt_builder",
        "modules.ocr_engine",
        "modules.result_processor",
    ]
    
    results = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
            results.append(True)
        except ImportError as e:
            print(f"  ❌ {module} (导入失败: {e})")
            results.append(False)
    
    return all(results)


def check_directories():
    """检查必要的目录"""
    print("\n检查目录结构...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    directories = [
        "modules",
        "outputs",
        "logs",
        "examples",
    ]
    
    results = []
    for directory in directories:
        path = os.path.join(base_dir, directory)
        if os.path.exists(path):
            print(f"  ✅ {directory}/")
            results.append(True)
        else:
            print(f"  ❌ {directory}/ (不存在)")
            results.append(False)
    
    return all(results)


def check_files():
    """检查必要的文件"""
    print("\n检查核心文件...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    files = [
        "gradio_ocr_app.py",
        "start_app.sh",
        "test_modules.py",
        "modules/__init__.py",
        "modules/model_manager.py",
        "modules/image_processor.py",
        "modules/prompt_builder.py",
        "modules/ocr_engine.py",
        "modules/result_processor.py",
    ]
    
    results = []
    for file in files:
        path = os.path.join(base_dir, file)
        if os.path.exists(path):
            print(f"  ✅ {file}")
            results.append(True)
        else:
            print(f"  ❌ {file} (不存在)")
            results.append(False)
    
    return all(results)


def print_summary(results):
    """打印检查结果摘要"""
    print("\n" + "=" * 60)
    print("环境检查结果摘要")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print("-" * 60)
    print(f"总计: {total} 项检查, {passed} 项通过, {failed} 项失败")
    print("=" * 60)
    
    return failed == 0


def print_recommendations(results):
    """打印修复建议"""
    if all(results.values()):
        print("\n✅ 所有检查通过！你可以运行应用了。")
        print("\n启动命令:")
        print("  ./start_app.sh")
        print("  或")
        print("  python gradio_ocr_app.py")
        return
    
    print("\n⚠️  发现问题，请按照以下建议修复：")
    
    if not results.get("Python 版本", True):
        print("\n1. 升级 Python 版本:")
        print("   conda create -n deepseek-ocr python=3.12")
        print("   conda activate deepseek-ocr")
    
    if not results.get("Python 包", True):
        print("\n2. 安装缺失的包:")
        print("   pip install -r requirements.txt")
        print("   pip install gradio")
    
    if not results.get("自定义模块", True):
        print("\n3. 检查模块文件:")
        print("   确保所有 .py 文件都存在且没有语法错误")
    
    if not results.get("目录结构", True):
        print("\n4. 创建缺失的目录:")
        print("   mkdir -p outputs logs examples")
    
    if not results.get("核心文件", True):
        print("\n5. 检查核心文件:")
        print("   确保所有必要的文件都存在")


def main():
    """主函数"""
    print("=" * 60)
    print("DeepSeek-OCR Gradio 应用 - 环境检查")
    print("=" * 60)
    
    results = {}
    
    # 执行所有检查
    results["Python 版本"] = check_python_version()
    results["Python 包"] = check_packages()
    results["PyTorch 设备"] = check_torch_device()
    results["自定义模块"] = check_modules()
    results["目录结构"] = check_directories()
    results["核心文件"] = check_files()
    
    # 打印摘要
    all_passed = print_summary(results)
    
    # 打印建议
    print_recommendations(results)
    
    # 返回状态码
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

