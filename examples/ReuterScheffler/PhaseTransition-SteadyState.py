import multiprocessing
import numpy

import scm
import scm.pyzacros as pz
import scm.pyzacros.models

rs = pz.models.ReuterScheffler()

scm.pyzacros.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

dt = 1e-6
sett = pz.Settings()
sett.random_seed = 14390
sett.temperature = 600.0
sett.pressure = 1.0
#sett.snapshots = ('time', 100*dt)
#sett.process_statistics = ('time', 10*dt)
sett.species_numbers = ('time', dt)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 1000*dt

job = pz.ZacrosJob( settings=sett, lattice=rs.lattice, mechanism=rs.mechanism, cluster_expansion=rs.cluster_expansion )

ss_sett = pz.Settings()
ss_sett.steady_state_job.turnover_frequency.nbatch = 20
ss_sett.steady_state_job.turnover_frequency.confidence = 0.90
ss_sett.steady_state_job.nreplicas = 4

parametersA = pz.ZacrosSteadyStateJob.Parameters()
parametersA.add( 'max_time', 'restart.max_time', 2*sett.max_time*( numpy.arange(20)+1 )**2 )

ssjob = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=job, parameters=parametersA, scaling=True )

parametersB = pz.ZacrosParametersScanJob.Parameters()
parametersB.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.900, 0.999, 0.001) )
parametersB.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
parametersB.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )

mjob = pz.ZacrosParametersScanJob( reference=ssjob, parameters=parametersB, name='mesh' )

results = mjob.run()

if( results.job.ok() ):
    x_CO = []
    ac_O = []
    ac_CO = []
    TOF_CO2 = []

    results_dict = results.turnover_frequency()
    results_dict = results.average_coverage( last=20, update=results_dict )

    for i in range(len(results_dict)):
        x_CO.append( results_dict[i]['x_CO'] )
        ac_O.append( results_dict[i]['average_coverage']['O*'] )
        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2']/1e4 )

    print( "---------------------------------------------------" )
    print( "%4s"%"cond", "%8s"%"x_CO", "%10s"%"ac_O", "%10s"%"ac_CO", "%10s"%"TOF_CO2.10^4" )
    print( "---------------------------------------------------" )
    for i in range(len(x_CO)):
        print( "%4d"%i, "%8.2f"%x_CO[i], "%10.6f"%ac_O[i], "%10.6f"%ac_CO[i] , "%10.6f"%TOF_CO2[i])

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
plt.text(0.3, 0.9, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.9, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF  x 10$^4$ (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.37, 1.5, 'CO$_2$', fontsize=18, color="red")

plt.show()
