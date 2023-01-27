.. |br| raw:: html

      <br>

Ziff-Gulari-Barshad model: Phase Transitions and ML-based Surrogate Model.
==========================================================================

.. Note::
   To follow this tutorial, either:

   * Download :download:`PhaseTransitions-ADP.py <../../../examples/ZiffGulariBarshad/PhaseTransitions-ADP.py>` (run as ``$AMSBIN/amspython PhaseTransitions-ADP.py``).
   * Download :download:`PhaseTransitions-ADP.ipynb <../../../examples/ZiffGulariBarshad/PhaseTransitions-ADP.ipynb>` (see also: how to install `Jupyterlab <../../Scripting/Python_Stack/Python_Stack.html#install-and-run-jupyter-lab-jupyter-notebooks>`__)

.. include:: PhaseTransitions-ADP.rst.include


.. You can download the full example script following this link :download:`PhaseTransitions-ADP.py <../../../examples/ZiffGulariBarshad/PhaseTransitions-ADP.py>`  and execute it with the following command:
..
.. .. code-block:: none
..
..    $ amspython PhaseTransitions-ADP.py
..
.. .. _pyzacros_code_noss:
.. .. code-block:: python
..   :linenos:
..   :caption: Hola
..
..    #-------------------------------------
..    # Calculating the rates with pyZacros
..    #-------------------------------------
..    def getRate( conditions ):
..
..        print("")
..        print("  Requesting:")
..        for cond in conditions:
..            print("    xCO = ", cond[0])
..        print("")
..
..        #---------------------------------------
..        # Zacros calculation
..        #---------------------------------------
..        zgb = pz.models.ZiffGulariBarshad()
..
..        z_sett = pz.Settings()
..        z_sett.random_seed = 953129
..        z_sett.temperature = 500.0
..        z_sett.pressure = 1.0
..        z_sett.species_numbers = ('time', 0.1)
..        z_sett.max_time = 10.0
..
..        z_job = pz.ZacrosJob( settings=z_sett, lattice=zgb.lattice,
..                              mechanism=zgb.mechanism,
..                              cluster_expansion=zgb.cluster_expansion )
..
..        #---------------------------------------
..        # Parameters scan calculation
..        #---------------------------------------
..        ps_params = pz.ZacrosParametersScanJob.Parameters()
..        ps_params.add( 'x_CO', 'molar_fraction.CO', [ cond[0] for cond in conditions ] )
..        ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
..
..        ps_job = pz.ZacrosParametersScanJob( reference=z_job, parameters=ps_params )
..
..        results = ps_job.run()
..
..        tof = numpy.nan*numpy.empty((len(conditions),1))
..        if( results.job.ok() ):
..            results_dict = results.turnover_frequency()
..
..            for i in range(len(results_dict)):
..                tof[i,0] = results_dict[i]['turnover_frequency']['CO2']
..
..        return tof
..
..
.. .. _adp_code_noss:
.. .. code-block:: python
..   :linenos:
..   :caption: Hola
..
..    #-----------------
..    # Surrogate model
..    #-----------------
..    input_var = ( { 'name'    : 'CO',
..                    'min'     : 0.001,
..                    'max'     : 0.999,
..                    'num'     : 5,
..                    'typevar' : 'lin' }, )
..
..    tab_var = ( { 'name'    : 'CO2',
..                  'typevar' : 'lin' }, )
..
..    outputDir = scm.plams.config.default_jobmanager.workdir+'/adp.results'
..
..    adpML = adp.adaptiveDesignProcedure( input_var, tab_var, getRate,
..                                         algorithmParams={'OOBth':0.05,'RADth':10},
..                                         benchmark=False,
..                                         outputDir=outputDir,
..                                         randomSeed=10 )
..
..    adpML.createTrainingDataAndML()
..
..    x_CO,TOF_CO2 = adpML.trainingData.T
..
..    print( '----------------------------' )
..    print( '%4s'%'cond', '%8s'%'x_CO', '%12s'%'TOF_CO2' )
..    print( '----------------------------' )
..    for i in range(len(x_CO)):
..        print( '%4d'%i, '%8.3f'%x_CO[i], '%12.6f'%TOF_CO2[i] )
..
..
.. .. code-block:: none
..   :linenos:
..   :caption: **Execution: Output**
..
..    ------ Adaptive generation of Training Data for Machine Learning ------
..
..    Input parameters:
..      * Forest file: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir/adp.results/ml_ExtraTrees.pkl
..      * Training file: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir/adp.results/tmp/train.dat
..      * Figure path: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir/adp.results/figures
..      * Plotting enabled: False
..      * Boruta as feature selector: True
..      * Use Weak Support Var in Boruta:True
..
..      * Forest parameters:
..        {
..            Ntree: 200
..            tps: 1
..            fraction: 0.7
..        }
..    ...
..      Requesting:
..        xCO =  0.001
..        xCO =  0.2505
..        xCO =  0.5
..        xCO =  0.7494999999999999
..        xCO =  0.999
..
..    [06.10|16:44:41] JOB plamsjob STARTED
..    [06.10|16:44:41] Waiting for job plamsjob to finish
..    [06.10|16:44:41] JOB plamsjob RUNNING
..    [06.10|16:44:41] JOB plamsjob/plamsjob_ps_cond000 STARTED
..    [06.10|16:44:41] JOB plamsjob/plamsjob_ps_cond001 STARTED
..    [06.10|16:44:41] JOB plamsjob/plamsjob_ps_cond002 STARTED
..    [06.10|16:44:41] JOB plamsjob/plamsjob_ps_cond003 STARTED
..    ...
..    [06.10|16:44:42] JOB plamsjob/plamsjob_ps_cond000 SUCCESSFUL
..    [06.10|16:44:42] JOB plamsjob/plamsjob_ps_cond002 FINISHED
..    [06.10|16:44:42] JOB plamsjob/plamsjob_ps_cond002 SUCCESSFUL
..    [06.10|16:44:46] JOB plamsjob FINISHED
..    [06.10|16:44:46] JOB plamsjob SUCCESSFUL
..    ...
..    ----------------------------
..    cond     x_CO      TOF_CO2
..    ----------------------------
..       0    0.001     0.000947
..       1    0.251     0.067284
..       2    0.313     0.148632
..       3    0.344     0.246042
..    ...
..      32    0.625     0.078358
..      33    0.749     0.002189
..      34    0.999    -0.000000
..    [06.10|16:46:04] PLAMS run finished. Goodbye
..
..
.. .. code-block:: python
..   :linenos:
..
..    fig = plt.figure()
..
..    x_CO_model = numpy.linspace(0.0,1.0,201)
..    TOF_CO2_model = adpML.predict( x_CO_model.reshape(-1,1) ).T[0]
..
..    ax = plt.axes()
..    ax.set_xlabel('Partial Pressure CO', fontsize=14)
..    ax.set_ylabel('TOF (mol/s/site)', fontsize=14)
..    ax.plot(x_CO_model, TOF_CO2_model, color='red', linestyle='-', lw=2, zorder=0)
..    ax.plot(x_CO, TOF_CO2, marker='$\u25EF$', color='black', markersize=4, lw=0, zorder=1)
..
..    plt.show()
..
..
.. .. Execution time ~1 min
.. .. figure:: ../../images/example_ZGB-PhaseTransitionsADP_0.05_10.png
..    :scale: 90 %
..    :align: center
..
..    Calculated catalytic activity (TOF of CO2) in non-steady-state conditions using the pyZacros and ADP configurations shown in :numref:`pyzacros_code_noss` and :numref:`adp_code_noss`, respectively. Particularly, notice the ADP parameters :code:`algorithmParams={'OOBth':0.05,'RADth':10}`, equivalent to a ``Normal`` numerical quality.
..
.. .. Execution time ~2 min
.. .. figure:: ../../images/example_ZGB-PhaseTransitionsADP_0.01_5.png
..    :scale: 90 %
..    :align: center
..
..    Calculated catalytic activity (TOF of CO2) in non-steady-state conditions using the pyZacros and ADP configurations shown in :numref:`pyzacros_code_noss` and :numref:`adp_code_noss`, respectively. However, for this case, we used the ADP parameters :code:`algorithmParams={'OOBth':0.01,'RADth':5}`, equivalent to a ``Good`` numerical quality.
..
..
.. You can download the full example script following this link :download:`PhaseTransitions-SteadyState-ADP.py <../../../examples/ZiffGulariBarshad/PhaseTransitions-SteadyState-ADP.py>`.
..
..
.. .. code-block:: python
..   :linenos:
..   :emphasize-lines: 28-42,52
..
..    #-------------------------------------
..    # Calculating the rates with pyZacros
..    #-------------------------------------
..    def getRate( conditions ):
..
..        zgb = pz.models.ZiffGulariBarshad()
..
..        print("")
..        print("  Requesting:")
..        for cond in conditions:
..            print("    xCO = ", cond[0])
..        print("")
..
..        #---------------------------------------
..        # Zacros calculation
..        #---------------------------------------
..        z_sett = pz.Settings()
..        z_sett.random_seed = 953129
..        z_sett.temperature = 500.0
..        z_sett.pressure = 1.0
..        z_sett.species_numbers = ('time', 0.1)
..        z_sett.max_time = 10.0
..
..        z_job = pz.ZacrosJob( settings=z_sett, lattice=zgb.lattice,
..                              mechanism=zgb.mechanism,
..                              cluster_expansion=zgb.cluster_expansion )
..
..        #---------------------------------------
..        # Steady-State calculation
..        #---------------------------------------
..        ss_sett = pz.Settings()
..        ss_sett.turnover_frequency.nbatch = 20
..        ss_sett.turnover_frequency.confidence = 0.96
..        ss_sett.turnover_frequency.ignore_nbatch = 5
..        ss_sett.nreplicas = 4
..
..        ss_params = pz.ZacrosSteadyStateJob.Parameters()
..        ss_params.add( 'max_time', 'restart.max_time',
..                       2*z_sett.max_time*( numpy.arange(100)+1 )**3 )
..
..        ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job,
..                                          parameters=ss_params )
..
..        #---------------------------------------
..        # Parameters scan calculation
..        #---------------------------------------
..        ps_params = pz.ZacrosParametersScanJob.Parameters()
..        ps_params.add( 'x_CO', 'molar_fraction.CO', [ cond[0] for cond in conditions ] )
..        ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
..
..        ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_params )
..
..        results = ps_job.run()
..
..        tof = numpy.nan*numpy.empty((len(conditions),1))
..        if( results.job.ok() ):
..            results_dict = results.turnover_frequency()
..
..            for i in range(len(results_dict)):
..                tof[i,0] = results_dict[i]['turnover_frequency']['CO2']
..
..        return tof
..
..
.. .. code-block:: none
..   :linenos:
..   :caption: **Execution: Output**
..
..    ------ Adaptive generation of Training Data for Machine Learning ------
..
..    Input parameters:
..      * Forest file: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir/adp.results/ml_ExtraTrees.pkl
..      * Training file: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir/adp.results/tmp/train.dat
..      * Figure path: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir/adp.results/figures
..      * Plotting enabled: False
..      * Boruta as feature selector: True
..      * Use Weak Support Var in Boruta:True
..
..      * Forest parameters:
..        {
..            Ntree: 200
..            tps: 1
..            fraction: 0.7
..        }
..    ...
..      Requesting:
..        xCO =  0.001
..        xCO =  0.2505
..        xCO =  0.5
..        xCO =  0.7494999999999999
..        xCO =  0.999
..
..    [06.10|22:18:09] JOB plamsjob Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=5,nreplicas=4
..    [06.10|22:18:09] JOB plamsjob_ps_cond000 Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=5,nreplicas=4
..    [06.10|22:18:09] JOB plamsjob_ps_cond001 Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=5,nreplicas=4
..    [06.10|22:18:09] JOB plamsjob_ps_cond002 Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=5,nreplicas=4
..    [06.10|22:18:09] JOB plamsjob_ps_cond003 Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=5,nreplicas=4
..    [06.10|22:18:09] JOB plamsjob_ps_cond004 Steady State Convergence: Using nbatch=20,confidence=0.96,ignore_nbatch=5,nreplicas=4
..    [06.10|22:18:09] JOB plamsjob STARTED
..    [06.10|22:18:09] Waiting for job plamsjob to finish
..    [06.10|22:18:09] JOB plamsjob RUNNING
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond000 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond001 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond002 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond000 RUNNING
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond003 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond000/plamsjob_ps_cond000_ss_iter000_rep000 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond004 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond001 RUNNING
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond000/plamsjob_ps_cond000_ss_iter000_rep001 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond002 RUNNING
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond001/plamsjob_ps_cond001_ss_iter000_rep000 STARTED
..    [06.10|22:18:09] JOB plamsjob/plamsjob_ps_cond000/plamsjob_ps_cond000_ss_iter000_rep002 STARTED
..    ...
..    [06.10|22:26:36]    Replica #0
..    [06.10|22:26:36]       species            TOF          error          ratio     conv?
..    [06.10|22:26:36]            CO       -0.34297        0.01918        0.05591     False
..    [06.10|22:26:36]            O2       -0.17148        0.00959        0.05592     False
..    [06.10|22:26:36]           CO2        0.34297        0.01918        0.05591     False
..    [06.10|22:26:40]    Replica #1
..    [06.10|22:26:40]       species            TOF          error          ratio     conv?
..    [06.10|22:26:40]            CO       -0.33099        0.02671        0.08070     False
..    [06.10|22:26:40]            O2       -0.16548        0.01337        0.08078     False
..    [06.10|22:26:40]           CO2        0.33099        0.02671        0.08070     False
..    [06.10|22:26:43]    Replica #2
..    [06.10|22:26:43]       species            TOF          error          ratio     conv?
..    [06.10|22:26:43]            CO       -0.34152        0.01653        0.04841     False
..    [06.10|22:26:43]            O2       -0.17075        0.00828        0.04849     False
..    [06.10|22:26:43]           CO2        0.34152        0.01653        0.04841     False
..    [06.10|22:26:47]    Replica #3
..    [06.10|22:26:47]       species            TOF          error          ratio     conv?
..    [06.10|22:26:47]            CO       -0.35172        0.02624        0.07461     False
..    [06.10|22:26:47]            O2       -0.17584        0.01313        0.07469     False
..    [06.10|22:26:47]           CO2        0.35172        0.02624        0.07461     False
..    [06.10|22:26:50]    Average
..    [06.10|22:26:50]       species            TOF          error          ratio     conv?
..    [06.10|22:26:51]            CO       -0.34180        0.00959        0.02804      True
..    [06.10|22:26:51]            O2       -0.17089        0.00480        0.02809      True
..    [06.10|22:26:51]           CO2        0.34180        0.00959        0.02804      True
..    [06.10|22:26:51] JOB plamsjob.006/plamsjob_ps_cond005 Steady State Convergence: CONVERGENCE REACHED. DONE!
..    [06.10|22:26:51] JOB plamsjob.006/plamsjob_ps_cond005 FINISHED
..    [06.10|22:26:52] JOB plamsjob.006/plamsjob_ps_cond005 SUCCESSFUL
..    [06.10|22:26:53] JOB plamsjob.006 FINISHED
..    [06.10|22:26:58] JOB plamsjob.006 SUCCESSFUL
..    ...
..    ----------------------------
..    cond     x_CO      TOF_CO2
..    ----------------------------
..       0    0.001     0.000189
..       1    0.251     0.006900
..       2    0.375     0.002636
..       3    0.391     0.037564
..       ...
..      23    0.625    -0.000000
..      24    0.749    -0.000000
..      25    0.999     0.000000
..    [06.10|22:27:42] PLAMS run finished. Goodbye
..
..
.. .. Execution time ~8 min
.. .. image:: ../../images/example_ZGB-PhaseTransitionsSSADP_0.06_40.png
..    :scale: 90 %
..    :align: center
..
..
.. You can download the full example script following this link :download:`PhaseTransitions-ADP_ViewResults.py <../../../examples/ZiffGulariBarshad/PhaseTransitions-ADP_ViewResults.py>`.
..
..
.. .. code-block:: python
..   :linenos:
..
..    import matplotlib.pyplot as plt
..
..    import numpy as np
..    import adaptiveDesignProcedure as adp
..
..    path = "plams_workdir/adp.results/ml_ExtraTrees_forCFD.pkl"
..
..    x_CO_model = np.linspace(0.0,1.0,200)
..    TOF_CO2_model = adp.predict( x_CO_model.reshape(-1,1), path ).T[0]
..
..    fig = plt.figure()
..
..    ax = plt.axes()
..    ax.set_xlabel('Partial Pressure CO', fontsize=14)
..    ax.set_ylabel('TOF (mol/s/site)', fontsize=14)
..    ax.plot(x_CO_model, TOF_CO2_model, color='red', linestyle='-', lw=2)
..
..    plt.show()
..
..
.. .. image:: ../../images/example_ZGB-PhaseTransitionsSSADP_0.06_40_viewResults.png
..    :scale: 90 %
..    :align: center
