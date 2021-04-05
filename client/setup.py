'''                       
Python package setup (used by Dockerfile).
'''

import os
import subprocess

from setuptools import setup, find_packages

data_files = []

setup(
    name='Weather cli',
    version='1.0',
    description='Sawtooth weather transaction family CLI',
    author='Nyquist',
    url='https://github.com/LadyTrejos/weather-app',
    packages=find_packages(),
    install_requires=[
        'colorlog',
        'sawtooth-sdk',
        'PyYAML',
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'sawtooth-weather = weather-client.cli:main_wrapper',
        ]
    })