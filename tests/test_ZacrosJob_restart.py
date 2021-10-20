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
    lattice = pz.Lattice( lattice_type=pz.Lattice.RECTANGULAR, lattice_constant=1.0, repeat_cell=[50,50] )

    #---------------------------------------------
    # Clusters:
    #---------------------------------------------
    CO_point = pz.Cluster(site_types=["1"], species=[CO_ads], cluster_energy=-1.3)
    O_point = pz.Cluster(site_types=["1"], species=[O_ads], cluster_energy=-2.3)

    cluster_expansion = [CO_point, O_point]

    #---------------------------------------------
    # Elementary Reactions
    #---------------------------------------------
    # CO_adsorption:
    CO_adsorption = pz.ElementaryReaction(site_types=["1"],
                                    initial=[s0,CO_gas],
                                    final=[CO_ads],
                                    reversible=False,
                                    pre_expon=10.0,
                                    activation_energy=0.0)

    # O2_adsorption:
    O2_adsorption = pz.ElementaryReaction(site_types=["1", "1"],
                                        initial=[s0,s0,O2_gas],
                                        final=[O_ads,O_ads],
                                        neighboring=[(1, 2)],
                                        reversible=False,
                                        pre_expon=2.5,
                                        activation_energy=0.0)

    # CO_oxidation:
    CO_oxidation = pz.ElementaryReaction(site_types=["1", "1"],
                                    initial=[CO_ads, O_ads],
                                    final=[s0, s0, CO2_gas],
                                    neighboring=[(1, 2)],
                                    reversible=False,
                                    pre_expon=1.0e+20,
                                    activation_energy=0.0)

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

    scm.plams.finish()

    print( output )

    expectedOutput = """\
  0.0       0
  0.1     650
  0.2    1364
  0.3    1913
  0.4    2408
  0.5    2891
  0.6    3377
  0.7    3812
  0.8    4216
  0.9    4597
  1.0    4999
  1.1    5416
  1.2    5823
  1.3    6167
  1.4    6547
  1.5    6928
  1.6    7298
  1.7    7651
  1.8    8009
  1.9    8374
--
  0.0       0
  0.1     650
  0.2    1364
  0.3    1913
  0.4    2408
  0.5    2891
  0.6    3377
  0.7    3812
  0.8    4216
  0.9    4597
  1.0    4999
--
  1.1    5416
  1.2    5823
  1.3    6167
  1.4    6547
  1.5    6928
  1.6    7298
  1.7    7651
  1.8    8009
  1.9    8374\
"""

    assert( compare( output, expectedOutput, 1e-3 ) )
