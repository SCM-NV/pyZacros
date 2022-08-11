# This is example aims to reproduce results reported in Section 4.2 of the following paper:
#  * Mauro Bracconi, and Matteo Maestri. Training set design for machine learning techniques
#    applied to the approximation of computationally intensive first-principles kinetic models
#    Chemical Engineering Journal 2022 (400) 125469
#
# The original model is described in:
#  * K. Reuter, M. Scheffler, First-principles kinetic Monte Carlo simulations for
#    heterogeneous catalysis: application to the CO oxidation at RuO2(110)
#    Phys. Rev. B – Condens. Matter Mater. Phys. 73 (2006) 1–17

try:
    import pyzacros as pz
except:
    import scm.pyzacros as pz

class ReuterScheffler:

    def __init__(self, repeat_cell=[10,20]):

        #---------------------------------------------
        # Species:
        #---------------------------------------------
        # Gas-species:
        O2_gas = pz.Species("O2")
        CO_gas = pz.Species("CO")
        CO2_gas = pz.Species("CO2", gas_energy=-3.072)

        # Surface species:
        s0 = pz.Species("*", 1)      # Empty adsorption site
        O_ads = pz.Species("O*", 1)
        CO_ads = pz.Species("CO*", 1)

        #---------------------------------------------
        # Lattice setup:
        #---------------------------------------------
        self.lattice = pz.Lattice( cell_vectors=[[6.43, 0.00],[0.00, 3.12]],
                                   repeat_cell=repeat_cell,
                                   site_types=['cus', 'brg'],
                                   site_coordinates=[[0.25, 0.50],
                                                     [0.75, 0.50]],
                                   neighboring_structure=[ [(0,1), pz.Lattice.SELF],
                                                           [(0,0), pz.Lattice.NORTH],
                                                           [(0,1), pz.Lattice.NORTH],
                                                           [(1,1), pz.Lattice.NORTH],
                                                           [(1,0), pz.Lattice.NORTH],
                                                           [(1,0), pz.Lattice.NORTHEAST],
                                                           [(1,0), pz.Lattice.EAST],
                                                           [(1,0), pz.Lattice.SOUTHEAST] ] )

        #---------------------------------------------
        # Clusters & Cluster expansion
        #---------------------------------------------
        O_point_brg = pz.Cluster(species=[O_ads], site_types=['brg'], multiplicity=1, energy=-2.3, label='O_point_brg')
        O_point_cus = pz.Cluster(species=[O_ads], site_types=['cus'], multiplicity=1, energy=-1.0, label='O_point_cus')

        CO_point_brg = pz.Cluster(species=[CO_ads], site_types=['brg'], multiplicity=1, energy=-1.6, label='CO_point_brg')
        CO_point_cus = pz.Cluster(species=[CO_ads], site_types=['cus'], multiplicity=1, energy=-1.3, label='CO_point_cus')

        O_brg_O_brg_1NN = pz.Cluster(species=[O_ads,O_ads], site_types=['brg','brg'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='O_brg_O_brg_1NN')
        O_cus_O_cus_1NN = pz.Cluster(species=[O_ads,O_ads], site_types=['cus','cus'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='O_cus_O_cus_1NN')
        O_cus_O_brg_1NN = pz.Cluster(species=[O_ads,O_ads], site_types=['cus','brg'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='O_cus_O_brg_1NN')

        CO_brg_CO_brg_1NN = pz.Cluster(species=[CO_ads,CO_ads], site_types=['brg','brg'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_brg_CO_brg_1NN')
        CO_cus_CO_cus_1NN = pz.Cluster(species=[CO_ads,CO_ads], site_types=['cus','cus'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_cus_CO_cus_1NN')
        CO_cus_CO_brg_1NN = pz.Cluster(species=[CO_ads,CO_ads], site_types=['cus','brg'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_cus_CO_brg_1NN')

        CO_brg_O_brg_1NN = pz.Cluster(species=[CO_ads,O_ads], site_types=['brg','brg'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_brg_O_brg_1NN')
        CO_cus_O_cus_1NN = pz.Cluster(species=[CO_ads,O_ads], site_types=['cus','cus'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_cus_O_cus_1NN')
        CO_cus_O_brg_1NN = pz.Cluster(species=[CO_ads,O_ads], site_types=['cus','brg'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_cus_O_brg_1NN')
        CO_brg_O_cus_1NN = pz.Cluster(species=[CO_ads,O_ads], site_types=['brg','cus'], neighboring=[(0,1)], multiplicity=2, energy=0.0, label='CO_brg_O_cus_1NN')

        self.cluster_expansion = pz.ClusterExpansion( [O_point_brg, O_point_cus,
                                                       CO_point_brg, CO_point_cus,
                                                       O_brg_O_brg_1NN, O_cus_O_cus_1NN, O_cus_O_brg_1NN,
                                                       CO_brg_CO_brg_1NN, CO_cus_CO_cus_1NN, CO_cus_CO_brg_1NN,
                                                       CO_brg_O_brg_1NN, CO_cus_O_cus_1NN, CO_cus_O_brg_1NN, CO_brg_O_cus_1NN] )

        #---------------------------------------------
        # Elementary Reactions & Mechanism
        #---------------------------------------------

        CO_brg_adsorption = pz.ElementaryReaction(
                                            initial=[s0,CO_gas],
                                            final=[CO_ads],
                                            site_types=['brg'],
                                            reversible=True,
                                            pre_expon=2.04e+08,
                                            pe_ratio=1.33e-10,
                                            activation_energy=0.0,
                                            prox_factor=0.0,
                                            label="CO_brg_adsorption")

        CO_cus_adsorption = pz.ElementaryReaction(
                                            initial=[s0,CO_gas],
                                            final=[CO_ads],
                                            site_types=['cus'],
                                            reversible=True,
                                            pre_expon=2.04e+08,
                                            pe_ratio=1.53e-10,
                                            activation_energy=0.0,
                                            prox_factor=0.0,
                                            label="CO_cus_adsorption")

        O_brg_adsorption = pz.ElementaryReaction(
                                            initial=[s0,s0,O2_gas],
                                            final=[O_ads,O_ads],
                                            site_types=['brg','brg'],
                                            neighboring=[(0, 1)],
                                            reversible=True,
                                            pre_expon=1.91e+08,
                                            pe_ratio=5.33e-11,
                                            activation_energy=0.000,
                                            prox_factor=0.0,
                                            label="O_brg_adsorption")

        O_cus_adsorption = pz.ElementaryReaction(
                                            initial=[s0,s0,O2_gas],
                                            final=[O_ads,O_ads],
                                            site_types=['cus','cus'],
                                            neighboring=[(0, 1)],
                                            reversible=True,
                                            pre_expon=1.91e+08,
                                            pe_ratio=5.33e-11,
                                            activation_energy=0.000,
                                            prox_factor=0.0,
                                            label="O_cus_adsorption")

        O_cus_O_brg_adsorption = pz.ElementaryReaction(
                                            initial=[s0,s0,O2_gas],
                                            final=[O_ads,O_ads],
                                            site_types=['cus','brg'],
                                            neighboring=[(0, 1)],
                                            reversible=True,
                                            pre_expon=1.91e+08,
                                            pe_ratio=5.33e-11,
                                            activation_energy=0.000,
                                            prox_factor=0.0,
                                            label="O_cus_O_brg_adsorption")

        CO_brg_O_cus_oxidation = pz.ElementaryReaction(
                                            initial=[CO_ads,O_ads],
                                            final=[s0,s0,CO2_gas],
                                            site_types=['brg','cus'],
                                            neighboring=[(0, 1)],
                                            reversible=False,
                                            pre_expon=6.25e+12,
                                            activation_energy=0.76,
                                            prox_factor=0.0,
                                            label="CO_brg_O_cus_oxidation")

        CO_brg_O_brg_oxidation = pz.ElementaryReaction(
                                            initial=[CO_ads,O_ads],
                                            final=[s0,s0,CO2_gas],
                                            site_types=['brg','brg'],
                                            neighboring=[(0, 1)],
                                            reversible=False,
                                            pre_expon=6.25e+12,
                                            activation_energy=1.54,
                                            prox_factor=0.0,
                                            label="CO_brg_O_brg_oxidation")

        CO_cus_O_cus_oxidation = pz.ElementaryReaction(
                                            initial=[CO_ads,O_ads],
                                            final=[s0,s0,CO2_gas],
                                            site_types=['cus','cus'],
                                            neighboring=[(0, 1)],
                                            reversible=False,
                                            pre_expon=6.25e+12,
                                            activation_energy=0.89,
                                            prox_factor=0.0,
                                            label="CO_cus_O_cus_oxidation")

        CO_cus_O_brg_oxidation = pz.ElementaryReaction(
                                            initial=[CO_ads,O_ads],
                                            final=[s0,s0,CO2_gas],
                                            site_types=['cus','brg'],
                                            neighboring=[(0, 1)],
                                            reversible=False,
                                            pre_expon=6.25e+12,
                                            activation_energy=1.25,
                                            prox_factor=0.0,
                                            label="CO_cus_O_brg_oxidation")

        self.mechanism = pz.Mechanism([CO_brg_adsorption, CO_cus_adsorption,
                                       O_brg_adsorption, O_cus_adsorption, O_cus_O_brg_adsorption,
                                       CO_brg_O_cus_oxidation, CO_brg_O_brg_oxidation, CO_cus_O_cus_oxidation, CO_cus_O_brg_oxidation])

