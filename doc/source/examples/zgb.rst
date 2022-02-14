The Ziff-Gulari-Barshad (ZGB) model.
------------------------------------

This tutorial is intended to show how to use pyZacros from a Zacros perspective. Thus, we will literally show how to translate the Zacros input files to a pyZacros script. To do that, we use the system described in the Zacros tutorial `Ziff-Gulari-Barshad Model in Zacros <https://zacros.org/index.php/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros?showall=1>`_. All physical/chemical description of the system is described in detail there. We invited you first to get familiar with the tutorial cited above to quickly appreciate the parallel between the Zacros input files and the pyZacros objects. This will allow you to follow line-by-line the example's python script easily.

You can download the example's python script from this link :download:`ZiffGulariBarshad.py <ZiffGulariBarshad.py>`.

If everything is working well, you should get the following information in the standard output and the figure shown at the end.

.. code-block:: none
  :linenos:

  [14.02|17:20:01] PLAMS working folder: /home/user/pyzacros/examples/ZiffGulariBarshad/plams_workdir
  ---------------------------------------------------------------------
  simulation_input.dat
  ---------------------------------------------------------------------
  random_seed         953129
  temperature          500.0
  pressure               1.0

  snapshots                 on time       0.5
  process_statistics        on time       0.01
  species_numbers           on time       0.01
  max_time          25.0

  n_gas_species    3
  gas_specs_names              CO           O2          CO2
  gas_energies        0.00000e+00  0.00000e+00 -2.33700e+00
  gas_molec_weights   2.79949e+01  3.19898e+01  4.39898e+01
  gas_molar_fracs     4.50000e-01  5.50000e-01  0.00000e+00

  n_surf_species    2
  surf_specs_names         CO*        O*
  surf_specs_dent            1         1

  finish
  ---------------------------------------------------------------------
  lattice_input.dat
  ---------------------------------------------------------------------
  lattice default_choice
    rectangular_periodic 1.0 50 50
  end_lattice
  ---------------------------------------------------------------------
  energetics_input.dat
  ---------------------------------------------------------------------
  energetics

  cluster CO*-0
    sites 1
    lattice_state
      1 CO* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng -1.30000e+00
  end_cluster

  cluster O*-0
    sites 1
    lattice_state
      1 O* 1
    site_types 1
    graph_multiplicity 1
    cluster_eng -2.30000e+00
  end_cluster

  end_energetics
  ---------------------------------------------------------------------
  mechanism_input.dat
  ---------------------------------------------------------------------
  mechanism

  step *-0:CO-->CO*-0
    gas_reacs_prods CO -1
    sites 1
    initial
      1 * 1
    final
      1 CO* 1
    site_types 1
    pre_expon  1.00000e+01
    activ_eng  0.00000e+00
  end_step

  step *_0-0,*_1-0:O2-->O*_0-0,O*_1-0;(0,1)
    gas_reacs_prods O2 -1
    sites 2
    neighboring 1-2
    initial
      1 * 1
      2 * 1
    final
      1 O* 1
      2 O* 1
    site_types 1 1
    pre_expon  2.50000e+00
    activ_eng  0.00000e+00
  end_step

  step CO*_0-0,O*_1-0-->*_0-0,*_1-0:CO2;(0,1)
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
    pre_expon  1.00000e+20
    activ_eng  0.00000e+00
  end_step

  end_mechanism
  [14.02|17:29:40] JOB plamsjob STARTED
  [14.02|17:29:40] JOB plamsjob RUNNING
  [14.02|17:29:41] JOB plamsjob FINISHED
  [14.02|17:29:41] JOB plamsjob SUCCESSFUL
  [14.02|17:32:01] PLAMS run finished. Goodbye


.. image:: ../../images/example_ZGB.gif
   :scale: 100 %
   :align: center
