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
s0 = Species("*", 1)      # Empty adsorption site
# -) Gas-species:
CO_gas = Species("CO", molar_fraction=1.0e-5)
H2O_gas = Species("H2O", molar_fraction=0.950)
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


myLattice = Lattice(lattice_type="default_choice",
                    default_lattice=["hexagonal_periodic", 1.0, 8, 10])
print(myLattice)
myCluster1 = Cluster(site_types=("1"),
                     neighboring=[(1, 2)],
                     species=(s0, CO_adsorbed))

#myCluster1 = Cluster(site_types=(1),
#                     neighboring=[(1, 2)],
#                     species=(s0, CO_adsorbed))
#
#myCluster1 = Cluster(site_types=(1),
#                     neighboring=[(1, 2)],
#                     species=(s0, CO_adsorbed))
#myCluster2 = Cluster( site_types=( "fcc", "fcc" ),
#                     neighboring=[ (1,2) ],
#                     species=[ s0, s0 ],
#                     gas_species=[ s3 ],
#                     multiplicity=2,
#                     cluster_energy=0.1 )
#
#myReaction1 = ElementaryReaction(site_types=("f", "f"),
#                                 neighboring=[(1, 2)],
#                                 initial=myCluster1,
#                                 final=myCluster2,
#                                 reversible=False,
#                                 pre_expon=1e+13,
#                                 pe_ratio=0.676,
#                                 activation_energy=0.2)
#
#myMechanism1 = Mechanism()
#myMechanism1.append(myReaction1)
##print(s0.mass())
##print(s1.mass())
##print(s2.mass())
##print(s3.mass())
##print(s1.denticity)
##
myLattice = Lattice(lattice_type="periodic_cell",
                    cell_vectors=[[2.814284989122459,  0.000000000000000],
                                  [1.407142494561229, 2.437242294069262]],
                    repeat_cell=[23, 24],
                    n_cell_sites=2,
                    n_site_types=2,
                    site_type_names=["fcc", "hcp"],
                    site_types=[1, 2],
                    site_coordinates=[[0.333333333333333, 0.333333333333333],
                                      [0.666666666666666, 0.666666666666666]],
                    neighboring_structure=[["1-1", "north"], ["1-1", "east"],
                                           ["1-1", "southeast"],
                                           ["2-1", "self"],
                                           ["2-1", "east"],
                                           ["2-1", "north"],
                                           ["2-2", "north"],
                                           ["2-2", "east"],
                                           ["2-2", "southeast"]])
#myLattice = Lattice(path_to_slab_yaml="./pyzacros/slabs/pd111.yaml")
#
print(myLattice)
#sett = KMCSettings()
#sett.random_seed = 123278 
#sett.temperature = 500.0 
#sett.pressure = 10
#sett.KMCEngine.name = 'ZacRos'
#sett.KMCEngine.path = '/Users/plopez/Programs'
#sett.KMCOutput.path = '/Users/plopez/job/Zacros/CO_tutorial'
#sett.AbinitioEngine.name = 'AMS'
#sett.AbinitioEngine.path = 'Programs'
#sett.snapshots = ('time', 1.e-4)
#sett.process_statistics = ('time', 2.e-4)
#sett.species_numbers = ('time', 3.e-4)
#sett.event_report = 'off'
#sett.max_steps = 'infinity'
#sett.max_time = 250.0
#sett.wall_time = 10
#myJob = KMCJob(settings=sett, lattice=myLattice, mechanism=myMechanism1)
#
#print(myJob)
#myJob.run()
#