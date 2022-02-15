.. _species_and_specieslist:

Species / Species List
----------------------

In a Zacros simulation, species are necessary to describe the chemistry involved in the system.
If one atom is identical to another, we can say they are the same chemical species. In the same way,
if one molecule is identical to another, we can say they are the same chemical species. Thus, we can
highlight two essential kinds of species: 1) gas species and 2) surface or adsorbed species. A
molecule in the gas phase is a species itself, but when it interacts with a catalytic surface,
its properties generally change enough to be different from its gas counterpart. However, once it
is adsorbed on the catalytic surface, its properties may not change enough to change its identity
as it moves on the surface. In that sense, for example, for a CO molecule, we can identify two kinds
of species: 1) CO in the gas phase and 2) CO adsorbed. Here, the CO is the same species independently
if it is adsorbed, e.g., on an fcc or an hcp site.

For any kind of species, the only required parameter is the symbol (e.g., ``"CO"``), and it can be created with the sentence
``pz.Species("CO")``. The ``Species`` constructor allows specifying different parameters like denticity, gas energy, kind, and mass.
By default, pyZacros parses the species symbol to get these parameters. If the symbol contains the character ``*``,
it assumes that the species is a surface species (``kind=pz.Species.SURFACE``) with a denticity given by the number
of times that ``*`` is found in the symbol; i.e. ``pz.Species("O2**")`` is equivalent to
``pz.Species("O2**",denticity=2,kind=pz.Species.SURFACE)``. On the other hand, if the symbol doesn't contain any ``*``,
it assumes that the species is a gas species (``kind=pz.Species.GAS``), with the mass calculated from the parsing of
the symbol as a chemical formula string; i.e. ``pz.Species("O2")`` is equivalent
to ``pz.Species("O2",kind=pz.Species.GAS,mass=31.9898)``.

For our example (see :ref:`use case system <use_case_model_zgb>`), we need to create
three gas species (CO, O\ :sub:`2`, and CO\ :sub:`2`), and three surface species (\*, CO\*, O\*).
This can be achieved by using the lines 1-10 of following code:

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

  # Species List
  spl = pz.SpeciesList([CO_g,O2_g,CO2_g,s0,CO_s])
  spl.append( O_s )
  print(spl)

Notice that the species symbol ``*`` is reserved for the empty site species (or pseudo-species).

In this script, we have also introduced the class ``SpeciesList``, which represents nothing more
than a list of species (see lines 11-13). But, in particular, it is helpful to look at the Zacros
code that will be generated based on it by using the ``print()`` function (see line 14). The execution
of the previous script displays the following on the standard output:

.. code-block:: none

  n_gas_species    3
  gas_specs_names              CO           O2          CO2
  gas_energies        0.00000e+00  0.00000e+00 -2.33700e+00
  gas_molec_weights   2.79949e+01  3.19898e+01  4.39898e+01
  n_surf_species    2
  surf_specs_names         CO*        O*
  surf_specs_dent            1         1

Please consult Zacros' user guide for more details about the specific meaning of the keywords used in the previous lines.

API
~~~

.. currentmodule:: scm.pyzacros.core.Species
.. autoclass:: Species
  :exclude-members: __eq__, __init__, __hash__, __str__, __weakref__


.. currentmodule:: scm.pyzacros.core.SpeciesList
.. autoclass:: SpeciesList
  :exclude-members: __init__, __hash__, __str__, _SpeciesList__updateLabel, default_entity_numbers
