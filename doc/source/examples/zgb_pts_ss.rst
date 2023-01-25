.. |br| raw:: html

      <br>

Ziff-Gulari-Barshad model: Phase Transitions under Steady State Conditions.
===========================================================================

.. code-block:: python
  :caption: **Code: Running the Calculations**
  :linenos:

   #---------------------------------------
   # Zacros calculation
   #---------------------------------------
   zgb = pz.models.ZiffGulariBarshad()

   z_sett = pz.Settings()
   z_sett.random_seed = 953129
   z_sett.temperature = 500.0
   z_sett.pressure = 1.0
   z_sett.species_numbers = ('time', 0.1)
   z_sett.max_time = 10.0

   z_job = pz.ZacrosJob( settings=z_sett, lattice=zgb.lattice,
                         mechanism=zgb.mechanism,
                         cluster_expansion=zgb.cluster_expansion )

   #---------------------------------------
   # Steady-State calculation
   #---------------------------------------

   ss_sett = pz.Settings()
   ss_sett.turnover_frequency.nbatch = 20
   ss_sett.turnover_frequency.confidence = 0.96
   ss_sett.turnover_frequency.ignore_nbatch = 5
   ss_sett.nreplicas = 4

   ss_params = pz.ZacrosSteadyStateJob.Parameters()
   ss_params.add( 'max_time', 'restart.max_time',
                  2*z_sett.max_time*( numpy.arange(20)+1 )**3 )

   ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job,
                                     parameters=ss_params )

   #---------------------------------------
   # Parameters scan calculation
   #---------------------------------------
   ps_params = pz.ZacrosParametersScanJob.Parameters()
   ps_params.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.2, 0.8, 0.01) )
   ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )

   ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_params )

   results = ps_job.run()


.. In the previous code, we used the predefined model ``LangmuirHinshelwood`` (line 5),
.. select the job settings' (lines 7-11), and creates the corresponding Zacros job (lines 13-16).
.. Up to here, this is a typical Zacros job. In particular, notice the parameters
.. ``z_sett.molar_fraction.CO = 0.2`` and ``z_sett.molar_fraction.O2 = 0.8`` of the settings
.. object, which specifically define the molar fractions of 0.2 and 0.8 for ``CO`` and ``O2``
.. respectively. This example aims to vary the molar fraction of ``CO`` in a given range and
.. run a Zacros calculation for each considered value.
..
.. In this example, we intend to modify the ``CO`` molar fraction from 0.05 to 0.95 every 0.05.
.. Firstly, remember that we have to modify the molar fraction of ``O`` accordingly so that
.. they sum 1. The way to include these conditions in pyZacros is through the object
.. ``ZacrosParametersScanJob.Parameters`` as shown in lines 18-21. Notice we created two variables,
.. ``x_CO`` and ``x_O2`` (equivalent to the parameters ``molar_fraction.CO`` and ``molar_fraction.O2``
.. in the Settings object), where the latter is the dependant variable (notice the lambda function
.. that forces the sum with ``x_CO`` to 1.0) and the former the independent one with its values
.. ranging within the interval described above.
..
.. Line 21 selects the generator. In this case, the scanning is one-dimensional, so the generator
.. is not required. Here it was included just for illustration purposes. The ``zipGenerator`` just
.. combines the values of the parameters one-to-one as they were defined; thus, it is expected that
.. all of them have the same dimensions. For more than two dimensions, the generator is essential.
.. Because it allows generating, for example, a grid by combining two parameters,
.. see ``meshgridGenerator`` for more details. The generator is a function that can be written by the user.
.. The execution of the code above generates the following output:
..
.. .. code-block:: none
..
..   [22.09|16:19:57] PLAMS working folder: /home/user/plams_workdir
..   [22.09|16:19:58] JOB plamsjob STARTED
..   [22.09|16:19:58] JOB plamsjob RUNNING
..   [22.09|16:19:58] JOB plamsjob/plamsjob_ps_cond000 STARTED
..   [22.09|16:19:58] JOB plamsjob/plamsjob_ps_cond000 RUNNING
..   [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond000 FINISHED
..   [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond000 SUCCESSFUL
..   [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond001 STARTED
..   [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond001 RUNNING
..   [22.09|16:27:16] JOB plamsjob/plamsjob_ps_cond001 FINISHED
..   [22.09|16:27:17] JOB plamsjob/plamsjob_ps_cond001 SUCCESSFUL
..   ...
..   [22.09|16:47:18] JOB plamsjob/plamsjob_ps_cond008 STARTED
..   [22.09|16:47:18] JOB plamsjob/plamsjob_ps_cond008 RUNNING
..   [22.09|16:52:37] JOB plamsjob/plamsjob_ps_cond008 FINISHED
..   [22.09|16:52:37] JOB plamsjob/plamsjob_ps_cond008 SUCCESSFUL
..   [22.09|16:52:37] JOB plamsjob FINISHED
..   [22.09|16:52:37] JOB plamsjob SUCCESSFUL
..   [22.09|16:52:37] PLAMS run finished. Goodbye
..
.. In this example, all conditions or molar fractions of ``CO`` are executed sequentially, but it is possible
.. to execute in parallel using a different JobRunner. Each condition is executed in a new job directory,
.. ``plamsjob/plamsjob_ps_cond000``, ``plamsjob/plamsjob_ps_cond001``, etc., where all output files are generated
.. and stored for future reference. The ``plams_job`` prefix can be replaced by using the option ``name`` in the
.. constructor. Notice the status of each job follows the sequence ``STARTED-->RUNNING-->FINISHED-->SUCCESSFUL``.
..
.. The information in the output directories can be easily accessed using the class ``ZacrosParametersScanResults``.
