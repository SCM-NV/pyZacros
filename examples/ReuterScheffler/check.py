import scm.plams
import scm.pyzacros as pz

scm.pyzacros.init()

job = scm.plams.load('plams_workdir-ok/plamsjob/plamsjob_ss_iter000.004/plamsjob_ss_iter000.004.dill')
print( job.results.provided_quantities_names() )
print( len(job.results.provided_quantities()['CO2']) )

scm.pyzacros.finish()
