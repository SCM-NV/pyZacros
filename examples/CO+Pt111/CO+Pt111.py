import scm.plams
import scm.pyzacros
import os

def main():
    scm.plams.init()

    mol = scm.plams.Molecule( 'CO_ads+Pt111.xyz' )

    #results_ads = run_pes_exploration(mol) #AMSResults
    #results_bs = run_binding_sites(results_ads) #AMSResults
    ##job = scm.plams.AMSJob.load_external( path="plams_workdir.ok/pes_exploration" ); results_ads=job.results
    ##job = scm.plams.AMSJob.load_external( path="plams_workdir.ok/binding_sites" ); results_bs=job.results

    #loader_ads = get_rkf_loader(results_ads) #RKFLoader
    #loader_bs = get_rkf_loader(results_bs) #RKFLoader

    #loader_bs.lattice.plot()
    #loader_bs.lattice.set_repeat_cell( (10,10) ) # create a 10x10 supercell
    #loader_bs.lattice.plot()

    #results_zacros = run_zacros(loader_ads, loader_bs) #ZacrosResults
    job = scm.pyzacros.ZacrosJob.load_external( path="plams_workdir.ok/zacros_job" ); results_zacros=job.results

    if( results_zacros.job.ok() ):
        results_zacros.plot_lattice_states( results_zacros.lattice_states() )
        #results_zacros.plot_molecule_numbers( ["CO*"] )

    scm.plams.finish()


def get_exploration_settings():
    """ Returns: Settings """
    engine_sett = scm.plams.Settings()
    engine_sett.input.ReaxFF.ForceField = 'CHONSFPtClNi.ff'
    engine_sett.input.ReaxFF.Charges.Solver = 'Direct'

    sett_ads = scm.plams.Settings()
    sett_ads.input.ams.Constraints.FixedRegion = 'surface'
    sett_ads.input.ams.Task = "PESExploration"
    sett_ads.input.ams.PESExploration.Job = 'ProcessSearch'
    sett_ads.input.ams.PESExploration.RandomSeed = 100
    sett_ads.input.ams.PESExploration.NumExpeditions = 30
    sett_ads.input.ams.PESExploration.NumExplorers = 4
    sett_ads.input.ams.PESExploration.SaddleSearch.MaxEnergy = 2.0
    sett_ads.input.ams.PESExploration.DynamicSeedStates = True
    sett_ads.input.ams.PESExploration.CalculateFragments = True
    sett_ads.input.ams.PESExploration.StatesAlignment.ReferenceRegion = 'surface'
    sett_ads.input.ams.PESExploration.StructureComparison.DistanceDifference = 0.1
    sett_ads.input.ams.PESExploration.StructureComparison.NeighborCutoff = 2.5
    sett_ads.input.ams.PESExploration.StructureComparison.EnergyDifference = 0.05
    sett_ads.input.ams.PESExploration.StructureComparison.CheckSymmetry = True
    sett_ads.input.ams.PESExploration.BindingSites.Calculate = True
    sett_ads.input.ams.PESExploration.BindingSites.NeighborCutoff = 3.8

    return sett_ads+engine_sett


def run_pes_exploration(mol: scm.plams.Molecule):
    """
        Runs and prints results from the PESExploration job.

        Returns: AMSResults
    """
    job = scm.plams.AMSJob(name='pes_exploration',
                           molecule=mol,
                           settings=get_exploration_settings())
    results_ads = job.run()

    energy_landscape = results_ads.get_energy_landscape() #EnergyLandscape
    print("Results from PES Exploration")
    print(energy_landscape)
    print("")

    return results_ads


def run_binding_sites(results_ads: scm.plams.AMSResults):
    """ Returns: AMSResults """
    exploration_dir = os.path.abspath(os.path.dirname(results_ads.rkfpath()))

    sett_bs = get_exploration_settings()
    sett_bs.input.ams.PESExploration.LoadEnergyLandscape.Path = exploration_dir
    sett_bs.input.ams.PESExploration.NumExpeditions = 1
    sett_bs.input.ams.PESExploration.NumExplorers = 1
    sett_bs.input.ams.PESExploration.GenerateSymmetryImages = True
    sett_bs.input.ams.PESExploration.CalculateFragments = False
    sett_bs.input.ams.PESExploration.StructureComparison.CheckSymmetry = False

    job = scm.plams.AMSJob(name='binding_sites',
                           molecule=results_ads.get_input_molecule(),
                           settings=sett_bs)
    results_bs = job.run()

    return results_bs


def get_rkf_loader(results: scm.plams.AMSResults):
    """
        Converts AMSResults into an RKFLoader
        Replaces site type names with 'fcc', 'br', 'hcp'

        Returns: RKFLoader
    """
    loader = scm.pyzacros.RKFLoader( results )
    loader.replace_site_types_names( ['A','B','C'], ['fcc','br','hcp'] )
    return loader


def run_zacros(loader_ads: scm.pyzacros.RKFLoader, loader_bs: scm.pyzacros.RKFLoader):
    """
        Constructs and prints the input for the Zacros job, and then runs it.

        Returns: ZacrosResults
    """

    settings = scm.pyzacros.Settings()
    settings.random_seed = 10
    settings.temperature = 273.15
    settings.pressure = 1.01325
    settings.molar_fraction.CO = 0.1

    dt = 1e-8
    settings.max_time = 1000*dt
    settings.snapshots = ('logtime', dt, 3.5)
    settings.species_numbers = ('time', dt)

    job = scm.pyzacros.ZacrosJob( name='zacros_job',
                                  lattice=loader_bs.lattice,
                                  mechanism=loader_ads.mechanism,
                                  cluster_expansion=loader_ads.clusterExpansion,
                                  settings=settings )
    print("Input to Zacros")
    print(job.get_input())

    results_pz = job.run()

    return results_pz


if __name__ == '__main__':
    main()
