Settings
--------

The Settings class provides a general-purpose data container for various kinds of information that need to be stored and processed by the pyZacros and PLAMS environment. It is formally identical that the Settings class in PLAMS. Please, see all details here `PLAMS.Settings <../../plams/components/settings.html>`_.

For our example (see :ref:`use case system <use_case_model_zgb>`), the following lines create the conditions we need for our calculation like e.g., the temperature (500 K) and pressure (1.0 atm.):

.. code-block:: python
  :linenos:

  # Settings:
  sett = pz.Settings()
  sett.random_seed = 953129
  sett.temperature = 500.0
  sett.pressure = 1.0
  sett.snapshots = ('time', 0.1)
  sett.process_statistics = ('time', 0.1)
  sett.species_numbers = ('time', 0.1)
  sett.event_report = 'off'
  sett.max_steps = 'infinity'
  sett.max_time = 1.0

  sett.molar_fraction.CO = 0.45
  sett.molar_fraction.O2 = 0.55

  print(sett)

As in the other pyZacros objects, the function ``print()`` (see line 16) shows the Settings object as it is going to be used
in the Zacros input files. The previous lines produce the following output:

.. code-block:: none

  random_seed         953129
  temperature          500.0
  pressure               1.0

  snapshots                 on time       0.1
  process_statistics        on time       0.1
  species_numbers           on time       0.1
  event_report      off
  max_steps         infinity
  max_time          1.0

Notice that the CO and O\ :sub:`2` molar fractions (keywords ``sett.molar_fraction.CO`` and ``sett.molar_fraction.O2``) are not printed out in the previous configuration block. This is because information about species involved in the mechanism and clusters is needed to generate the corresponding block in the ``simulation_input.dat`` zacros file. This information is going to print out from the
`ZacrosJob <../components/zacrosjob.html>`_ object.
Please consult Zacros' user guide for more details about the specific meaning of the keywords used above.

API
~~~

.. currentmodule:: scm.pyzacros.core.Settings
.. autoclass:: Settings
    :exclude-members: __init__, __str__

