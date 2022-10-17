import numpy

import scm.pyzacros as pz
import scm.pyzacros.utils

def test_Parameters():
    print( "---------------------------------------------------" )
    print( ">>> Testing Parameters class" )
    print( "---------------------------------------------------" )

    output = ""

    params = pz.ZacrosParametersScanJob.Parameters()
    params.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.0, 1.0, 0.25) )
    params.add( 'x_O2', 'molar_fraction.O2', lambda p: 1.0-p['x_CO'] )
    params.set_generator( pz.ZacrosParametersScanJob.zipGenerator )

    output += "zipGenerator:\n"
    output += str(params)
    output += "\n"

    params = pz.ZacrosParametersScanJob.Parameters()
    params.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.0, 1.0, 0.4) )
    params.add( 'x_O2', 'molar_fraction.O2', numpy.arange(0.0, 1.0, 0.4) )
    params.add( 'x_N2', 'molar_fraction.N2', lambda p: 0.11+p['x_CO']+p['x_O2'] )
    params.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )

    output += "meshgridGenerator:\n"
    output += str(params)

    print(output)

    expectedOutput = """\
zipGenerator:
0: {'x_CO': 0.0, 'x_O2': 1.0}
1: {'x_CO': 0.25, 'x_O2': 0.75}
2: {'x_CO': 0.5, 'x_O2': 0.5}
3: {'x_CO': 0.75, 'x_O2': 0.25}

meshgridGenerator:
(0, 0): {'x_CO': 0.0, 'x_O2': 0.0, 'x_N2': 0.11}
(0, 1): {'x_CO': 0.4, 'x_O2': 0.0, 'x_N2': 0.51}
(0, 2): {'x_CO': 0.8, 'x_O2': 0.0, 'x_N2': 0.91}
(1, 0): {'x_CO': 0.0, 'x_O2': 0.4, 'x_N2': 0.51}
(1, 1): {'x_CO': 0.4, 'x_O2': 0.4, 'x_N2': 0.91}
(1, 2): {'x_CO': 0.8, 'x_O2': 0.4, 'x_N2': 1.31}
(2, 0): {'x_CO': 0.0, 'x_O2': 0.8, 'x_N2': 0.91}
(2, 1): {'x_CO': 0.4, 'x_O2': 0.8, 'x_N2': 1.31}
(2, 2): {'x_CO': 0.8, 'x_O2': 0.8, 'x_N2': 1.71}\
"""
    assert( pz.utils.compare( output, expectedOutput, 1e-3 ) )
