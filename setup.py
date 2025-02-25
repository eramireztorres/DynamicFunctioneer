from setuptools import setup, find_packages


setup(
    name="dynamic_functioneer",
    version="0.1.0",
    description="A Python package for dynamic function and method handling with LLM support.",
    author="Erick Eduardo Ramirez Torres",
    author_email="erickeduardoramireztorres@gmail.com",
    license="MIT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=[
        "astunparse",
        "uv",
        # "openai==1.55.3",
        # "openai",
        "openai==1.64.0",
        "httpx==0.27.2",
        "requests==2.32.3"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    packages=find_packages(),
    include_package_data=True,  # Ensure package data is included
    package_data={
        "dynamic_functioneer": ["prompts/*"],
    },
    exclude_package_data={
        "": ["tests", "examples"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="dynamic methods functions LLM hot-swapping",
    url="https://github.com/eramireztorres/DynamicFunctioneer",
    project_urls={
        "Documentation": "https://github.com/eramireztorres/DynamicFunctioneer",
        "Source": "https://github.com/eramireztorres/DynamicFunctioneer",
    },
)


