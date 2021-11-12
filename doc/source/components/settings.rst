Settings
--------

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

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

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

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

API
~~~

.. currentmodule:: scm.pyzacros.core.Settings
.. autoclass:: Settings
    :exclude-members: __init__, __str__

