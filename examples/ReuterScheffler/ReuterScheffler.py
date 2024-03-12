import scm.pyzacros as pz
import scm.pyzacros.models

rs = pz.models.ReuterScheffler()

scm.pyzacros.init()

dt = 1e-6
sett = pz.Settings()
sett.random_seed = 14390
sett.temperature = 600.0
sett.pressure = 1.0
sett.snapshots = ("time", 100 * dt)
sett.process_statistics = ("time", 10 * dt)
sett.species_numbers = ("time", dt)
sett.event_report = "off"
sett.max_steps = "infinity"
sett.max_time = 1000 * dt
sett.wall_time = 600

sett.molar_fraction.CO = 0.995
sett.molar_fraction.O2 = 1.0 - sett.molar_fraction.CO

job = pz.ZacrosJob(settings=sett, lattice=rs.lattice, mechanism=rs.mechanism, cluster_expansion=rs.cluster_expansion)

results = job.run()

if job.ok():
    results.plot_molecule_numbers(["CO2"])
    print("turnover_frequency = ", results.turnover_frequency(species_name="CO2")[0])

scm.pyzacros.finish()
