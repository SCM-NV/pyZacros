import scm.pyzacros as pz
import scm.pyzacros.utils


def test_SpeciesList():
    print("---------------------------------------------------")
    print(">>> Testing SpeciesList class")
    print("---------------------------------------------------")

    # Adsorbed species
    H2_d1 = pz.Species("H2*", denticity=1)
    O2_d1 = pz.Species("O2*", denticity=1)
    fas = pz.Species("*")  # Free adsorption site

    # Gas species
    H2_g = pz.Species("H2", gas_energy=0.0)
    O2_g = pz.Species("O2", gas_energy=0.0)

    mySpeciesList = pz.SpeciesList()
    mySpeciesList.append(H2_d1)
    mySpeciesList.append(O2_d1)
    mySpeciesList.append(H2_g)
    mySpeciesList.append(O2_g)
    mySpeciesList.append(fas)

    print(mySpeciesList)

    output = str(mySpeciesList)
    expectedOutput = """\
n_gas_species 2
gas_specs_names           H2        O2
gas_energies             0.0       0.0
gas_molec_weights     2.0156   31.9898
n_surf_species 2
surf_specs_names         H2*       O2*
surf_specs_dent            1         1\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)
    assert (
        mySpeciesList.mass()
        == 2 * pz.Species._ATOMIC_MASS["H"]
        + 2 * pz.Species._ATOMIC_MASS["O"]
        + 2 * pz.Species._ATOMIC_MASS["H"]
        + 2 * pz.Species._ATOMIC_MASS["O"]
    )

    H2_d2 = pz.Species("H2**")
    mySpeciesList = pz.SpeciesList([H2_d2, O2_d1, H2_d2, H2_g, O2_g, fas])

    print(mySpeciesList)

    output = str(mySpeciesList)
    expectedOutput = """\
n_gas_species 2
gas_specs_names           H2        O2
gas_energies             0.0       0.0
gas_molec_weights     2.0156   31.9898
n_surf_species 3
surf_specs_names         H2**       O2*       H2**
surf_specs_dent             2         1        2\
"""
    assert pz.utils.compare(output, expectedOutput, 1e-3)
    assert (
        mySpeciesList.mass(entity_numbers=[0, 1, 0, 2])
        == 2 * pz.Species._ATOMIC_MASS["H"]
        + 2 * pz.Species._ATOMIC_MASS["O"]
        + 2 * pz.Species._ATOMIC_MASS["H"]
        + 2 * pz.Species._ATOMIC_MASS["O"]
    )
