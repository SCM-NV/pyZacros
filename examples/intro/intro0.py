import scm
import scm.pyzacros as pz

# Gas species:
CO_g = pz.Species("CO")
O2_g = pz.Species("O2")
CO2_g = pz.Species("CO2", gas_energy=-2.337)

# Surface species:
s0 = pz.Species("*")      # Empty adsorption site
CO_s = pz.Species("CO*")
O_s = pz.Species("O*")

# Lattice setup:
lattice = pz.Lattice( lattice_type=pz.Lattice.RECTANGULAR,
                      lattice_constant=1.0, repeat_cell=[10,10] )
lattice.plot()

# Clusters:
CO_p = pz.Cluster( species=[CO_s], energy=-1.3 )
O_p = pz.Cluster( species=[O_s], energy=-2.3 )

# Elementary Reactions
CO_ads = pz.ElementaryReaction( initial=[s0, CO_g], final=[CO_s],
                                reversible=False, pre_expon=10.0, activation_energy=0.0 )

O2_ads = pz.ElementaryReaction( initial=[s0, s0, O2_g], final=[O_s, O_s], neighboring=[(0, 1)],
                                reversible=False, pre_expon=2.5, activation_energy=0.0 )

CO_oxi = pz.ElementaryReaction( initial=[CO_s, O_s], final=[s0, s0, CO2_g], neighboring=[(0, 1)],
                                reversible=False, pre_expon=1.0e+20, activation_energy=0.0)

scm.pyzacros.init()

# Settings:
sett = pz.Settings()
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 5.e-1)
sett.process_statistics = ('time', 1.e-2)
sett.species_numbers = ('time', 1.e-2)
sett.max_time = 25.0
sett.random_seed = 953129

sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55

myJob = pz.ZacrosJob( settings=sett, lattice=lattice,
                        mechanism=[CO_ads, O2_ads, CO_oxi],
                        cluster_expansion=[CO_p, O_p] )

results = myJob.run()

print( "nCO2 = ", results.provided_quantities()["CO2"][-10:] )
results.plot_molecule_numbers( results.gas_species_names() )
results.plot_molecule_numbers( results.surface_species_names() )

scm.pyzacros.finish()
