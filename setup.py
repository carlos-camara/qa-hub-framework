from setuptools import setup, find_packages

setup(
    name="qa-automation-framework",
    version="0.1.0",
    description="Reusable QA Automation Framework for UI and API testing",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "behave",
        "requests"
    ],
)
