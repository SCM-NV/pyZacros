import os

import scm.plams
import pyzacros as pz
from pyzacros.utils.compareReports import compare


def test_ZacrosJob_restart():
    """Test of the ZacrosJob restart mechanism."""
    print( "---------------------------------------------------" )
    print( ">>> Testing ZacrosJob_restart mechanism" )
    print( "---------------------------------------------------" )

    #---------------------------------------------
    # Species:
    #---------------------------------------------
    # Gas-species:
    CO_gas = pz.Species("CO")
    O2_gas = pz.Species("O2")
    CO2_gas = pz.Species("CO2", gas_energy=-2.337)

    # Surface species:
    s0 = pz.Species("*", 1)      # Empty adsorption site
    CO_ads = pz.Species("CO*", 1)
    O_ads = pz.Species("O*", 1)

    #---------------------------------------------
    # Lattice setup:
    #---------------------------------------------
    lattice = pz.Lattice( lattice_type=pz.Lattice.RECTANGULAR, lattice_constant=1.0, repeat_cell=[20,20] )

    #---------------------------------------------
    # Clusters:
    #---------------------------------------------
    CO_point = pz.Cluster(species=[CO_ads], cluster_energy=-1.3)
    O_point = pz.Cluster(species=[O_ads], cluster_energy=-2.3)

    cluster_expansion = [CO_point, O_point]

    #---------------------------------------------
    # Elementary Reactions
    #---------------------------------------------
    # CO_adsorption:
    CO_adsorption = pz.ElementaryReaction( initial=[s0,CO_gas],
                                           final=[CO_ads],
                                           reversible=False,
                                           pre_expon=10.0,
                                           label="CO_adsorption")

    # O2_adsorption:
    O2_adsorption = pz.ElementaryReaction( initial=[s0,s0,O2_gas],
                                           final=[O_ads,O_ads],
                                           neighboring=[(0, 1)],
                                           reversible=False,
                                           pre_expon=2.5,
                                           label="O2_adsorption")

    # CO_oxidation:
    CO_oxidation = pz.ElementaryReaction( initial=[CO_ads, O_ads],
                                          final=[s0, s0, CO2_gas],
                                          neighboring=[(0, 1)],
                                          reversible=False,
                                          pre_expon=1.0e+20,
                                          label="CO_oxidation")

    mechanism = [CO_adsorption, O2_adsorption, CO_oxidation]

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init()

    # Settings:
    sett = pz.Settings()
    sett.molar_fraction.CO = 0.45
    sett.molar_fraction.O2 = 0.55
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ('time', 0.5)
    sett.process_statistics = ('time', 0.1)
    sett.species_numbers = ('time', 0.1)
    sett.max_steps = 'infinity'

    #---------------------------------------------
    # Running the calculations
    #---------------------------------------------
    output = ""

    # Running the full simulation for 2s
    sett.max_time = 2.0
    job0 = pz.ZacrosJob( settings=sett,
                        lattice=lattice,
                        mechanism=mechanism,
                        cluster_expansion=cluster_expansion )

    job0.run()

    if( not job0.ok() and "AMSBIN" not in os.environ ):
        print( "Warning: Zacros is not available! So let's skip this test." )
        return

    data = job0.results.provided_quantities()
    for time,nCO2 in zip(data['Time'],data['CO2']):
        output += "%5.1f"%time + "%8d"%nCO2 + "\n"
    output += "--"+"\n"

    # Running the only the first 1s
    sett.max_time = 1.0
    job1 = pz.ZacrosJob( settings=sett,
                        lattice=lattice,
                        mechanism=mechanism,
                        cluster_expansion=cluster_expansion )

    job1.run()
    data = job1.results.provided_quantities()
    for time,nCO2 in zip(data['Time'],data['CO2']):
        output += "%5.1f"%time + "%8d"%nCO2 + "\n"
    output += "--"+"\n"

    # Resuming the simulation, starting at 1s and finishing at 2s
    sett.restart.max_time = 2.0
    job2 = pz.ZacrosJob( settings=sett,
                        lattice=lattice,
                        mechanism=mechanism,
                        cluster_expansion=cluster_expansion,
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
  1.9    1224
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
  1.8    1199
  1.9    1224\
"""

    assert( compare( output, expectedOutput, 1e-3 ) )

    lattice_states0 = job0.results.lattice_states()
    lattice_states2 = job2.results.lattice_states()

    assert len(lattice_states0) == len(lattice_states2)

    job0.results.plot_lattice_states( pause=2, close=True )
    job2.results.plot_lattice_states( pause=2, close=True )

    process_statistics0 = job0.results.get_process_statistics()
    process_statistics1 = job1.results.get_process_statistics()
    process_statistics2 = job2.results.get_process_statistics()

    assert len(process_statistics0) == len(process_statistics2)

    job0.results.plot_process_statistics( process_statistics0[19], key="occurence_frequency", log_scale=True, pause=2, close=True )
    job2.results.plot_process_statistics( process_statistics2[19], key="occurence_frequency", log_scale=True, pause=2, close=True )

    scm.plams.finish()
