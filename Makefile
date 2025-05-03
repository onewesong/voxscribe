.PHONY: install install-dev install-apple start cli web dev clean help

# 检测是否为Apple Silicon芯片（用于安装mlx_whisper）
UNAME_PROCESSOR := $(shell uname -m)
ifeq ($(UNAME_PROCESSOR),arm64)
	ON_APPLE_SILICON = 1
else
	ON_APPLE_SILICON = 0
endif

help:
	@echo "VoxScribe 命令帮助"
	@echo "------------------"
	@echo "make install      - 使用uv安装所有依赖"
	@echo "make install-dev  - 安装开发环境（包含所有依赖）"
	@echo "make install-apple- 安装Apple Silicon特定依赖（包含mlx_whisper）"
	@echo "make start        - 启动VoxScribe网页界面"
	@echo "make cli file=... - 运行命令行转录（例如：make cli file=audio.mp3）"
	@echo "make web          - 启动网页界面"
	@echo "make dev          - 以开发模式启动网页界面"
	@echo "make clean        - 清理临时文件和缓存"

install:
	@echo "使用uv安装VoxScribe依赖..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements.txt; \
	else \
		echo "uv未安装，请先安装uv："; \
		echo "curl -sSf https://install.python-uv.org | python3"; \
		exit 1; \
	fi
	@echo "安装VoxScribe包..."
	@uv pip install -e .
	@echo "安装完成！运行 'make start' 启动VoxScribe"

install-dev: install
	@echo "安装开发依赖..."
	@uv pip install pytest black isort mypy
	@echo "开发环境安装完成！"

install-apple:
	@if [ $(ON_APPLE_SILICON) -eq 1 ]; then \
		echo "检测到Apple Silicon，安装mlx_whisper..."; \
		uv pip install mlx_whisper; \
		echo "MLX加速已启用！"; \
	else \
		echo "非Apple Silicon设备，跳过mlx_whisper安装"; \
	fi

start: web

cli:
	@if [ -z "$(file)" ]; then \
		echo "请指定音频文件，例如：make cli file=audio.mp3"; \
	else \
		voxscribe-cli $(file); \
	fi

web:
	@echo "启动VoxScribe网页界面..."
	@voxscribe

dev:
	@echo "以开发模式启动VoxScribe..."
	@python -m streamlit run voxscribe/app.py --server.runOnSave=true

clean:
	@echo "清理临时文件和缓存..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@rm -rf build/ dist/
	@echo "清理完成！" 