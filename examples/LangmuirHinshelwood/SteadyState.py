"""
This example reproduces the Zacros example described in:
https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros
# Execution time: aprox. 3.5 h without any scaling (TOF_CO2 = 301.32544 +/- 5.34132; ratio=0.04000)
# Execution time: aprox. 1 min with manual scaling (TOF_CO2 = 295.40334 +/- 3.33394; ratio=0.04000)
# Execution time: aprox. 1.5 min with auto scaling (TOF_CO2 = 296.68140 +/- 3.59279; ratio=0.04000)
"""
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
z_sett = pz.Settings()
z_sett.random_seed = 1609
z_sett.temperature = 500.0
z_sett.pressure = 1.000
#z_sett.snapshots = ('time', 10*dt)
#z_sett.process_statistics = ('time', dt)
z_sett.species_numbers = ('time', dt)
z_sett.max_time = 100*dt

#z_sett.molar_fraction.CO = 0.4
#z_sett.molar_fraction.O2 = 1.0 - z_sett.molar_fraction.CO
z_sett.molar_fraction.CO = 0.9
z_sett.molar_fraction.O2 = 1.0 - z_sett.molar_fraction.CO

## Adsorption and diffusion scaling factors
#for rxn in lh.mechanism:
    #if 'adsorption' in rxn.label(): rxn.pre_expon *= 1e-2
    #if  'diffusion' in rxn.label(): rxn.pre_expon *= 1e-2

job = pz.ZacrosJob( settings=z_sett, lattice=lh.lattice, mechanism=lh.mechanism, cluster_expansion=lh.cluster_expansion )

dt = 5.0e-5
ss_sett = pz.Settings()
ss_sett.turnover_frequency.nbatch = 20
ss_sett.turnover_frequency.confidence = 0.96
ss_sett.nreplicas = 4
ss_sett.scaling.enabled = 'T'
ss_sett.scaling.partial_equilibrium_index_threshold = 0.1
ss_sett.scaling.upper_bound = 100
ss_sett.scaling.max_time = 10*dt
ss_sett.scaling.species_numbers = ('time', dt)

ss_params = pz.ZacrosSteadyStateJob.Parameters()
ss_params.add( 'max_time', 'restart.max_time',
                2*z_sett.max_time*( numpy.arange(50)+1 )**2 )

cjob = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=job, parameters=ss_params )

results = cjob.run()

if cjob.ok():
   for i,step in enumerate(results.history()):
      print("%8d"%i, "%10.5f"%step['turnover_frequency']['CO2'], "%10.5f"%step['max_time'],
               "%10.5f"%step['turnover_frequency_error']['CO2'], "%15s"%step['converged']['CO2'])

scm.pyzacros.finish()
