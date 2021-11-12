Cluster / Cluster Expansion
---------------------------

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: python
  :linenos:

   # Clusters
   CO_p = pz.Cluster( species=[CO_s], cluster_energy=-1.3 )
   O_p = pz.Cluster( species=[O_s], cluster_energy=-2.3 )

   ce = pz.ClusterExpansion([CO_p, O_p])

   print(ce)


For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

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

API
~~~

.. currentmodule:: scm.pyzacros.core.Cluster
.. autoclass:: Cluster
   :exclude-members: __init__, __len__, __eq__, __hash__, __str__, _Cluster__updateLabel, __weakref__


.. currentmodule:: scm.pyzacros.core.ClusterExpansion
.. autoclass:: ClusterExpansion
   :exclude-members: __init__, __str__
