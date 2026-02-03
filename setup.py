import os
from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="qa-automation-framework",
    version="0.1.0",
    description="Reusable QA Automation Framework for UI and API testing",
    packages=find_packages(),
    install_requires=read_requirements(),
)
