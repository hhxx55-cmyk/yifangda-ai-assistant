"""
估值核对AI助手 - 快速启动脚本
一键生成数据并启动应用
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 估值核对AI助手 - 快速启动")
    print("=" * 60)
    
    # 检查依赖
    print("\n📦 检查依赖包...")
    try:
        import streamlit
        import pandas
        import numpy
        import sklearn
        import plotly
        print("✅ 所有依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return
    
    # 生成数据
    print("\n📊 生成样例数据...")
    try:
        from data_generator import ValuationDataGenerator
        
        generator = ValuationDataGenerator(seed=42)
        generator.save_all_data()
        print("✅ 样例数据生成完成")
    except Exception as e:
        print(f"❌ 数据生成失败: {e}")
        return
    
    # 启动应用
    print("\n🚀 启动Streamlit应用...")
    print("\n" + "=" * 60)
    print("应用将在浏览器中自动打开")
    print("默认地址: http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    print("=" * 60 + "\n")
    
    try:
        # 获取app.py的绝对路径
        app_path = Path(__file__).parent / "app.py"
        
        # 启动Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")


if __name__ == '__main__':
    main()