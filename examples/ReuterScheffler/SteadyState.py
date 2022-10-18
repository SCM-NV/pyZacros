# Execution time: aprox. 2 min
import multiprocessing
import numpy

import scm.plams
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

sett.steady_state_job.turnover_frequency.nbatch = 20
sett.steady_state_job.turnover_frequency.confidence = 0.90
sett.steady_state_job.nreplicas = 4

sett.steady_state_job.scaling.partial_equilibrium_index_threshold = 0.1
sett.steady_state_job.scaling.scaling_upper_bound = 100

sett.molar_fraction.CO = 0.900 # OK
#sett.molar_fraction.CO = 0.950 # ???
sett.molar_fraction.O2 = 1.0-sett.molar_fraction.CO

job = pz.ZacrosJob( settings=sett, lattice=rs.lattice, mechanism=rs.mechanism, cluster_expansion=rs.cluster_expansion )

parameters = pz.ZacrosSteadyStateJob.Parameters()
parameters.add( 'max_time', 'restart.max_time', 2*sett.max_time*( numpy.arange(20)+1 )**2 )

cjob = pz.ZacrosSteadyStateJob( reference=job, parameters=parameters )

results = cjob.run()

if cjob.ok():
   for i,step in enumerate(results.history()):
      print("%8d"%i, "%10.5f"%step['turnover_frequency']['CO2'], "%10.5f"%step['max_time'],
               "%10.5f"%step['turnover_frequency_error']['CO2'], "%15s"%step['converged']['CO2'])

scm.pyzacros.finish()
