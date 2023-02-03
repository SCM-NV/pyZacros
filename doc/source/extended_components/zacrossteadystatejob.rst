.. _zacrossteadystatejob:

ZacrosSteadyStateJob
--------------------

.. currentmodule:: scm.pyzacros.core.ZacrosSteadyStateJob

``ZacrosSteadyStateJob`` class represents a job that is a container for other jobs, called children jobs, which must be :ref:`ZacrosJobs <zacrosjob>` or :ref:`ZacrosSteadyStateJob <zacrossteadystatejob>` kind objects. This class is an extension of the PLAMS MultiJob class. So it inherits all its powerful features, e.g., being executed locally or submitted to some external queueing system transparently or executing jobs in parallel with a predefined dependency structure. See all configure possibilities on the PLAMS MultiJob class documentation in this link: `PLAMS.MultiJob <../../plams/components/jobs.html#multijobs>`_.

The ``ZacrosSteadyStateJob`` class constructor requires a Settings object to set the parameters for the Steady-State calculation. The rest of the parameters related to the Zacros calculation ( e.g., lattice, mechanism, and the cluster expansion Hamiltonian ) are provided indirectly through a reference job ``reference`` from which the calculation ``Settings`` is taken to be replicated through its children. Children are initially copies of the reference job. However, just before they are run, their corresponding Settings are altered accordingly to the rules defined through a ``Parameters`` object provided in the constructor. In particular, this ``Parameters`` object should be specially tailored to modify the Zacros parameters that control Zacros’s behavior in terminating and resuming a simulation, namely ``max_steps``, ``max_time``, or ``wall_time``. Please consult Zacros' user guide (``$AMSHOME/scripting/scm/pyzacros/doc/ZacrosManual.pdf``; the section "Setting up a KMC Simulation in Zacros"->"Command-Line Arguments") for more details about the specific meaning of these keywords.

This class handles three aspects:
  1) Convergence of the calculation until steady-state conditions are reached by assessing the turnover frequencies of gas species at various times.
  2) Parallel execution of replicas (different random seeds) to achieve faster convergence on the turnover frequencies by increasing the efficiency in the sampling process at the cost of more computational power.
  3) Automatic scaling of the kinetic constants (if requested by the user) in the event that processes occurring in the reaction mechanisms have very different time scales

In summary, The steady-state computation goes like this: If automatic rate constant scaling is required (``settings.scaling.enabled=True``), the calculation is run for a brief time (specified by the user ``settings.scaling.max_time``) and then post-processed to extract the occurrence frequency of each elementary step, allowing the quasi-equilibrated events to be detected and scaled. Then, the calculation is started from the beginning. The convergence of the system is evaluated at multiple stopping points in time (defined by the user using a ``Parameters`` object) along its temporal evolution. When the turn-over frequency (TOF) for all gas species is statistically invariant with time, convergence is achieved. The calculation is stopped at each stopping point and evaluated for convergence; if it converged, the calculation is declared complete; otherwise, it is resumed and evolved until the next point. The methods for reaching the steady state (Batch means stopping method) and scaling the rate constants are discussed in full in the original papers `J.Chem. Phys. 144, 074104 (2016) <https://doi.org/10.1063/1.4942008>`_ and `J. Chem. Phys. 147, 164103 (2017) <https://doi.org/10.1063/1.4998926>`_, respectively.

The following lines illustrates how to use this class:

.. code-block:: python
  :linenos:

  ss_sett = pz.Settings()
  ss_sett.turnover_frequency.nbatch = 20
  ss_sett.turnover_frequency.confidence = 0.96
  ss_sett.turnover_frequency.nreplicas = 2
  ss_sett.scaling.enabled = 'T'

  params = pz.ZacrosSteadyStateJob.Parameters()
  params.add( 'max_time', 'restart.max_time', numpy.arange(20.0, 100.0, 20.0) )
  print(params)

  ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job, parameters=params )
  results = ss_job.run()

Lines 6-7 demonstrate how to use the ``Parameters`` object.
The object is created by invoking its constructor (line 6). Then we added an independent variable called ``max time``, which ranges from 20.0 to 100.0 in 20.0 increments (stopping points). Line 8 displays the parameter's final values.
Finally, lines 10 and 11 construct the ``ZacrosSteadyStateJob`` object and call its method ``run()`` to execute it.

.. code-block:: none

   0: {'max_time': 20.0}
   1: {'max_time': 40.0}
   2: {'max_time': 60.0}
   3: {'max_time': 80.0}

   [06.01|14:12:49] JOB plamsjob Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=1,nreplicas=2
   [06.01|14:12:49] JOB plamsjob STARTED
   [06.01|14:12:49] JOB plamsjob RUNNING
   [06.01|14:12:49] JOB plamsjob/plamsjob_ss_iter000_rep000 STARTED
   [06.01|14:12:49] JOB plamsjob/plamsjob_ss_iter000_rep000 RUNNING
   [06.01|14:12:49] JOB plamsjob/plamsjob_ss_iter000_rep000 FINISHED
   [06.01|14:12:50] JOB plamsjob/plamsjob_ss_iter000_rep000 SUCCESSFUL
      ...
   [06.01|14:12:54] JOB plamsjob/plamsjob_ss_iter002_rep001 FINISHED
   [06.01|14:12:54] JOB plamsjob/plamsjob_ss_iter002_rep001 SUCCESSFUL
   [06.01|14:12:54]    Replica #0
   [06.01|14:12:54]       species            TOF          error          ratio     conv?
   [06.01|14:12:54]            CO       -0.61962        0.03855        0.06221     False
   [06.01|14:12:54]            O2       -0.31003        0.02014        0.06497     False
   [06.01|14:12:54]           CO2        0.61966        0.03866        0.06239     False
   [06.01|14:12:54]    Replica #1
   [06.01|14:12:54]       species            TOF          error          ratio     conv?
   [06.01|14:12:54]            CO       -0.62079        0.02415        0.03890      True
   [06.01|14:12:54]            O2       -0.31134        0.01282        0.04118     False
   [06.01|14:12:54]           CO2        0.62094        0.02423        0.03902      True
   [06.01|14:12:54]    Average
   [06.01|14:12:54]       species            TOF          error          ratio     conv?
   [06.01|14:12:54]            CO       -0.62020        0.02150        0.03467      True
   [06.01|14:12:54]            O2       -0.31068        0.01158        0.03727      True
   [06.01|14:12:54]           CO2        0.62030        0.02156        0.03476      True
   [06.01|14:12:54] JOB plamsjob Steady State Convergence: CONVERGENCE REACHED. DONE!
   [06.01|14:12:55] JOB plamsjob FINISHED
   [06.01|14:12:55] JOB plamsjob SUCCESSFUL
   ---------------------------------------------------------------
       iter    TOF_CO2        max_time   TOF_CO2_error      conv?
            mol/s/site               s      mol/s/site
   ---------------------------------------------------------------
          0    0.75498              20         0.11099      False
          1    0.63210              40         0.03387      False
          2    0.62030              60         0.02156       True

When running the ``ZacrosSteadyStateJob`` calculation (see :meth:`~ZacrosSteadyStateJob.run` method), all necessary input files for zacros are generated in the job directory (see option ``name`` in the constructor), and Zacros is internally executed. Then, all output files generated by Zacros are stored for future reference in the same directory. The information contained in the output files can be easily accessed by using the class ``ZacrosSteadyStateResults``.

Each iteration (at each stopping point) is executed in a new job directory,
``plamsjob/plamsjob_ss_iter000``, ``plamsjob/plamsjob_ss_iter001``, etc. In case of replicas, the sufix ``_repXXX`` is added to the job directories, i.e., ``plamsjob/plamsjob_ss_iter000_rep000``, ``plamsjob/plamsjob_ss_iter000_rep001``, etc. All output files are generated and stored for future reference. The ``plams_job`` prefix can be replaced by using the option ``name`` in the constructor. Notice the status of each job follows the sequence ``STARTED-->RUNNING-->FINISHED-->SUCCESSFUL``.

As a final comment, be aware that ``ZacrosParametersScanJob`` can be used in combination with ``ZacrosSteadyStateJob``; to do that, just use the latter one as a reference.

The following lines illustrates how to do so:

.. code-block:: python
  :linenos:

  # Steady-State calculation
  ss_sett = pz.Settings()
  ss_sett.turnover_frequency.nbatch = 20
  ss_sett.turnover_frequency.confidence = 0.96
  ss_sett.turnover_frequency.nreplicas = 2
  ss_sett.scaling.enabled = 'T'

  ss_params = pz.ZacrosSteadyStateJob.Parameters()
  ss_params.add( 'max_time', 'restart.max_time', numpy.arange(20.0, 100.0, 20.0) )

  ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job, parameters=ss_params )

  # Parameters scan calculation
  ps_params = pz.ZacrosParametersScanJob.Parameters()
  ps_parameters.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.1, 1.0, 0.1) )
  ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )

  ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_params )
  results = ps_job.run()

API
~~~

.. autoclass:: ZacrosSteadyStateJob
    :exclude-members: _result_type, __init__, Parameter, Parameters, new_children

.. autoclass:: scm.pyzacros::ZacrosSteadyStateJob.Parameter
    :exclude-members: __init__

.. autoclass:: scm.pyzacros::ZacrosSteadyStateJob.Parameters
    :exclude-members: __init__
