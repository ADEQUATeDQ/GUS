#!/usr/bin/env python
from setuptools import setup, find_packages
from gus import description

setup(name='gus',
      version='1.0',
      description=description.DESCRIPTION,
      author='Sebastian Neumaier',
      url='https://github.com/ADEQUATeDQ/gitlab-update-service',
      packages=find_packages(include=['gus']),
      entry_points={
          'console_scripts': ['gus=gus.main:main'],
      },
      install_requires=[
          'Flask==0.12.2',
          'flask-restplus==0.10.1',
          'python-gitlab==1.3.0',
          'rdflib==4.2.2',
          'rdflib-jsonld==0.4.0'
      ]
      )
