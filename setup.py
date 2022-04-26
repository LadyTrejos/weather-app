import os
from setuptools import setup, find_packages

DATA_FILES = []

if os.path.exists("/etc/default"):
    DATA_FILES.append(("/etc/default", ["packaging/systemd/sawtooth-weather-tp"]))

if os.path.exists("/lib/systemd/system"):
    DATA_FILES.append(
        ("/lib/systemd/system", ["packaging/systemd/sawtooth-weather-tp.service"])
    )

setup(
    name="Sawtooth Weather",
    version="1.0",
    description="Sawtooth weather python",
    author="Nyquist",
    url="https://github.com/LadyTrejos/weather-app",
    packages=find_packages(),
    install_requires=["requests", "cbor", "sawtooth-sdk", "PyYAML", "colorlog"],
    data_files=DATA_FILES,
    entry_points={
        "console_scripts": [
            "weather-tp = weather.processor.main:main",
            "weather = weather.client.cli:main_wrapper",
        ]
    },
)
