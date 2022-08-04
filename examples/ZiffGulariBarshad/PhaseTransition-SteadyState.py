import numpy
import multiprocessing

import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

zgb = pz.models.ZiffGulariBarshad()

#---------------------------------------------
# Calculation Settings
#---------------------------------------------
scm.plams.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

# Settings:
sett = pz.Settings()
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 2.0)
sett.species_numbers = ('time', 0.1)
sett.max_time = 10.0

parametersA = { 'max_time':pz.ZacrosSteadyStateJob.Parameter('restart.max_time', 2*sett.max_time*( numpy.arange(10)+1 )**3) }

parametersB = { 'x_CO':pz.ZacrosParametersScanJob.Parameter('molar_fraction.CO', numpy.arange(0.2, 0.8, 0.01)),
                'x_O2':pz.ZacrosParametersScanJob.Parameter('molar_fraction.O2', lambda params: 1.0-params['x_CO']) }

job = pz.ZacrosJob( settings=sett, lattice=zgb.lattice, mechanism=zgb.mechanism,
                    cluster_expansion=zgb.cluster_expansion )

ssjob = pz.ZacrosSteadyStateJob( reference=job, generator_parameters=parametersA )

mjob = pz.ZacrosParametersScanJob( reference=ssjob,
                                   generator=pz.ZacrosParametersScanJob.meshGenerator,
                                   generator_parameters=parametersB, name='mesh' )

results = mjob.run()

output = ""
if( results.job.ok() ):
    x_CO = []
    ac_O = []
    ac_CO = []
    TOF_CO2 = []
    TOF_CO2_conv = []

    results_dict = results.turnover_frequency()
    results_dict = results.average_coverage( last=20, update=results_dict )

    for i in range(len(results_dict)):
        x_CO.append( results_dict[i]['x_CO'] )
        ac_O.append( results_dict[i]['average_coverage']['O*'] )
        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )
        TOF_CO2_conv.append( results_dict[i]['turnover_frequency_converged']['CO2'] )

    output += "----------------------------------------------\n"
    output += "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %12s"%"TOF_CO2\n"
    output += "----------------------------------------------\n"
    for i in range(len(x_CO)):
        output += "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i] \
                    +" %12.6f"%TOF_CO2[i]+" %8s"%TOF_CO2_conv[i]+"\n"

scm.plams.finish()

print(output)

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
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.37, 1.5, 'CO$_2$', fontsize=18, color="red")

plt.show()
