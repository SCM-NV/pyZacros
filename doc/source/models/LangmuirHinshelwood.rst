.. |br| raw:: html

      <br>

Langmuir-Hinshelwood Model
--------------------------

For more information, see file :download:`LangmuirHinshelwood.py <../../../models/LangmuirHinshelwood.py>`.

The LH model includes the following elementary reactions:

.. math::
   :nowrap:

   \begin{align}
      \text{CO}_{(\text{g})} + \text{*}  & \overset{k_\text{CO}}{\longleftrightarrow} \text{CO}^\text{*} &\qquad \text{'CO_adsorption'} \\
      \text{O}_{2(\text{g})} + 2\text{*} & \overset{k_{\text{O}_2}}{\longleftrightarrow} \text{O}^\text{*} + \text{O}^\text{*}  &\qquad \text{'O_adsorption'}\\
      \text{O}^\text{*} + \text{*} & \overset{k_\text{O}}{\longleftrightarrow} \text{*} + \text{O}^\text{*} &\qquad \text{'O_diffusion'}\\
      \text{CO}^\text{*} + \text{*} & \overset{k_\text{CO}}{\longleftrightarrow} \text{*} + \text{CO}^\text{*} &\qquad \text{'CO_diffusion'} \\
      \text{CO}^\text{*} + \text{O}^\text{*} & \overset{k_\text{oxi}}{\longleftrightarrow} 2\text{*} + \text{CO}_{2(\text{g})} &\qquad \text{'CO_oxidation'} \\
   \end{align}

.. figure:: ../../images/lh_lattice5x5.png
   :scale: 80 %
   :align: center

   Lattice generated using the option ``repeat_cell=(5,5)``
