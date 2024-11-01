from setuptools import setup, find_packages

setup(
    name="movie-aggregator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "requests",
        "httpx",
    ],
)