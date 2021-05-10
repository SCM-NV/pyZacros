.. list-table::
   :widths: 25 25
   :header-rows: 1

   * - fair-software.nl recommendations
     - Badges
   * - \1. Code repository
     - |GitHub Badge|
   * - \2. License
     - |License Badge|
   * - \3. Community Registry
     - |PyPI Badge| |Research Software Directory Badge|
   * - \4. Enable Citation
     - |Zenodo Badge|
   * - \5. Checklist
     - |CII Best Practices Badge|
   * - **Other best practices**
     -
   * - Continuous integration
     - |Python Build| |PyPI Publish|

(Customize these badges with your own links, and check https://shields.io/ or https://badgen.net/ to see which other badges are available.)

.. |GitHub Badge| image:: https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue
   :target: https://github.com/NLeSC/pyZacros
   :alt: GitHub Badge

.. |License Badge| image:: https://img.shields.io/github/license/NLeSC/pyZacros
   :target: https://github.com/NLeSC/pyZacros
   :alt: License Badge

.. |PyPI Badge| image:: https://img.shields.io/pypi/v/pyZacros.svg?colorB=blue
   :target: https://pypi.python.org/project/pyZacros/
   :alt: PyPI Badge
.. |Research Software Directory Badge| image:: https://img.shields.io/badge/rsd-pyZacros-00a3e3.svg
   :target: https://www.research-software.nl/software/pyZacros
   :alt: Research Software Directory Badge

..
    Goto https://zenodo.org/account/settings/github/ to enable Zenodo/GitHub integration.
    After creation of a GitHub release at https://github.com/NLeSC/pyZacros/releases
    there will be a Zenodo upload created at https://zenodo.org/deposit with a DOI, this DOI can be put in the Zenodo badge urls.
    In the README, we prefer to use the concept DOI over versioned DOI, see https://help.zenodo.org/#versioning.
.. |Zenodo Badge| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4354011.svg
   :target: https://doi.org/10.5281/zenodo.4354011
   :alt: Zenodo Badge

..
    A CII Best Practices project can be created at https://bestpractices.coreinfrastructure.org/en/projects/new
.. |CII Best Practices Badge| image:: https://bestpractices.coreinfrastructure.org/projects/< replace with created project identifier >/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/< replace with created project identifier >
   :alt: CII Best Practices Badge

.. |Python Build| image:: https://github.com/NLeSC/pyZacros/workflows/Python/badge.svg
   :target: https://github.com/NLeSC/pyZacros/actions?query=workflow%3A%22Python%22
   :alt: Python Build

.. |PyPI Publish| image:: https://github.com/NLeSC/pyZacros/workflows/PyPI/badge.svg
   :target: https://github.com/NLeSC/pyZacros/actions?query=workflow%3A%22PyPI%22
   :alt: PyPI Publish

################################################################################
pyZacros
################################################################################

A Python library to handle KMC codes.


The project setup is documented in `a separate document <project_setup.rst>`_. Feel free to remove this document (and/or the link to this document) if you don't need it.

Installation
------------

To install pyZacros, do:

.. code-block:: console

  git clone https://github.com/NLeSC/pyZacros.git
  cd pyZacros
  pip install .


Run tests (including coverage) with:

.. code-block:: console

  python setup.py test


Documentation
*************

.. _README:

Include a link to your project's full documentation here.

Contributing
************

If you want to contribute to the development of pyZacros,
have a look at the `contribution guidelines <CONTRIBUTING.rst>`_.

License
*******

pyZacros is an Open Source project supported by the Netherlands eScience Center (NLeSC) and Software for Chemistry & Materials BV (SCM, and previously known as Scientific Computing & Modelling NV). The terms of the [LGPL-3.0 license]* apply. As an exception to the LGPL-3.0 license, you agree to grant SCM a [BSD 3-Clause license]** to the contributions you commit on this Github or provide to SCM in another manner.

\* https://opensource.org/licenses/LGPL-3.0

** https://opensource.org/licenses/BSD-3-Clause

[LGPL-3.0 license]:  https://opensource.org/licenses/LGPL-3.0 "LGPL-3.0 license"
[BSD 3-Clause license]: https://opensource.org/licenses/BSD-3-Clause  "BSD 3-Clause license"

Credits
*******

This package was created with `Cookiecutter <https://github.com/audreyr/cookiecutter>`_ and the `NLeSC/python-template <https://github.com/NLeSC/python-template>`_.
