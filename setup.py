from setuptools import setup, find_packages

setup(
    name="dynamic_functioneer",  # Replace with your project name
    version="0.1.0",  # Update as per semantic versioning
    author="Erick Eduardo Ramirez Torres",
    author_email="erickeduardoramireztorres@gmail.com",
    description="A Python package for dynamic function and method handling with LLM support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/eramireztorres/DynamicFunctioneer",  
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    include_package_data=True,  # Includes files specified in MANIFEST.in
    python_requires=">=3.7",  # Update based on your project’s requirements
    install_requires=[
        "setuptools>=42",
        "importlib-metadata>=1.0; python_version<'3.8'",  # Example dependency
        # "numpy>=1.19.0",
        "astunparse",  # If used in your project
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
    entry_points={
        "console_scripts": [
            "dynamic-cli=dynamic_functioneer.cli:main",  # Example CLI entry point
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",  # Update license if needed
        "Operating System :: OS Independent",
    ],
    license="MIT",  
    keywords="dynamic methods functions LLM hot-swapping",

)
