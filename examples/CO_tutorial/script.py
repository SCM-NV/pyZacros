"""Test script that will reproduce CO_tutorial inputs."""

import pyzacros as pz

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
myLattice = pz.Lattice(lattice_type="default_choice",
                        default_lattice=["hexagonal_periodic", 1.0, 8, 10])

#print(myLattice)

#---------------------------------------------
# Clusters:
#---------------------------------------------
CO_point = pz.Cluster(site_types=["1"],
                   species=[CO_adsorbed],
                   cluster_energy=-2.077)

H2O_point = pz.Cluster(site_types=["1"],
                    species=[H2O_adsorbed],
                    cluster_energy=-0.362)

OH_point = pz.Cluster(site_types=["1"],
                   species=[OH_adsorbed],
                   cluster_energy=0.830)

O_point = pz.Cluster(site_types=["1"],
                  species=[O_adsorbed],
                  cluster_energy=1.298)

H_point = pz.Cluster(site_types=["1"],
                  species=[H_adsorbed],
                  cluster_energy=-0.619)

COOH_point = pz.Cluster(site_types=["1"],
                     species=[COOH_adsorbed],
                     cluster_energy=-1.487)

CO_pair_1NN = pz.Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[CO_adsorbed, CO_adsorbed],
                      cluster_energy=0.560)

OH_H_1NN = pz.Cluster(site_types=["1", "1"],
                   neighboring=[(1, 2)],
                   species=[OH_adsorbed, H_adsorbed],
                   cluster_energy=0.021)

O_H_1NN = pz.Cluster(site_types=["1", "1"],
                  neighboring=[(1, 2)],
                  species=[O_adsorbed, H_adsorbed],
                  cluster_energy=0.198)

CO_OH_1NN = pz.Cluster(site_types=["1", "1"],
                    neighboring=[(1, 2)],
                    species=[CO_adsorbed, OH_adsorbed],
                    cluster_energy=0.066)

CO_O_1NN = pz.Cluster(site_types=["1", "1"],
                   neighboring=[(1, 2)],
                   species=[CO_adsorbed, O_adsorbed],
                   cluster_energy=0.423)

#---------------------------------------------
# Cluster expansion:
#---------------------------------------------
myClusterExpansion = pz.ClusterExpansion()
myClusterExpansion.extend( [CO_point, H2O_point] )
myClusterExpansion.append( OH_point )
myClusterExpansion.extend( [O_point, H_point, COOH_point] )
myClusterExpansion.extend( [CO_pair_1NN, OH_H_1NN, O_H_1NN, CO_OH_1NN, CO_O_1NN] )

#print(myClusterExpansion)

#---------------------------------------------
# Elementary Reactions
#---------------------------------------------

# CO_adsoprtion:
CO_adsorption = pz.ElementaryReaction(site_types=["1"],
                                   initial=[s0,CO_gas],
                                   final=[CO_adsorbed],
                                   reversible=True,
                                   pre_expon=2.226e+007,
                                   pe_ratio=2.137e-006,
                                   activation_energy=0.0)
# H2_dissoc_adsorp:
H2_dissoc_adsorp = pz.ElementaryReaction(site_types=["1", "1"],
                                      initial=[s0, s0, H2_gas],
                                      final=[H_adsorbed, H_adsorbed],
                                      neighboring=[(1, 2)],
                                      reversible=True,
                                      pre_expon=8.299e+007,
                                      pe_ratio=7.966e-006,
                                      activation_energy=0.0)

# H2O_adsorption:
H2O_adsorption = pz.ElementaryReaction(site_types=["1"],
                                    initial=[s0, H2O_gas],
                                    final=[H2O_adsorbed],
                                    reversible=True,
                                    pre_expon=2.776e+002,
                                    pe_ratio=2.665e-006,
                                    activation_energy=0.0)

# H2O_dissociation:
H2O_dissoc_adsorp = pz.ElementaryReaction(site_types=["1", "1"],
                                       initial=[H2O_adsorbed, s0],
                                       final=[OH_adsorbed, H_adsorbed],
                                       neighboring=[(1, 2)],
                                       reversible=True,
                                       pre_expon=1.042e+13,
                                       pe_ratio=1.000e+00,
                                       activation_energy=0.777)

# OH_decomposition:
OH_decomposition = pz.ElementaryReaction(site_types=["1", "1"],
                                      initial=[s0, OH_adsorbed],
                                      final=[O_adsorbed, H_adsorbed],
                                      neighboring=[(1, 2)],
                                      reversible=True,
                                      pre_expon=1.042e+13,
                                      pe_ratio=1.000e+00,
                                      activation_energy=0.940)

# COOH_formation:
COOH_formation = pz.ElementaryReaction(site_types=["1", "1"],
                                    initial=[CO_adsorbed, OH_adsorbed],
                                    final=[s0, COOH_adsorbed],
                                    neighboring=[(1, 2)],
                                    reversible=True,
                                    pre_expon=1.042e+13,
                                    pe_ratio=1.000e+00,
                                    activation_energy=0.405)

# COOH_decomposition:
COOH_decomposition = pz.ElementaryReaction(site_types=["1", "1"],
                                        initial=[COOH_adsorbed, s0],
                                        final=[s0, H_adsorbed, CO2_gas],
                                        neighboring=[(1, 2)],
                                        reversible=False,
                                        pre_expon=1.042e+13,
                                        activation_energy=0.852)

# CO_oxidation:
CO_oxidation = pz.ElementaryReaction(site_types=["1", "1"],
                                  initial=[CO_adsorbed, O_adsorbed],
                                  final=[s0, s0, CO2_gas],
                                  neighboring=[(1, 2)],
                                  reversible=False,
                                  pre_expon=1.042e+13,
                                  activation_energy=0.988)

#---------------------------------------------
# Build-up mechanism:
#---------------------------------------------
myMechanism = pz.Mechanism([CO_adsorption, H2_dissoc_adsorp, H2O_adsorption,
                            H2O_dissoc_adsorp, OH_decomposition, COOH_formation,
                            COOH_decomposition, CO_oxidation])

#print(myMechanism.adsorbed_species())
#print(myMechanism.gas_species())

#---------------------------------------------
# Settings:
#---------------------------------------------
sett = pz.KMCSettings()

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

myJob = pz.KMCJob( settings=sett, lattice=myLattice, mechanism=myMechanism, cluster_expansion=myClusterExpansion )

print(myJob)
myJob.run()
