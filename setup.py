from setuptools import setup, find_packages

setup(
    name="goblin-forge",
    version="0.1.0",
    description="A web application for executing CLI binaries through a menu-driven interface",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "pydantic>=2.4.2",
        "celery>=5.3.4",
        "redis>=5.0.1",
        "python-multipart>=0.0.6",
        "httpx>=0.25.0",
        "asyncio>=3.4.3",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
