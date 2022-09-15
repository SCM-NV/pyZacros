import numpy
import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

zgb = pz.models.ZiffGulariBarshad()

scm.plams.init()

z_sett = pz.Settings()
z_sett.molar_fraction.CO = 0.42
z_sett.molar_fraction.O2 = 1.0 - z_sett.molar_fraction.CO
z_sett.random_seed = 953129
z_sett.temperature = 500.0
z_sett.pressure = 1.0
z_sett.species_numbers = ('time', 1.e-2)
z_sett.max_time = 20.0

job = pz.ZacrosJob( settings=z_sett,
                    lattice=zgb.lattice,
                    mechanism=zgb.mechanism,
                    cluster_expansion=zgb.cluster_expansion )

ss_sett = pz.Settings()
ss_sett.turnover_frequency.nbatch = 20
ss_sett.turnover_frequency.confidence = 0.98
ss_sett.nreplicas = 8

parameters = { 'max_time':pz.ZacrosSteadyStateJob.Parameter('restart.max_time', numpy.arange(20.0, 50000.0, 100)) }

ss_job = pz.ZacrosSteadyStateJob( settings=ss_sett, reference=job, generator_parameters=parameters )

results = ss_job.run()

print((8+10+15+15+10+ 5)*"-")
print("%8s"%"iter", "%10s"%"TOF_CO2",    "%15s"%"max_time","%15s"%"TOF_CO2_error", "%10s"%"conv?")
print("%8s"%"",     "%10s"%"mol/s/site", "%15s"%"s",       "%15s"%"mol/s/site",    "%10s"%"")
print((8+10+15+15+10+ 5)*"-")

if ss_job.ok():
   for i,step in enumerate(results.history()):
      print("%8d"%i, "%10.5f"%step['turnover_frequency']['CO2'], "%15d"%step['max_time'],
               "%15.5f"%step['turnover_frequency_error']['CO2'], "%10s"%step['converged']['CO2'])

scm.plams.finish()
