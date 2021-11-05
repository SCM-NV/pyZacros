"""
This example shows how to get the turnover frequency (TOF) surface
at the steady-state for CO2 production in the Ziff–Gulari–Barshad (ZGB) model.

The ZGB model consists of the following three steps:
  * Adsorption of the reacting species CO and O2
  * The actual reaction step on the surface: CO + O → CO2
  * Desorption of the products.

The steady-state is detected for each given composition when the derivative
of the CO2 production with respect to time is zero and remains so.

   d
  -- n_CO2 = 0, for all present and future t
  dt

For a given composition, several simulations are run in progressive chunks
of time of 5s. At the end of each chunk of time, the steady-state condition
is verified to determine if the convergence was reached. Calculations for
each composition are run in parallel.

Approximate run time: 40 min
"""

import numpy
import scipy
import scipy.stats
import multiprocessing

import scm.plams
import scm.pyzacros as pz

#--------------------------------------------------------------
# Function to compute the rate of CO2 production
# Original author: Mauro Bracconi (mauro.bracconi@polimi.it)
# Evaluation of the steady state is inspired by this publication:
#   Hashemi et al., J.Chem. Phys. 144, 074104 (2016)
#--------------------------------------------------------------
def compute_rate( t_vect, spec, n_sites, n_batch ):

   def time_search(t,tvec):
      ind_geq = 0
      while tvec[ind_geq] < t:
         ind_geq += 1

      ind_leq = len( tvec ) - 1
      while ind_leq>0 and tvec[ind_leq] > t:
         ind_leq -= 1
      low_frac = 1.0
      if not (ind_geq == ind_leq):
         low_frac = (tvec[ind_geq] - t) / (tvec[ind_geq] - tvec[ind_leq])
      return [ (ind_leq,ind_geq), (low_frac,1-low_frac)]

   t_vect = numpy.array(t_vect)
   prod_mol = numpy.array(spec)/n_sites

   n_batch = min( len(t_vect), int(len(t_vect)/n_batch) )
   dt_batch = t_vect[-1]/n_batch
   bin_edge = numpy.linspace(0,t_vect[-1],n_batch+1)

   rate = numpy.zeros( n_batch )

   for i in range(n_batch):
      idb_s = time_search( bin_edge[i], t_vect )
      idb_e = time_search( bin_edge[i+1], t_vect )

      pp_s = idb_s[1][0] * prod_mol[idb_s[0][0]] + idb_s[1][1] * prod_mol[idb_s[0][1]]
      pp_e = idb_e[1][0] * prod_mol[idb_e[0][0]] + idb_e[1][1] * prod_mol[idb_e[0][1]]
      rate[i] = (pp_e-pp_s)/dt_batch

   confidence = 0.99
   rate = rate[1:]

   rate_av, se = numpy.mean(rate), scipy.stats.sem(rate)

   rate_CI = se * scipy.stats.t._ppf((1+confidence)/2.0, n_batch - 1)

   if ( rate_CI/(rate_av+1e-8)<1.0-confidence ):
      return (rate_av,rate_CI,rate_CI/(rate_av+1e-8),True)
   else:
      return ( rate_av,rate_CI,rate_CI/rate_av,False )

#---------------------------------------------
# System setup
#---------------------------------------------

# Gas-species:
CO_gas = pz.Species("CO")
O2_gas = pz.Species("O2")
CO2_gas = pz.Species("CO2", gas_energy=-2.337)

# Surface species:
s0 = pz.Species("*", 1)      # Empty adsorption site
CO_ads = pz.Species("CO*", 1)
O_ads = pz.Species("O*", 1)

# Lattice setup:
lattice = pz.Lattice( lattice_type=pz.Lattice.RECTANGULAR, lattice_constant=1.0, repeat_cell=[50,50] )

# Clusters:
CO_point = pz.Cluster(site_types=["1"], species=[CO_ads], cluster_energy=-1.3)
O_point = pz.Cluster(site_types=["1"], species=[O_ads], cluster_energy=-2.3)

cluster_expansion = [CO_point, O_point]

# Elementary Reactions
CO_adsorption = pz.ElementaryReaction(site_types=["1"],
                                initial=[s0,CO_gas],
                                final=[CO_ads],
                                reversible=False,
                                pre_expon=10.0,
                                activation_energy=0.0)

O2_adsorption = pz.ElementaryReaction(site_types=["1", "1"],
                                    initial=[s0,s0,O2_gas],
                                    final=[O_ads,O_ads],
                                    neighboring=[(1, 2)],
                                    reversible=False,
                                    pre_expon=2.5,
                                    activation_energy=0.0)

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

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

# Calculation settings:
sett = pz.Settings()
sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 0.05)
sett.process_statistics = ('time', 0.01)
sett.species_numbers = ('time', 0.01)
sett.max_steps = 'infinity'
sett.max_time = 5.0

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

previousJob = len(conditions)*[ None ]
jobsList = len(conditions)*[ None ]
isConverged = len(conditions)*[ False ]
convergedAt = len(conditions)*[ 0.0 ]
TOF_CO2 = len(conditions)*[ None ]
prevTOF_CO2 = len(conditions)*[ None ]

# Loop over iterations
max_iter = 100
for iter in range(max_iter):
   print(">> Iteration: "+str(iter))

   # Loop over the conditions to run the jobs
   for i,(x_CO,x_O2) in enumerate(conditions):
      if( isConverged[i] ): continue

      sett.molar_fraction.CO = x_CO
      sett.molar_fraction.O2 = x_O2

      if( previousJob[i] is not None ):
         sett.restart.max_time = sett.max_time*(iter+1)**2

      job = pz.ZacrosJob( settings=sett,
                           lattice=lattice,
                           mechanism=mechanism,
                           cluster_expansion=cluster_expansion,
                           name="cond"+"%03d"%i+"-iter"+"%03d"%iter,
                           restart=( None if iter==0 else previousJob[i] ) )

      job.run()

      previousJob[i] = job
      jobsList[i] = job

   # Loop over the conditions to collect the results and check convergence
   for i,x in enumerate(conditions):
      if( isConverged[i] ): continue

      if( jobsList[i].ok() ):
         data = jobsList[i].results.provided_quantities()
         number_of_sites = jobsList[i].results.number_of_lattice_sites()

         if( jobsList[i].check() ):
            TOF_CO2[i],ci,ratio,conv = compute_rate( data['Time'], data['CO2'], number_of_sites, 20 )
            print(">> cond"+"%03d"%i+":", TOF_CO2[i], ci, ratio, conv)

            if( conv ):
               print(">> cond"+"%03d"%i+": converged on iteration", iter)
               isConverged[i] = True
               convergedAt[i] = jobsList[i].settings.max_time if previousJob[i] is None else jobsList[i].settings.restart.max_time
         else:
            isConverged[i] = True
      else:
         isConverged[i] = True

   print(">> End Iteration: "+str(iter))

   # Print current status
   print("----------------------------------------------------------------------------------")
   print("%4s"%"cond", "%8s"%"x_CO", "%8s"%"x_O2", "%18s"%"TOFs[CO2]", "%18s"%"prevTOFs[CO2]", "%10s"%"tconv(s)", "%10s"%"Converged?")
   print("----------------------------------------------------------------------------------")

   for i,(x_CO,x_O2) in enumerate(conditions):
      if( prevTOF_CO2[i] is not None ):
         if( isConverged[i] ):
            print("%4d"%i, "%8.2f"%x_CO, "%8.2f"%x_O2, "%18.6f"%TOF_CO2[i], "%18.6f"%prevTOF_CO2[i], "%10.1f"%convergedAt[i], "%10s"%isConverged[i])
         else:
            print("%4d"%i, "%8.2f"%x_CO, "%8.2f"%x_O2, "%18.6f"%TOF_CO2[i], "%18.6f"%prevTOF_CO2[i], "%10s"%"--", "%10s"%isConverged[i])
      else:
         print("%4d"%i, "%8.2f"%x_CO, "%8.2f"%x_O2, "%18.6f"%TOF_CO2[i], "%18s"%"--", "%10s"%"--", "%10s"%isConverged[i])

      if( not isConverged[i] ): prevTOF_CO2[i] = TOF_CO2[i]

   if( all(isConverged) ): break

scm.plams.finish()

#---------------------------------------------
# Plot the results
#---------------------------------------------

try:
    import matplotlib.pyplot as plt
except ImportError as e:
    print('Consider to install matlibplot to visualize the results!')
    exit(0)

x_COvec = [ v[0] for v in conditions ]
x_O2vec = [ v[1] for v in conditions ]

print("x_COvec = ", x_COvec)
print("x_O2vec = ", x_O2vec)
print("TOF_CO2 = ", TOF_CO2)

fig = plt.figure()
ax = plt.axes( projection='3d' )
ax.set_xlabel('x CO')
ax.set_ylabel('x O2')
ax.set_zlabel('TOF CO2')
ax.plot_trisurf(x_COvec, x_O2vec, TOF_CO2, cmap=plt.get_cmap('hot'), antialiased=True);

plt.show()
