Elementary Reaction / Mechanism
-------------------------------

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: python
  :linenos:

  # Elementary Reactions
  CO_ads = pz.ElementaryReaction( initial=[s0, CO_g], final=[CO_s],
                                  reversible=False, pre_expon=10.0,
                                  label="CO_adsorption" )

  O2_ads = pz.ElementaryReaction( initial=[s0, s0, O2_g], final=[O_s, O_s],
                                  neighboring=[(0,1)],
                                  reversible=False, pre_expon=2.5,
                                  label="O2_adsorption" )

  CO_oxi = pz.ElementaryReaction( initial=[CO_s, O_s], final=[s0, s0, CO2_g],
                                  neighboring=[(0,1)],
                                  reversible=False, pre_expon=1.0e+20,
                                  label="CO_oxidation")

  mech = pz.Mechanism([O2_ads, CO_ads, CO_oxi])

  print(mech)

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: none

  mechanism

    step O2_adsorption
      gas_reacs_prods O2 -1
      sites 2
      neighboring 1-2
      initial
        1 * 1
        2 * 1
      final
        1 O* 1
        2 O* 1
      site_types 1 1
      pre_expon  2.50000e+00
      activ_eng  0.00000e+00
    end_step

    step CO_adsorption
      gas_reacs_prods CO -1
      sites 1
      initial
        1 * 1
      final
        1 CO* 1
      site_types 1
      pre_expon  1.00000e+01
      activ_eng  0.00000e+00
    end_step

    step CO_oxidation
      gas_reacs_prods CO2 1
      sites 2
      neighboring 1-2
      initial
        1 CO* 1
        2 O* 1
      final
        1 * 1
        2 * 1
      site_types 1 1
      pre_expon  1.00000e+20
      activ_eng  0.00000e+00
    end_step

  end_mechanism

API
~~~

.. currentmodule:: scm.pyzacros.core.ElementaryReaction
.. autoclass:: ElementaryReaction
  :exclude-members: __init__, __eq__, __hash__, _ElementaryReaction__updateLabel, __weakref__, __str__

.. currentmodule:: scm.pyzacros.core.Mechanism
.. autoclass:: Mechanism
  :exclude-members: __init__, __str__
