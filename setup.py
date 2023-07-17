from setuptools import find_packages, setup

long_description = ""

setup(
    name="altscore",
    version="0.0.94",
    description="Python SDK for AltScore. It provides a simple interface to the AltScore API.",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/altscore/altscore-python",
    author="AltScore",
    author_email="developers@altscore.ai",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.80",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "click",
        "requests",
        "pandas",
        "pydantic<=1.10.12",
        "tabulate",
        "httpx",
        "stringcase"
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.8",
)
