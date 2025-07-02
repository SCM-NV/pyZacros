.. _zacrosparametersscanresults:

ZacrosParametersScanResults
---------------------------

The ``ZacrosParametersScanResults`` class was designed to take charge of the job folder after executing the ``ZacrosParametersScanJob``. It gathers the information from the output files and helps to extract data of interest from them. Every ZacrosParametersScanJob instance has an associated ``ZacrosParametersScanResults`` instance created automatically on job creation and stored in its results attribute. This class extends the `PLAMS Results <../../plams/components/results.html>`_ class.

The following lines of code show an example of how to use the ``ZacrosParametersScanResults`` class:

.. code-block:: python
  :linenos:

  ps_parameters = pz.ZacrosParametersScanJob.Parameters()
  ps_parameters.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.1, 1.0, 0.1) )
  ps_parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
  ps_parameters.set_generator( pz.ZacrosParametersScanJob.zipGenerator )
  print(ps_parameters)

  ps_job = pz.ZacrosParametersScanJob( reference=z_job, parameters=ps_parameters )
  results = ps_job.run()

  if( ps_job.ok() ):
     results_dict = results.turnover_frequency()
     print(results_dict[0])

     print("%4s"%"cond", "%8s"%"x_CO", "%10s"%"TOF_CO2")
     for i,idx in enumerate(results.indices()):
         print( '%4d'%i,
                '%8.2f'%results_dict[i]['x_CO'],
                '%10.6f'%results_dict[i]['turnover_frequency']['CO2'] )

Lines 1-8 were already discussed before (see :ref:`ZacrosParametersScanJob <zacrosparametersscanjob>`).
Here, the ``ZacrosParametersScanResults`` object ``results`` is created by calling the method ``run()`` of the corresponding ``ZacrosParametersScanJob`` job (line 8).

Afterward, the method ``ok()`` is invoked to assure that the calculation finished appropriately (line 10), and only after that,
it is good to go to get information from the output files by using the ``ZacrosParametersScanResults`` methods (lines 11-18).
As an example, the method ``turnover_frequency()`` returns the turnover frequency (TOF) for every gas species (for this example they are ``CO``, ``O2``, and ``CO2``) and for every composition (``x_CO`` and ``x_O2`` values) in the form of a dictionary (line 11).

The execution of the code above after line 8 shows the following information to the standard output:

.. code-block:: none

   {'x_CO': 0.1,
    'x_O2': 0.9,
    'turnover_frequency': {'CO': -0.017600, 'O2': -0.014926, 'CO2': 0.017600},
    'turnover_frequency_error': {'CO': 0.018148, 'O2': 0.015503, 'CO2': 0.018148},
    'turnover_frequency_converged': {'CO': False, 'O2': False, 'CO2': False}}

   cond     x_CO     TOF_CO2
      0     0.10    0.017600
      1     0.20    0.049895
      2     0.30    0.123811
      3     0.40    0.577095
      4     0.50    2.108442
      5     0.60    0.221453
      6     0.70    0.008863
      7     0.80    0.000589
      8     0.90   -0.000000

Line 12 prints out the first element of the list ``results_dict``. As you can see in the output generated, this element contains the molar fractions of the gas species (``x_CO`` and ``x_O2``) and three values related to the turnover frequency calculation, namely the value itself (``turnover_frequency``), its error (``turnover_frequency_error``), and a flag to determine if the calculation is converged or not (``turnover_frequency_converged``). Finally, lines 14-18 show the values of ``x_CO`` and ``TOF_CO2`` for all compositions in a summary table.

API
~~~

.. currentmodule:: scm.pyzacros.core.ZacrosParametersScanJob
.. autoclass:: ZacrosParametersScanResults
    :exclude-members: __init__

