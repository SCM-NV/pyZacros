import scm.plams
import scm.pyzacros as pz

scm.pyzacros.init()

job = scm.pyzacros.load("plams_workdir/plamsjob/plamsjob.dill")
results = job.results

scm.pyzacros.finish()

print((8 + 10 + 15 + 15 + 10 + 5) * "-")
print("%8s" % "iter", "%10s" % "TOF_CO2", "%15s" % "max_time", "%15s" % "TOF_CO2_error", "%10s" % "conv?")
print("%8s" % "", "%10s" % "mol/s/site", "%15s" % "s", "%15s" % "mol/s/site", "%10s" % "")
print((8 + 10 + 15 + 15 + 10 + 5) * "-")

for i, step in enumerate(results.history()):
    print(
        "%8d" % i,
        "%10.5f" % step["turnover_frequency"]["CO2"],
        "%15d" % step["max_time"],
        "%15.5f" % step["turnover_frequency_error"]["CO2"],
        "%10s" % step["converged"]["CO2"],
    )

import matplotlib.pyplot as plt

fig = plt.figure()
ax = plt.axes()
ax.set_xlabel("Time (s)", fontsize=14)
ax.set_ylabel("CO$_2$ Production (mol/site)", fontsize=14)

colors = "bgrcmykb"
for i in range(results.niterations()):
    for j in range(results.nreplicas()):
        molecule_numbers = results.children_results(i, j).molecule_numbers(["CO2"], normalize_per_site=True)
        ax.plot(molecule_numbers["Time"], molecule_numbers["CO2"], lw=3, color=colors[i], zorder=-i)
        ax.vlines(
            max(molecule_numbers["Time"]),
            0,
            max(molecule_numbers["CO2"]),
            colors="0.8",
            linestyles="--",
        )

plt.show()
