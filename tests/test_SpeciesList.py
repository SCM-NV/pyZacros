import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_SpeciesList():
    """Test of the SpeciesList class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing SpeciesList class" )
    print( "---------------------------------------------------" )

    # Adsorbed specie
    asp1 = pz.Species( "H2*", denticity=1 )
    asp2 = pz.Species( "O2*", denticity=1 )

    # Gas specie
    gs1 = pz.Species( "H2", gas_energy=0.0 )

    # Gas specie
    gs2 = pz.Species( "O2", gas_energy=0.0 )

    # Free adsorption site
    fas = pz.Species( "*" )

    #mySpeciesList = pz.SpeciesList()
    #mySpeciesList.append( asp1 )
    #mySpeciesList.append( asp2 )
    #mySpeciesList.append( gs1 )
    #mySpeciesList.append( gs2 )
    #mySpeciesList.append( fas )

    mySpeciesList = pz.SpeciesList( [asp1, asp2, gs1, gs2, fas] )

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
    assert( compare( output, expectedOutput, 1e-3 ) )
