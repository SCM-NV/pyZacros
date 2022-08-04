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
dt = 5.0e-5

sett = pz.Settings()
sett.random_seed = 1609
sett.temperature = 500.0
sett.pressure = 1.000
sett.process_statistics = ('time', dt)
sett.species_numbers = ('time', dt)
sett.max_time = 100*dt

sett.steady_state_job.turnover_frequency.nbatch = 20
sett.steady_state_job.turnover_frequency.confidence = 0.93

# Adsorption and diffusion scaling factors
for rxn in lh.mechanism:
    if 'adsorption' in rxn.label(): rxn.pre_expon *= 1e-2
    if  'diffusion' in rxn.label(): rxn.pre_expon *= 1e-2

parametersA = { 'max_time':pz.ZacrosSteadyStateJob.Parameter('restart.max_time', 2*sett.max_time*( numpy.arange(10)+1 )**2) }

parametersB = { 'x_CO':pz.ZacrosParametersScanJob.Parameter('molar_fraction.CO', numpy.arange(0.0, 1.0+0.1, 0.1)),
                'x_O2':pz.ZacrosParametersScanJob.Parameter('molar_fraction.O2', lambda params: 1.0-params['x_CO']) }

job = pz.ZacrosJob( settings=sett, lattice=lh.lattice, mechanism=lh.mechanism, cluster_expansion=lh.cluster_expansion )

ssjob = pz.ZacrosSteadyStateJob( reference=job, generator_parameters=parametersA )

mjob = pz.ZacrosParametersScanJob( reference=ssjob,
                                   generator=pz.ZacrosParametersScanJob.meshGenerator,
                                   generator_parameters=parametersB, name='mesh' )

results = mjob.run()

if( results.job.ok() ):
    x_CO = []
    ac_O = []
    ac_CO = []
    TOF_CO2 = []
    TOF_CO2_conv = []

    results_dict = results.turnover_frequency()
    results_dict = results.average_coverage( last=10, update=results_dict )

    for i in range(len(results_dict)):
        x_CO.append( results_dict[i]['x_CO'] )
        ac_O.append( results_dict[i]['average_coverage']['O*'] )
        ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
        TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )
        TOF_CO2_conv.append( results_dict[i]['turnover_frequency_converged']['CO2'] )

    print( "----------------------------------------------" )
    print( "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %12s"%"TOF_CO2" )
    print( "----------------------------------------------" )
    for i in range(len(x_CO)):
        print( "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i]+" %12.6f"%TOF_CO2[i]+" %8s"%TOF_CO2_conv[i] )

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
plt.text(0.3, 0.6, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.4, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.3, 0.3, 'CO$_2$', fontsize=18, color="red")

plt.show()

## Lattice states for x_CO=0.54 and CO=0.55
#results[33].last_lattice_state().plot()
#results[34].last_lattice_state().plot()

## Molecule numbers for x_CO=0.54 and CO=0.55
#results[33].plot_molecule_numbers( ["CO2"], normalize_per_site=True )
#results[34].plot_molecule_numbers( ["CO2"], normalize_per_site=True )

## Molecule numbers for x_CO=0.54 and CO=0.55. First Derivative
#results[33].plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )
#results[34].plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )

