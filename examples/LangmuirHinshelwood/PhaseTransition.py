# Execution time: aprox. 35 min
import multiprocessing
import numpy

import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

lh = pz.models.LangmuirHinshelwood()

#---------------------------------------------
# Calculation Settings
#---------------------------------------------
scm.pyzacros.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

# Settings:
dt = 1.0e-5
z_sett = pz.Settings()
z_sett.random_seed = 1609
z_sett.temperature = 500.0
z_sett.pressure = 1.000
#z_sett.process_statistics = ('time', dt)
z_sett.species_numbers = ('time', dt)
z_sett.max_time = 100*dt

z_job = pz.ZacrosJob( settings=z_sett, lattice=lh.lattice, mechanism=lh.mechanism, cluster_expansion=lh.cluster_expansion )

ss_sett = pz.Settings()
ss_sett.turnover_frequency.nbatch = 20
ss_sett.turnover_frequency.confidence = 0.98
ss_sett.nreplicas = 4
ss_sett.scaling.partial_equilibrium_index_threshold = 0.1
ss_sett.scaling.upper_bound = 10
ss_sett.scaling.max_time = 10*dt
ss_sett.scaling.species_numbers = ('time', dt)
#ss_sett.scaling.nevents_per_timestep = 10000

ss_parameters = pz.ZacrosSteadyStateJob.Parameters()
ss_parameters.add( 'max_time', 'restart.max_time', 2*z_sett.max_time*( numpy.arange(50)+1 )**2 )

ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=z_job, parameters=ss_parameters, scaling=True )

ps_parameters = pz.ZacrosParametersScanJob.Parameters()
ps_parameters.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.1, 1.0, 0.05) )
ps_parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
ps_parameters.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )

ps_job = pz.ZacrosParametersScanJob( reference=ss_job, parameters=ps_parameters, name='mesh' )

results = ps_job.run()

if( results.job.ok() ):
    x_CO = []
    ac_O = []
    ac_CO = []
    TOF_CO2 = []

    results_dict = results.turnover_frequency()
    results_dict = results.average_coverage( last=10, update=results_dict )

    for i in range(len(results_dict)):
        x_CO.append( results_dict[i]['x_CO'] )
        ac_O.append( results_dict[i]['average_coverage']['O*'] )
        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )

    print( "----------------------------------------------" )
    print( "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %12s"%"TOF_CO2" )
    print( "----------------------------------------------" )
    for i in range(len(x_CO)):
        print( "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i]+" %12.6f"%TOF_CO2[i] )

scm.plams.finish()

#---------------------------------------------
# Plotting the results
#---------------------------------------------
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print('Consider to install matplotlib to visualize the results!')
    exit(0)

# Coverage and TOF plot
fig = plt.figure()

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel("Coverage Fraction (%)", color="blue", fontsize=14)
ax.plot(x_CO, ac_O, color="blue", linestyle="-.", lw=2, zorder=1)
ax.plot(x_CO, ac_CO, color="blue", linestyle="-", lw=2, zorder=2)
plt.text(0.3, 0.60, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.45, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.3, 200.0, 'CO$_2$', fontsize=18, color="red")

plt.show()
