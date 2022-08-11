"""
This example reproduces the Zacros example described in:
https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros
# Execution time: aprox. 3.5 h without any scaling (TOF_CO2 = 301.32544 +/- 5.34132; ratio=0.04000)
# Execution time: aprox. 1 min with manual scaling (TOF_CO2 = 295.40334 +/- 3.33394; ratio=0.04000)
# Execution time: aprox. 1.5 min with auto scaling (TOF_CO2 = 296.68140 +/- 3.59279; ratio=0.04000)
"""
import numpy
import multiprocessing
import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

lh = pz.models.LangmuirHinshelwood()

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
dt = 5.0e-5

sett = pz.Settings()
sett.random_seed = 1609
sett.temperature = 500.0
sett.pressure = 1.000
#sett.snapshots = ('time', 10*dt)
#sett.process_statistics = ('time', dt)
sett.species_numbers = ('time', dt)
sett.max_time = 100*dt

sett.molar_fraction.CO = 0.4
sett.molar_fraction.O2 = 1.0 - sett.molar_fraction.CO

sett.steady_state_job.turnover_frequency.nbatch = 20
sett.steady_state_job.turnover_frequency.confidence = 0.96
sett.steady_state_job.nreplicas = 4

sett.steady_state_job.scaling.max_time = 2*dt
sett.steady_state_job.scaling.partial_equilibrium_index_threshold = 0.1
sett.steady_state_job.scaling.upper_bound = 100

## Adsorption and diffusion scaling factors
#for rxn in lh.mechanism:
    #if 'adsorption' in rxn.label(): rxn.pre_expon *= 1e-2
    #if  'diffusion' in rxn.label(): rxn.pre_expon *= 1e-2

job = pz.ZacrosJob( settings=sett,
                    lattice=lh.lattice,
                    mechanism=lh.mechanism,
                    cluster_expansion=lh.cluster_expansion )

parameters = { 'max_time':pz.ZacrosSteadyStateJob.Parameter('restart.max_time', 2*sett.max_time*( numpy.arange(10)+1 )**2) }

cjob = pz.ZacrosSteadyStateJob( reference=job, generator_parameters=parameters, scaling=True )

results = cjob.run()

if cjob.ok():
   for i,step in enumerate(results.history()):
      print("%8d"%i, "%10.5f"%step['turnover_frequency']['CO2'], "%10.5f"%step['max_time'],
               "%10.5f"%step['turnover_frequency_error']['CO2'], "%15s"%step['converged']['CO2'])
