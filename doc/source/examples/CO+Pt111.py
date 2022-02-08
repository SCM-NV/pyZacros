import scm.plams
import scm.pyzacros

mol = scm.plams.Molecule( 'CO_ads+Pt111.xyz' )

scm.plams.init()

engine_sett = scm.plams.Settings()
engine_sett.input.ReaxFF.ForceField = 'CHONSFPtClNi.ff'
engine_sett.input.ReaxFF.Charges = 'Solver=Direct'

sett_ads = scm.plams.Settings()
sett_ads.input.ams.Constraints.FixedRegion = 'surface'
sett_ads.input.ams.Task = "PESExploration"
sett_ads.input.ams.PESExploration.Job = 'ProcessSearch'
sett_ads.input.ams.PESExploration.RandomSeed = 100
sett_ads.input.ams.PESExploration.NumExpeditions = 10
sett_ads.input.ams.PESExploration.NumExplorers = 4
sett_ads.input.ams.PESExploration.DynamicSeedStates = True
sett_ads.input.ams.PESExploration.CalculateFragments = True
sett_ads.input.ams.PESExploration.BindingSites.Calculate = True
sett_ads.input.ams.PESExploration.BindingSites.NeighborCutoff = 3.8
sett_ads.input.ams.PESExploration.SaddleSearch.MaxEnergy = 2.0
sett_ads.input.ams.PESExploration.StatesAlignment.ReferenceRegion = 'surface'
sett_ads.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
sett_ads.input.ams.PESExploration.StructureComparison.NeighborCutoff = 2.5
sett_ads.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.05
sett_ads.input.ams.PESExploration.StructureComparison.CheckSymmetry = True

job = scm.plams.AMSJob(name='CO_ads+Pt111', molecule=mol, settings=sett_ads+engine_sett)
results_ads = job.run()

energy_landscape = results_ads.get_energy_landscape()
print(energy_landscape)

sett_bs = sett_ads.copy()
sett_bs.input.ams.PESExploration.LoadEnergyLandscape.Path= '../CO_ads+Pt111'
sett_bs.input.ams.PESExploration.NumExpeditions = 1
sett_ads.input.ams.PESExploration.NumExplorers = 1
sett_bs.input.ams.PESExploration.DynamicSeedStates = False
sett_bs.input.ams.PESExploration.GenerateSymmetryImages = True
sett_bs.input.ams.PESExploration.CalculateFragments = False
sett_bs.input.ams.PESExploration.StructureComparison.CheckSymmetry = False

job = scm.plams.AMSJob(name='CO_bs+Pt111', molecule=mol, settings=sett_bs+engine_sett)
results_bs = job.run()

loader_ads = scm.pyzacros.RKFLoader( results_ads )
loader_bs = scm.pyzacros.RKFLoader( results_bs )

loader_ads.replace_site_types_names( ['A','B','C'], ['fcc','br','hcp'] )
loader_bs.replace_site_types_names( ['A','B','C'], ['fcc','br','hcp'] )
loader_bs.lattice.set_repeat_cell( (10,10) )

loader_bs.lattice.plot()

initialState = scm.pyzacros.LatticeState( loader_bs.lattice, surface_species=loader_ads.mechanism.surface_species() )
initialState.fill_sites_random( site_name='fcc', species='CO*', coverage=0.05 )

settings = scm.pyzacros.Settings()
settings.random_seed = 10
settings.temperature = 273.15
settings.pressure = 1.01325
settings.molar_fraction.CO = 0.1

dt = 1e-8
settings.snapshots = ('logtime', dt, 3.5)
settings.species_numbers = ('time', dt)
settings.event_report = 'off'
settings.max_time = 1000*dt

job = scm.pyzacros.ZacrosJob( lattice=loader_bs.lattice, mechanism=loader_ads.mechanism,
                                cluster_expansion=loader_ads.clusterExpansion,
                                initial_state=initialState, settings=settings )
results_pz = job.run()

if( job.ok() ):
    results_pz.plot_lattice_states( results_pz.lattice_states() )
    results_pz.plot_molecule_numbers( ["CO*"] )

scm.plams.finish()
