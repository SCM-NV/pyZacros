Poisoning of Pt(111) by CO: From atomistic to mesoscopic modeling
-----------------------------------------------------------------

This example illustrates a procedure for simulating molecular phenomena on catalytic surfaces, starting from an atomic-level description up to a mesoscopic regime in an automated way and with the lowest human supervision possible. We follow the strategy based on the intercommunication and cooperation of the three packages AMS-driver (hereafter AMS for shorter), EON, and Zacros. The full workflow is carried out in python.

From the technical point of view, EON is combined with AMS at the source code level, and they work together transparently from an AMS user point of view (see PESExploration in the input file). On top of that, we used the PLAMS library to access AMS from python. On the other side, Zacros is coupled through pyZacros that generates the pyZacros objects from the AMS/EON results, run the calculation, and parse the output files to get back the calculation results to the python interface.

From the physical/chemical point of view, AMS is used to explore the energy landscape of the system by using specialized algorithms. Additionally, it processes the obtained energy landscape to calculate the binding sites and their interconnections. Finally, pyZacros translates this information to clusters, mechanisms, and binding-sites lattices (building blocks of a Zacros calculation) and runs the KMC (Kinetic Monte-Carlo) simulation to perform dynamic modeling of adsorption, desorption, surface diffusion, and/or reaction processes. Everything from a simple python script!

The example we show here is a toy model system for the adsorption and diffusion of carbon monoxide on the Pt(111) surface. We are not interested in an accurate description of the system itself. We are interested in studying a simple and computationally cheap design to start with and illustrate all possible issues we can face during the automation process. In particular, we will not consider any lateral interaction energy correction among CO molecules at this stage. The simulation described here basically shows the poisoning process of Pt(111) by CO.

This example shows how to conduct a Kinetic Monte-Carlo simulation of CO interacting with Pt(111) surface, starting from its atomic representation. To that aim, we use a 3x3 Pt(111) surface to avoid artificial lateral interactions between the CO and its periodic images. Here, it is essential to point out that both the absorption-sites and the reaction mechanisms will be automatically obtained from the results of the AMS calculation and translated appropriately to Zacros. There is not any predefined knowledge about the system. The expected mechanisms are sketched in the following figure.

.. image:: ../../images/CO+Pt111-sketch.png
   :scale: 60 %
   :align: center

As we said before, the only necessary information from the system is an initial guess for its geometry. We used the AMS GUI for this. Here we do not show details on how to do that, so please referees to our GUI's documentation. In a nutshell, we generated a 3x3 Pt(111) surface, put a CO molecule on top of it, and optimized the geometry by keeping the whole Pt(111) surface frozen. Additionally, we created two regions, namely 'adsorbate' and 'surface.' The former for the CO atoms and the latter for the atoms of the platinum surface.

To make this example reproducible, we provide the geometry in ``XYZ`` format. See the figure below.

.. |co_pt111_xyz| image:: ../../images/example_CO+Pt111-initxyz.png
   :scale: 60 %

.. csv-table::
   :header: |co_pt111_xyz|

   "Link to download: :download:`CO_ads+Pt111.xyz <CO_ads+Pt111.xyz>`"

.. Note::
  If you prepare the initial geometry yourself, keep in mind that you can start from a different geometry, and the final results should be identical. The only requirements are to select a local minimum and create the corresponding regions.

Now, you can download the complete example script from this link :download:`CO+Pt111.py <CO+Pt111.py>`. Hereafter, we briefly explain the different sections of the code.

The script starts as follows:

.. code-block:: python
  :linenos:

  import scm.plams
  import scm.pyzacros

  mol = scm.plams.Molecule( 'CO_ads+Pt111.xyz' )

  scm.plams.init()

Firstly we load the required python libraries: PLAMS and pyZacros (lines 1-2). Then, we create a PLAMS molecule using the XYZ geometry file we provided above (line 4). Take note that the molecule automatically includes the information about regions that are described in the XYZ file. Finally, we start the PLAM environment (line 6).

It is convenient to divide our script into four parts for clarity. In the first part (:ref:`getting_energy_landscape`), we will obtain the symmetry's irreducible energy landscape for this system, which will indirectly allow us to define the associated reaction mechanisms and the cluster expansion Hamiltonian. In the second part (:ref:`getting_kmc_lattice`), we will get the KMC lattice, which requires applying all symmetry operators of the Pt surface. In the third part (:ref:`generating_pyzacros_objects`), we will use this information to create the corresponding pyZacros to finally, in the fourth part (:ref:`running_pyzacros_simulation`), run the KMC simulation itself.

.. _getting_energy_landscape:

Getting the Energy Landscape
============================

This section aims to get the energy landscape of the system, but by being careful of getting only the states that are irreducible by symmetry. This requirement significantly reduces the computational effort of the calculation and simplifies the analysis of the obtained results. This section references the section of code shown below:

.. code-block:: python
  :linenos:
  :lineno-start: 8

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

  job = scm.plams.AMSJob(name='CO_ads+Pt111', molecule=mol, settings=sett_ads+engine_sett)
  results_ads = job.run()

  energy_landscape = results_ads.get_energy_landscape()
  print(energy_landscape)


This code basically setup a PESExploration calculation using AMS and run it. We will describe the most relevant options in this context. For more information, please referees to our AMS user's manual.

Lines 8-10 select the engine to use. Here we chose the reactive force field (ReaxFF) method in combination with the parameterization 'CHONSFPtClNi.ff,' which has been specially designed to study the surface oxidation of Pt(111).

Lines 12-28 specify the PESExploration task settings. The results of this calculation are the set of critical points that compose the energy landscape, what we call the energy landscape for short. Here we fix the position of the platinum surface atoms (line 13), use the ProcesSearch method to find the escape mechanisms from the different states (line 15), distributed in 10 expeditions with 4 explorers each (lines 17-18), and allow transition states within a 2 eV energy window (line 19). Any newfound local minimum is used as the origin of a new expedition (line 19). For the final set of local minima found, a geometry optimization of the corresponding independent fragments (CO and Pt surface) is carried out to consider the gas-phase configurations into the energy landscape (line 20). The two fragments are defined as 1) the atoms belonging to the reference region and 2) the rest, equivalently to the adsorbate atoms. Additionally, all obtained states will be aligned with respect to this reference (line 21).

For the structure comparison, we establish that the structures are the same if their interatomic distances are less than 0.1 A in neighborhoods of 2.5 A and energy differences are less than 0.05 eV (lines 25-27). Additionally, we verify that molecules are irreducible by the symmetry operations of the Pt surface (line 28).

.. code-block:: none
  :linenos:

  All stationary points:
  ======================
  State 1: COPt36 local minimum @ -7.65164210 Hartree (found 1 times, results on State-1_MIN)
  State 2: COPt36 local minimum @ -7.65157184 Hartree (found 1 times, results on State-2_MIN)
  State 3: COPt36 local minimum @ -7.62381952 Hartree (found 1 times, results on State-3_MIN)
  State 4: COPt36 transition state @ -7.62254756 Hartree (found 5 times, results on State-4_TS_2-3)
    +- Reactants: State 2: COPt36 local minimum @ -7.65157184 Hartree (found 1 times, results on State-2_MIN)
       Products:  State 3: COPt36 local minimum @ -7.62381952 Hartree (found 1 times, results on State-3_MIN)
       Prefactors: 1.586E+13:2.362E+12
  State 5: COPt36 transition state @ -7.62242984 Hartree (found 3 times, results on State-5_TS_3-1)
    +- Reactants: State 3: COPt36 local minimum @ -7.62381952 Hartree (found 1 times, results on State-3_MIN)
       Products:  State 1: COPt36 local minimum @ -7.65164210 Hartree (found 1 times, results on State-1_MIN)
       Prefactors: 2.205E+12:1.504E+13
  Fragment 1: CO local minimum @ -0.42445368 Hartree (results on Fragment-1)
  Fragment 2: Pt36 local minimum @ -7.154286 Hartree (results on Fragment-2)
  FragmentedState 1: CO+Pt36 local minimum @ -7.57874007 Hartree (fragments [1, 2])
    +- State 1: COPt36 local minimum @ -7.65164210 Hartree (found 1 times, results on State-1_MIN)
    |  Prefactors: 8.051E+06:1.668E+16
    +- State 2: COPt36 local minimum @ -7.65157184 Hartree (found 1 times, results on State-2_MIN)
    |  Prefactors: 8.051E+06:1.642E+16
    +- State 3: COPt36 local minimum @ -7.62381952 Hartree (found 1 times, results on State-3_MIN)
       Prefactors: 8.051E+06:2.446E+15

.. code-block:: none

   $ amsmovie plams_workdir/CO_ads+Pt111/ams.rkf

.. image:: ../../images/example_CO+Pt111-iel.png
   :scale: 80 %
   :align: center


.. code-block:: none

   $ amsinput plams_workdir/CO_ads+Pt111/ams.rkf

.. image:: ../../images/example_CO+Pt111-ibs.png
   :scale: 60 %
   :align: center


.. _getting_kmc_lattice:

Getting the KMC Lattice
=======================


.. code-block:: python
  :linenos:
  :lineno-start: 36

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


.. code-block:: none

   $ amsmovie plams_workdir/CO_bs+Pt111/ams.rkf


.. image:: ../../images/example_CO+Pt111-bs.png
   :scale: 60 %
   :align: center


.. _generating_pyzacros_objects:

Generating the pyZacros objects
===============================

.. code-block:: python
  :linenos:
  :lineno-start: 48

  loader_ads = scm.pyzacros.RKFLoader( results_ads )
  loader_bs = scm.pyzacros.RKFLoader( results_bs )

  loader_ads.replace_site_types_names( ['A','B','C'], ['fcc','br','hcp'] )
  loader_bs.replace_site_types_names( ['A','B','C'], ['fcc','br','hcp'] )
  loader_bs.lattice.set_repeat_cell( (10,10) )


The following figure is a schematic representation of reaction processes as defined in AMS and pyZacros. The pyZacros' RKFLoader class translates from one to the other. Red crosses represent the binding sites. A and B are the attached atoms to the binding sites (parent atoms), and R is the remainder of the adsorbed molecule.

.. image:: ../../images/example_CO+Pt111-rfkloader.png
   :scale: 60 %
   :align: center

.. code-block:: python
  :linenos:

  print(loader_ads.clusterExpansion)
  print(loader_ads.mechanism)
  loader_bs.lattice.plot()

.. code-block:: none

  mechanism

  reversible_step CO*_0-fcc,*_1-br<-->*_0-fcc,CO*_1-br;(0,1)
    sites 2
    neighboring 1-2
    initial
      1 CO* 1
      2 * 1
    final
      1 * 1
      2 CO* 1
    site_types fcc br
    pre_expon  1.58623e+13
    pe_ratio  6.71496e+00
    activ_eng  7.89791e-01
  end_reversible_step

  ...
  end_mechanism


.. code-block:: none

  energetics

  cluster CO*_0-fcc,*_1-br:(0,1)
    sites 2
    neighboring 1-2
    lattice_state
      1 CO* 1
      2 * 1
    site_types fcc br
    graph_multiplicity 2
    cluster_eng -1.98185e+00
  end_cluster

  ...
  end_energetics

.. image:: ../../images/example_CO+Pt111-lattice.png
   :scale: 60 %
   :align: center


.. _running_pyzacros_simulation:

Running the pyZacros simulation
===============================

.. code-block:: python
  :linenos:
  :lineno-start: 60

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


.. code-block:: python
  :linenos:
  :lineno-start: 77

  if( job.ok() ):
      results_pz.plot_lattice_states( results_pz.lattice_states() )
      results_pz.plot_molecule_numbers( ["CO*"] )

  scm.plams.finish()

.. image:: ../../images/example_CO+Pt111-ls.png
   :scale: 60 %
   :align: center

.. image:: ../../images/example_CO+Pt111-mn.png
   :scale: 60 %
   :align: center
