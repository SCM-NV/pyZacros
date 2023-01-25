.. |br| raw:: html

      <br>

Phase Transitions in the ZGB model.
===================================

.. Note::
   To follow this tutorial, either:

   * Download :download:`PhaseTransitions.py <../../../examples/ZiffGulariBarshad/PhaseTransitions.py>` (run as ``$AMSBIN/amspython PhaseTransitions.py``).
   * Download :download:`PhaseTransitions.ipynb <../../../examples/ZiffGulariBarshad/PhaseTransitions.ipynb>` (see also: how to install `Jupyterlab <../../Scripting/Python_Stack/Python_Stack.html#install-and-run-jupyter-lab-jupyter-notebooks>`__)

.. include:: PhaseTransitions.rst.include

As a final note, you can use the following script to visualize the results by loading them directly from disk rather than running the entire calculation.

.. code-block:: python

  import scm.pyzacros as pz

  # xCO=0.54
  job = pz.ZacrosJob.load_external( path="plams_workdir/plamsjob.034" )
  job.results.last_lattice_state().plot()
  job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True )
  job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )

  # xCO=0.55
  job = pz.ZacrosJob.load_external( path="plams_workdir/plamsjob.035" )
  job.results.last_lattice_state().plot()
  job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True )
  job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )

.. note::
  The code described in this tutorial that allows defining the system can be significantly reduced using the ``ZiffGulariBarshad`` predefined model in **pyZacros** as follows:

  .. code-block:: python

     import scm.pyzacros.models
     zgb = pz.models.ZiffGulariBarshad()

  Then you can access its properties using ``zgb.lattice``, ``zgb.mechanism``, and ``zgb.cluster_expansion``.

  Additionally, the code taking care of individual executions of the ``ZacrosJob`` objects and recovering the results for each condition can also be simplified by using the **Extended Component** ``ZacrosParametersScanJob``.

  Take a look at the example :download:`PhaseTransitions-v2.py <../../../examples/ZiffGulariBarshad/PhaseTransitions-v2.py>` for further details. It reproduces the results of this tutorial but using the predefined models and the extended components.
