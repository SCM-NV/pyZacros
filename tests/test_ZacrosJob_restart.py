import os

import scm.plams

import pyzacros as pz
import pyzacros.models
import pyzacros.utils


def test_ZacrosJob_restart():
    print( "---------------------------------------------------" )
    print( ">>> Testing ZacrosJob_restart mechanism" )
    print( "---------------------------------------------------" )

    zgb = pz.models.ZiffGulariBarshad( repeat_cell=[20,20] )

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init(folder='test_ZacrosJob_restart')

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
    sett.max_steps = 'infinity'

    #---------------------------------------------
    # Running the calculations
    #---------------------------------------------
    output = ""

    # Running the full simulation for 2s
    sett.max_steps = 3225
    job0 = pz.ZacrosJob( settings=sett,
                         lattice=zgb.lattice,
                         mechanism=zgb.mechanism,
                         cluster_expansion=zgb.cluster_expansion )

    try:
        job0.run()

        if( not job0.ok() ):
            raise scm.plams.JobError("Error: The Zacros calculation FAILED!")

    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         So let's skip this test." )
        return

    data = job0.results.provided_quantities()
    for time,nCO2 in zip(data['Time'],data['CO2']):
        output += "%5.1f"%time + "%8d"%nCO2 + "\n"
    output += "--"+"\n"

    # Running the only the first 1s
    sett.max_steps = 2222
    job1 = pz.ZacrosJob( settings=sett,
                         lattice=zgb.lattice,
                         mechanism=zgb.mechanism,
                         cluster_expansion=zgb.cluster_expansion )

    job1.run()
    data = job1.results.provided_quantities()
    for time,nCO2 in zip(data['Time'],data['CO2']):
        output += "%5.1f"%time + "%8d"%nCO2 + "\n"
    output += "--"+"\n"

    # Resuming the simulation, starting at 1s and finishing at 2s
    sett.restart.max_steps = 3225
    job2 = pz.ZacrosJob( settings=sett,
                         lattice=zgb.lattice,
                         mechanism=zgb.mechanism,
                         cluster_expansion=zgb.cluster_expansion,
                         restart=job1 )

    job2.run()
    data = job2.results.provided_quantities()
    for time,nCO2 in zip(data['Time'],data['CO2']):
        output += "%5.1f"%time + "%8d"%nCO2 + "\n"

    print( output )

    expectedOutput = """\
  0.0       0
  0.1     100
  0.2     202
  0.3     309
  0.4     398
  0.5     478
  0.6     566
  0.7     642
  0.8     714
  0.9     765
  1.0     835
  1.1     898
  1.2     956
  1.3    1005
  1.4    1047
  1.5    1089
  1.6    1124
  1.7    1167
  1.8    1199
--
  0.0       0
  0.1     100
  0.2     202
  0.3     309
  0.4     398
  0.5     478
  0.6     566
  0.7     642
  0.8     714
  0.9     765
--
  0.0       0
  0.1     100
  0.2     202
  0.3     309
  0.4     398
  0.5     478
  0.6     566
  0.7     642
  0.8     714
  0.9     765
  1.0     835
  1.1     898
  1.2     956
  1.3    1005
  1.4    1047
  1.5    1089
  1.6    1124
  1.7    1167
  1.8    1199\
"""

    assert( pz.utils.compare( output, expectedOutput, 1e-3 ) )

    lattice_states0 = job0.results.lattice_states()
    lattice_states2 = job2.results.lattice_states()

    assert len(lattice_states0) == len(lattice_states2)

    n = len(lattice_states0)

    job0.results.plot_lattice_states( lattice_states0[n-1], pause=2, close=True )
    job2.results.plot_lattice_states( lattice_states2[n-1], pause=2, close=True )

    process_statistics0 = job0.results.get_process_statistics()
    process_statistics1 = job1.results.get_process_statistics()
    process_statistics2 = job2.results.get_process_statistics()

    assert len(process_statistics0) == len(process_statistics2)

    job0.results.plot_process_statistics( process_statistics0[n-1], key="occurence_frequency", log_scale=True, pause=2, close=True )
    job2.results.plot_process_statistics( process_statistics2[n-1], key="occurence_frequency", log_scale=True, pause=2, close=True )

    scm.plams.finish()
