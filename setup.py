#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="polycom-recorder",
    version="0.1.1",
    packages=[ "polycom_recorder" ],
    package_data={
        "polycom_recorder": [ 'effects' ],
    },
    description="Sound-activated audio recorder",
    author="Christian Ullrich",
    author_email="christian.ullrich@traditionsa.lu",
    license="Proprietary",
    url="https://github.com/chrullrich/polycom-recorder/",
    entry_points={
        "console_scripts": [
            'polycom-recorder = polycom_recorder.recorder:main',
            'polycom-updater = polycom_recorder.website:main',
        ],
    },
)
