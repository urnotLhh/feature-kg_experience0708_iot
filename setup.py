#!/usr/bin/env python
# coding: utf-8
"""
TransE Knowledge Graph Embedding Project Setup
知识图谱嵌入项目安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "TransE Knowledge Graph Embedding Project"

# 读取requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="transe-kge",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="TransE Knowledge Graph Embedding for IoT Device Identification",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/transe-kge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=5.0.0",
            "pytest-cov>=2.8.0",
            "black>=19.0.0",
            "flake8>=3.7.0",
        ],
        "docs": [
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "transe-kge=transe_kge.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 