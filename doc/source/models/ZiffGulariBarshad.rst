.. |br| raw:: html

      <br>

Ziff-Gulari-Barshad Model
-------------------------

For more information, see file :download:`ZiffGulariBarshad.py <../../../src/scm/pyzacros/models/ZiffGulariBarshad.py>`.

The ZGB model includes the following elementary reactions:

.. math::
   :nowrap:

   \begin{align}
      \text{CO}_{(\text{g})} + \text{*}  & \overset{k_\text{CO}}{\longrightarrow} \text{CO}^\text{*} &\qquad \text{'CO_adsorption'} \\
      \text{O}_{2(\text{g})} + 2\text{*} & \overset{k_{\text{O}_2}}{\longrightarrow} \text{O}^\text{*} + \text{O}^\text{*}  &\qquad \text{'O2_adsorption'}\\
      \text{CO}^\text{*} + \text{O}^\text{*} & \overset{k_\text{oxi}}{\longrightarrow} 2\text{*} + \text{CO}_{2(\text{g})} &\qquad \text{'CO_oxidation'} \\
   \end{align}


.. figure:: ../../images/zgb_lattice5x5.png
   :scale: 60 %
   :align: center

   Lattice generated using the option ``repeat_cell=(5,5)``
