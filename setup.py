#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='chemview',
      version='0.1.1',
      description='Interactive molecular viewer for IPython notebook',
      author='Gabriele Lanaro',
      author_email='gabriele.lanaro@gmail.com',
      url='https://github.com/gabrielelanaro/chemview',
      packages=find_packages(),
      install_requires = ['numpy', 'ipython[notebook]', 'numba'],
      package_data = {'': ['*.js', "*.css"]},
      include_package_data=True
      )
