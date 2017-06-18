# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='PySpaceX',
    version='0.1.0',
    description='A simple game shooter made with pygame',
    long_description=readme,
    author='Daniel Biehle',
    author_email='dannybrain@dannybrain.org',
    url='https://github.com/dannybrain/PySpaceX',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

