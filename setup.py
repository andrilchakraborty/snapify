from setuptools import setup

setup(
    name="snapify",
    version="0.1.0",
    py_modules=["snapify_core", "snapify_cli"],
    install_requires=[
        "aiohttp",
        "aiofiles",
        "beautifulsoup4",
        "typer",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "snapify = snapify_cli:snapify",
        ],
    },
    python_requires=">=3.7",
)
