ZacrosJob
---------

The Settings class provides a general-purpose data container for various kinds of information that need to be stored and processed by the pyZacros and PLAMS environment. It is formally identical that the Settings class in PLAMS. Please, see all details here `PLAMS.Job <../../plams/components/jobs.html>`_.


.. code-block:: python
  :linenos:

   job = pz.ZacrosJob( settings=sett, lattice=lat,
                       mechanism=[CO_ads, O2_ads, CO_oxi],
                       cluster_expansion=[CO_p, O_p] )

   print(job)

For an explanation purpose let us assume that ``/home/user/xyz`` contains three files: ``ammonia.xyz``, ``ethanol.xyz``, ``water.xyz``.
When you run this script the standard output will look something like:

.. code-block:: none

   ---------------------------------------------------------------------
   simulation_input.dat
   ---------------------------------------------------------------------
   random_seed         953129
   temperature          500.0
   pressure               1.0

   snapshots                 on time       0.1
   process_statistics        on time       0.1
   species_numbers           on time       0.1
   event_report      off
   max_steps         infinity
   max_time          1.0

   n_gas_species    3
   gas_specs_names              CO           O2          CO2
   gas_energies        0.00000e+00  0.00000e+00 -2.33700e+00
   gas_molec_weights   2.79949e+01  3.19898e+01  4.39898e+01
   gas_molar_fracs     4.50000e-01  5.50000e-01  0.00000e+00

   n_surf_species    2
   surf_specs_names         CO*        O*
   surf_specs_dent            1         1

   finish
   ---------------------------------------------------------------------
   lattice_input.dat
   ---------------------------------------------------------------------
   lattice default_choice
     triangular_periodic 1.0 10 3
   end_lattice
   ---------------------------------------------------------------------
   energetics_input.dat
   ---------------------------------------------------------------------
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
   ---------------------------------------------------------------------
   mechanism_input.dat
   ---------------------------------------------------------------------
   mechanism

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

.. currentmodule:: scm.pyzacros.core.ZacrosJob
.. autoclass:: ZacrosJob
    :exclude-members: _result_type, __init__, _get_ready, __str__
