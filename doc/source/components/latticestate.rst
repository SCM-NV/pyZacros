LatticeState
------------

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: python
  :linenos:

   # LatticeState setup (initial state)
   ist = pz.LatticeState(lat, surface_species=spl.surface_species())
   ist.fill_sites_random(site_name='StTp1', species='CO*', coverage=0.1)
   ist.fill_sites_random(site_name='StTp1', species='O*', coverage=0.1)

   print(ist)

   ist.plot()

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: none

      initial_state
        # species * CO* O*
        # species_numbers
        #   - CO*  12
        #   - O*  11
        seed_on_sites CO* 1
        seed_on_sites CO* 4
        seed_on_sites O* 6
        seed_on_sites O* 10
        seed_on_sites O* 20
        seed_on_sites CO* 30
        seed_on_sites CO* 43
        seed_on_sites O* 48
        seed_on_sites O* 52
        seed_on_sites CO* 55
        seed_on_sites O* 58
        seed_on_sites CO* 62
        seed_on_sites CO* 69
        seed_on_sites CO* 70
        seed_on_sites O* 72
        seed_on_sites CO* 73
        seed_on_sites CO* 78
        seed_on_sites CO* 93
        seed_on_sites O* 99
        seed_on_sites O* 106
        seed_on_sites O* 109
        seed_on_sites O* 110
        seed_on_sites CO* 115
      end_initial_state

.. image:: ../../images/lattice_initial_state.png
   :scale: 100 %
   :align: center

API
~~~

.. currentmodule:: scm.pyzacros.core.LatticeState
.. autoclass:: LatticeState
   :exclude-members: __init__, __str__, __weakref__
