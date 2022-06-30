#!/usr/bin/env python
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

packages = ['pyzacros'] + ['pyzacros.'+i for i in find_packages('.')]

# To update the package version number, edit pyZacros/__version__.py
version = {}
with open(os.path.join(here, '__version__.py')) as f:
    exec(f.read(), version)

with open('README.md') as readme_file:
    readme = readme_file.read()

def package_files( directory ):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_data_files = []
extra_data_files.extend( package_files('examples') )
extra_data_files.extend( package_files('tests') )

setup(
    name='pyzacros',
    version=version['__version__'],
    description="Python Library for Automating Zacros Simulations",
    long_description=readme + '\n\n',
    author="Pablo Lopez-Tarifa",
    author_email='p.lopez@esciencecenter.nl',
    url='https://github.com/SCM-NV/pyZacros',
    packages=packages,
    package_dir = {'pyzacros': '.'},
    package_data={'': extra_data_files},
    include_package_data=True,
    license="LGPLv3",
    zip_safe=False,
    keywords = ['molecular modeling', 'computational chemistry', 'workflow', 'python interface'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'pyaml', 'chemparse', 'scipy<=1.5.4', 'numpy<=1.19.5', 'networkx<=2.5.1',
        'plams@git+https://github.com/SCM-NV/PLAMS@master'],
    extras_require={
        'test': ['coverage', 'pytest>=3.9', 'pytest-cov'],
        'doc': ['sphinx', 'sphinx_rtd_theme', 'nbsphinx']
    }
)
