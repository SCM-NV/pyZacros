"""Metadata hook required for correct automatic versioning of SCM Python deps.

We constrain deps to > the last major version and <= the current tag to allow .dev builds.
Example: 2025.207.dev4 < 2025.207, so <= 2025.207 includes dev releases.
"""
from __future__ import annotations

from hatchling.metadata.plugin.interface import MetadataHookInterface
from packaging.version import Version


class ScmDependenciesMetadataHook(MetadataHookInterface):
    def update(self, metadata):
        raw_version = metadata["version"]
        version = Version(raw_version)

        base_version = version.base_version
        major_version = version.major

        dependencies = [
            f"plams>{major_version},<={base_version}",
            "chemparse>=0.1.1",
            "matplotlib>=3.5.1",
            "networkx>=2.7.1",
            "numpy>=1.21.2,<2",
            "scipy>=1.8.0",
        ]

        metadata["dependencies"] = dependencies

        optional_dependencies = {
            "test": [
                "pytest>=7.4.0",
                "coverage>=7.5.3",
                "pytest-cov>=3",
            ],
            "doc": [
                "sphinx>=6.2.1,<8.2",
                "sphinx-rtd-theme>=3.0.1",
                "sphinx_copybutton>=0.5.2",
                "nbconvert>=6.4.5",
            ],
        }

        metadata["optional-dependencies"] = optional_dependencies
