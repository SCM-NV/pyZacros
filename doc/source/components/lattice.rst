Lattice
-------

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: python
  :linenos:

   # Lattice setup
   lat = pz.Lattice( lattice_type=pz.Lattice.TRIANGULAR,
                     lattice_constant=1.0, repeat_cell=[10,3] )

   print(lat)

   lattice.plot()

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: none

   lattice default_choice
   triangular_periodic 1.0 10 3
   end_lattice

.. image:: ../../images/lattice.png
   :scale: 100 %
   :align: center

API
~~~

.. currentmodule:: scm.pyzacros.core.Lattice
.. autoclass:: Lattice
  :exclude-members: __init__, __str__, __weakref__, _Lattice__fromDefaultLattices, _Lattice__fromExplicitlyDefined, _Lattice__fromUnitCellDefined
