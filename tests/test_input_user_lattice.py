"""Test script that will reproduce CO_tutorial inputs."""

from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.KMCJob import KMCJob
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.Species import Species
from pyzacros.classes.ElementaryReaction import ElementaryReaction


def pyzacros_example():
    """Creeate pyZacros input files using a default Lattice."""
    # Instantiate settings:
    sett = KMCSettings()

    # Species:
    s0 = Species("*", 1)      # Empty adsorption site

    # - Gas-species:
    CO_gas = Species("CO")
    sett.molar_fraction.CO = 1.e-5
    H2O_gas = Species("H2O")
    sett.molar_fraction.H2O = 0.950  # molar fractions now via settings.
    H2_gas = Species("H2")
    CO2_gas = Species("CO2", gas_energy=-0.615)
    O2_gas = Species("O2", gas_energy=4.913)

    # - Adsorbed species:
    CO_adsorbed = Species("CO*", 1)
    H2O_adsorbed = Species("H2O*", 1)
    OH_adsorbed = Species("OH*", 1)
    O_adsorbed = Species("O*", 1)
    H_adsorbed = Species("H*", 1)
    COOH_adsorbed = Species("COOH*", 1)

    # Lattice:

    myLattice = Lattice(lattice_type="periodic_cell",
                        cell_vectors=[[2.814284989122459,  0.000000000000000],
                                      [1.407142494561229, 2.437242294069262]],
                        repeat_cell=[23, 24],
                        n_cell_sites=2,
                        n_site_types=2,
                        site_type_names=["fcc", "hcp"],
                        site_types=[1, 2],
                        site_coordinates=[[0.333333333333333,
                                          0.333333333333333],
                                          [0.666666666666666,
                                           0.666666666666666]],
                        neighboring_structure=[["1-1", "north"],
                                               ["1-1", "east"],
                                               ["1-1", "southeast"],
                                               ["2-1", "self"],
                                               ["2-1", "east"],
                                               ["2-1", "north"],
                                               ["2-2", "north"],
                                               ["2-2", "east"],
                                               ["2-2", "southeast"]])

    # Cluster expansions:
    #
    CO_point = Cluster(site_types=["1"],
                       species=[CO_adsorbed],
                       cluster_energy=-2.077)

    H2O_point = Cluster(site_types=["1"],
                        species=[H2O_adsorbed],
                        cluster_energy=-0.362)

    OH_point = Cluster(site_types=["1"],
                       species=[OH_adsorbed],
                       cluster_energy=0.830)

    O_point = Cluster(site_types=["1"],
                      species=[O_adsorbed],
                      cluster_energy=1.298)

    H_point = Cluster(site_types=["1"],
                      species=[H_adsorbed],
                      cluster_energy=-0.619)

    COOH_point = Cluster(site_types=["1"],
                         species=[COOH_adsorbed],
                         cluster_energy=-1.487)

    CO_pair_1NN = Cluster(site_types=["1", "1"],
                          neighboring=[(1, 2)],
                          species=[CO_adsorbed, CO_adsorbed],
                          cluster_energy=0.560)

    OH_H_1NN = Cluster(site_types=["1", "1"],
                       neighboring=[(1, 2)],
                       species=[OH_adsorbed, H_adsorbed],
                       cluster_energy=0.021)

    O_H_1NN = Cluster(site_types=["1", "1"],
                      neighboring=[(1, 2)],
                      species=[O_adsorbed, H_adsorbed],
                      cluster_energy=0.198)

    CO_OH_1NN = Cluster(site_types=["1", "1"],
                        neighboring=[(1, 2)],
                        species=[CO_adsorbed, OH_adsorbed],
                        cluster_energy=0.066)

    CO_O_1NN = Cluster(site_types=["1", "1"],
                       neighboring=[(1, 2)],
                       species=[CO_adsorbed, O_adsorbed],
                       cluster_energy=0.423)
    # CO_adsoprtion:
    CO_adsorption = ElementaryReaction(site_types=["1"],
                                       initial=[CO_gas, s0],
                                       final=[CO_adsorbed],
                                       reversible=True,
                                       pre_expon=2.226e+007,
                                       pe_ratio=2.137e-006,
                                       activation_energy=0.0)

    # H2_dissoc_adsorp:
    H2_dissoc_adsorp = ElementaryReaction(site_types=["1", "1"],
                                          initial=[s0, s0, H2_gas],
                                          final=[H_adsorbed, H_adsorbed],
                                          neighboring=[(1, 2)],
                                          reversible=True,
                                          pre_expon=8.299e+007,
                                          pe_ratio=7.966e-006,
                                          activation_energy=0.0)
    # H2O_adsoroption:
    H2O_adsorption = ElementaryReaction(site_types=["1"],
                                        initial=[s0, H2O_gas],
                                        final=[H2O_adsorbed],
                                        reversible=True,
                                        pre_expon=2.776e+002,
                                        pe_ratio=2.665e-006,
                                        activation_energy=0.0)

    # H2O_dissociation:
    H2O_dissoc_adsorp = ElementaryReaction(site_types=["1", "1"],
                                           initial=[H2O_adsorbed, s0],
                                           final=[OH_adsorbed, H_adsorbed],
                                           neighboring=[(1, 2)],
                                           reversible=True,
                                           pre_expon=1.042e+13,
                                           pe_ratio=1.000e+00,
                                           activation_energy=0.777)

    # OH_decomposition:
    OH_decomposition = ElementaryReaction(site_types=["1", "1"],
                                          initial=[s0, OH_adsorbed],
                                          final=[O_adsorbed, H_adsorbed],
                                          neighboring=[(1, 2)],
                                          reversible=True,
                                          pre_expon=1.042e+13,
                                          pe_ratio=1.000e+00,
                                          activation_energy=0.940)

    # COOH_formation:
    COOH_formation = ElementaryReaction(site_types=["1", "1"],
                                        initial=[CO_adsorbed, OH_adsorbed],
                                        final=[s0, COOH_adsorbed],
                                        neighboring=[(1, 2)],
                                        reversible=True,
                                        pre_expon=1.042e+13,
                                        pe_ratio=1.000e+00,
                                        activation_energy=0.405)

    # COOH_decomposition:
    COOH_decomposition = ElementaryReaction(site_types=["1", "1"],
                                            initial=[COOH_adsorbed, s0],
                                            final=[s0, H_adsorbed, CO2_gas],
                                            neighboring=[(1, 2)],
                                            reversible=False,
                                            pre_expon=1.042e+13,
                                            activation_energy=0.852)

    # CO_oxidation:
    CO_oxidation = ElementaryReaction(site_types=["1", "1"],
                                      initial=[CO_adsorbed, O_adsorbed],
                                      final=[s0, s0, CO2_gas],
                                      neighboring=[(1, 2)],
                                      reversible=False,
                                      pre_expon=1.042e+13,
                                      activation_energy=0.988)

    # Build-up mechanism:

    myMechanism = [CO_adsorption, H2_dissoc_adsorp, H2O_adsorption,
                   H2O_dissoc_adsorp, OH_decomposition, COOH_formation,
                   COOH_decomposition, CO_oxidation]
    #
    # Settings:
    sett.random_seed = 123278
    sett.temperature = 500.0
    sett.pressure = 10
    sett.KMCEngine.name = 'ZacRos'
    #sett.KMCEngine.path = '/Users/plopez/Programs'
    sett.KMCOutput.path = './tests'
    sett.AbinitioEngine.name = 'AMS'
    sett.AbinitioEngine.path = 'Programs'
    sett.snapshots = ('time', 5.e-4)
    sett.process_statistics = ('time', 5.e-4)
    sett.species_numbers = ('time', 5.e-4)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 250.0
    sett.wall_time = 30

    myClusters = [CO_point, H2O_point]
    myClusters.append(OH_point)
    myClusters = [CO_point, H2O_point]
    myClusters.append(OH_point)
    myClusters.extend((O_point, H_point, COOH_point))
    myClusters.extend((CO_pair_1NN, OH_H_1NN, O_H_1NN, CO_OH_1NN, CO_O_1NN))

    myJob = KMCJob(settings=sett,
                   lattice=myLattice,
                   mechanism=myMechanism,
                   cluster_expansions=myClusters)
    return


def test_pyzacros_example():
    """Assert input files."""
    pyzacros_example()
    list_of_files = ["energetics_input.dat",
                     "lattice_input.dat",
                     "mechanism_input.dat",
                     "simulation_input.dat"]
    for ij in list_of_files:
        f = open("tests/"+ij, "r")
        f_original = open("tests/original_inputs/user_lattice/"+ij, "r")
        assert (f.read() == f_original.read())
    return
