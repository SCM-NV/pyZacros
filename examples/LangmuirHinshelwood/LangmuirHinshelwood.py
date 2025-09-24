import scm.plams
import scm.pyzacros as pz
import scm.pyzacros.models

lh = pz.models.LangmuirHinshelwood()

scm.pyzacros.init()

dt = 5.0e-5

sett = pz.Settings()
sett.random_seed = 1609
sett.temperature = 300.0
sett.pressure = 1.000
sett.snapshots = ("time", 10 * dt)
sett.process_statistics = ("time", dt)
sett.species_numbers = ("time", dt)
sett.max_time = 100 * dt

sett.molar_fraction.O2 = 0.500
sett.molar_fraction.CO = 0.500

# Adsorption and diffusion scaling factors
for rxn in lh.mechanism:
    if "adsorption" in rxn.label():
        rxn.pre_expon *= 1e-2
    if "diffusion" in rxn.label():
        rxn.pre_expon *= 1e-2

job = pz.ZacrosJob(settings=sett, lattice=lh.lattice, mechanism=lh.mechanism, cluster_expansion=lh.cluster_expansion)

results = job.run()

if job.ok():
    results.plot_molecule_numbers(["CO2"])
    print("turnover_frequency = ", results.turnover_frequency(species_name="CO2")[0])

scm.pyzacros.finish()
