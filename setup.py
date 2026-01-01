from setuptools import setup, find_packages

setup(
    name="codelancer",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "codelancer=codelancer.cli:main",
        ],
    },
)
