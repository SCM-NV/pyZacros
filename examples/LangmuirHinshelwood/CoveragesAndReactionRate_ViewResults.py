import math
import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models
import matplotlib.pyplot as plt

scm.plams.init()

#------------------------
# Collecting the results
#------------------------
job = scm.plams.load( 'plams_workdir/mesh/mesh.dill' )
results = job.results

x_CO = []
ac_O = []
ac_CO = []
TOF_CO2 = []

results_dict = results.turnover_frequency()
results_dict = results.average_coverage( last=10, update=results_dict )

for i in range(len(results_dict)):
    x_CO.append( results_dict[i]['x_CO'] )
    ac_O.append( results_dict[i]['average_coverage']['O*'] )
    ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
    TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )

print( '------------------------------------------------' )
print( '%4s'%'cond', '%8s'%'x_CO', '%10s'%'ac_O', '%10s'%'ac_CO', '%12s'%'TOF_CO2' )
print( '------------------------------------------------' )
for i in range(len(x_CO)):
    print( '%4d'%i, '%8.2f'%x_CO[i], '%10.6f'%ac_O[i], '%10.6f'%ac_CO[i], '%12.6f'%TOF_CO2[i] )

#------------------------
# Analytical model
#------------------------
lh = pz.models.LangmuirHinshelwood()

K_CO = lh.mechanism.find_one( 'CO_adsorption' ).pe_ratio
K_O2 = lh.mechanism.find_one( 'O2_adsorption' ).pe_ratio
k_oxi = lh.mechanism.find_one( 'CO_oxidation' ).pre_expon

ac_O_model = []
ac_CO_model = []
TOF_CO2_model = []

for i in range(len(x_CO)):
    x_O2 = 1 - x_CO[i]
    ac_O_model.append( math.sqrt(K_O2*x_O2)/( 1 + K_CO*x_CO[i] + math.sqrt(K_O2*x_O2) ) )
    ac_CO_model.append( K_CO*x_CO[i]/( 1 + K_CO*x_CO[i] + math.sqrt(K_O2*x_O2) ) )
    TOF_CO2_model.append( 6*k_oxi*ac_CO_model[i]*ac_O_model[i] )

#------------------------
# Plotting the results
#------------------------
fig = plt.figure()

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel('Coverage Fraction (%)', color='blue', fontsize=14)
ax.plot(x_CO, ac_O_model, color='blue', linestyle='-.', lw=2, zorder=1)
ax.plot(x_CO, ac_O, marker='$\u25CF$', color='blue', lw=0, markersize=4, zorder=2)
ax.plot(x_CO, ac_CO_model, color='blue', linestyle='-', lw=2, zorder=3)
ax.plot(x_CO, ac_CO, marker='$\u25EF$', color='blue', markersize=4, lw=0, zorder=4)
plt.text(0.3, 0.60, 'O', fontsize=18, color='blue')
plt.text(0.7, 0.45, 'CO', fontsize=18, color='blue')

ax2 = ax.twinx()
ax2.set_ylabel('TOF (mol/s/site)',color='red', fontsize=14)
ax2.plot(x_CO, TOF_CO2_model, color='red', linestyle='-', lw=2, zorder=5)
ax2.plot(x_CO, TOF_CO2, marker='$\u25EF$', color='red', markersize=4, lw=0, zorder=6)
plt.text(0.3, 200.0, 'CO$_2$', fontsize=18, color='red')

plt.show()

scm.plams.finish()
