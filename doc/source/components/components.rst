Components overview
===================

.. note::

    In this documentation, we assume you are familiarized with both projects PLAMS and Zacros. If not, first, please
    take a look at our comprehensive documentation about PLAMS on this
    link: `https://www.scm.com/doc/plams <https://www.scm.com/doc/plams/index.html>`_,
    and the documentation about Zacros on its official web page:
    `https://zacros.org <https://zacros.org>`_

This chapter contains a description of all components (classes) that can be used within pyZacros scripts.
The image below shows all classes available in pyZacros.

.. image:: ../../images/architecture.png
   :scale: 60 %
   :align: center

The classes represented in gray boxes are extensions of PLAMS. Settings, ZacrosJob, and ZacrosResults are subclasses
of the PLAMS classes `Settings <https://www.scm.com/doc/plams/components/settings.html>`_,
`SingleJob <https://www.scm.com/doc/plams/components/jobs.html#scm.plams.core.basejob.SingleJob>`_,
and `Results <https://www.scm.com/doc/plams/components/results.html>`_ respectively. Thus, these classes
inherit from PLAMS the robust way of managing the inputs file preparation, job execution, file management,
and output file processing. In a nutshell, the class `Settings <settings.html>`_ is used for establishing the parameters of the
calculation. The `ZacrosJob <zacrosjob.html>`_ class is the primary piece of computational work, and it takes care of running jobs.
Finally, the `ZacrosResults <zacrosresults.html>`_ class takes care of the job results after the execution is finished; it gathers
information about output files, helps to manage them, and extracts data of interest from them.

On the other side, the rest of the classes are specifically designed to define a system in Zacros. The Zacros
package implements a Graph-Theoretical KMC on-lattice methodology coupled with cluster expansion Hamiltonians
for the adlayer energetics and Brønsted-Evans-Polanyi relations for the activation energies of elementary events.
Thus, every system in Zacros needs at least the definition of a set of clusters to evaluate the system's energy
(`ClusterExpansion <clusters.html>`_), a set of elementary events
(`Mechanism <mechanism.html>`_), a lattice representing the catalytic surface
(`Lattice <lattice.html>`_), and possibly an initial state configuration
(`LatticeState <latticestate.html>`_).

.. image:: ../../images/reaction_example.png
   :scale: 60 %
   :align: center

In the following sections, you can find the API specifications of a particular component, an explanation of its role
in the whole environment, and examples of usage:

.. toctree::
    :maxdepth: 1

    species
    cluster
    mechanism
    lattice
    latticestate
    settings
    zacrosjob
    zacrosresults
