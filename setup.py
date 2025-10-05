"""
QEC (Quantum Entanglement Chess) Package Setup
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'core', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "0.1.0"

# Read README for long description
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Quantum Entanglement Chess - A novel chess variant with quantum mechanics"

setup(
    name="qec",
    version=get_version(),
    author="QEC Research Team",
    author_email="research@qec.dev",
    description="Quantum Entanglement Chess - A novel chess variant with quantum mechanics",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nemeca99/QED",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "toml>=0.10.0",
        "matplotlib>=3.3.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "hypothesis>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "pdoc>=12.0.0",
            "sphinx>=4.0.0",
        ],
        "bench": [
            "pytest-benchmark>=3.4.0",
            "memory-profiler>=0.60.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qec-simulate=qec.cli:simulate",
            "qec-research=qec.cli:research", 
            "qec-validate=qec.cli:validate",
        ],
    },
    include_package_data=True,
    package_data={
        "qec": [
            "schemas/*.json",
            "examples/*.toml",
            "examples/*.json",
        ],
    },
    zip_safe=False,
)
