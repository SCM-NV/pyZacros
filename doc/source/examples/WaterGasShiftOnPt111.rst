.. _pyzacros-wgs-tutorial:

Water-Gas Shift Reaction on Pt(111)
-----------------------------------

This tutorial shows how to translate a typical Zacros workflow to pyZacros.
To do this, we will look at the water-gas shift reaction on Pt(111). The required physical/chemical descriptions of the system have been published in the `literature <https://zacros.org/tutorials/10-tutorial-4-dft-energies-to-zacros-input?showall=1>`__.

This example shows how to include gas species, transition states, as well as stable surface species, and the lateral interactions between them. All information about the energetics was obtained via density functional theory (DFT) calculations. Importantly, lateral interactions are also discussed and included in the example script.

The script can be downloaded through this link: :download:`WaterGasShiftOnPt111.py <../../../examples/WaterGasShiftOnPt111/WaterGasShiftOnPt111.py>`

The following section will discuss the structure of the script step-by-step.
You can also :ref:`skip ahead <label-pyzacros-wgs-output>` to check out the results of the simulation.


pyZacros Setup
++++++++++++++

A pyZacros script always starts by loading the pyZacros module. For this example, we also define the ``pz`` alias in order to quickly access the necessary functions.

.. code-block:: python
  :linenos:

  import scm
  import scm.pyzacros as pz


We then proceed by defining the chemical species that make up the reaction system. This is done using the ``Species`` API. By default, the reference energy is set to 0. By including an ``*`` in the name of a species, they are automatically designated as an adsorbate.

.. code-block:: python
  :linenos:

  # ---------------------------------------------
  # Species:
  # ---------------------------------------------
  # - Gas-species:
  CO_gas = pz.Species("CO")
  H2O_gas = pz.Species("H2O")
  H2_gas = pz.Species("H2")
  CO2_gas = pz.Species("CO2", gas_energy=-0.615)
  O2_gas = pz.Species("O2", gas_energy=4.913)

  # - Surface species:
  s0 = pz.Species("*", 1) # Empty adsorption site
  CO_adsorbed = pz.Species("CO*", 1)
  H2O_adsorbed = pz.Species("H2O*", 1)
  OH_adsorbed = pz.Species("OH*", 1)
  O_adsorbed = pz.Species("O*", 1)
  H_adsorbed = pz.Species("H*", 1)
  COOH_adsorbed = pz.Species("COOH*", 1)


For constructing the lattice, we will use the built-in hexagonal lattice provided by pyZacros:

.. code-block:: python
  :linenos:

  # ---------------------------------------------
  # Lattice setup:
  # ---------------------------------------------
  latt = pz.Lattice(lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0, repeat_cell=[8, 10])


Now that we have a lattice, we can proceed by writing down the adsorption energies and the lateral interactions. For this example, we will limit ourselves to a small selection of nearest-neighbor interactions. Our set of cluster energies is then collected in a ``ClusterExpansion``. This is a special Python list that allows us to more conveniently access the cluster energies.

.. code-block:: python
  :linenos:

  # ---------------------------------------------
  # Clusters:
  # ---------------------------------------------
  CO_point = pz.Cluster(species=[CO_adsorbed], energy=-2.077, label="CO_point")
  H2O_point = pz.Cluster(species=[H2O_adsorbed], energy=-0.362, label="H2O_point")
  OH_point = pz.Cluster(species=[OH_adsorbed], energy=0.830, label="OH_point")
  O_point = pz.Cluster(species=[O_adsorbed], energy=1.298, label="O_point")
  H_point = pz.Cluster(species=[H_adsorbed], energy=-0.619, label="H_point")
  COOH_point = pz.Cluster(species=[COOH_adsorbed], energy=-1.487, label="COOH_point")

  CO_pair_1NN = pz.Cluster(species=[CO_adsorbed, CO_adsorbed], neighboring=[(0, 1)], energy=0.560, label="CO_pair_1NN")
  OH_H_1NN = pz.Cluster(species=[OH_adsorbed, H_adsorbed], neighboring=[(0, 1)], energy=0.021, label="OH_H_1NN")
  O_H_1NN = pz.Cluster(species=[O_adsorbed, H_adsorbed], neighboring=[(0, 1)], energy=0.198, label="O_H_1NN")
  CO_OH_1NN = pz.Cluster(species=[CO_adsorbed, OH_adsorbed], neighboring=[(0, 1)], energy=0.066, label="CO_OH_1NN")
  CO_O_1NN = pz.Cluster(species=[CO_adsorbed, O_adsorbed], neighboring=[(0, 1)], energy=0.423, label="CO_O_1NN")

  # ---------------------------------------------
  # Cluster expansion:
  # ---------------------------------------------
  myClusterExpansion = pz.ClusterExpansion()
  myClusterExpansion.extend([CO_point, H2O_point])
  myClusterExpansion.append(OH_point)
  myClusterExpansion.extend([O_point, H_point, COOH_point])
  myClusterExpansion.extend([CO_pair_1NN, OH_H_1NN, O_H_1NN, CO_OH_1NN, CO_O_1NN])

The reaction mechanism is constructed by writing out the elementary steps. For each reaction, we define the reactants and products, the reversibility, and the kinetic parameters. (Note how the parameter names match those found in the Zacros input files.)

.. code-block:: python
  :linenos:

  # ---------------------------------------------
  # Elementary Reactions
  # ---------------------------------------------
  CO_adsorption = pz.ElementaryReaction(
      initial=[s0, CO_gas],
      final=[CO_adsorbed],
      reversible=True,
      pre_expon=2.226e007,
      pe_ratio=2.137e-006,
      activation_energy=0.0,
      label="CO_adsorption",
  )

  H2_dissoc_adsorp = pz.ElementaryReaction(
      initial=[s0, s0, H2_gas],
      final=[H_adsorbed, H_adsorbed],
      neighboring=[(0, 1)],
      reversible=True,
      pre_expon=8.299e007,
      pe_ratio=7.966e-006,
      activation_energy=0.0,
      label="H2_dissoc_adsorp",
  )

  H2O_adsorption = pz.ElementaryReaction(
      initial=[s0, H2O_gas],
      final=[H2O_adsorbed],
      reversible=True,
      pre_expon=2.776e002,
      pe_ratio=2.665e-006,
      activation_energy=0.0,
      label="H2O_adsorption",
  )

  H2O_dissoc_adsorp = pz.ElementaryReaction(
      initial=[H2O_adsorbed, s0],
      final=[OH_adsorbed, H_adsorbed],
      neighboring=[(0, 1)],
      reversible=True,
      pre_expon=1.042e13,
      pe_ratio=1.000e00,
      activation_energy=0.777,
      label="H2O_dissoc_adsorp",
  )

  OH_decomposition = pz.ElementaryReaction(
      initial=[s0, OH_adsorbed],
      final=[O_adsorbed, H_adsorbed],
      neighboring=[(0, 1)],
      reversible=True,
      pre_expon=1.042e13,
      pe_ratio=1.000e00,
      activation_energy=0.940,
      label="OH_decomposition",
  )

  COOH_formation = pz.ElementaryReaction(
      initial=[CO_adsorbed, OH_adsorbed],
      final=[s0, COOH_adsorbed],
      neighboring=[(0, 1)],
      reversible=True,
      pre_expon=1.042e13,
      pe_ratio=1.000e00,
      activation_energy=0.405,
      label="COOH_formation",
  )

  COOH_decomposition = pz.ElementaryReaction(
      initial=[COOH_adsorbed, s0],
      final=[s0, H_adsorbed, CO2_gas],
      neighboring=[(0, 1)],
      reversible=False,
      pre_expon=1.042e13,
      activation_energy=0.852,
      label="COOH_decomposition",
  )

  CO_oxidation = pz.ElementaryReaction(
      initial=[CO_adsorbed, O_adsorbed],
      final=[s0, s0, CO2_gas],
      neighboring=[(0, 1)],
      reversible=False,
      pre_expon=1.042e13,
      activation_energy=0.988,
      label="CO_oxidation",
  )

  # ---------------------------------------------
  # Full mechanism:
  # ---------------------------------------------
  mech = pz.Mechanism(
      [
          CO_adsorption,
          H2_dissoc_adsorp,
          H2O_adsorption,
          H2O_dissoc_adsorp,
          OH_decomposition,
          COOH_formation,
          COOH_decomposition,
          CO_oxidation
      ]
  )


Lastly, we define the general simulation settings. By creating a ``Settings`` object, we automatically load the default Zacros parameters. For this tutorial, we will use a short simulation time in order to quickly see the results of our simulation.

.. code-block:: python
  :linenos:

  # ---------------------------------------------
  # Settings:
  # ---------------------------------------------
  sett = pz.Settings()

  sett.molar_fraction.CO = 1.0e-5
  sett.molar_fraction.H2O = 0.950

  sett.random_seed = 123278
  sett.temperature = 500.0
  sett.pressure = 10.0
  sett.snapshots = ("time", 5.0e-4)
  sett.process_statistics = ("time", 5.0e-4)
  sett.species_numbers = ("time", 5.0e-4)
  sett.event_report = "off"
  sett.max_steps = "infinity"
  sett.max_time = 0.25


When we want to run a pyZacros job, we first start up Zacros itself by using the ``init()`` call. We then collect all of our settings into a ``ZacrosJob``. The example script uses the ``print`` function to now show you an overview of the final settings, using the familiar Zacros input format (:ref:`shown below <label-pyzacros-wgs-overview>`).

The ``run`` function is used to start the actual Zacros simulation. Once the job has finished, we can use one of the built-in post-processing functions to plot the transient profiles for our key reaction species.

.. code-block:: python
  :linenos:

  scm.pyzacros.init()

  job = pz.ZacrosJob(settings=sett, lattice=latt, mechanism=mech, cluster_expansion=myClusterExpansion)

  print(job)
  results = job.run()

  if job.ok():
      results.plot_molecule_numbers(["CO*", "H*", "H2O*", "COOH*"])

  scm.pyzacros.finish()


The ``finish()`` call is used to wrap up the Zacros job and close the script.


.. _label-pyzacros-wgs-output:

Running the Simulation
++++++++++++++++++++++

pyZacros scripts are executed using PLAMS. The PLAMS documentation contains `examples <../../Tutorials/WorkflowsAndAutomation/PythonScriptingWithPLAMS.html>`__ for running Python workflows on Windows, Linux and MacOS systems.
If you are using the default AMS installation:

``$AMSBIN/amspython WaterGasShiftOnPt111.py``

The script will first print an overview of the provided simulation parameters.
The actual simulation (denoted by the ``plamsjob``) will then start running. This example script only runs for a very short time, and should finish in under 1 minute.
A figure will be shown at the end of the simulation, containing the transient composition of surface species.

.. figure:: ../../images/example_WaterGasShiftOnPt111.png
   :scale: 100 %
   :align: center

.. _label-pyzacros-wgs-overview:

.. code-block:: none
  :linenos:

  $ amspython WaterGasShiftOnPt111.py
  PLAMS working folder: /home/user/pyzacros/examples/WaterGasShiftOnPt111/plams_workdir
  ---------------------------------------------------------------------
  simulation_input.dat
  ---------------------------------------------------------------------
  random_seed         123278
  temperature          500.0
  pressure              10.0

  snapshots                 on time       0.0005
  process_statistics        on time       0.0005
  species_numbers           on time       0.0005
  event_report      off
  max_steps         infinity
  max_time          0.25

  n_gas_species    4
  gas_specs_names              CO           H2          H2O          CO2
  gas_energies        0.00000e+00  0.00000e+00  0.00000e+00 -6.15000e-01
  gas_molec_weights   2.79949e+01  2.01560e+00  1.80105e+01  4.39898e+01
  gas_molar_fracs     1.00000e-05  0.00000e+00  9.50000e-01  0.00000e+00

  n_surf_species    6
  surf_specs_names         CO*        H*      H2O*       OH*        O*     COOH*
  surf_specs_dent            1         1         1         1         1         1

  finish
  ---------------------------------------------------------------------
  lattice_input.dat
  ---------------------------------------------------------------------
  lattice default_choice
    hexagonal_periodic 1.0 8 10
  end_lattice
  ---------------------------------------------------------------------
  energetics_input.dat
  ---------------------------------------------------------------------
  energetics

  cluster CO_point
    sites 1
    lattice_state
      1 CO* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng -2.07700e+00
  end_cluster

  cluster H2O_point
    sites 1
    lattice_state
      1 H2O* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng -3.62000e-01
  end_cluster

  cluster OH_point
    sites 1
    lattice_state
      1 OH* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng  8.30000e-01
  end_cluster

  cluster O_point
    sites 1
    lattice_state
      1 O* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng  1.29800e+00
  end_cluster

  cluster H_point
    sites 1
    lattice_state
      1 H* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng -6.19000e-01
  end_cluster

  cluster COOH_point
    sites 1
    lattice_state
      1 COOH* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng -1.48700e+00
  end_cluster

  cluster CO_pair_1NN
    sites 2
    neighboring 1-2
    lattice_state
      1 CO* 1
      2 CO* 1
    site_types 1 1
    graph_multiplicity 1
    cluster_eng  5.60000e-01
  end_cluster

  cluster OH_H_1NN
    sites 2
    neighboring 1-2
    lattice_state
      1 OH* 1
      2 H* 1
    site_types 1 1
    graph_multiplicity 1
    cluster_eng  2.10000e-02
  end_cluster

  cluster O_H_1NN
    sites 2
    neighboring 1-2
    lattice_state
      1 O* 1
      2 H* 1
    site_types 1 1
    graph_multiplicity 1
    cluster_eng  1.98000e-01
  end_cluster

  cluster CO_OH_1NN
    sites 2
    neighboring 1-2
    lattice_state
      1 CO* 1
      2 OH* 1
    site_types 1 1
    graph_multiplicity 1
    cluster_eng  6.60000e-02
  end_cluster

  cluster CO_O_1NN
    sites 2
    neighboring 1-2
    lattice_state
      1 CO* 1
      2 O* 1
    site_types 1 1
    graph_multiplicity 1
    cluster_eng  4.23000e-01
  end_cluster

  end_energetics
  ---------------------------------------------------------------------
  mechanism_input.dat
  ---------------------------------------------------------------------
  mechanism

  reversible_step CO_adsorption
    gas_reacs_prods CO -1
    sites 1
    initial
      1 * 1
    final
      1 CO* 1
    site_types 1
    pre_expon  2.22600e+07
    pe_ratio  2.13700e-06
    activ_eng  0.00000e+00
  end_reversible_step

  reversible_step H2_dissoc_adsorp
    gas_reacs_prods H2 -1
    sites 2
    neighboring 1-2
    initial
      1 * 1
      2 * 1
    final
      1 H* 1
      2 H* 1
    site_types 1 1
    pre_expon  8.29900e+07
    pe_ratio  7.96600e-06
    activ_eng  0.00000e+00
  end_reversible_step

  reversible_step H2O_adsorption
    gas_reacs_prods H2O -1
    sites 1
    initial
      1 * 1
    final
      1 H2O* 1
    site_types 1
    pre_expon  2.77600e+02
    pe_ratio  2.66500e-06
    activ_eng  0.00000e+00
  end_reversible_step

  reversible_step H2O_dissoc_adsorp
    sites 2
    neighboring 1-2
    initial
      1 H2O* 1
      2 * 1
    final
      1 OH* 1
      2 H* 1
    site_types 1 1
    pre_expon  1.04200e+13
    pe_ratio  1.00000e+00
    activ_eng  7.77000e-01
  end_reversible_step

  reversible_step OH_decomposition
    sites 2
    neighboring 1-2
    initial
      1 * 1
      2 OH* 1
    final
      1 O* 1
      2 H* 1
    site_types 1 1
    pre_expon  1.04200e+13
    pe_ratio  1.00000e+00
    activ_eng  9.40000e-01
  end_reversible_step

  reversible_step COOH_formation
    sites 2
    neighboring 1-2
    initial
      1 CO* 1
      2 OH* 1
    final
      1 * 1
      2 COOH* 1
    site_types 1 1
    pre_expon  1.04200e+13
    pe_ratio  1.00000e+00
    activ_eng  4.05000e-01
  end_reversible_step

  step COOH_decomposition
    gas_reacs_prods CO2 1
    sites 2
    neighboring 1-2
    initial
      1 COOH* 1
      2 * 1
    final
      1 * 1
      2 H* 1
    site_types 1 1
    pre_expon  1.04200e+13
    activ_eng  8.52000e-01
  end_step

  step CO_oxidation
    gas_reacs_prods CO2 1
    sites 2
    neighboring 1-2
    initial
      1 CO* 1
      2 O* 1
    final
      1 * 1
      2 * 1
    site_types 1 1
    pre_expon  1.04200e+13
    activ_eng  9.88000e-01
  end_step

  end_mechanism
  [08.02|15:34:32] JOB plamsjob STARTED
  [08.02|15:34:32] JOB plamsjob RUNNING
  [08.02|15:34:57] JOB plamsjob FINISHED
  [08.02|15:34:57] JOB plamsjob SUCCESSFUL
  [08.02|15:35:10] PLAMS run finished. Goodbye
