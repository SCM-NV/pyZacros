"""Test script that will reproduce CO_tutorial inputs."""

from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.KMCJob import KMCJob
from pyzacros.classes.Mechanism import Mechanism
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Species import Species
from pyzacros.classes.SpeciesList import SpeciesList
from pyzacros.classes.ElementaryReaction import ElementaryReaction

# Species:
sett = KMCSettings()
s0 = Species("*", 1)      # Empty adsorption site

# -) Gas-species:
CO_gas = Species("CO")
sett.molar_fraction.CO = 1.e-5
H2O_gas = Species("H2O")
sett.molar_fraction.H2O = 0.950
H2_gas = Species("H2")
CO2_gas = Species("CO2", gas_energy=-0.615)
O2_gas = Species("O2", gas_energy=4.913)

# -) Adsorbed species:
CO_adsorbed = Species("CO*", 1)
H2O_adsorbed = Species("H2O*", 1)
OH_adsorbed = Species("OH*", 1)
O_adsorbed = Species("O*", 1)
H_adsorbed = Species("H*", 1)
COOH_adsorbed = Species("COOH*", 1)
# Build-up list:
mySpeciesList = SpeciesList()
mySpeciesList.append(CO_gas)
mySpeciesList.append(CO_adsorbed)
mySpeciesList.append(H2O_gas)
mySpeciesList.append(H2O_adsorbed)
mySpeciesList.append(H2_gas)
mySpeciesList.append(CO2_gas)
mySpeciesList.append(O2_gas)
mySpeciesList.append(OH_adsorbed)
mySpeciesList.append(O_adsorbed)
mySpeciesList.append(H_adsorbed)
mySpeciesList.append(COOH_adsorbed)
#print(mySpeciesList)

# Lattice:

myLattice = Lattice(lattice_type="default_choice",
                    default_lattice=["hexagonal_periodic", 1.0, 8, 10])
#print(myLattice)

# CO_adsoprtion:

myCluster1 = Cluster(site_types=["1"],
                     species=[s0],
                     gas_species=[CO_gas])

myCluster2 = Cluster(site_types=["1"],
                     species=[CO_adsorbed],
                     cluster_energy=-2.077)

CO_adsorption = ElementaryReaction(site_types=["1"],
                                   initial=myCluster1,
                                   final=myCluster2,
                                   reversible=True,
                                   pre_expon=2.226e+007,
                                   pe_ratio=2.137e-006,
                                   activation_energy=0.0)

# H2_dissoc_adsorp:

myCluster3 = Cluster(site_types=["1", "1"],
                     neighboring=[(1, 2)],
                     species=[s0, s0],
                     gas_species=[H2_gas],
                     cluster_energy=0.0)

myCluster4 = Cluster(site_types=["1", "1"],
                     neighboring=[(1, 2)],
                     species=[H_adsorbed, H_adsorbed],
                     cluster_energy=0.0)

H2_dissoc_adsorp = ElementaryReaction(site_types=["1", "1"],
                                      initial=myCluster3,
                                      final=myCluster4,
                                      neighboring=[(1, 2)],
                                      reversible=True,
                                      pre_expon=8.299e+007,
                                      pe_ratio=7.966e-006,
                                      activation_energy=0.0)
# H2O_adsoroption:

myCluster5 = Cluster(site_types=["1"],
                     species=[s0],
                     gas_species=[H2O_gas])

myCluster6 = Cluster(site_types=["1"],
                     species=[H2O_adsorbed],
                     cluster_energy=-0.362)

H2O_adsorption = ElementaryReaction(site_types=["1"],
                                    initial=myCluster5,
                                    final=myCluster6,
                                    reversible=True,
                                    pre_expon=2.776e+002,
                                    pe_ratio=2.665e-006,
                                    activation_energy=0.0)

# H2O_dissociation:

myCluster7 = Cluster(site_types=["1", "1"],
                     neighboring=[(1, 2)],
                     species=[H2O_adsorbed, s0],
                     cluster_energy=0.0)

myCluster8 = Cluster(site_types=["1", "1"],
                     neighboring=[(1, 2)],
                     species=[OH_adsorbed, H_adsorbed],
                     cluster_energy=0.021)

H2O_dissoc_adsorp = ElementaryReaction(site_types=["1", "1"],
                                       initial=myCluster7,
                                       final=myCluster8,
                                       neighboring=[(1, 2)],
                                       reversible=True,
                                       pre_expon=1.042e+13,
                                       pe_ratio=1.000e+00,
                                       activation_energy=0.777)

# OH_decomposition:

myCluster9 = Cluster(site_types=["1", "1"],
                     neighboring=[(1, 2)],
                     species=[s0, OH_adsorbed],
                     cluster_energy=0.0)

myCluster10 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[O_adsorbed, H_adsorbed],
                      cluster_energy=0.0)

OH_decomposition = ElementaryReaction(site_types=["1", "1"],
                                      initial=myCluster9,
                                      final=myCluster10,
                                      neighboring=[(1, 2)],
                                      reversible=True,
                                      pre_expon=1.042e+13,
                                      pe_ratio=1.000e+00,
                                      activation_energy=0.940)

# COOH_formation:
myCluster11 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[CO_adsorbed, OH_adsorbed],
                      cluster_energy=0.066)

myCluster12 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[s0, COOH_adsorbed],
                      cluster_energy=0.0)

COOH_formation = ElementaryReaction(site_types=["1", "1"],
                                    initial=myCluster11,
                                    final=myCluster12,
                                    neighboring=[(1, 2)],
                                    reversible=True,
                                    pre_expon=1.042e+13,
                                    pe_ratio=1.000e+00,
                                    activation_energy=0.405)

# COOH_decomposition:

myCluster13 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[COOH_adsorbed, s0],
                      cluster_energy=0.0)

myCluster14 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[s0, H_adsorbed],
                      gas_species=[CO2_gas],
                      cluster_energy=0.0)

COOH_decomposition = ElementaryReaction(site_types=["1", "1"],
                                        initial=myCluster13,
                                        final=myCluster14,
                                        neighboring=[(1, 2)],
                                        reversible=False,
                                        pre_expon=1.042e+13,
                                        activation_energy=0.852)

# CO_oxidation:

myCluster15 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[CO_adsorbed, O_adsorbed],
                      cluster_energy=0.423)

myCluster16 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[s0, s0],
                      gas_species=[CO2_gas],
                      cluster_energy=0.0)

CO_oxidation = ElementaryReaction(site_types=["1", "1"],
                                  initial=myCluster15,
                                  final=myCluster16,
                                  neighboring=[(1, 2)],
                                  reversible=False,
                                  pre_expon=1.042e+13,
                                  activation_energy=0.988)

# Extra:
myCluster17 = Cluster(site_types=["1", "1"],
                      species=[CO_adsorbed, CO_adsorbed],
                      cluster_energy=0.560)
myCluster18 = Cluster(site_types=["1"],
                      species=[COOH_adsorbed],
                      cluster_energy=-1.487)


# Build-up mechanism:

myMechanism1 = Mechanism()
myMechanism1.append(CO_adsorption)
myMechanism1.append(H2_dissoc_adsorp)
myMechanism1.append(H2O_adsorption)
myMechanism1.append(H2O_dissoc_adsorp)
myMechanism1.append(OH_decomposition)
myMechanism1.append(COOH_formation)
myMechanism1.append(COOH_decomposition)
myMechanism1.append(CO_oxidation)
#print(myMechanism1)

# Settings:
sett.random_seed = 123278
sett.temperature = 500.0
sett.pressure = 10
sett.KMCEngine.name = 'ZacRos'
sett.KMCEngine.path = '/home/aguirre/bin/'
sett.KMCOutput.path = '/home/aguirre/Develop/pyZacros/examples/CO_tutorial/output'
sett.AbinitioEngine.name = 'AMS'
sett.AbinitioEngine.path = 'Programs'
sett.snapshots = ('time', 5.e-4)
sett.process_statistics = ('time', 5.e-4)
sett.species_numbers = ('time', 5.e-4)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 250.0
sett.wall_time = 30
myJob = KMCJob(settings=sett, lattice=myLattice, mechanism=myMechanism1)
#print(myJob)
myJob.run()
##
