#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit pyZacros/__version__.py
version = {}
with open(os.path.join(here, 'pyzacros', '__version__.py')) as f:
    exec(f.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='pyzacros',
    version=version['__version__'],
    description="A Python library to handle KMC codes.",
    long_description=readme + '\n\n',
    author="Pablo Lopez-Tarifa",
    author_email='p.lopez@esciencecenter.nl',
    url='https://github.com/NLeSC/pyZacros',
    packages=find_packages(),
    include_package_data=True,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='pyZacros',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    install_requires=[
        'pyaml', 'chemparse',
        'plams@git+https://github.com/SCM-NV/PLAMS@master'],

    extras_require={
        'test': ['coverage', 'pycodestyle', 'pytest>=3.9', 'pytest-cov'],
        'doc': ['sphinx', 'sphinx_rtd_theme', 'nbsphinx']
    }
)
