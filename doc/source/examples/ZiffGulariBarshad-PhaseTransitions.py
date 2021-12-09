import multiprocessing
import numpy

import scm.plams
import scm.pyzacros as pz

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

# Run as many job simultaneously as there are cpu on the system
maxjobs = multiprocessing.cpu_count()
scm.plams.config.default_jobrunner = scm.plams.JobRunner(parallel=True, maxjobs=maxjobs)
scm.plams.config.job.runscript.nproc = 1
print('Running up to {} jobs in parallel simultaneously'.format(maxjobs))

# Settings:
sett = pz.Settings()
sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 0.5)
sett.species_numbers = ('time', 0.01)
sett.max_time = 10.0

#---------------------------------------------
# Running the calculations
#---------------------------------------------

dx = 0.01
x_CO = numpy.arange(0.2,0.8+dx,dx)
results = []

# Loop over the conditions to run the jobs
for x in x_CO:
   sett.molar_fraction.CO = x
   sett.molar_fraction.O2 = 1.0-x

   job = pz.ZacrosJob( settings=sett,
                        lattice=lattice,
                        mechanism=mechanism,
                        cluster_expansion=cluster_expansion )

   results.append(job.run())

#---------------------------------------------
# Getting the results
#---------------------------------------------
cf_O = []
cf_CO = []
TOF_CO2 = []

for i,x in enumerate(x_CO):
   if( results[i].ok() ):
      acf = { "O*":0.0, "CO*":0.0 }
      for lattice_state in results[i].lattice_states(last=5):
         fractions = lattice_state.coverage_fractions()
         acf["O*"] += fractions["O*"]/5
         acf["CO*"] += fractions["CO*"]/5

      TOFs,_,_ = results[i].get_TOFs()

      cf_O.append( acf["O*"] )
      cf_CO.append( acf["CO*"] )
      TOF_CO2.append( TOFs["CO2"] )

scm.plams.finish()

print("----------------------------------------------")
print("%4s"%"cond", "%8s"%"x_CO", "%10s"%"acf_O", "%10s"%"acf_CO", "%10s"%"TOF_CO2")
print("----------------------------------------------")

for i,x in enumerate(x_CO):
   print("%4d"%i, "%8.2f"%x_CO[i], "%10.6f"%cf_O[i], "%10.6f"%cf_CO[i], "%10.6f"%TOF_CO2[i])

#---------------------------------------------
# Plotting the results
#---------------------------------------------

# Coverage and TOF plot
fig = plt.figure()

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel("Coverage Fraction (%)", color="blue", fontsize=14)
ax.plot(x_CO, cf_O, color="blue", linestyle="-.", lw=2, zorder=1)
ax.plot(x_CO, cf_CO, color="blue", linestyle="-", lw=2, zorder=2)
plt.text(0.3, 0.9, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.9, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.37, 1.5, 'CO$_2$', fontsize=18, color="red")

plt.show()

# Lattice states for x_CO=0.54 and CO=0.55
results[33].last_lattice_state().plot()
results[34].last_lattice_state().plot()

# Molecule numbers for x_CO=0.54 and CO=0.55
results[33].plot_molecule_numbers( ["CO2"], normalize_per_site=True )
results[34].plot_molecule_numbers( ["CO2"], normalize_per_site=True )

# Molecule numbers for x_CO=0.54 and CO=0.55. First Derivative
results[33].plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )
results[34].plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )
