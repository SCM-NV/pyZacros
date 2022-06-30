import scm.plams
import scm.pyzacros as pz

# Gas species
CO_g = pz.Species("CO")
O2_g = pz.Species("O2")
CO2_g = pz.Species("CO2", gas_energy=-2.337)

# Surface species
s0 = pz.Species("*")   # Empty adsorption site
CO_s = pz.Species("CO*")
O_s = pz.Species("O*")

# Species List
spl = pz.SpeciesList([CO_g,O2_g,CO2_g,s0,CO_s])
spl.append( O_s )
print(spl)

# Lattice setup
lat = pz.Lattice( lattice_type=pz.Lattice.TRIANGULAR,
                  lattice_constant=1.0, repeat_cell=[10,3] )

print(lat)

lat.plot()

# Clusters
CO_p = pz.Cluster( species=[CO_s], cluster_energy=-1.3 )
O_p = pz.Cluster( species=[O_s], cluster_energy=-2.3 )
print(CO_p)

# Cluster Expansion
ce = pz.ClusterExpansion([CO_p, O_p])
print(ce)

# Elementary Reactions
CO_ads = pz.ElementaryReaction( initial=[s0, CO_g], final=[CO_s],
                                reversible=False, pre_expon=10.0,
                                label="CO_adsorption" )

O2_ads = pz.ElementaryReaction( initial=[s0, s0, O2_g], final=[O_s, O_s], neighboring=[(0,1)],
                                reversible=False, pre_expon=2.5,
                                label="O2_adsorption" )

CO_oxi = pz.ElementaryReaction( initial=[CO_s, O_s], final=[s0, s0, CO2_g],
                                neighboring=[(0,1)],
                                reversible=False, pre_expon=1.0e+20,
                                label="CO_oxidation")

mech = pz.Mechanism([O2_ads, CO_ads, CO_oxi])

print(mech)

# LatticeState setup (initial state)
ist = pz.LatticeState(lat, surface_species=spl.surface_species())
ist.fill_sites_random(site_name='StTp1', species='CO*', coverage=0.1)
ist.fill_sites_random(site_name='StTp1', species='O*', coverage=0.1)

print(ist)

ist.plot()

scm.plams.init()

# Settings:
sett = pz.Settings()
sett.random_seed = 953129
sett.temperature = 500.0
sett.pressure = 1.0
sett.snapshots = ('time', 0.1)
sett.process_statistics = ('time', 0.1)
sett.species_numbers = ('time', 0.1)
sett.event_report = 'off'
sett.max_steps = 'infinity'
sett.max_time = 1.0

sett.molar_fraction.CO = 0.45
sett.molar_fraction.O2 = 0.55

print(sett)

job = pz.ZacrosJob( settings=sett, lattice=lat,
                    mechanism=[CO_ads, O2_ads, CO_oxi],
                    cluster_expansion=[CO_p, O_p] )

print(job)

results = job.run()

if( job.ok() ):
   provided_quantities = results.provided_quantities()
   print("nCO2 =", provided_quantities['CO2'])

   results.plot_molecule_numbers( results.gas_species_names() )
   results.plot_lattice_states( results.lattice_states() )

   pstat = results.get_process_statistics()
   results.plot_process_statistics( pstat, key="number_of_events" )

scm.plams.finish()
