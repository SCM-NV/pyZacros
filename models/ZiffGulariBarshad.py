# Taken from: https://zacros.org/tutorials/4-tutorial-1-ziff-gulari-barshad-model-in-zacros?showall=1

try:
    import pyzacros as pz
except:
    import scm.pyzacros as pz

class ZiffGulariBarshad:

    def __init__(self, lattice_constant=1.0, repeat_cell=[50,50]):

        #---------------------------------------------
        # Species:
        #---------------------------------------------
        # Gas-species:
        CO_gas = pz.Species("CO")
        O2_gas = pz.Species("O2")
        CO2_gas = pz.Species("CO2", gas_energy=-2.337)

        # Surface species:
        s0 = pz.Species("*", 1)      # Empty adsorption site
        CO_ads = pz.Species("CO*", 1)
        O_ads = pz.Species("O*", 1)

        #---------------------------------------------
        # Lattice setup:
        #---------------------------------------------
        self.lattice = pz.Lattice( lattice_type=pz.Lattice.RECTANGULAR,
                                    lattice_constant=lattice_constant, repeat_cell=repeat_cell )

        #---------------------------------------------
        # Clusters:
        #---------------------------------------------
        CO_point = pz.Cluster(species=[CO_ads], energy=-1.3, label="CO_point")
        O_point = pz.Cluster(species=[O_ads], energy=-2.3, label="O_point")

        self.cluster_expansion = pz.ClusterExpansion( [CO_point, O_point] )

        #---------------------------------------------
        # Elementary Reactions
        #---------------------------------------------
        # CO_adsorption:
        CO_adsorption = pz.ElementaryReaction(initial=[s0,CO_gas],
                                              final=[CO_ads],
                                              reversible=False,
                                              pre_expon=10.0,
                                              activation_energy=0.0,
                                              label="CO_adsorption")

        # O2_adsorption:
        O2_adsorption = pz.ElementaryReaction(initial=[s0,s0,O2_gas],
                                              final=[O_ads,O_ads],
                                              neighboring=[(0, 1)],
                                              reversible=False,
                                              pre_expon=2.5,
                                              activation_energy=0.0,
                                              label="O2_adsorption")

        # CO_oxidation:
        CO_oxidation = pz.ElementaryReaction(initial=[CO_ads, O_ads],
                                             final=[s0, s0, CO2_gas],
                                             neighboring=[(0, 1)],
                                             reversible=False,
                                             pre_expon=1.0e+20,
                                             activation_energy=0.0,
                                             label="CO_oxidation")

        self.mechanism = [CO_adsorption, O2_adsorption, CO_oxidation]
