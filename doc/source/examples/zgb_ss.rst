.. |br| raw:: html

      <br>

Ziff-Gulari-Barshad model: Steady State Conditions.
===================================================

.. Note::
   To follow this tutorial, either:

   * Download :download:`SteadyState.py <../../../examples/ZiffGulariBarshad/SteadyState.py>` (run as ``$AMSBIN/amspython SteadyState.py``).
   * Download :download:`SteadyState.ipynb <../../../examples/ZiffGulariBarshad/SteadyState.ipynb>` (see also: how to install `Jupyterlab <../../Scripting/Python_Stack/Python_Stack.html#install-and-run-jupyter-lab-jupyter-notebooks>`__)

.. include:: SteadyState.rst.include

Finally, if you run the entire script, replacing ``ss_sett.nreplicas = 1`` with ``ss_sett.nreplicas = 4``, you should get the following result:

.. figure:: ../../images/example_ZGB-SS-nrep4.png
   :scale: 90 %
   :align: center

The calculation now converged in two iterations rather than the previous eight. When using replicas, each replica uses the same
parameters as the reference job but with different random seeds, and the corresponding TOFs are evaluated as an average over the
entire replica set. This accelerates convergence by increasing the accessible space's sampling efficiency.
