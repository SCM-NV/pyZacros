import numpy
import multiprocessing
import scm.plams

import pyzacros as pz
from pyzacros.utils.compareReports import compare

def test_ZacrosMultiJob():
    """Test of the Mechanism class."""
    print( "---------------------------------------------------" )
    print( ">>> Testing TOFSurfaceJob class" )
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
    CO_point = pz.Cluster(species=[CO_ads], energy=-1.3)
    O_point = pz.Cluster(species=[O_ads], energy=-2.3)

    cluster_expansion = [CO_point, O_point]

    #---------------------------------------------
    # Elementary Reactions
    #---------------------------------------------
    # CO_adsorption:
    CO_adsorption = pz.ElementaryReaction(initial=[s0,CO_gas],
                                        final=[CO_ads],
                                        reversible=False,
                                        pre_expon=10.0,
                                        activation_energy=0.0)

    # O2_adsorption:
    O2_adsorption = pz.ElementaryReaction(initial=[s0,s0,O2_gas],
                                        final=[O_ads,O_ads],
                                        neighboring=[(0, 1)],
                                        reversible=False,
                                        pre_expon=2.5,
                                        activation_energy=0.0)

    # CO_oxidation:
    CO_oxidation = pz.ElementaryReaction(initial=[CO_ads, O_ads],
                                        final=[s0, s0, CO2_gas],
                                        neighboring=[(0, 1)],
                                        reversible=False,
                                        pre_expon=1.0e+20,
                                        activation_energy=0.0)

    mechanism = [CO_adsorption, O2_adsorption, CO_oxidation]

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init(folder='test_ZacrosMultiJob')

    # Run as many job simultaneously as there are cpu on the system
    maxjobs = multiprocessing.cpu_count()
    scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
    scm.plams.config.job.runscript.nproc = 1
    print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

    # Settings:
    sett = pz.Settings()
    sett.random_seed = 953129
    sett.temperature = 500.0
    sett.pressure = 1.0
    sett.snapshots = ('time', 2.0)
    sett.species_numbers = ('time', 0.1)
    sett.max_time = 10.0

    parameters = { 'x_CO':pz.ZacrosMultiJob.Parameter('molar_fraction.CO', numpy.arange(0.2, 0.8, 0.1)),
                   'x_O2':pz.ZacrosMultiJob.Parameter('molar_fraction.O2', lambda params: 1.0-params['x_CO']) }

    try:
        job = pz.ZacrosMultiJob( settings=sett,
                                    lattice=lattice,
                                    mechanism=mechanism,
                                    cluster_expansion=cluster_expansion,
                                    parameters=parameters )

        results = job.run()

    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        job = scm.plams.load( 'tests/test_ZacrosMultiJob.idata/plamsjob/plamsjob.dill' )
        results = job.results

    output = ""

    if( results.job.ok() ):
        x_CO = []
        ac_O = []
        ac_CO = []
        TOF_CO2 = []

        results_dict = results.turnover_frequency()
        results_dict = results.average_coverage( last=3, update=results_dict )

        for i in range(len(results_dict)):
            x_CO.append( results_dict[i]['x_CO'] )
            ac_O.append( results_dict[i]['average_coverage']['O*'] )
            ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
            TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )

        output += "----------------------------------------------\n"
        output += "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %10s"%"TOF_CO2\n"
        output += "----------------------------------------------\n"
        for i in range(len(x_CO)):
            output += "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i]+" %10.6f"%TOF_CO2[i]+"\n"

    scm.plams.finish()

    print(output)

    expectedOutput = """\
----------------------------------------------
cond     x_CO       ac_O      ac_CO   TOF_CO2
----------------------------------------------
   0     0.20   0.997467   0.000000   0.020759
   1     0.30   0.989600   0.000000   0.075326
   2     0.40   0.894667   0.000533   0.482301
   3     0.50   0.554267   0.023867   2.073205
   4     0.60   0.000000   1.000000   0.012715
   5     0.70   0.000000   1.000000   0.000000
   6     0.80   0.000000   1.000000  -0.000000\
"""

    assert( compare( output, expectedOutput, rel_error=0.1 ) )

    #---------------------------------------------
    # Plotting the results
    #---------------------------------------------
    try:
        import matplotlib.pyplot as plt
    except ImportError as e:
        print('Consider to install matplotlib to visualize the results!')
        return

    # Coverage and TOF plot
    fig = plt.figure()

    ax = plt.axes()
    ax.set_xlabel('Partial Pressure CO', fontsize=14)
    ax.set_ylabel("Coverage Fraction (%)", color="blue", fontsize=14)
    ax.plot(x_CO, ac_O, color="blue", linestyle="-.", lw=2, zorder=1)
    ax.plot(x_CO, ac_CO, color="blue", linestyle="-", lw=2, zorder=2)
    plt.text(0.3, 0.9, 'O', fontsize=18, color="blue")
    plt.text(0.7, 0.9, 'CO', fontsize=18, color="blue")

    ax2 = ax.twinx()
    ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
    ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
    plt.text(0.37, 1.5, 'CO$_2$', fontsize=18, color="red")

    plt.pause(2)
