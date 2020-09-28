"""
This example reproduces the Zacros example described in:
https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros
"""

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
CO_gas = Species("CO")
O2_gas = Species("O2")
CO2_gas = Species("CO2", gas_energy=-2.337)

# -) Adsorbed species:
CO_ads = Species("CO*", 1)
O_ads = Species("O*", 1)

# Lattice:
myLattice = Lattice(lattice_type="default_choice",
                    default_lattice=["rectangular_periodic", 1.0, 50, 50])

# CO_adsorption:
myCluster1 = Cluster(site_types=["1"],
                     species=[s0],
                     gas_species=[CO_gas])

myCluster2 = Cluster(site_types=["1"],
                     species=[CO_ads],
                     cluster_energy=-1.3)

CO_adsorption = ElementaryReaction(site_types=["1"],
                                   initial=myCluster1,
                                   final=myCluster2,
                                   reversible=False,
                                   pre_expon=10.0,
                                   activation_energy=0.0)

# O2_adsorption:
myCluster5 = Cluster(site_types=["1", "1"],
                     species=[s0,s0],
                     gas_species=[O2_gas])

myCluster6 = Cluster(site_types=["1", "1"],
                     species=[O_ads,O_ads],
                     cluster_energy=-1)  # Fake energy

O2_adsorption = ElementaryReaction(site_types=["1", "1"],
                                    initial=myCluster5,
                                    final=myCluster6,
                                    reversible=False,
                                    pre_expon=2.5,
                                    activation_energy=0.0)

# CO_oxidation:
myCluster15 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[CO_ads, O_ads],
                      cluster_energy=-1.0) # Fake energy

myCluster16 = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[s0, s0],
                      gas_species=[CO2_gas],
                      cluster_energy=-1.0) # Fake energy

CO_oxidation = ElementaryReaction(site_types=["1", "1"],
                                  initial=myCluster15,
                                  final=myCluster16,
                                  neighboring=[(1, 2)],
                                  reversible=False,
                                  pre_expon=1.0e+20,
                                  activation_energy=0.0)

## Extra:
#myCluster17 = Cluster(site_types=["1", "1"],
                      #species=[CO_adsorbed, CO_adsorbed],
                      #cluster_energy=0.560)
#myCluster18 = Cluster(site_types=["1"],
                      #species=[COOH_adsorbed],
                      #cluster_energy=-1.487)


# Build-up mechanism:
myMechanism1 = Mechanism()
myMechanism1.append(CO_adsorption)
myMechanism1.append(O2_adsorption)
myMechanism1.append(CO_oxidation)

# Settings:
sett = KMCSettings()
sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.KMCEngine.name = 'ZacRos'
sett.KMCEngine.path = '/home/aguirre/bin/'
sett.KMCOutput.path = '/home/aguirre/Develop/pyZacros/examples/ZiffGulariBarshad/output'
sett.snapshots = ('time', 5.e-1)
sett.process_statistics = ('time', 1.e-2)
sett.species_numbers = ('time', 1.e-2)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 25.0
sett.wall_time = 3600
myJob = KMCJob(settings=sett, lattice=myLattice, mechanism=myMechanism1)
#print(myJob)
myJob.run()
##
