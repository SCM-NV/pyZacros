.. _zacrossteadystateresults:

ZacrosSteadyStateResults
------------------------

The ``ZacrosSteadyStateResults`` class was designed to take charge of the job folder after executing the ``ZacrosSteadyStateJob``. It gathers the information from the output files and helps to extract data of interest from them. Every ZacrosSteadyStateJob instance has an associated ``ZacrosSteadyStateResults`` instance created automatically on job creation and stored in its results attribute. This class extends the `PLAMS Results <../../plams/components/results.html>`_ class.

The following lines of code show an example of how to use the ``ZacrosSteadyStateResults`` class:

.. code-block:: python
  :linenos:

  ss_sett = pz.Settings()
  ss_sett.turnover_frequency.nbatch = 20
  ss_sett.turnover_frequency.confidence = 0.96
  ss_sett.nreplicas = 2

  params = pz.ZacrosSteadyStateJob.Parameters()
  params.add( 'max_time', 'restart.max_time', numpy.arange(20.0, 100.0, 20.0) )
  print(params)

  ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=job, parameters=params )
  results = ss_job.run()

  if ss_job.ok():
     print(results.history()[0])

     print("%8s"%"iter", "%10s"%"TOF_CO2", "%15s"%"max_time",
           "%15s"%"TOF_CO2_error", "%10s"%"conv?")

     for i,step in enumerate(results.history()):
        print("%8d"%i,
              "%10.5f"%step['turnover_frequency']['CO2'],
              "%15d"%step['max_time'],
              "%15.5f"%step['turnover_frequency_error']['CO2'],
              "%10s"%(all(step['converged'].values())))

Lines 1-11 were already discussed before (see :ref:`ZacrosSteadyStateJob <zacrosparametersscanjob>`).
Here, the ``ZacrosSteadyStateResults`` object ``results`` is created by calling the method ``run()`` of the corresponding ``ZacrosSteadyStateJob`` job (line 11).

Afterward, the method ``ok()`` is invoked to assure that the calculation finished appropriately (line 13), and only after that,
it is good to go to get information from the output files by using the ``ZacrosSteadyStateResults`` methods (lines 14-24).
In this example, we want to print information about the history of the calculation after each iteration. Line 14 prints the first item of the list returned by the ``history()`` method to show its structure. Then after line 16, we show this information for all iterations summarized in a table.

The execution of the code above after line 13 shows the following information to the standard output:

.. code-block:: none

   {'turnover_frequency': {'CO': -0.75409, 'O2': -0.39222, 'CO2': 0.75498},
    'turnover_frequency_error': {'CO': 0.11055, 'O2': 0.06458, 'CO2': 0.11099},
    'converged': {'CO': False, 'O2': False, 'CO2': False},
    'max_time': 20.0}

    iter    TOF_CO2        max_time   TOF_CO2_error      conv?
       0    0.75498              20         0.11099      False
       1    0.63210              40         0.03387      False
       2    0.62030              60         0.02156       True

As you can see in the output, each element of the history includes the maximum amount of time (referred to as ``max time``) used in that iteration as well as three numbers related to the turnover frequency calculation: the value itself (referred to as ``turnover frequency``), its error (referred to as ``turnover frequency error``), and a flag (referred to as ``turnover frequency converged``) that denotes whether or not the calculation has converged. Finally, lines 14-18 show the values of ``x_CO`` and ``TOF_CO2`` for all compositions in a summary table.

API
~~~

.. currentmodule:: scm.pyzacros.core.ZacrosSteadyStateJob
.. autoclass:: ZacrosSteadyStateResults
    :exclude-members: _ZacrosSteadyStateResults__plot_process_statistics

