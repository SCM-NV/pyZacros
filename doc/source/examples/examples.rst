.. |br| raw:: html

      <br>

Examples
========

In this chapter we present example pyZacros scripts covering various applications.

Simple examples
---------------

This section contains some simple tutorial examples to gain a basic understanding of the pyZacros classes.
They are mainly focused on how to translate a typical Zacros input file to the equivalent one in python.
These examples often use short runtimes, making them perfect candidates for exploring, testing, and gaining
experience before moving on to more complex configurations.

.. toctree::
   :maxdepth: 1
   :hidden:

   WaterGasShiftOnPt111.rst
   zgb.rst

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Water-gas shift reaction on Pt(111)
      :link: WaterGasShiftOnPt111.html

      .. image:: ../../images/example_WaterGasShiftOnPt111.png
         :scale: 50 %

      +++
      **Keywords:** Water-gas shift, Pt(111) surface, CO oxidation, surface catalysis

   .. grid-item-card:: Ziff-Gulari-Barshad model
      :link: zgb.html

      .. image:: ../../images/example_ZGB.gif
         :scale: 50 %

      +++
      **Keywords:** ZGB model, nearest-neighbor reaction, absorbing states


Intermediate examples
---------------------

This section contains intermediate-level examples.
The keywords used are fundamentally the same, but their chemistry or
physics may be more complex. These examples may result in longer run
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

   .. grid-item-card:: Ziff-Gulari-Barshad model: |br| Phase Transitions |br|
      :link: zgb_pts.html

      .. image:: PhaseTransitions_files/PhaseTransitions_28_0.png
         :scale: 50 %

      +++
      **Keywords:** First-order transition, continuous transition, CO-poisoned phase, O-poisoned phase

   .. grid-item-card:: Ziff-Gulari-Barshad model: |br| Steady State Conditions
      :link: zgb_ss.html

      .. image:: SteadyState_files/SteadyState_19_0.png
         :scale: 50 %

      +++
      **Keywords:** Stationary regime, coverage plateaus, turnover frequency, long-time averaging

   .. grid-item-card:: Ziff-Gulari-Barshad model: |br| Phase Transitions under Steady |br| State Conditions
      :link: zgb_pts_ss.html

      .. image:: PhaseTransitions-SteadyState_files/PhaseTransitions-SteadyState_21_0.png
         :scale: 50 %

      +++
      **Keywords:** Steady-state transitions, ZacrosSteadyStateJob, steady-state convergence

   .. grid-item-card:: Langmuir-Hinshelwood model: |br| Acceleration by Automated |br| Rescaling of the Rate Constants |br|
      :link: lh_rrc.html

      .. image:: CoveragesAndReactionRate_ViewResults_files/CoveragesAndReactionRate_ViewResults_10_0.png
         :scale: 50 %

      +++
      **Keywords:** Rate-constant rescaling, timescale separation, accelerated kMC

Advanced examples
-----------------

This section contains challenging examples often involving multiphysics throw specific coupling with external codes.
Many of these examples represent industrial problems or show some state-of-the-art validation problems.
.. Switching to Massively Parallel Processing (MPP) becomes recommended.

.. toctree::
   :maxdepth: 1
   :hidden:

   COPt111
   zgb_pts_sm.rst

.. grid:: 2
   :gutter: 2

   .. grid-item-card:: Poisoning of Pt(111) by CO: |br| From atomistic to mesoscopic modeling
      :link: COPt111.html

      .. image:: ../../images/example_CO+Pt111-main.png
         :scale: 70 %

      +++
      **Keywords:** CO site blocking, Pt(111) deactivation, atomistic energetics, coarse-grained kinetics, multiscale bridge

   .. grid-item-card:: Ziff-Gulari-Barshad model: |br| Phase Transitions and ML-based |br| Surrogate Model |br|
      :link: zgb_pts_sm.html

      .. image:: PhaseTransitions-ADP_improved.png
         :scale: 50 %

      +++
      **Keywords:** phase transitions, machine learning surrogate, training from kMC, fast parameter scan, data-driven kinetics
