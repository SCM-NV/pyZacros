"""
This example reproduces the Zacros example described in:
https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros
"""
import numpy
import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

zgb = pz.models.ZiffGulariBarshad()

#---------------------------------------------
# Calculation Settings
#---------------------------------------------
scm.plams.init()

# Settings:
sett = pz.Settings()
sett.molar_fraction.CO = 0.42
sett.molar_fraction.O2 = 1.0 - sett.molar_fraction.CO
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 5.e-1)
sett.process_statistics = ('time', 1.e-2)
sett.species_numbers = ('time', 1.e-2)
sett.max_time = 20.0

job = pz.ZacrosJob( settings=sett,
                    lattice=zgb.lattice,
                    mechanism=zgb.mechanism,
                    cluster_expansion=zgb.cluster_expansion )

parameters = { 'max_time':pz.ZacrosSteadyStateJob.Parameter('restart.max_time', numpy.arange(20.0, 5000.0, 100)) }

cjob = pz.ZacrosSteadyStateJob( reference=job, generator_parameters=parameters )

results = cjob.run()

if cjob.ok():
   for i,step in enumerate(results.history()):
      print("%8d"%i, "%10.5f"%step['turnover_frequency']['CO2'], "%15d"%step['max_time'],
               "%10.5f"%step['turnover_frequency_error']['CO2'], "%15s"%step['converged']['CO2'])
