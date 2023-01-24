import numpy
import multiprocessing
import scm.plams

import scm.pyzacros as pz
import scm.pyzacros.models
import scm.pyzacros.utils


def test_ZacrosSteadyStateJob():
    print( "---------------------------------------------------" )
    print( ">>> Testing ZacrosSteadyStateJob class" )
    print( "---------------------------------------------------" )

    zgb = pz.models.ZiffGulariBarshad()

    #---------------------------------------------
    # Calculation Settings
    #---------------------------------------------
    scm.plams.init(folder='test_ZacrosSteadyStateJob')

    try:
        sett = pz.Settings()
        sett.random_seed = 953129
        sett.temperature = 500.0
        sett.pressure = 1.0
        sett.species_numbers = ('time', 0.1)
        sett.max_time = 10.0
        sett.molar_fraction.CO = 0.42
        sett.molar_fraction.O2 = 1.0 - sett.molar_fraction.CO

        parameters = pz.ZacrosSteadyStateJob.Parameters()
        parameters.add( 'max_time', 'restart.max_time', 2*sett.max_time*( numpy.arange(10)+1 )**3 )

        job = pz.ZacrosJob( settings=sett, lattice=zgb.lattice, mechanism=zgb.mechanism,
                            cluster_expansion=zgb.cluster_expansion )

        sett = pz.Settings()
        sett.turnover_frequency.nbatch = 20
        sett.turnover_frequency.confidence = 0.97
        sett.turnover_frequency.nreplicas = 2

        mjob = pz.ZacrosSteadyStateJob( settings=sett, reference=job, parameters=parameters )

        results = mjob.run()

    except pz.ZacrosExecutableNotFoundError:
        print( "Warning: The calculation FAILED because the zacros executable is not available!" )
        print( "         For testing purposes, now we load precalculated results.")

        mjob = scm.plams.load( 'tests/test_ZacrosSteadyStateJob.data/plamsjob/plamsjob.dill' )
        results = mjob.results

    scm.plams.finish()

    output = ""

    if mjob.ok():
        output += "------------------------------------------------\n"
        output += "%4s"%"iter"+" %10s"%"TOF_CO2"+" %10s"%"error"+" %10s"%"max_time"+" %10s"%"conv?\n"
        output += "------------------------------------------------\n"

        for i,step in enumerate(results.history()):
            output += "%4d"%i+" %10.5f"%step['turnover_frequency']['CO2']+" %10.5f"%step['turnover_frequency_error']['CO2'] \
                        +" %10d"%step['max_time']+" %10s"%step['converged']['CO2']+"\n"

    print(output)

    expectedOutput = """\
------------------------------------------------
iter    TOF_CO2      error   max_time     conv?
------------------------------------------------
   0    0.75498    0.11813         20      False
   1    0.59235    0.02422        160      False
   2    0.60063    0.01698        540       True\
"""

    assert( pz.utils.compare( output, expectedOutput, rel_error=0.1 ) )

