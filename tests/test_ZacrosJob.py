import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.utils


def test_ZacrosJob(test_folder, tmp_path):
    print("---------------------------------------------------")
    print(">>> Testing ZacrosJob class")
    print("---------------------------------------------------")

    s0 = pz.Species("*", 1)  # Empty adsorption site
    H_ads = pz.Species("H*", 1)  # H adsorbed with dentation 1
    H2_ads = pz.Species("H2*", 1)  # H2 adsorbed with dentation 1
    H2_gas = pz.Species("H2", gas_energy=0.0)  # H2(gas)

    myLattice = pz.Lattice(lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0, repeat_cell=[8, 10])

    myCluster1 = pz.Cluster(neighboring=[(0, 1)], species=[H_ads, H_ads], multiplicity=2, energy=0.1)

    myCluster2 = pz.Cluster(neighboring=[(0, 1)], species=[H2_ads, s0], multiplicity=2, energy=0.1)

    myCluster3 = pz.Cluster(neighboring=[(0, 1)], species=[s0, s0], multiplicity=2, energy=0.1)

    myClusterExpansion = pz.ClusterExpansion([myCluster1, myCluster2, myCluster3])

    reaction1 = pz.ElementaryReaction(
        neighboring=[(0, 1)],
        initial=[H_ads, H_ads],
        final=[H2_ads, s0],
        pre_expon=2.5,
        pe_ratio=1.0,
        activation_energy=0.2,
    )

    reaction2 = pz.ElementaryReaction(
        neighboring=[(0, 1)],
        initial=[H2_ads, s0],
        final=[s0, s0, H2_gas],
        pre_expon=10.0,
        pe_ratio=0.7,
        activation_energy=0.2,
    )

    myMechanism = pz.Mechanism()
    myMechanism.append(reaction1)
    myMechanism.append(reaction2)

    scm.plams.init(folder=str(tmp_path / "test_ZacrosJob"))

    sett = pz.Settings()
    sett.random_seed = 10
    sett.temperature = 380.0
    sett.pressure = 2.00
    sett.max_steps = 1
    sett.molar_fraction.H2 = 1.0

    myJob = pz.ZacrosJob(myLattice, myMechanism, myClusterExpansion, settings=sett)
    print(myJob)
    output = str(myJob)
    with open(test_folder / "test_ZacrosJob_expected_input.txt", "r") as inp:
        expectedOutput = inp.read()
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    myJob.run()

    if not myJob.ok():
        error_msg = myJob.get_errormsg()
        if "ZacrosExecutableNotFoundError" in error_msg:
            print("Warning: The calculation FAILED because the zacros executable is not available!")
            print("         For testing purposes, we just omit this step.")
        else:
            raise scm.plams.JobError(f"Error: The Zacros calculation FAILED! Error was: {error_msg}")

    myJob = pz.ZacrosJob.load_external(path=test_folder / "test_ZacrosJob.idata/default")
    print(myJob)
    output = str(myJob)
    with open(test_folder / "test_ZacrosJob_expected_input_default.txt", "r") as inp:
        expectedOutput = inp.read()
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    myJob = pz.ZacrosJob.load_external(path=test_folder / "test_ZacrosJob.idata/periodic_cell")
    print(myJob)
    output = str(myJob)
    with open(test_folder / "test_ZacrosJob_expected_input_periodic_cell.txt", "r") as inp:
        expectedOutput = inp.read()
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    myJob = pz.ZacrosJob.load_external(path=test_folder / "test_ZacrosJob.idata/explicit")
    print(myJob)
    output = str(myJob)
    with open(test_folder / "test_ZacrosJob_expected_input_explicit.txt", "r") as inp:
        expectedOutput = inp.read()
    assert pz.utils.compare(output, expectedOutput, 1e-3)

    scm.plams.finish()
