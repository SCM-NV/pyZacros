.. _zacrosparametersscanjob:

ZacrosParametersScanJob
-----------------------

.. currentmodule:: scm.pyzacros.core.ZacrosParametersScanJob

``ZacrosParametersScanJob`` class represents a job that is a container for other jobs, called children jobs, which must be :ref:`ZacrosJobs <zacrosjob>` or :ref:`ZacrosSteadyStateJob <zacrossteadystatejob>` kind objects. This class is an extension of the PLAMS MultiJob class. So it inherits all its powerful features, e.g., being executed locally or submitted to some external queueing system transparently or executing jobs in parallel with a predefined dependency structure. See all configure possibilities on the PLAMS MultiJob class documentation in this link: `PLAMS.MultiJob <../../plams/components/jobs.html#multijobs>`_.

The ``ZacrosParametersScanJob`` class constructor doesn't require a Settings object; instead, it requires a reference job ``reference`` from which the calculation ``Settings`` is taken to be replicated through its children. Children are initially copies of the reference job. However, just before they are run, their corresponding Settings are altered accordingly to the rules defined through a ``Parameter`` object provided using the parameters ``generator`` and ``generator_parameters``  in the constructor. The following example illustrates how to use this class:

.. code-block:: python
  :linenos:

  import numpy
  import scm.pyzacros as pz
  import scm.pyzacros.models

  lh = pz.models.LangmuirHinshelwood()

  z_sett = pz.Settings()
  z_sett.temperature = 500.0
  z_sett.molar_fraction.CO = 0.1
  z_sett.molar_fraction.O2 = 0.9
  ...

  z_job = pz.ZacrosJob( settings=z_sett,
                        lattice=lh.lattice,
                        mechanism=lh.mechanism,
                        cluster_expansion=lh.clusterExpansion )

  params = pz.ZacrosParametersScanJob.Parameters()
  params.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.1, 1.0, 0.05) )
  params.add( 'x_O2', 'molar_fraction.O2', lambda p: 1.0-p['x_CO'] )
  params.generator = pz.ZacrosParametersScanJob.zipGenerator

  ps_job = pz.ZacrosParametersScanJob(
                reference=ss_job, parameters=parameters, name='mesh' )

  results = ps_job.run()


In the previous code, we used the predefined model ``LangmuirHinshelwood`` (line 5),
select the job settings' (lines 7-11), and creates the corresponding job (lines 13-16).


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

When running the ``ZacrosParametersScanJob`` calculation (see :meth:`~ZacrosParametersScanJob.run` method), all necessary input files for zacros are generated in the job directory (see option ``name`` in the constructor), and Zacros is internally executed. Then, all output files generated by Zacros are stored for future reference in the same directory. The information contained in the output files can be easily accessed by using the class ``ZacrosResults``.

API
~~~

.. autoclass:: ZacrosParametersScanJob
    :exclude-members: _result_type, __init__

.. autoclass:: scm.pyzacros::ZacrosParametersScanJob.Parameter


