import pyzacros as pz
from pyzacros.utils.compareReports import compare

def test_Cluster():
    job = pz.ZacrosJob.load_external( path='tests/test_ZacrosResults.data' )
    data = job.results.provided_quantities()
    output = str(data)

    expectedOutput = """\
{'Entry': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'Nevents': [0, 346, 614, 888, 1117, 1314, 1535, 1726, 1920, 2056, 2222], 'Time': [0.0, 0.1, 0.2, 0.30000000000000004, 0.4, 0.5, 0.6, 0.7, 0.7999999999999999, 0.8999999999999999, 0.9999999999999999], 'Temperature': [500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0], 'Energy': [0.0, -362.40000000000106, -435.4000000000014, -481.8000000000016, -531.5000000000013, -514.4000000000016, -528.9000000000013, -530.2000000000013, -614.3999999999997, -653.499999999999, -612.0999999999998], 'CO*': [0, 24, 20, 15, 9, 10, 7, 8, 2, 2, 2], 'O*': [0, 144, 178, 201, 226, 218, 226, 226, 266, 283, 265], 'CO': [0, -124, -222, -324, -407, -488, -573, -650, -716, -767, -837], 'O2': [0, -122, -190, -255, -312, -348, -396, -434, -490, -524, -550], 'CO2': [0, 100, 202, 309, 398, 478, 566, 642, 714, 765, 835]}\
"""

    assert( compare( output, expectedOutput, 1e-3 ) )