"""Test script that reproduces https://zacros.org/tutorials/10-tutorial-4-dft-energies-to-zacros-input?showall=1."""

import scm
import scm.pyzacros as pz

#---------------------------------------------
# Species:
#---------------------------------------------
# - Gas-species:
CO_gas = pz.Species("CO")
H2O_gas = pz.Species("H2O")
H2_gas = pz.Species("H2")
CO2_gas = pz.Species("CO2", gas_energy=-0.615)
O2_gas = pz.Species("O2", gas_energy=4.913)

# - Surface species:
s0 = pz.Species("*", 1)      # Empty adsorption site
CO_adsorbed = pz.Species("CO*", 1)
H2O_adsorbed = pz.Species("H2O*", 1)
OH_adsorbed = pz.Species("OH*", 1)
O_adsorbed = pz.Species("O*", 1)
H_adsorbed = pz.Species("H*", 1)
COOH_adsorbed = pz.Species("COOH*", 1)

#---------------------------------------------
# Lattice setup:
#---------------------------------------------
latt = pz.Lattice( lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0, repeat_cell=[8,10] )

#---------------------------------------------
# Clusters:
#---------------------------------------------
CO_point = pz.Cluster( species=[CO_adsorbed],
                       cluster_energy=-2.077,
                       label="CO_point")

H2O_point = pz.Cluster(species=[H2O_adsorbed],
                       cluster_energy=-0.362,
                       label="H2O_point")

OH_point = pz.Cluster(species=[OH_adsorbed],
                      cluster_energy=0.830,
                      label="OH_point")

O_point = pz.Cluster(species=[O_adsorbed],
                     cluster_energy=1.298,
                     label="O_point")

H_point = pz.Cluster(species=[H_adsorbed],
                     cluster_energy=-0.619,
                     label="H_point")

COOH_point = pz.Cluster(species=[COOH_adsorbed],
                        cluster_energy=-1.487,
                        label="COOH_point")

CO_pair_1NN = pz.Cluster(species=[CO_adsorbed, CO_adsorbed],
                         neighboring=[(0, 1)],
                         cluster_energy=0.560,
                         label="CO_pair_1NN")

OH_H_1NN = pz.Cluster(species=[OH_adsorbed, H_adsorbed],
                      neighboring=[(0, 1)],
                      cluster_energy=0.021,
                      label="OH_H_1NN")

O_H_1NN = pz.Cluster(species=[O_adsorbed, H_adsorbed],
                     neighboring=[(0, 1)],
                     cluster_energy=0.198,
                     label="O_H_1NN")

CO_OH_1NN = pz.Cluster(species=[CO_adsorbed, OH_adsorbed],
                       neighboring=[(0, 1)],
                       cluster_energy=0.066,
                       label="CO_OH_1NN")

CO_O_1NN = pz.Cluster(species=[CO_adsorbed, O_adsorbed],
                      neighboring=[(0, 1)],
                      cluster_energy=0.423,
                      label="CO_O_1NN")

#---------------------------------------------
# Cluster expansion:
#---------------------------------------------
myClusterExpansion = pz.ClusterExpansion()
myClusterExpansion.extend( [CO_point, H2O_point] )
myClusterExpansion.append( OH_point )
myClusterExpansion.extend( [O_point, H_point, COOH_point] )
myClusterExpansion.extend( [CO_pair_1NN, OH_H_1NN, O_H_1NN, CO_OH_1NN, CO_O_1NN] )

#---------------------------------------------
# Elementary Reactions
#---------------------------------------------

CO_adsorption = pz.ElementaryReaction(initial=[s0,CO_gas],
                                      final=[CO_adsorbed],
                                      reversible=True,
                                      pre_expon=2.226e+007,
                                      pe_ratio=2.137e-006,
                                      activation_energy=0.0,
                                      label="CO_adsorption")

H2_dissoc_adsorp = pz.ElementaryReaction(initial=[s0, s0, H2_gas],
                                         final=[H_adsorbed, H_adsorbed],
                                         neighboring=[(0, 1)],
                                         reversible=True,
                                         pre_expon=8.299e+007,
                                         pe_ratio=7.966e-006,
                                         activation_energy=0.0,
                                         label="H2_dissoc_adsorp")

H2O_adsorption = pz.ElementaryReaction(initial=[s0, H2O_gas],
                                       final=[H2O_adsorbed],
                                       reversible=True,
                                       pre_expon=2.776e+002,  # Scaled-down 1e+5 times for efficiency
                                       pe_ratio=2.665e-006,
                                       activation_energy=0.0,
                                       label="H2O_adsorption")

H2O_dissoc_adsorp = pz.ElementaryReaction(initial=[H2O_adsorbed, s0],
                                          final=[OH_adsorbed, H_adsorbed],
                                          neighboring=[(0, 1)],
                                          reversible=True,
                                          pre_expon=1.042e+13,
                                          pe_ratio=1.000e+00,
                                          activation_energy=0.777,
                                          label="H2O_dissoc_adsorp")

OH_decomposition = pz.ElementaryReaction(initial=[s0, OH_adsorbed],
                                         final=[O_adsorbed, H_adsorbed],
                                         neighboring=[(0, 1)],
                                         reversible=True,
                                         pre_expon=1.042e+13,
                                         pe_ratio=1.000e+00,
                                         activation_energy=0.940,
                                         label="OH_decomposition")

COOH_formation = pz.ElementaryReaction(initial=[CO_adsorbed, OH_adsorbed],
                                       final=[s0, COOH_adsorbed],
                                       neighboring=[(0, 1)],
                                       reversible=True,
                                       pre_expon=1.042e+13,
                                       pe_ratio=1.000e+00,
                                       activation_energy=0.405,
                                       label="COOH_formation")

COOH_decomposition = pz.ElementaryReaction(initial=[COOH_adsorbed, s0],
                                           final=[s0, H_adsorbed, CO2_gas],
                                           neighboring=[(0, 1)],
                                           reversible=False,
                                           pre_expon=1.042e+13,
                                           activation_energy=0.852,
                                           label="COOH_decomposition")

CO_oxidation = pz.ElementaryReaction(initial=[CO_adsorbed, O_adsorbed],
                                     final=[s0, s0, CO2_gas],
                                     neighboring=[(0, 1)],
                                     reversible=False,
                                     pre_expon=1.042e+13,
                                     activation_energy=0.988,
                                     label="CO_oxidation")

#---------------------------------------------
# Build-up mechanism:
#---------------------------------------------
mech = pz.Mechanism([CO_adsorption, H2_dissoc_adsorp, H2O_adsorption,
                     H2O_dissoc_adsorp, OH_decomposition, COOH_formation,
                     COOH_decomposition, CO_oxidation])

#---------------------------------------------
# Settings:
#---------------------------------------------
scm.pyzacros.init()

sett = pz.Settings()

sett.molar_fraction.CO = 1.e-5
sett.molar_fraction.H2O = 0.950

sett.random_seed = 123278
sett.temperature = 500.0
sett.pressure = 10.0
sett.snapshots = ('time', 5.e-4)
sett.process_statistics = ('time', 5.e-4)
sett.species_numbers = ('time', 5.e-4)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 250.0
sett.wall_time = 30

job = pz.ZacrosJob( settings=sett, lattice=latt, mechanism=mech, cluster_expansion=myClusterExpansion )

print(job)
results = job.run()

if( job.ok() ):
   results.plot_molecule_numbers( ["CO*", "H*", "H2O*", "COOH*"] )

scm.pyzacros.finish()
