import os
from setuptools import setup, find_packages

def read_requirements():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, "requirements.txt")) as f:
        return f.read().splitlines()

setup(
    name="qa-automation-framework",
    version="0.1.1",
    description="Reusable QA Automation Framework for UI and API testing",
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'qa-hub = qa_framework.cli:main',
        ],
    },
)
