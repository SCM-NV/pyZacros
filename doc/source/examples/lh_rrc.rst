.. |br| raw:: html

      <br>

.. Note::
   To follow the example of this tutorial, either:

   * Download :download:`SteadyState.py <../../../examples/LangmuirHinshelwood/CoveragesAndReactionRate.py>` (run as ``$AMSBIN/amspython CoveragesAndReactionRate.py``).
   * Download :download:`SteadyState.ipynb <../../../examples/LangmuirHinshelwood/CoveragesAndReactionRate.ipynb>` (see also: how to install `Jupyterlab <:ref:`install-and-run-jupyter-lab-jupyter-notebooks>`)

.. include:: CoveragesAndReactionRate.rst.include

.. You can download the full example script following this link :download:`CoveragesAndReactionRate.py <../../../examples/LangmuirHinshelwood/CoveragesAndReactionRate.py>`  and execute it with the following command:
..
.. .. code-block:: none
..
..    $ amspython CoveragesAndReactionRate.py
..
..
.. .. code-block:: python
..   :caption: **Code: Running the Calculations**
..   :linenos:
..
..    #---------------------------------------
..    # Zacros calculation
..    #---------------------------------------
..    lh = pz.models.LangmuirHinshelwood()
..
..    dt = 1.0e-5
..    z_sett = pz.Settings()
..    z_sett.random_seed = 1609
..    z_sett.temperature = 500.0
..    z_sett.pressure = 1.000
..    z_sett.species_numbers = ('time', dt)
..    z_sett.max_time = 100*dt
..
..    z_job = pz.ZacrosJob( settings=z_sett, lattice=lh.lattice,
..                          mechanism=lh.mechanism,
..                          cluster_expansion=lh.cluster_expansion )
..
..    #---------------------------------------
..    # Steady-State calculation
..    #---------------------------------------
..    ss_sett = pz.Settings()
..    ss_sett.turnover_frequency.nbatch = 20
..    ss_sett.turnover_frequency.confidence = 0.98
..    ss_sett.turnover_frequency.ignore_nbatch = 5
..    ss_sett.nreplicas = 4
..    ss_sett.scaling.enabled = 'T'
..    ss_sett.scaling.partial_equilibrium_index_threshold = 0.1
..    ss_sett.scaling.upper_bound = 100
..    ss_sett.scaling.max_time = 10*dt
..
..    ss_params = pz.ZacrosSteadyStateJob.Parameters()
..    ss_params.add( 'max_time', 'restart.max_time',
..                    2*z_sett.max_time*( numpy.arange(50)+1 )**2 )
..
..    ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job,
..                                      parameters=ss_params )
..
..    #---------------------------------------
..    # Parameters scan calculation
..    #---------------------------------------
..    ps_params = pz.ZacrosParametersScanJob.Parameters()
..    ps_params.add( 'x_CO', 'molar_fraction.CO', numpy.linspace(0.0, 1.0, 21) )
..    ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
..
..    ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_params )
..
..    results = ps_job.run()
..
..
.. .. code-block:: python
..   :caption: **Code: Running the Calculations**
..   :linenos:
..
..    #---------------------------------------------
..    # Getting the results
..    #---------------------------------------------
..    if( results.job.ok() ):
..        x_CO = []
..        ac_O = []
..        ac_CO = []
..        TOF_CO2 = []
..
..        results_dict = results.turnover_frequency()
..        results_dict = results.average_coverage( last=10, update=results_dict )
..
..        for i in range(len(results_dict)):
..            x_CO.append( results_dict[i]['x_CO'] )
..            ac_O.append( results_dict[i]['average_coverage']['O*'] )
..            ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
..            TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )
..
..        print( '------------------------------------------------' )
..        print( '%4s'%'cond', '%8s'%'x_CO', '%10s'%'ac_O', '%10s'%'ac_CO', '%12s'%'TOF_CO2' )
..        print( '------------------------------------------------' )
..        for i in range(len(x_CO)):
..            print( '%4d'%i, '%8.2f'%x_CO[i], '%10.6f'%ac_O[i], '%10.6f'%ac_CO[i], '%12.6f'%TOF_CO2[i] )
..
..
.. .. code-block:: none
..   :linenos:
..   :caption: **Execution: Output**
..
..    [07.10|01:00:04] PLAMS working folder: /home/user/pyzacros/examples/LangmuirHinshelwood/plams_workdir
..    Running up to 8 jobs in parallel simultaneously
..    [07.10|01:00:04] JOB plamsjob Steady State Convergence: Using nbatch=20,confidence=0.98,ignore_nbatch=5,nreplicas=4
..    [07.10|01:00:04] JOB plamsjob_ps_cond000 Steady State Convergence: Using nbatch=20,confidence=0.98,ignore_nbatch=5,nreplicas=4
..    ...
..    [07.10|01:00:04] JOB plamsjob RUNNING
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond000 STARTED
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond001 STARTED
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond002 STARTED
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond003 STARTED
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond000 RUNNING
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond001 RUNNING
..    ...
..    [07.10|01:00:04] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_scaling STARTED
..    [07.10|01:00:04] Waiting for job plamsjob_ps_cond007_ss_scaling to finish
..    [07.10|01:00:05] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_scaling RUNNING
..    [07.10|01:00:33] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_scaling FINISHED
..    [07.10|01:00:33] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_scaling SUCCESSFUL
..    [07.10|01:00:33]       id         PE     kind       orig_pexp              sf        new_pexp    label
..    [07.10|01:00:33]        0    0.00109     fast     1.00000e+07     1.06000e-02     1.06000e+05    CO_adsorption
..    [07.10|01:00:33]        1    0.00043     fast     1.00000e+07     3.35057e-03     3.35057e+04    O2_adsorption
..    [07.10|01:00:33]        2   -0.00694     fast     1.00000e+06     1.20638e-02     1.20638e+04    O_diffusion
..    [07.10|01:00:33]        3    0.00461     fast     1.00000e+06     3.07642e-02     3.07642e+04    CO_diffusion
..    [07.10|01:00:33]        4    1.00000     slow     4.50000e+02     1.00000e+00     4.50000e+02    CO_oxidation
..    [07.10|01:00:33] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter000_rep000 STARTED
..    [07.10|01:00:33] Waiting for job plamsjob_ps_cond007_ss_iter000_rep000 to finish
..    [07.10|01:00:33] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter000_rep000 RUNNING
..    [07.10|01:01:40] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter000_rep000 FINISHED
..    [07.10|01:01:41] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter000_rep000 SUCCESSFUL
..    [07.10|01:01:51]    Replica #0
..    [07.10|01:01:51]       species            TOF          error          ratio     conv?
..    [07.10|01:01:52]            CO     -239.16667      397.81644        1.66334     False
..    [07.10|01:01:52]            O2     -119.16667      195.97248        1.64452     False
..    [07.10|01:01:52]           CO2      267.50000       51.60366        0.19291     False
..    [07.10|01:01:52]    Replica #1
..    [07.10|01:01:52]       species            TOF          error          ratio     conv?
..    [07.10|01:01:52]            CO     -440.00000      308.66709        0.70152     False
..    [07.10|01:01:52]            O2      -75.83333      260.12445        3.43021     False
..    [07.10|01:01:52]           CO2      270.00000       47.24870        0.17500     False
..    [07.10|01:01:52]    Replica #2
..    [07.10|01:01:52]       species            TOF          error          ratio     conv?
..    [07.10|01:01:52]            CO     -273.33333      403.31799        1.47555     False
..    [07.10|01:01:52]            O2     -271.66667      234.48995        0.86315     False
..    [07.10|01:01:52]           CO2      273.33333       56.90008        0.20817     False
..    [07.10|01:01:53]    Replica #3
..    [07.10|01:01:53]       species            TOF          error          ratio     conv?
..    [07.10|01:01:53]            CO     -259.16667      229.00556        0.88362     False
..    [07.10|01:01:53]            O2      -94.16667      191.44835        2.03308     False
..    [07.10|01:01:53]           CO2      280.83333       74.25031        0.26439     False
..    [07.10|01:01:53]    Average
..    [07.10|01:01:53]       species            TOF          error          ratio     conv?
..    [07.10|01:01:53]            CO     -302.91667      173.47300        0.57268     False
..    [07.10|01:01:53]            O2     -140.20833      108.53716        0.77411     False
..    [07.10|01:01:53]           CO2      272.91667       25.20483        0.09235     False
..    ...
..    [07.10|01:08:11] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter003_rep000 STARTED
..    [07.10|01:08:11] Waiting for job plamsjob_ps_cond007_ss_iter003_rep000 to finish
..    [07.10|01:08:11] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter003_rep000 RUNNING
..    [07.10|01:17:38] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter003_rep000 FINISHED
..    [07.10|01:17:43] JOB plamsjob/plamsjob_ps_cond007/plamsjob_ps_cond007_ss_iter003_rep000 SUCCESSFUL
..    [07.10|01:18:07]    Replica #0
..    [07.10|01:18:07]       species            TOF          error          ratio     conv?
..    [07.10|01:18:07]            CO     -268.06914        7.58278        0.02829     False
..    [07.10|01:18:07]            O2     -135.12312        3.67089        0.02717     False
..    [07.10|01:18:07]           CO2      269.19734        7.25154        0.02694     False
..    [07.10|01:18:14]    Replica #1
..    [07.10|01:18:14]       species            TOF          error          ratio     conv?
..    [07.10|01:18:15]            CO     -270.83215       10.81504        0.03993     False
..    [07.10|01:18:15]            O2     -134.85025        4.26640        0.03164     False
..    [07.10|01:18:15]           CO2      271.02003        9.20220        0.03395     False
..    [07.10|01:18:22]    Replica #2
..    [07.10|01:18:22]       species            TOF          error          ratio     conv?
..    [07.10|01:18:23]            CO     -264.85490       12.67602        0.04786     False
..    [07.10|01:18:23]            O2     -134.58720        5.69649        0.04233     False
..    [07.10|01:18:23]           CO2      266.62348       11.76371        0.04412     False
..    [07.10|01:18:33]    Replica #3
..    [07.10|01:18:33]       species            TOF          error          ratio     conv?
..    [07.10|01:18:34]            CO     -267.04957       11.52371        0.04315     False
..    [07.10|01:18:34]            O2     -132.71496        4.03123        0.03038     False
..    [07.10|01:18:34]           CO2      267.03099        9.50399        0.03559     False
..    [07.10|01:18:40]    Average
..    [07.10|01:18:40]       species            TOF          error          ratio     conv?
..    [07.10|01:18:40]            CO     -267.70144        5.13917        0.01920      True
..    [07.10|01:18:40]            O2     -134.31889        1.95727        0.01457      True
..    [07.10|01:18:40]           CO2      268.46796        4.44802        0.01657      True
..    [07.10|01:18:40] JOB plamsjob/plamsjob_ps_cond007 Steady State Convergence: CONVERGENCE REACHED. DONE!
..    [07.10|01:18:40] JOB plamsjob/plamsjob_ps_cond007 FINISHED
..    ...
..    [07.10|02:06:45] JOB plamsjob FINISHED
..    [07.10|02:07:19] JOB plamsjob SUCCESSFUL
..    ------------------------------------------------
..    cond     x_CO       ac_O      ac_CO      TOF_CO2
..    ------------------------------------------------
..       0     0.00   0.690438   0.000000     0.000000
..       1     0.05   0.667875   0.029125    53.443618
..       2     0.10   0.638875   0.058594   101.145947
..       3     0.15   0.614094   0.087094   145.588142
..       4     0.20   0.583875   0.118406   184.732985
..       5     0.25   0.568281   0.141531   215.009393
..       6     0.30   0.534938   0.173906   247.728258
..       7     0.35   0.514656   0.198656   268.467961
..       8     0.40   0.496312   0.218031   295.157187
..       9     0.45   0.470750   0.241750   316.246484
..      10     0.50   0.445313   0.273750   334.606525
..      11     0.55   0.416625   0.304219   339.422966
..      12     0.60   0.391906   0.322594   345.763876
..      13     0.65   0.369250   0.354063   350.440322
..      14     0.70   0.339625   0.379719   349.458283
..      15     0.75   0.313000   0.406000   344.884926
..      16     0.80   0.281719   0.436875   328.781099
..      17     0.85   0.240469   0.474875   314.187987
..      18     0.90   0.199250   0.514125   276.360645
..      19     0.95   0.152813   0.544031   219.888250
..      20     1.00   0.000000   0.652937     0.000000
..    [07.10|02:12:36] PLAMS run finished. Goodbye
..
..
.. You can download the full example script following this link :download:`CoveragesAndReactionRate_ViewResults.py <../../../examples/LangmuirHinshelwood/CoveragesAndReactionRate_ViewResults.py>`  and execute it with the following command:
..
.. .. code-block:: none
..
..    $ amspython CoveragesAndReactionRate_ViewResults.py
..
..
.. .. code-block:: python
..   :caption: **Code: Running the Calculations**
..   :linenos:
..
..    #------------------------
..    # Collecting the results
..    #------------------------
..    job = scm.pyzacros.load( 'plams_workdir/mesh/mesh.dill' )
..    results = job.results
..
..    x_CO = []
..    ac_O = []
..    ac_CO = []
..    TOF_CO2 = []
..
..    results_dict = results.turnover_frequency()
..    results_dict = results.average_coverage( last=10, update=results_dict )
..
..    for i in range(len(results_dict)):
..        x_CO.append( results_dict[i]['x_CO'] )
..        ac_O.append( results_dict[i]['average_coverage']['O*'] )
..        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
..        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )
..
..    print( '------------------------------------------------' )
..    print( '%4s'%'cond', '%8s'%'x_CO', '%10s'%'ac_O', '%10s'%'ac_CO', '%12s'%'TOF_CO2' )
..    print( '------------------------------------------------' )
..    for i in range(len(x_CO)):
..        print( '%4d'%i, '%8.2f'%x_CO[i], '%10.6f'%ac_O[i], '%10.6f'%ac_CO[i], '%12.6f'%TOF_CO2[i] )
..
..
.. .. math::
..
..    \begin{gather}
..    \theta_\text{CO} = \frac{ K_\text{CO}P_\text{CO} }{ 1 + K_\text{CO}P_\text{CO} + \sqrt{K_{\text{O}_2}P_\text{O}} } \\
..    \theta_\text{O} = \frac{ \sqrt{K_{\text{O}_2}P_\text{O}} }{ 1 + K_\text{CO}P_\text{CO} + \sqrt{K_{\text{O}_2}P_\text{O}} } \\[7mm]
..    \text{TOF}_{\text{CO}_2} = 6 \, k_\text{oxi}\theta_\text{CO}\theta_\text{O}
..    \end{gather}
..
..
.. .. code-block:: python
..   :caption: **Code: Running the Calculations**
..   :linenos:
..
..    #------------------------
..    # Analytical model
..    #------------------------
..    lh = pz.models.LangmuirHinshelwood()
..
..    K_CO = lh.mechanism.find_one( 'CO_adsorption' ).pe_ratio
..    K_O2 = lh.mechanism.find_one( 'O2_adsorption' ).pe_ratio
..    k_oxi = lh.mechanism.find_one( 'CO_oxidation' ).pre_expon
..
..    x_CO_model = numpy.linspace(0.0,1.0,201)
..
..    ac_O_model = []
..    ac_CO_model = []
..    TOF_CO2_model = []
..
..    for i in range(len(x_CO_model)):
..        x_O2 = 1 - x_CO_model[i]
..        ac_O_model.append( numpy.sqrt(K_O2*x_O2)/( 1 + K_CO*x_CO_model[i] + numpy.sqrt(K_O2*x_O2) ) )
..        ac_CO_model.append( K_CO*x_CO_model[i]/( 1 + K_CO*x_CO_model[i] + numpy.sqrt(K_O2*x_O2) ) )
..        TOF_CO2_model.append( 6*k_oxi*ac_CO_model[i]*ac_O_model[i] )
..
..
.. .. code-block:: python
..   :caption: **Code: Running the Calculations**
..   :linenos:
..
..    #------------------------
..    # Plotting the results
..    #------------------------
..    fig = plt.figure()
..
..    ax = plt.axes()
..    ax.set_xlabel('Partial Pressure CO', fontsize=14)
..    ax.set_ylabel('Coverage Fraction (%)', color='blue', fontsize=14)
..    ax.plot(x_CO, ac_O_model, color='blue', linestyle='-.', lw=2, zorder=1)
..    ax.plot(x_CO, ac_O, marker='$\u25CF$', color='blue', lw=0, markersize=4, zorder=2)
..    ax.plot(x_CO, ac_CO_model, color='blue', linestyle='-', lw=2, zorder=3)
..    ax.plot(x_CO, ac_CO, marker='$\u25EF$', color='blue', markersize=4, lw=0, zorder=4)
..    plt.text(0.3, 0.60, 'O', fontsize=18, color='blue')
..    plt.text(0.7, 0.45, 'CO', fontsize=18, color='blue')
..
..    ax2 = ax.twinx()
..    ax2.set_ylabel('TOF (mol/s/site)',color='red', fontsize=14)
..    ax2.plot(x_CO, TOF_CO2_model, color='red', linestyle='-', lw=2, zorder=5)
..    ax2.plot(x_CO, TOF_CO2, marker='$\u25EF$', color='red', markersize=4, lw=0, zorder=6)
..    plt.text(0.3, 200.0, 'CO$_2$', fontsize=18, color='red')
..
..    plt.show()
..
..
.. .. figure:: ../../images/example_LH-ProductionRate.png
..    :scale: 90 %
..    :align: center

