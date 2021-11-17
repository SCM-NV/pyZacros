Species / Species List
----------------------

For our example (see :ref:`link title <use_case_model_zgb>`), we need to create
three gas species (CO, O\ :sub:`2`, and CO\ :sub:`2`), and three surface species (\*, CO\*, O\*).

.. code-block:: python
  :linenos:

  # Gas species
  CO_g = pz.Species("CO")
  O2_g = pz.Species("O2")
  CO2_g = pz.Species("CO2", gas_energy=-2.337)

  # Surface species
  s0 = pz.Species("*")   # Empty adsorption site
  CO_s = pz.Species("CO*")
  O_s = pz.Species("O*", denticity=1)

  spl = pz.SpeciesList([CO_g,O2_g,CO2_g,s0,CO_s])
  spl.append( O_s )

  print(spl)

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: none

  n_gas_species    3
  gas_specs_names              CO           O2          CO2
  gas_energies        0.00000e+00  0.00000e+00 -2.33700e+00
  gas_molec_weights   2.79949e+01  3.19898e+01  4.39898e+01
  n_surf_species    2
  surf_specs_names         CO*        O*
  surf_specs_dent            1         1

API
~~~

.. currentmodule:: scm.pyzacros.core.Species
.. autoclass:: Species
  :exclude-members: __eq__, __init__, __hash__, __str__, __weakref__


.. currentmodule:: scm.pyzacros.core.SpeciesList
.. autoclass:: SpeciesList
  :exclude-members: __init__, __hash__, __str__, _SpeciesList__updateLabel
