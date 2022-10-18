import multiprocessing
import numpy

import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

import adaptiveDesignProcedure as adp

#-------------------------------------
# Calculating the rates with pyZacros
#-------------------------------------
def getRate( conditions ):

    print("")
    print("  Requesting:")
    for cond in conditions:
        print("    xCO = ", cond[0])
    print("")

    #---------------------------------------
    # Zacros calculation
    #---------------------------------------
    zgb = pz.models.ZiffGulariBarshad()

    z_sett = pz.Settings()
    z_sett.random_seed = 953129
    z_sett.temperature = 500.0
    z_sett.pressure = 1.0
    z_sett.species_numbers = ('time', 0.1)
    z_sett.max_time = 10.0

    z_job = pz.ZacrosJob( settings=z_sett, lattice=zgb.lattice,
                          mechanism=zgb.mechanism,
                          cluster_expansion=zgb.cluster_expansion )

    #---------------------------------------
    # Parameters scan calculation
    #---------------------------------------
    ps_params = pz.ZacrosParametersScanJob.Parameters()
    ps_params.add( 'x_CO', 'molar_fraction.CO', [ cond[0] for cond in conditions ] )
    ps_params.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )

    ps_job = pz.ZacrosParametersScanJob( reference=z_job, parameters=ps_params )

    results = ps_job.run()

    tof = numpy.nan*numpy.empty((len(conditions),1))
    if( results.job.ok() ):
        results_dict = results.turnover_frequency()

        for i in range(len(results_dict)):
            tof[i,0] = results_dict[i]['turnover_frequency']['CO2']

    return tof


scm.pyzacros.init()

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

#-----------------
# Surrogate model
#-----------------
input_var = ( { 'name'    : 'CO',
                'min'     : 0.001,
                'max'     : 0.999,
                'num'     : 5,
                'typevar' : 'lin' }, )

tab_var = ( { 'name'    : 'CO2',
              'typevar' : 'lin' }, )

outputDir = scm.pyzacros.workdir()+'/adp.results'

adpML = adp.adaptiveDesignProcedure( input_var, tab_var, getRate,
                                     algorithmParams={'dth':0.05,'d2th':0.7},
                                     benchmark=False,
                                     outputDir=outputDir,
                                     randomState=10 )

adpML.createTrainingDataAndML()

x_CO,TOF_CO2 = adpML.trainingData.T

print( '----------------------------' )
print( '%4s'%'cond', '%8s'%'x_CO', '%12s'%'TOF_CO2' )
print( '----------------------------' )
for i in range(len(x_CO)):
    print( '%4d'%i, '%8.3f'%x_CO[i], '%12.6f'%TOF_CO2[i] )

scm.pyzacros.finish()

#---------------------------------------------
# Plotting the results
#---------------------------------------------
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print('Consider to install matplotlib to visualize the results!')
    exit(0)

fig = plt.figure()

x_CO_model = numpy.linspace(0.0,1.0,201)
TOF_CO2_model = adpML.predict( x_CO_model.reshape(-1,1) ).T[0]

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel('TOF (mol/s/site)', fontsize=14)
ax.plot(x_CO_model, TOF_CO2_model, color='red', linestyle='-', lw=2, zorder=0)
ax.plot(x_CO, TOF_CO2, marker='$\u25EF$', color='black', markersize=4, lw=0, zorder=1)

plt.show()
