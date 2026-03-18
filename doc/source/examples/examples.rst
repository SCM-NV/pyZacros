.. |br| raw:: html

      <br>

.. _label-pyzacros-examples-index:

Examples
========

The following list of examples illustrates how to use pyZacros for running and analyzing kMC simulations.

Simple Examples
---------------

This section contains some simple tutorial examples to gain a basic understanding of the pyZacros classes.
They are mainly focused on how to translate a typical Zacros input file to Python.
These examples have short runtimes, making them perfect candidates for exploring, testing, and gaining
experience before moving on to more complex systems.

.. toctree::
   :maxdepth: 1
   :hidden:

   WaterGasShiftOnPt111.rst
   zgb.rst


.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Water-Gas Shift Reaction on Pt(111)
      :link: WaterGasShiftOnPt111.html

      .. image:: ../../images/example_WaterGasShiftOnPt111.png
         :scale: 50 %

      +++
      **Keywords:** Water-gas shift, Pt(111) surface, CO oxidation, surface catalysis

   .. grid-item-card:: Ziff-Gulari-Barshad Model
      :link: zgb.html

      .. image:: ../../images/example_ZGB.gif
         :scale: 50 %

      +++
      **Keywords:** ZGB model, Nearest-neighbor reaction, Adsorption


Intermediate Examples
---------------------

This section contains intermediate-level examples.
The scripts have the same structure as the simple examples, but the chemistry /
physics are more complex. These examples may result in longer run
times and require access to higher computational resources.

.. toctree::
   :maxdepth: 1
   :hidden:

   zgb_pts.rst
   zgb_ss.rst
   zgb_pts_ss.rst
   lh_rrc.rst


.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Ziff-Gulari-Barshad Model: Phase Transitions
      :link: zgb_pts.html

      .. image:: PhaseTransitions_files/PhaseTransitions_28_0.png
         :scale: 50 %

      +++
      **Keywords:** First-order transition, Continuous transition, CO poisoning, O poisoning

   .. grid-item-card:: Ziff-Gulari-Barshad Model: Steady State Conditions
      :link: zgb_ss.html

      .. image:: SteadyState_files/SteadyState_19_0.png
         :scale: 50 %

      +++
      **Keywords:** Stationary regime, Coverage plateau, Turnover frequency, Time averaging

   .. grid-item-card:: Ziff-Gulari-Barshad Model: Phase Transitions under Steady State Conditions
      :link: zgb_pts_ss.html

      .. image:: PhaseTransitions-SteadyState_files/PhaseTransitions-SteadyState_21_0.png
         :scale: 50 %

      +++
      **Keywords:** Steady-state transitions, ZacrosSteadyStateJob, Steady-state convergence

   .. grid-item-card:: Langmuir-Hinshelwood Model: Acceleration by Automated Rescaling of the Rate Constants
      :link: lh_rrc.html

      .. image:: CoveragesAndReactionRate_ViewResults_files/CoveragesAndReactionRate_ViewResults_10_0.png
         :scale: 50 %

      +++
      **Keywords:** Rate-constant rescaling, Timescale separation, Accelerated kMC


Advanced Examples
-----------------

This section contains more complicated scripting examples involving multiphysics by coupling pyZacros with external codes.
These examples represent industrial problems and showcase state-of-the-art validation methods.

.. toctree::
   :maxdepth: 1
   :hidden:

   COPt111
   zgb_pts_sm.rst
   ElectrodepositionDendriteGrowth.rst


.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Poisoning of Pt(111) by CO: From Atomistic to Mesoscopic Modeling
      :link: COPt111.html

      .. image:: ../../images/example_CO+Pt111-main.png
         :scale: 70 %

      +++
      **Keywords:** Site blocking, Deactivation, Atomistic energetics, Coarse-grained kinetics, Multiscale

   .. grid-item-card:: Ziff-Gulari-Barshad Model: Phase Transitions and ML-based Surrogate Models
      :link: zgb_pts_sm.html

      .. image:: PhaseTransitions-ADP_improved.png
         :scale: 50 %

      +++
      **Keywords:** Phase transitions, Machine learning surrogate, Training from kMC, Fast parameter scan, Data-driven kinetics

   .. grid-item-card:: Modeling Electrodeposition and Dendrite Growth
      :link: ElectrodepositionDendriteGrowth.html

      .. image:: ../../images/example_Electrodeposition.png
         :scale: 30 %

      +++
      **Keywords:** electrodeposition, surface diffusion, electrochemical kinetics, Butler-Volmer, dendrite growth
