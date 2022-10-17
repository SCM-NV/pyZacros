import os

import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.models
import scm.pyzacros.utils


def test_post_process():
    print( "---------------------------------------------------" )
    print( ">>> Testing Zacros post_process methods" )
    print( "---------------------------------------------------" )

    zgb = pz.models.ZiffGulariBarshad( repeat_cell=[20,20] )

    scm.plams.init( folder='test_post_process' )

    # Settings:
    sett = pz.Settings()
    sett.molar_fraction.CO = 0.45
    sett.molar_fraction.O2 = 0.55
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ('time', 0.1)
    sett.process_statistics = ('time', 0.1)
    sett.species_numbers = ('time', 0.1)
    sett.event_report = 'off'
    sett.max_steps = 'infinity'
    sett.max_time = 1.0
    sett.wall_time = 3600

    job = pz.ZacrosJob( settings=sett, lattice=zgb.lattice, mechanism=zgb.mechanism,
                        cluster_expansion=zgb.cluster_expansion )

    #-----------------------
    # Running the job
    #-----------------------
    load_precalculated = False

    try:
        results = job.run()
    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")
        load_precalculated = True

    scm.plams.finish()

    if( load_precalculated ):
        job = pz.ZacrosJob.load_external( path="tests/test_ZacrosResults.data/plamsjob" )
    else:
        job = pz.ZacrosJob.load_external( path='test_post_process/plamsjob' )

    data = job.results.provided_quantities()
    output = str(data)
    print(output)

    expectedOutput = """\
{'Entry': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'Nevents': [0, 346, 614, 888, 1117, 1314, 1535, 1726, 1920, 2056, 2222], 'Time': [0.0, 0.1, 0.2, 0.30000000000000004, 0.4, 0.5, 0.6, 0.7, 0.7999999999999999, 0.8999999999999999, 0.9999999999999999], 'Temperature': [500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0], 'Energy': [0.0, -362.40000000000106, -435.4000000000014, -481.8000000000016, -531.5000000000013, -514.4000000000016, -528.9000000000013, -530.2000000000013, -614.3999999999997, -653.499999999999, -612.0999999999998], 'CO*': [0, 24, 20, 15, 9, 10, 7, 8, 2, 2, 2], 'O*': [0, 144, 178, 201, 226, 218, 226, 226, 266, 283, 265], 'CO': [0, -124, -222, -324, -407, -488, -573, -650, -716, -767, -837], 'O2': [0, -122, -190, -255, -312, -348, -396, -434, -490, -524, -550], 'CO2': [0, 100, 202, 309, 398, 478, 566, 642, 714, 765, 835]}\
"""

    assert( pz.utils.compare( output, expectedOutput, 1e-3 ) )
