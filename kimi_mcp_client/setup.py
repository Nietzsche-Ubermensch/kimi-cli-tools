#!/usr/bin/env python3
"""
Setup script for Kimi MCP Client
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="kimi-mcp-client",
    version="1.0.0",
    author="Nietzsche-Ubermensch",
    author_email="peterbilt5018@gmail.com",
    description="8-server MCP orchestration for Kimi CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nietzsche-Ubermensch/kimi-cli-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "rich>=13.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "kimi-mcp=kimi_mcp_client.cli:main",
        ],
    },
)
