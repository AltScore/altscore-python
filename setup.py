from setuptools import find_packages, setup

long_description = "Python SDK for AltScore"

setup(
    name="altscore",
    version="0.1.11",
    description="Python SDK for AltScore. It provides a simple interface to the AltScore API.",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/altscore/altscore-python",
    author="AltScore",
    author_email="developers@altscore.ai",
    license="MIT",
    entry_points={
        'console_scripts': [
            'altscore-tui = tui.app:main',  # Adjust the path and function
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.80",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "click",
        "requests",
        "pydantic<=1.10.12",
        "httpx",
        "stringcase"
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2", "textual", "pandas", "tabulate"],
        "data-tools": ["pandas", "tabulate"],
        "cli": ["textual", "pandas", "tabulate"],
    },
    python_requires=">=3.8",
)
