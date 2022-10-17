import scm.pyzacros as pz
import scm.pyzacros.utils


def test_SpeciesList():
    print( "---------------------------------------------------" )
    print( ">>> Testing SpeciesList class" )
    print( "---------------------------------------------------" )

    # Adsorbed species
    asp1 = pz.Species( "H2*", denticity=1 )
    asp2 = pz.Species( "O2*", denticity=1 )
    fas = pz.Species( "*" ) # Free adsorption site

    # Gas species
    gs1 = pz.Species( "H2", gas_energy=0.0 )
    gs2 = pz.Species( "O2", gas_energy=0.0 )

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
    assert( pz.utils.compare( output, expectedOutput, 1e-3 ) )
