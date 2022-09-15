import scm.plams
import scm.pyzacros as pz
import matplotlib.pyplot as plt

scm.plams.init()

INCOMPLETO. ARREGLAR

job = scm.plams.load( "plams_workdir.autoscaling/mesh/plamsjob.dill" )
results = job.results

print((8+10+15+15+10+ 5)*"-")
print("%8s"%"iter", "%10s"%"TOF_CO2",    "%15s"%"max_time","%15s"%"TOF_CO2_error", "%10s"%"conv?")
print("%8s"%"",     "%10s"%"mol/s/site", "%15s"%"s",       "%15s"%"mol/s/site",    "%10s"%"")
print((8+10+15+15+10+ 5)*"-")

for i,step in enumerate(results.history()):
    print("%8d"%i, "%10.5f"%step['turnover_frequency']['CO2'], "%15d"%step['max_time'],
            "%15.5f"%step['turnover_frequency_error']['CO2'], "%10s"%step['converged']['CO2'])

#x_CO = []
#ac_O = []
#ac_CO = []
#TOF_CO2 = []

#results_dict = results.turnover_frequency()
#results_dict = results.average_coverage( last=10, update=results_dict )

#for i in range(len(results_dict)):
    #x_CO.append( results_dict[i]['x_CO'] )
    #ac_O.append( results_dict[i]['average_coverage']['O*'] )
    #ac_CO.append( results_dict[i]['average_coverage']['CO*'] )
    #TOF_CO2.append( results_dict[i]['turnover_frequency']['CO2'] )

#print( "----------------------------------------------" )
#print( "%4s"%"cond"+" %8s"%"x_CO"+" %10s"%"ac_O"+" %10s"%"ac_CO"+" %12s"%"TOF_CO2" )
#print( "----------------------------------------------" )
#for i in range(len(x_CO)):
    #print( "%4d"%i+" %8.2f"%x_CO[i]+" %10.6f"%ac_O[i]+" %10.6f"%ac_CO[i]+" %12.6f"%TOF_CO2[i] )


#fig = plt.figure()
#ax = plt.axes()
#ax.set_xlabel('Time (s)', fontsize=14)
#ax.set_ylabel("CO$_2$ Production (mol/site)", fontsize=14)

#for i in range(len(job.children)):
    #molecule_numbers = job.children[i].results.molecule_numbers(['CO2'], normalize_per_site=True)
    #ax.plot( molecule_numbers['Time'], molecule_numbers['CO2'], lw=3, zorder=-i )
    #ax.vlines( max(molecule_numbers['Time']) , 0, 200, colors='0.8', linestyles='--',)

#plt.show()

fig = plt.figure()

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel("Coverage Fraction (%)", color="blue", fontsize=14)
ax.plot(x_CO, ac_O, color="blue", linestyle="-.", lw=2, zorder=1)
ax.plot(x_CO, ac_CO, color="blue", linestyle="-", lw=2, zorder=2)
plt.text(0.3, 0.60, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.45, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO, TOF_CO2, color="red", lw=2, zorder=5)
plt.text(0.3, 200.0, 'CO$_2$', fontsize=18, color="red")

plt.show()


scm.plams.finish()
