from __future__ import print_function

import subprocess

from setuptools import setup, find_packages


setup(
    name='weather-processor',
    version=subprocess.check_output(
        ['../bin/get_version']).decode('utf-8').strip(),
    description='Sawtooth weather transaction processor',
    author='Nyquist',
    url='https://github.com/LadyTrejos/weather-app',
    packages=find_packages(),
    install_requires=[
        'requests', 'cbor', 'sawtooth-sdk'
    ],
    entry_points={
        'console_scripts': [
            'weather-processor = processor.main:main'
        ]
    })
