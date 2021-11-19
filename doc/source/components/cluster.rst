Cluster / Cluster Expansion
---------------------------

In a Zacros simulation, clusters  (also
referred to as patterns) are used as the base of a cluster expansion Hamiltonian for
calculating the energy of a given lattice configuration. The energy is calculated based
on the number of times that each cluster/pattern is found on the catalytic surface during
the simulation. A cluster consists of a collection of binding sites, their connectivity,
the surface species bonded to those sites, and the energetic contribution thereof.

For our example (see :ref:`use case system <use_case_model_zgb>`), the following lines create the
two needed clusters; the CO* and O* individual adsorbates:

.. code-block:: python
  :linenos:

   # Clusters
   CO_p = pz.Cluster( species=[CO_s], cluster_energy=-1.3 )
   O_p = pz.Cluster( species=[O_s], cluster_energy=-2.3 )
   print(CO_p)

which produce the following output:

.. code-block:: none

   cluster CO*_0-0
     sites 1
     lattice_state
       1 CO* 1
     site_types 1
     graph_multiplicity 1
     cluster_eng -1.30000e+00
   end_cluster


Please consult Zacros' user guide for more details about the specific meaning of the keywords used in the previous lines.
Notice that the function ``print()`` in line 4 shows the cluster ``CO_p`` as it is going to be used in the Zacros input files.
The label ``CO*_0-0`` is automatically generated except if the user specifies it by the parameter ``label`` in the constructor.
This label is used as a unique identifier to avoid duplicates.

    .. note::

        pyZacros lists are always numbered from 0 to be consistent with the Python language. However, notice that Zacros input files require all elements should be numbered from 1; pyZacros takes care internally of this transformation.

The ``ClusterExpansion`` object is formally a list of clusters and as such inherits all properties of Python lists.
The following lines illustrate an example:

.. code-block:: python
  :linenos:

   # Cluster Expansion
   ce = pz.ClusterExpansion([CO_p, O_p])
   print(ce)

which produce the following output:

.. code-block:: none

   energetics

     cluster CO*_0-0
     sites 1
     lattice_state
        1 CO* 1
     site_types 1
     graph_multiplicity 1
     cluster_eng -1.30000e+00
     end_cluster

     cluster O*_0-0
     sites 1
     lattice_state
        1 O* 1
     site_types 1
     graph_multiplicity 1
     cluster_eng -2.30000e+00
     end_cluster

   end_energetics

These lines will be used to create the Zacros input file ``energetics_input.dat``.

API
~~~

.. currentmodule:: scm.pyzacros.core.Cluster
.. autoclass:: Cluster
   :exclude-members: __init__, __len__, __eq__, __hash__, __str__, _Cluster__updateLabel, __weakref__


.. currentmodule:: scm.pyzacros.core.ClusterExpansion
.. autoclass:: ClusterExpansion
   :exclude-members: __init__, __str__
