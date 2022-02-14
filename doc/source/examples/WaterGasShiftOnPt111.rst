Water-gas shift reaction on Pt(111).
------------------------------------

This tutorial is intended to show how to use pyZacros from a Zacros perspective. Thus, we will literally show how to translate the Zacros input files to a pyZacros script. To do that, we use the system described in the Zacros tutorial `Mapping DFT Energies to Zacros Input as an example <https://zacros.org/tutorials/10-tutorial-4-dft-energies-to-zacros-input?showall=1>`_. All physical/chemical description of the system is described in detail there. This example shows how to include gas species, transition states, as well as stable surface species, and the lateral interactions between them. All information about the energetics is obtained via density functional theory (DFT) calculations. Importantly, lateral interactions are also discussed and included in the example's script. We invited you first to get familiar with the tutorial cited above to quickly appreciate the parallel between the Zacros input files and the pyZacros objects. This will allow you to follow line-by-line the example's python script easily.

You can download the example's python script from this link :download:`WaterGasShiftOnPt111.py <WaterGasShiftOnPt111.py>`.

If everything is working well, you should get the following information in the standard output and the figure shown at the end.

.. code-block:: none
  :linenos:

  $ amspython WaterGasShiftOnPt111.py
  [14.02|16:30:47] PLAMS working folder: /home/user/pyzacros/examples/WaterGasShiftOnPt111/plams_workdir
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
  max_time          250.0
  wall_time         30

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
  [14.02|16:30:47] JOB plamsjob STARTED
  [14.02|16:30:47] JOB plamsjob RUNNING
  [14.02|16:31:17] JOB plamsjob FINISHED
  [14.02|16:31:17] JOB plamsjob SUCCESSFUL
  [14.02|16:31:27] PLAMS run finished. Goodbye

.. image:: ../../images/example_WaterGasShiftOnPt111.png
   :scale: 100 %
   :align: center
