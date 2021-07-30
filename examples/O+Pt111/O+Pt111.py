# export PYTHONPATH=$HOME/Develop/pyZacros:$AMSHOME/scripting:$PYTHONPATH

import scm.plams
from pyzacros.classes.InitialState import InitialState
from pyzacros.classes.RKFLoader import RKFLoader
from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.KMCJob import KMCJob

scm.plams.init()

molecule = scm.plams.Molecule( "O+Pt111.xyz" )
for atom in molecule:
    if( atom.symbol == "O" ):
        atom.properties.suffix = "region=adsorbate"
    else:
        atom.properties.suffix = "region=surface"

settings = scm.plams.Settings()
settings.input.ams.Task = "PESExploration"

settings.input.ams.Constraints.FixedRegion = "surface"

settings.input.ams.PESExploration.Job = "ProcessSearch"
settings.input.ams.PESExploration.RandomSeed = 100
settings.input.ams.PESExploration.NumExpeditions = 50
settings.input.ams.PESExploration.NumExplorers = 4
settings.input.ams.PESExploration.DynamicSeedStates = True
settings.input.ams.PESExploration.SaddleSearch.MaxEnergy = 2.0
settings.input.ams.PESExploration.Optimizer.ConvergedForce = 0.001
settings.input.ams.PESExploration.BindingSites.Calculate = True
settings.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
settings.input.ams.PESExploration.StructureComparison.NeighborCutoff = 10.0
settings.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.1
settings.input.ams.PESExploration.StatesAlignment.ReferenceRegion = "surface"
settings.input.ams.PESExploration.BindingSites.AllowDisconnected = False

settings.input.ReaxFF
settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
settings.input.ReaxFF.Charges.Solver = "direct"

job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="PESExploration")
results = job.run()

scm.plams.finish()

loader = RKFLoader( results )

#loader.replace( site_name='A', 'fcc' )
#loader.replace( site_name='B', 'hcp' )
loader.lattice.repeat_cell = [10,10]

print(loader.mechanism)

initialState = InitialState( loader.lattice, mechanism=loader.mechanism )
#initialState.fillSites( site_name='fcc', species='O1*', coverage=0.5 )
initialState.fillSites( site_name='A', species='O1*', coverage=0.5 )

settings = KMCSettings()
settings.random_seed = 10
settings.temperature = 273.15
settings.pressure = 1.01325
settings.snapshots = ('event', 1)
settings.process_statistics = ('event', 1)
settings.species_numbers = ('event', 1)
settings.event_report = 'off'
settings.max_steps = 5000
#settings.max_time = 250.0
#settings.wall_time = 30

job = KMCJob( lattice=loader.lattice, mechanism=loader.mechanism,
                cluster_expansion=loader.clusterExpansion,
                initialState=initialState, settings=settings, name='ZACROS' )
results = job.run()

