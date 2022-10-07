.. |br| raw:: html

      <br>

Ziff-Gulari-Barshad model: Phase Transitions under Steady State Conditions.
---------------------------------------------------------------------------


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


