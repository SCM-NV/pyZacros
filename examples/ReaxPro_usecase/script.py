"""Test script that will reproduce CO_tutorial inputs."""

from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.KMCJob import KMCJob
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Species import Species
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.utils.setting_utils import *
from pyzacros.utils.io_utils import *
# Instantiate settings:
sett = KMCSettings()

# Species:
s0 = Species("*", 1)      # Empty adsorption site
#
# - Gas-species:
O2_gas = Species("O2", gas_energy=0.0)
sett.molar_fraction.O2 = 0.50
CO_gas = Species("CO")
sett.molar_fraction.CO = 0.50
CO2_gas = Species("CO2")
CO2_gas = Species("CO2", gas_energy=-3.22)

## - Adsorbed species:
O_adsorbed = Species("O*", 1)
CO_adsorbed = Species("CO*", 1)
CO2_adsorbed = Species("CO2*", 2)
# O2_adsorption:
O2_adsorption = ElementaryReaction(site_types=["brg", "brg"],
                                   initial=[s0, s0, O2_gas],
                                   final=[O_adsorbed, O_adsorbed],
                                   neighboring=[(1, 2)],
                                   reversible=True,
                                   pre_expon=7.980e+07,
                                   pe_ratio=9.431e-09,
                                   activation_energy=0.0)

# CO_adsoprtion:
CO_adsorption = ElementaryReaction(site_types=["brg"],
                                   initial=[CO_gas, s0],
                                   final=[CO_adsorbed],
                                   reversible=True,
                                   pre_expon=4.265e+07,
                                   pe_ratio=6.563e-09,
                                   activation_energy=0.0)

# CO_oxidation:
CO_oxidation = ElementaryReaction(site_types=["brg", "brg"],
                                  initial=[CO_adsorbed, O_adsorbed],
                                  final=[s0, s0, CO2_gas],
                                  neighboring=[(1, 2)],
                                  reversible=True,
                                  pre_expon=2.786e+12,
                                  pe_ratio=3.231e+07,
                                  activation_energy=0.52)

myMechanism = [O2_adsorption, CO_adsorption, CO_oxidation]
#
# Settings:
sett.random_seed = 8949321
sett.temperature = 900.0
sett.pressure = 1.00
sett.KMCEngine.name = 'ZacRos'
sett.KMCEngine.path = '/Users/plopez/Programs'
sett.KMCOutput.path = '/Users/plopez/job/Zacros/example/ReaxPro_user_case'
sett.AbinitioEngine.name = 'AMS'
sett.AbinitioEngine.path = 'Programs'
sett.snapshots = ('time', 5.e-4)
sett.process_statistics = ('time', 5.e-4)
sett.species_numbers = ('time', 5.e-4)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 200.0
sett.wall_time = 30

myJob = KMCJob(settings=sett,
               mechanism=myMechanism, additional_species=[CO2_adsorbed])
myJob.run()
