import scm.pyzacros as pz

# xCO=0.54
job = pz.ZacrosJob.load_external( path="plams_workdir/plamsjob.034" )
job.results.last_lattice_state().plot()
job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True )
job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )

# xCO=0.55
job = pz.ZacrosJob.load_external( path="plams_workdir/plamsjob.035" )
job.results.last_lattice_state().plot()
job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True )
job.results.plot_molecule_numbers( ["CO2"], normalize_per_site=True, derivative=True )
