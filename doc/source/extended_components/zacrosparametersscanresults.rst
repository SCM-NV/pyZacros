.. _zacrosparametersscanresults:

ZacrosParametersScanResults
---------------------------

The ``ZacrosParametersScanResults`` class was designed to take charge of the job folder after executing the ``ZacrosJob``. It gathers the information from the output files and helps extract data of interest from them. Every ZacrosJob instance has an associated ``ZacrosParametersScanResults`` instance created automatically on job creation and stored in its results attribute. This class extends the `PLAMS Results <../../plams/components/results.html>`_ class.

For our example (see :ref:`use case system <use_case_model_zgb>`), the following lines of code show an example of how to use the ``ZacrosParametersScanResults`` class:

.. code-block:: python
  :linenos:

   results = job.run()

   if( job.ok() ):
      provided_quantities = results.provided_quantities()
      print("nCO2 =", provided_quantities['CO2'])

      results.plot_molecule_numbers( results.gas_species_names() )
      results.plot_lattice_states( results.lattice_states() )

      pstat = results.get_process_statistics()
      results.plot_process_statistics( pstat, key="number_of_events" )


Here, the ``ZacrosParametersScanResults`` object ``results`` is created by calling the method ``run()`` of the corresponding ``ZacrosJob`` job (line 1).
Afterward, the method ``ok()`` is invoked to assure that the calculation finished appropriately (line 3), and only after that,
it is good to go to get information from the output files by using the ZacrosParametersScanResults methods (lines 4-11).
As an example, the method ``provided quantities()`` returns the content of the zacros output file ``specnum_output.txt`` in the form of a dictionary. Thus, in line 5, we print out the number of CO\ :sub:`2` molecules produced during the simulation. In addition to getting the information from the output files, the ZacrosParametersScanResults class also offers some methods to plot the results directly, as shown in lines 7-11.

The execution of the block of code shown above produces the following information to the standard output:

.. code-block:: none

   [05.11|10:22:27] JOB plamsjob STARTED
   [05.11|10:22:27] JOB plamsjob RUNNING
   [05.11|10:22:27] JOB plamsjob FINISHED
   [05.11|10:22:27] JOB plamsjob SUCCESSFUL
   nCO2 = [0, 28, 57, 85, 118, 139, 161, 184, 212, 232, 264]

Notice the line corresponding to the number of CO\ :sub:`2` molecules produced during the simulation. The rest of the functions generate the following figures:

.. code-block:: python

   results.plot_molecule_numbers( results.gas_species_names() )

.. image:: ../../images/mol_gas_nums.png
   :scale: 100 %
   :align: center

.. code-block:: python

   results.plot_lattice_states( results.lattice_states() )

.. image:: ../../images/lattice_state.gif
   :scale: 100 %
   :align: center

.. code-block:: python

   pstat = results.get_process_statistics()
   results.plot_process_statistics( pstat, key="number_of_events" )

.. image:: ../../images/number_of_events.gif
   :scale: 80 %
   :align: center

API
~~~

.. currentmodule:: scm.pyzacros.core.ZacrosParametersScanJob
.. autoclass:: ZacrosParametersScanResults
    :exclude-members: __init__

