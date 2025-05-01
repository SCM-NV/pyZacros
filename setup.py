from setuptools import find_packages, setup
from glob import glob
import os

# This minimal setup.py exists alongside the pyproject.toml for legacy reasons.
# Currently, the "artificial" prefix "scm." is added to the (sub)package names, which is not supported via the pyproject.toml.
# ToDo: the package should be restructured with a directory structure that reflects this, then the setuptools package finding used.
# See: https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
doc_files = [
    os.path.relpath(path)  # relative to package_dir
    for path in glob("doc/*")
    if os.path.isfile(path)
]

test_files = [
    os.path.relpath(path)  # relative to package_dir
    for path in glob("tests/**", recursive=True)
    if os.path.isfile(path)
]

examples_files = [
    os.path.relpath(path)  # relative to package_dir
    for path in glob("examples/**", recursive=True)
    if os.path.isfile(path)
]

setup(
    packages=["scm.pyzacros"] + ["scm.pyzacros." + i for i in find_packages(".")],
    package_dir={"scm.pyzacros": "."},
    package_data={"scm.pyzacros": doc_files + test_files + examples_files},
)
