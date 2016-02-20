#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='chemview',
      version='0.6',
      description='Interactive molecular viewer for IPython notebook',
      author='Gabriele Lanaro',
      install_requires=['notebook', 'numpy', 'matplotlib', 'vapory'],
      author_email='gabriele.lanaro@gmail.com',
      url='https://github.com/gabrielelanaro/chemview',
      packages=find_packages(),
      package_data={'': ['*.js', "*.css"]},
      include_package_data=True
      )
