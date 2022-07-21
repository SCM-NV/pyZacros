import numpy
import multiprocessing
import scm.plams

#import pyzacros as pz
#from pyzacros.utils.compareReports import compare
import scm.pyzacros as pz
from scm.pyzacros.utils.compareReports import compare

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
    sett.snapshots = ('time', 0.5)
    sett.species_numbers = ('time', 0.1)
    sett.max_time = 10.0

    parameters = { 'x_CO':pz.ZacrosMultiJob.Parameter('molar_fraction.CO', numpy.arange(0.2, 0.8, 0.01)),
                   'x_O2':pz.ZacrosMultiJob.Parameter('molar_fraction.O2', lambda params: 1.0-params['x_CO']) }

    job = pz.ZacrosMultiJob( settings=sett,
                                lattice=lattice,
                                mechanism=mechanism,
                                cluster_expansion=cluster_expansion,
                                parameters=parameters )

    results = job.run()

    output = ""

    if( results.job.ok() ):
        x_CO = []
        ac_O = []
        ac_CO = []
        TOF_CO2 = []

        results_dict = results.turnover_frequency()
        results_dict = results.average_coverage( update=results_dict )

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
cond     x_CO       ac_O      ac_CO    TOF_CO2
----------------------------------------------
   0     0.20   0.998000   0.000000   0.020759
   1     0.21   0.999520   0.000000   0.014204
   2     0.22   1.000000   0.000000   0.021340
   3     0.23   0.998400   0.000000   0.018694
   4     0.24   0.997360   0.000000   0.028042
   5     0.25   0.993360   0.000000   0.044783
   6     0.26   0.998400   0.000000   0.031256
   7     0.27   0.997280   0.000000   0.045270
   8     0.28   0.997440   0.000000   0.050511
   9     0.29   0.993440   0.000080   0.065989
  10     0.30   0.993120   0.000000   0.075326
  11     0.31   0.995040   0.000000   0.076805
  12     0.32   0.991120   0.000000   0.105631
  13     0.33   0.988640   0.000000   0.105635
  14     0.34   0.986640   0.000000   0.149911
  15     0.35   0.974160   0.000080   0.207944
  16     0.36   0.961360   0.000240   0.238777
  17     0.37   0.956160   0.000320   0.284597
  18     0.38   0.933280   0.000400   0.321649
  19     0.39   0.925680   0.000320   0.439182
  20     0.40   0.897760   0.000880   0.482301
  21     0.41   0.862640   0.002160   0.569744
  22     0.42   0.867040   0.001280   0.669620
  23     0.43   0.820560   0.001680   0.841014
  24     0.44   0.815760   0.002160   0.917175
  25     0.45   0.743920   0.003680   1.199928
  26     0.46   0.719840   0.006320   1.281847
  27     0.47   0.653200   0.011520   1.488050
  28     0.48   0.648240   0.009360   1.705636
  29     0.49   0.602320   0.016240   1.830680
  30     0.50   0.561440   0.020480   2.073205
  31     0.51   0.540320   0.025440   2.222495
  32     0.52   0.450880   0.057120   2.502978
  33     0.53   0.396160   0.078080   2.776352
  34     0.54   0.073440   0.708800   1.922850
  35     0.55   0.019040   0.896560   1.537623
  36     0.56   0.000000   0.998720   0.589056
  37     0.57   0.000000   1.000000   0.159712
  38     0.58   0.000000   1.000000   0.041097
  39     0.59   0.000000   1.000000   0.011441
  40     0.60   0.000000   1.000000   0.012715
  41     0.61   0.000000   1.000000   0.000994
  42     0.62   0.000000   1.000000   0.000675
  43     0.63   0.000000   1.000000   0.000000
  44     0.64   0.000000   1.000000   0.000000
  45     0.65   0.000000   1.000000   0.000000
  46     0.66   0.000000   1.000000   0.000000
  47     0.67   0.000000   1.000000   0.000000
  48     0.68   0.000000   1.000000  -0.000000
  49     0.69   0.000000   1.000000  -0.000000
  50     0.70   0.000000   1.000000   0.000000
  51     0.71   0.000000   1.000000   0.000000
  52     0.72   0.000000   1.000000  -0.000000
  53     0.73   0.000000   1.000000  -0.000000
  54     0.74   0.000000   1.000000   0.000000
  55     0.75   0.000000   1.000000   0.000000
  56     0.76   0.000000   1.000000   0.000000
  57     0.77   0.000000   1.000000  -0.000000
  58     0.78   0.000000   1.000000   0.000000
  59     0.79   0.000000   1.000000   0.000000
  60     0.80   0.000000   1.000000  -0.000000\
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

test_ZacrosMultiJob()
