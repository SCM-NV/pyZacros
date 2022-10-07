.. _zacrosparametersscanjob:

ZacrosParametersScanJob
-----------------------

.. currentmodule:: scm.pyzacros.core.ZacrosParametersScanJob

``ZacrosParametersScanJob`` class represents a job that is a container for other jobs, called children jobs, which must be :ref:`ZacrosJobs <zacrosjob>` or :ref:`ZacrosSteadyStateJob <zacrossteadystatejob>` kind objects. This class is an extension of the PLAMS MultiJob class. So it inherits all its powerful features, e.g., being executed locally or submitted to some external queueing system transparently or executing jobs in parallel with a predefined dependency structure. See all configure possibilities on the PLAMS MultiJob class documentation in this link: `PLAMS.MultiJob <../../plams/components/jobs.html#multijobs>`_.

The ``ZacrosParametersScanJob`` class constructor doesn't require a Settings object; instead, it requires a reference job ``reference`` from which the calculation ``Settings`` is taken to be replicated through its children. Children are initially copies of the reference job. However, just before they are run, their corresponding Settings are altered accordingly to the rules defined through a ``Parameters`` object provided in the constructor. The following lines illustrates how to use this class:

.. code-block:: python
  :linenos:

  ps_parameters = pz.ZacrosParametersScanJob.Parameters()
  ps_parameters.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.1, 1.0, 0.1) )
  ps_parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
  ps_parameters.set_generator( pz.ZacrosParametersScanJob.zipGenerator )

  ps_job = pz.ZacrosParametersScanJob( reference=z_job, parameters=ps_parameters )

  results = ps_job.run()


Here we assumed that there is a ZacrosJob object already configured ``z_job`` that we call the reference job, and we aim to modify its settings to vary ``z_job.settings.molar_fraction.CO`` and ``z_job.settings.molar_fraction.O2`` in the range [0.1:0.9] with the restriction that their sum is 1. This is achieved with lines 1-3. First, we created a new ``ZacrosParametersScanJob.Parameters`` object (line 1), and then we added as many parameters to modify as needed through the method ``add``. Notice that in this case, we created two variables, ``x_CO`` and ``x_O2`` (equivalent to the parameters ``molar_fraction.CO`` and ``molar_fraction.O2`` in the Settings object), where the latter is the dependent variable (notice the lambda function that forces the sum with ``x_CO`` to 1.0) and the former is the independent one with its values ranging within the interval described above.

Line 4 selects the generator, which will generate the final values of the parameters after combining them. In this case, the scanning is one-dimensional, so their combination is trivial. In the example, we used the ``zipGenerator`` (the default option), which combines the values of the parameters one-to-one following the order as they were defined. This means that for this example, the final set of calculations will use the following list of parameters: ``('xCO','xO2') = [(0.1,0.9), (0.2,0.8), ..., (0.9,0.1)]``. For more than two dimensions, the generator is essential. Because it allows generating, for example, a grid by combining two parameters, see ``pz.ZacrosParametersScanJob.meshgridGenerator`` for more details. Moreover, remember that the generator is a function that can be written by the user.

The execution of the code above generates the following output:

.. code-block:: none

  [22.09|16:19:57] PLAMS working folder: /home/user/plams_workdir
  [22.09|16:19:58] JOB plamsjob STARTED
  [22.09|16:19:58] JOB plamsjob RUNNING
  [22.09|16:19:58] JOB plamsjob/plamsjob_ps_cond000 STARTED
  [22.09|16:19:58] JOB plamsjob/plamsjob_ps_cond000 RUNNING
  [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond000 FINISHED
  [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond000 SUCCESSFUL
  [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond001 STARTED
  [22.09|16:23:33] JOB plamsjob/plamsjob_ps_cond001 RUNNING
  [22.09|16:27:16] JOB plamsjob/plamsjob_ps_cond001 FINISHED
  [22.09|16:27:17] JOB plamsjob/plamsjob_ps_cond001 SUCCESSFUL
  ...
  [22.09|16:47:18] JOB plamsjob/plamsjob_ps_cond008 STARTED
  [22.09|16:47:18] JOB plamsjob/plamsjob_ps_cond008 RUNNING
  [22.09|16:52:37] JOB plamsjob/plamsjob_ps_cond008 FINISHED
  [22.09|16:52:37] JOB plamsjob/plamsjob_ps_cond008 SUCCESSFUL
  [22.09|16:52:37] JOB plamsjob FINISHED
  [22.09|16:52:37] JOB plamsjob SUCCESSFUL
  [22.09|16:52:37] PLAMS run finished. Goodbye

In this example, all conditions or molar fractions of ``CO`` are executed sequentially, but it is possible
to execute in parallel using a different JobRunner. Each condition is executed in a new job directory,
``plamsjob/plamsjob_ps_cond000``, ``plamsjob/plamsjob_ps_cond001``, etc., where all output files are generated
and stored for future reference. The ``plams_job`` prefix can be replaced by using the option ``name`` in the
constructor. Notice the status of each job follows the sequence ``STARTED-->RUNNING-->FINISHED-->SUCCESSFUL``.

The information in the output directories can be easily accessed using the class ``ZacrosParametersScanResults``.

API
~~~

.. autoclass:: ZacrosParametersScanJob
    :exclude-members: _result_type, __init__, Parameter, Parameters

.. autoclass:: scm.pyzacros::ZacrosParametersScanJob.Parameter
    :exclude-members: __init__

.. autoclass:: scm.pyzacros::ZacrosParametersScanJob.Parameters
    :exclude-members: __init__
