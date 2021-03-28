# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

readme = 'Sidewinder is a jazz programming library'
#with open('README.rst') as f:
#    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sidewinder',
    version='0.1.1',
    description='Sidewinder jazz programming library',
    long_description=readme,
    author='Sam Gould',
    author_email='samg7b5@gmail.com',
    url='https://github.com/samg7b5/sidewinder',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'midi_out', 'data', 'Lilypond'))
)

