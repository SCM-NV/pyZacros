import numpy as np
import adaptiveDesignProcedure as adp
import matplotlib.pyplot as plt

path = "plams_workdir/adp.results/ml_ExtraTrees_forCFD.pkl"

x_CO_model = np.linspace(0.0,1.0,200)
TOF_CO2_model = adp.predict( x_CO_model.reshape(-1,1), path ).T[0]

fig = plt.figure()

ax = plt.axes()
ax.set_xlabel('Partial Pressure CO', fontsize=14)
ax.set_ylabel('TOF (mol/s/site)', fontsize=14)
ax.plot(x_CO_model, TOF_CO2_model, color='red', linestyle='-', lw=2)

plt.show()
