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
settings.input.ams.Task = "ProcessSearch-EON"

settings.input.ams.Constraints.FixedRegion = "surface"

settings.input.ams.EON.RandomSeed = 100
settings.input.ams.EON.SamplingFreq = "Normal"
settings.input.ams.EON.NumJobs = 150
settings.input.ams.EON.DynamicSeedStates = True

settings.input.ams.EON.SaddleSearch.MinModeMethod = "dimer"
settings.input.ams.EON.SaddleSearch.DisplaceRadius = 4.0
settings.input.ams.EON.SaddleSearch.DisplaceMagnitude = 0.01
settings.input.ams.EON.SaddleSearch.MaxEnergy = 2.0

settings.input.ams.EON.Optimizer.Method = "CG"
settings.input.ams.EON.Optimizer.ConvergedForce = 0.001
settings.input.ams.EON.Optimizer.MaxIterations = 2000

settings.input.ams.EON.StructureComparison.DistanceDifference = 0.1
settings.input.ams.EON.StructureComparison.NeighborCutoff = 10.0
settings.input.ams.EON.StructureComparison.CheckRotation = False
settings.input.ams.EON.StructureComparison.IndistinguishableAtoms = True
settings.input.ams.EON.StructureComparison.EnergyDifference = 0.1
settings.input.ams.EON.StructureComparison.RemoveTranslation = True

settings.input.ams.EON.EnergyLandscape.Adsorbate = "adsorbate"
settings.input.ams.EON.BindingSites.DistanceDifference = 5.0
settings.input.ams.EON.BindingSites.AllowDisconnected = False

settings.input.ReaxFF
settings.input.ReaxFF.ForceField = "CHONSFPtClNi.ff"
settings.input.ReaxFF.Charges.Converge.Charge = 1e-12

settings.input.ams.Properties.NormalModes = True

job = scm.plams.AMSJob(molecule=molecule, settings=settings, name="ProcessSearch-EON")
results = job.run()

scm.plams.finish()

loader = RKFLoader( results )

#loader.replace( site_name='A', 'fcc' )
#loader.replace( site_name='B', 'hcp' )
loader.lattice.repeat_cell = [10,10]

initialState = InitialState( loader.lattice, mechanism=loader.mechanism )
#initialState.fillSites( site_name='fcc', species='O1*', coverage=0.5 )
initialState.fillSites( site_name='A', species='O1*', coverage=0.5 )

myRKFLoader = RKFLoader( results )

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

#job = KMCJob( lattice=loader.lattice, clusters=loader.clusters,
                #mechanism=loader.mechanism, initialState=initialState,
                #settings=settings, name='ZACROS' )
job = KMCJob( lattice=loader.lattice, mechanism=loader.mechanism,
                initialState=initialState, settings=settings, name='ZACROS' )
results = job.run()

