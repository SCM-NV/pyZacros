"""Test script that reproduces https://zacros.org/tutorials/12-about-kinetic-monte-carlo?showall=1"""

import scm
import scm.pyzacros as pz

#---------------------------------------------
# Species:
#---------------------------------------------
# - Gas-species:
O2_gas = pz.Species("O2")
CO_gas = pz.Species("CO")
CO2_gas = pz.Species("CO2", gas_energy=-3.1800)

# - Surface species:
s0 = pz.Species("*", 1)      # Empty adsorption site
O_adsorbed = pz.Species("O*", 1)
CO_adsorbed = pz.Species("CO*", 1)

#---------------------------------------------
# Lattice setup:
#---------------------------------------------
latt = pz.Lattice( lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0, repeat_cell=[20,20] )

#---------------------------------------------
# Clusters & Cluster expansion
#---------------------------------------------
empty_point = pz.Cluster( species=[pz.Species.UNSPECIFIED], energy=0.0, label="Empty")
myClusterExpansion = pz.ClusterExpansion( [empty_point] )

#---------------------------------------------
# Elementary Reactions & Mechanism
#---------------------------------------------

CO_adsorption = pz.ElementaryReaction(initial=[s0,CO_gas],
                                      final=[CO_adsorbed],
                                      reversible=True,
                                      pre_expon=1.000e+7,
                                      pe_ratio=2.000,
                                      activation_energy=0.000,
                                      label="CO_adsorption")

O2_adsorption = pz.ElementaryReaction(initial=[s0,s0,O2_gas],
                                      final=[O_adsorbed,O_adsorbed],
                                      neighboring=[(0, 1)],
                                      reversible=True,
                                      pre_expon=1.000e+7,
                                      pe_ratio=5.000,
                                      activation_energy=0.000,
                                      label="O2_adsorption")

O_diffusion = pz.ElementaryReaction(initial=[O_adsorbed,s0],
                                      final=[s0,O_adsorbed],
                                      neighboring=[(0, 1)],
                                      reversible=True,
                                      pre_expon=1.000e+6,
                                      pe_ratio=1.000,
                                      activation_energy=0.000,
                                      label="O_diffusion")

CO_diffusion = pz.ElementaryReaction(initial=[CO_adsorbed,s0],
                                      final=[s0,CO_adsorbed],
                                      neighboring=[(0, 1)],
                                      reversible=True,
                                      pre_expon=1.000e+6,
                                      pe_ratio=1.000,
                                      activation_energy=0.000,
                                      label="CO_diffusion")

CO_oxidation = pz.ElementaryReaction(initial=[CO_adsorbed, O_adsorbed],
                                     final=[s0, s0, CO2_gas],
                                     neighboring=[(0, 1)],
                                     reversible=False,
                                     pre_expon=4.500e+2,
                                     activation_energy=0.000,
                                     label="CO_oxidation")

mech = pz.Mechanism([CO_adsorption, O2_adsorption, O_diffusion, CO_diffusion, CO_oxidation])

#---------------------------------------------
# Settings:
#---------------------------------------------
scm.pyzacros.init()

sett = pz.Settings()

sett.molar_fraction.O2 = 0.500
sett.molar_fraction.CO = 0.500

sett.random_seed = 1609
sett.temperature = 300.0
sett.pressure = 1.000

sett.snapshots = ('time', 5.0e-04)
sett.process_statistics = ('time', 5.0e-05)
sett.species_numbers = ('time', 5.0e-05)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 5.0e-2
sett.wall_time = 21600 # 6 hrs

job = pz.ZacrosJob( settings=sett, lattice=latt, mechanism=mech, cluster_expansion=myClusterExpansion )

print(job)
results = job.run()

if( job.ok() ):
   results.plot_molecule_numbers( ["CO2"] )

scm.pyzacros.finish()
