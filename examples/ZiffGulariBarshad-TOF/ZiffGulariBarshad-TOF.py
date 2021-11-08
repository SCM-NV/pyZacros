"""
Based on the Zacros example:
https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros
"""
import multiprocessing
import numpy

import scm.plams
import pyzacros as pz

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
CO_point = pz.Cluster(species=[CO_ads], cluster_energy=-1.3)
O_point = pz.Cluster(species=[O_ads], cluster_energy=-2.3)

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
scm.plams.init()

# Run as many job simultaneously as there are cpu on the system:
maxjobs = multiprocessing.cpu_count()
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

# Set the default jobrunner to be parallel:
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)

# Number of cores for each job:
scm.plams.config.job.runscript.nproc = 1

# Settings:
sett = pz.Settings()
sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 5.e-1)
sett.process_statistics = ('time', 1.e-2)
sett.species_numbers = ('time', 1.e-2)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 25.0
sett.wall_time = 3600

#---------------------------------------------
# Running the calculations
#---------------------------------------------

# Set composition space
conditions = []
dx = 0.1
for x_CO in numpy.arange(0.0,1.0+dx,dx):
   for x_O2 in numpy.arange(0.0,1.0+dx,dx):
      if( x_CO+x_O2>1.0 ): continue

      conditions.append( [ x_CO, x_O2 ] )

# Some additional points to make the final figure nicer
dx = 0.05
for a in numpy.arange(dx,1.0,2*dx):
   if( 2.0*a>1.0 ): continue
   conditions.append( [ a, a ] )

results = []

# Loop over the conditions to run the jobs
for i,(x_CO,x_O2) in enumerate(conditions):
   sett.molar_fraction.CO = x_CO
   sett.molar_fraction.O2 = x_O2

   job = pz.ZacrosJob( settings=sett,
                        lattice=lattice,
                        mechanism=mechanism,
                        cluster_expansion=cluster_expansion,
                        name="CO_{:>.2f}-O2_{:>.2f}".format(x_CO,x_O2) )

   results.append(job.run())

#---------------------------------------------
# Getting the results
#---------------------------------------------
x = []
y = []
z = []

# Only print the results of the succesful calculations:
#for result in [r for r in results if r.ok()]:
for result in results:
    xCO,xO2 = [ float(s.replace('CO_','').replace('O2_','')) for s in result.job.name.split('-') ]
    TOFs,_ = result.get_TOFs( npoints=1000 )

    x.append( xCO )
    y.append( xO2 )
    z.append( TOFs["CO2"] )

scm.plams.finish()

print("--------------------------------------")
print("%8s"%"xCO", "%8s"%"xO2", "%18s"%"TOFs[CO2]")
print("--------------------------------------")

for i in range(len(x)):
    print("%8.2f"%x[i], "%8.2f"%y[i], "%18.6f"%z[i])

#---------------------------------------------
# Plotting the results
#---------------------------------------------
try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print('Consider to install matlibplot to visualize the results!')
    exit(0)

fig = plt.figure()
ax = plt.axes( projection='3d' )
ax.set_xlabel('x CO')
ax.set_ylabel('x O2')
ax.set_zlabel('TOF CO2')
ax.plot_trisurf(x, y, z, cmap=plt.get_cmap('hot'), antialiased=True);

plt.show()
