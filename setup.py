"""Setup configuration for EnvLint."""

from setuptools import setup, find_packages

setup(
    name="envlint",
    version="0.1.0",
    description="CLI tool for validating .env files against a schema",
    author="EnvLint Contributors",
    packages=find_packages(),
    package_data={
        "envlint": ["templates/*.html"],
    },
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "flask>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "envlint=envlint.main:main",
        ],
    },
    python_requires=">=3.11",
)
