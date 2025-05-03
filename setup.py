from setuptools import setup, find_packages

setup(
    name="voxscribe",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "datasets",
        "accelerate",
        "streamlit>=1.22.0",
    ],
    entry_points={
        "console_scripts": [
            "voxscribe-cli=voxscribe.cli:main",
            "voxscribe=voxscribe.run_app:main",
        ],
    },
    python_requires=">=3.8",
    author="",
    author_email="",
    description="VoxScribe - 优雅的音频转文字工具，提供直观的网页界面和强大的命令行支持",
    keywords="whisper, asr, speech-to-text, streamlit, web-interface",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 