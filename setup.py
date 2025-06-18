"""
Setup configuration for Consumer Credit Vintage Analysis package
"""

from setuptools import setup, find_packages
import pathlib

# Read the contents of README file
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="vintage-analysis",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive vintage analysis tool for consumer credit portfolios",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vintage-analysis",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "viz": [
            "plotly>=5.0.0",
            "seaborn>=0.11.0",
        ],
        "stats": [
            "scipy>=1.9.0",
            "scikit-learn>=1.1.0",
            "statsmodels>=0.13.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "vintage-analysis=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/vintage-analysis/issues",
        "Source": "https://github.com/yourusername/vintage-analysis",
        "Documentation": "https://vintage-analysis.readthedocs.io/",
    },
    keywords="credit-risk vintage-analysis finance banking consumer-credit risk-management",
)
