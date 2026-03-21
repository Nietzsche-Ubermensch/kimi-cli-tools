#!/usr/bin/env python3
"""
Setup for CogGraph MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="coggraph-mcp-server",
    version="1.0.0",
    author="Nietzsche-Ubermensch",
    description="Cognitive Graph MCP Server - Persistent Reasoning Context",
    long_description=open("README.md").read(),
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
        "networkx>=3.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "coggraph-server=coggraph.server:main",
        ],
    },
)
