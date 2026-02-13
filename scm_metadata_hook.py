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

        scm_dependencies = [
            f"plams>{major_version},<={base_version}",
        ]

        metadata["dependencies"].extend(scm_dependencies)

