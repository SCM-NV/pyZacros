import numpy as np
import adaptiveDesignProcedure as adp
import matplotlib.pyplot as plt

path = "plams_workdir.007/adp.results/"

x_CO_model = np.linspace(0.2,0.8,201)
ac_O_model,ac_CO_model,TOF_CO2_model = adp.predict( x_CO_model.reshape(-1,1), path ).T

ax = plt.axes()
ax.set_xlabel('Molar Fraction CO', fontsize=14)

ax.set_ylabel("Coverage Fraction (%)", color="blue", fontsize=14)
ax.plot(x_CO_model, ac_O_model, color="blue", linestyle="-.", lw=2, zorder=1)
ax.plot(x_CO_model, ac_CO_model, color="blue", linestyle="-", lw=2, zorder=2)
plt.text(0.3, 0.9, 'O', fontsize=18, color="blue")
plt.text(0.7, 0.9, 'CO', fontsize=18, color="blue")

ax2 = ax.twinx()
ax2.set_ylabel("TOF (mol/s/site)",color="red", fontsize=14)
ax2.plot(x_CO_model, TOF_CO2_model, color='red', linestyle='-', lw=2, zorder=0)
plt.text(0.37, 1.5, 'CO$_2$', fontsize=18, color="red")

plt.show()
