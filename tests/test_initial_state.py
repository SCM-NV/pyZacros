"""Script to test the InitialState class."""
from pyzacros.classes.Species import Species
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.KMCJob import KMCJob
from pyzacros.classes.InitialState import InitialState
import random


def pyzacros_example():
    """Dummy example to test the InitialState class."""
    # Instantiate settings:
    sett = KMCSettings()

    s0 = Species("*", 1)            # Empty adsorption site
    H2_gas = Species("H2")          # H2 gas.
    sett.molar_fraction.H2 = 1.00
    H2_adsorbed = Species("H2*", 1)  # H2 adsorbed with dentation 1
    H_adsorbed = Species("H*", 1)    # H adsorbed with dentation 1

    H_H_1NN = Cluster(site_types=("fcc", "fcc"),
                      neighboring=[(1, 2)],
                      species=[H_adsorbed, H_adsorbed],
                      multiplicity=2,
                      cluster_energy=0.1)

    H_H2_1NN = Cluster(site_types=("fcc", "fcc"),
                       neighboring=[(1, 2)],
                       species=[H_adsorbed, H2_adsorbed],
                       multiplicity=2,
                       cluster_energy=0.1)

    # H2_dissoc_adsorp:
    H2_dissoc_adsorp = ElementaryReaction(site_types=["1", "1"],
                                          initial=[s0, s0, H2_gas],
                                          final=[H_adsorbed, H_adsorbed],
                                          neighboring=[(1, 2)],
                                          reversible=True,
                                          pre_expon=8.299e+007,
                                          pe_ratio=7.966e-006,
                                          activation_energy=0.0)

    H2_formation = ElementaryReaction(site_types=("1", "1"),
                                      neighboring=[(1, 2)],
                                      initial=[H_adsorbed, H_adsorbed],
                                      final=[H2_adsorbed, s0],
                                      reversible=True,
                                      pre_expon=1e+13,
                                      pe_ratio=0.676,
                                      activation_energy=-1.2)
    #
    myLattice = Lattice(lattice_type="periodic_cell",
                        cell_vectors=[[2.814, 0.000], [1.407, 2.437]],
                        repeat_cell=[3, 3],
                        n_cell_sites=2,
                        n_site_types=2,
                        site_type_names=["fcc", "hcp"],
                        site_types=["fcc", "hcp"],
                        site_coordinates=[[0.33333, 0.33333],
                                          [0.66667, 0.66667]],
                        neighboring_structure=[["1-1", "north"],
                                               ["1-1", "east"],
                                               ["1-1", "southeast"],
                                               ["2-1", "self"],
                                               ["2-1", "east"],
                                               ["2-1", "north"],
                                               ["2-2", "north"],
                                               ["2-2", "east"],
                                               ["2-2", "southeast"]])

    myInitialState = InitialState(myLattice, [H2_dissoc_adsorp, H2_formation])
    random.seed(10)

    myInitialState.fillSites(site_name="fcc",
                             species=H_adsorbed, coverage=0.5)
    myInitialState.fillSites(site_name="fcc",
                             species=H2_adsorbed, coverage=0.5)
    myInitialState.fillSites(site_name="hcp",
                             species=H_adsorbed, coverage=1.0)

    # Settings:
    sett.random_seed = 123278
    sett.temperature = 500.0
    sett.pressure = 10
    sett.KMCEngine.name = 'ZacRos'
    sett.KMCEngine.path = './'
    sett.KMCOutput.path = './tests'
    sett.snapshots = ('time', 5.e-4)
    sett.process_statistics = ('time', 5.e-4)
    sett.species_numbers = ('time', 5.e-4)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 250.0
    sett.wall_time = 30

    myLattice = Lattice(lattice_type="default_choice",
                        default_lattice=["hexagonal_periodic", 1.0, 8, 10])

    myJob = KMCJob(settings=sett,
                   lattice=myLattice,
                   mechanism=[H2_dissoc_adsorp, H2_formation],
                   cluster_expansions=[H_H_1NN, H_H_1NN],
                   initialState=myInitialState)
    return


def test_pyzacros_example():
    """Assert input files."""
    pyzacros_example()
    list_of_files = ["energetics_input.dat",
                     "lattice_input.dat",
                     "mechanism_input.dat",
                     "state_input.dat",
                     "simulation_input.dat"]
    for ij in list_of_files:
        f = open("tests/"+ij, "r")
        f_original = open("tests/original_inputs/initial_state/"+ij, "r")
        assert (f.read() == f_original.read())
    return
