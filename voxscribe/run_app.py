#!/usr/bin/env python
"""
快速启动VoxScribe网页界面
"""

import os
import sys
import subprocess
import streamlit.web.bootstrap
from pathlib import Path


def main():
    """启动VoxScribe网页应用"""
    # 获取app.py的路径
    app_path = Path(__file__).parent / "app.py"
    
    if not app_path.exists():
        print(f"错误：找不到应用文件 {app_path}")
        sys.exit(1)
    
    print(f"启动 VoxScribe 网页界面...")
    print(f"应用路径: {app_path}")
    print(f"按 Ctrl+C 停止应用")
    
    # 通过Streamlit的bootstrap API启动应用
    sys.argv = ["streamlit", "run", str(app_path), "--browser.serverAddress=localhost", "--server.port=8501"]
    streamlit.web.bootstrap.run()


if __name__ == "__main__":
    main() 