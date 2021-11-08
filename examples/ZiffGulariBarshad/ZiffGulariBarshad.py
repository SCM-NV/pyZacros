"""
This example reproduces the Zacros example described in:
https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros
"""

import scm.plams
import pyzacros as pz

#---------------------------------------------
# Species:
#---------------------------------------------
# - Gas-species:
CO_gas = pz.Species("CO")
O2_gas = pz.Species("O2")
CO2_gas = pz.Species("CO2", gas_energy=-2.337)

# -) Surface species:
s0 = pz.Species("*", 1)      # Empty adsorption site
CO_ads = pz.Species("CO*", 1)
O_ads = pz.Species("O*", 1)

#---------------------------------------------
# Lattice setup:
#---------------------------------------------
lattice = pz.Lattice( lattice_type=pz.Lattice.RECTANGULAR, lattice_constant=1.0, repeat_cell=[50,50] )

#---------------------------------------------
# Clusters:
#---------------------------------------------
CO_point = pz.Cluster(species=[CO_ads], cluster_energy=-1.3)
O_point = pz.Cluster(species=[O_ads], cluster_energy=-2.3)

#---------------------------------------------
# Elementary Reactions
#---------------------------------------------
# CO_adsorption:
CO_adsorption = pz.ElementaryReaction(initial=[s0,CO_gas],
                                      final=[CO_ads],
                                      reversible=False,
                                      pre_expon=10.0,
                                      activation_energy=0.0)

# O2_adsorption:
O2_adsorption = pz.ElementaryReaction(initial=[s0,s0,O2_gas],
                                      final=[O_ads,O_ads],
                                      neighboring=[(0, 1)],
                                      reversible=False,
                                      pre_expon=2.5,
                                      activation_energy=0.0)

# CO_oxidation:
CO_oxidation = pz.ElementaryReaction(initial=[CO_ads, O_ads],
                                     final=[s0, s0, CO2_gas],
                                     neighboring=[(0, 1)],
                                     reversible=False,
                                     pre_expon=1.0e+20,
                                     activation_energy=0.0)

scm.plams.init()

# Settings:
sett = pz.Settings()
sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 5.e-1)
sett.process_statistics = ('time', 1.e-2)
sett.species_numbers = ('time', 1.e-2)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 25.0
sett.wall_time = 3600

job = pz.ZacrosJob( settings=sett,
                    lattice=lattice,
                    mechanism=[CO_adsorption, O2_adsorption, CO_oxidation],
                    cluster_expansion=[CO_point, O_point] )

print(job)
results = job.run()

if( job.ok() ):
   results.plot_lattice_states( results.lattice_states() )

scm.plams.finish()
