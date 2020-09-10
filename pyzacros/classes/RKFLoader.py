import os
import sys

#from .Cluster import *
#from .ElementaryReaction import *
from .Mechanism import *

class RKFLoader:

    def __init__( self, results ):
        """
        Creates a new RKFLoader object

        :parm results
        """
        self.mechanism = None

        self.__deriveClustersAndMechanisms( results )


    def __deriveClustersAndMechanisms( self, results ):  # @TODO results -> scm.plams.Results
        """
        The next lines feed self%state2BindingSites.
        The binding sites for the reactants or products are already defined
        The binding sites for a TS are the union of the ones from its reactants and products

        TS ----> R --> bsR1, bsR2, ...
            |
            +--> P --> bsP1, bsP2, ...
        """
        import scm.plams

        self.mechanism = Mechanism()

        regions = results.readrkf("Molecule", "EngineAtomicInfo").split()

        nStates = results.readrkf("EnergyLandscape", "nStates")
        fileNames = results.readrkf("EnergyLandscape", "fileNames").replace(".rkf","").split()
        counts = results.readrkf("EnergyLandscape", "counts")
        isTS = results.readrkf("EnergyLandscape", "isTS")
        reactants = results.readrkf("EnergyLandscape", "reactants")
        products = results.readrkf("EnergyLandscape", "products")

        # Fix ids from Fortran to python
        reactants = [ max(0,idState-1) for idState in reactants ]
        products = [ max(0,idState-1) for idState in products ]

        nSites = results.readrkf("BindingSites", "nSites")
        adsorbateLabel = results.readrkf("BindingSites", "AdsorbateLabel").strip()
        labels = results.readrkf("BindingSites", "Labels"); labels = labels.split()
        averEnergy = results.readrkf("BindingSites", "AverEnergy")
        stdevEnergy = results.readrkf("BindingSites", "StdevEnergy")
        coords = results.readrkf("BindingSites", "Coords")
        nConnections = results.readrkf("BindingSites", "nConnections")
        fromSites = results.readrkf("BindingSites", "FromSites")
        toSites = results.readrkf("BindingSites", "ToSites")
        latticeDisplacements = results.readrkf("BindingSites", "LatticeDisplacements")
        nParentStates = results.readrkf("BindingSites", "nParentStates")
        parentStatesRaw = results.readrkf("BindingSites", "ParentStates")
        parentAtomsRaw = results.readrkf("BindingSites", "ParentAtoms")

        # Fix ids from Fortran to python
        fromSites = [ max(0,idSite-1) for idSite in fromSites ]
        toSites = [ max(0,idSite-1) for idSite in toSites ]
        parentStatesRaw = [ max(0,i-1) for i in parentStatesRaw ]

        # Reformats of the connections in a more accessible way and disables original variables
        sitesConnections = []
        for i in range(nConnections):
            sitesConnections.append( (fromSites[i],toSites[i]) )
            sitesConnections.append( (toSites[i],fromSites[i]) )
        nConnections = None
        fromSites = None
        toSites = None

        # It is not neccessary for fix the parentAtomsRaw, because PLAMS
        # uses also 1-based indices for its atoms
        #parentAtomsRaw = [ max(0,i-1) for i in parentAtomsRaw ]

        state2Molecule = nStates*[ None ]
        state2Energy = nStates*[ None ]
        for i,fileName in enumerate(fileNames):
            mol = results.get_molecule("Molecule", file=fileNames[i])
            amsResults = results.read_rkf_section("AMSResults", file=fileNames[i])

            state2Molecule[i] = mol
            state2Energy[i] = amsResults["Energy"]

            #vibrations = results.read_rkf_section("Vibrations", file=fileNames[i])
            #print("Frequencies = ", vibrations["Frequencies[cm-1]"])

        # parentStates and parentAtoms elements are actually vectors for each binding site
        # Here I split the vectors in that way and disable original variables
        parentStates = nSites*[ None ]
        parentAtoms = nSites*[ None ]
        for idSite in range(nSites):
            idStart = sum(nParentStates[0:idSite])
            idEnd = sum(nParentStates[0:idSite])+nParentStates[idSite]

            parentStates[idSite] = parentStatesRaw[idStart:idEnd]
            parentAtoms[idSite] = parentAtomsRaw[idStart:idEnd]
        nParentStates = None
        parentStatesRaw = None
        parentAtomsRaw = None

        #--------------------------------------------------------------------------------------
        # The next lines feed the array state2BindingSites.
        # The binding sites for the reactants or products are already defined
        # The binding sites for a TS are the union of the ones from its reactants and products
        #
        # TS ----> R --> bsR1, bsR2, ...
        #     |
        #     +--> P --> bsP1, bsP2, ...
        #--------------------------------------------------------------------------------------

        state2BindingSites = nStates*[ None ]
        attachedMolecule = {}   # attachedMolecule[idState][idSite]

        # Loop over the binding sites to load the binding sites for local minima
        for idSite in range(nSites):

            # Loop over the parent states of each binding site
            for i,idState in enumerate(parentStates[idSite]):
                if( state2BindingSites[ idState ] is None ):
                    state2BindingSites[ idState ] = []
                    attachedMolecule[ idState ] = {}

                state2BindingSites[ idState ].append( idSite )

                #----------------------------------------------------------------
                # Finds the attached molecule to the binding site idSite
                attachedAtom = parentAtoms[idSite][i]

                adsorbate = scm.plams.Molecule()
                for j,atom in enumerate(state2Molecule[idState]):
                    if( regions[j] == "region="+adsorbateLabel ):
                        adsorbate.add_atom( atom )

                adsorbateMols = adsorbate.separate()

                loc = 0
                for sMol in adsorbateMols:
                    for atom in sMol:
                        if( all( [ abs(atom.coords[i]-state2Molecule[idState][attachedAtom].coords[i]) < 1e-6 ] ) ):
                            attachedMolecule[idState][idSite] = sMol.get_formula()
                            loc = 1
                            break
                    if( loc == 1 ):
                        break
                #----------------------------------------------------------------

        # Loop over the TSs to load their binding sites
        for idState in range(nStates):
            if( isTS[idState] ):
                idReactant = reactants[idState]
                idProduct = products[idState]

                # Loop over the binding sites of the reactant
                for i,idSite in enumerate(state2BindingSites[idReactant]):
                    if( state2BindingSites[ idState ] is None ):
                        state2BindingSites[ idState ] = []

                    state2BindingSites[ idState ].append( idSite )

                # Loop over the binding sites of the products
                for i,idSite in enumerate(state2BindingSites[idProduct]):
                    if( state2BindingSites[ idState ] is None ):
                        state2BindingSites[ idState ] = []

                    state2BindingSites[ idState ].append( idSite )

                attachedMolecule[idState] = { **attachedMolecule[idReactant], **attachedMolecule[idProduct] }

        #print(state2BindingSites)
        #for idState in range(nStates):
            #if( idState in attachedMolecule ):
                #print(idState, attachedMolecule[idState])

        # Each TS defines an ElementaryReaction and at the same time it defines
        # two Clusters from reactants and products.

        # Loop over the TSs to find the species
        state2Species = nStates*[ None ]
        for idState in range(nStates):
            if( isTS[idState] ):
                idTS = idState

                # Locates the reactant and product
                idReactant = reactants[idTS]
                idProduct = products[idTS]
                #print( "idReactant : ", idReactant )
                #print( " idProduct : ", idProduct )

                # Filters the connection specifically for this TS
                neighboring = []
                connectedSites = {}
                for i,bs1 in enumerate(state2BindingSites[idTS]):
                    for j,bs2 in enumerate(state2BindingSites[idTS]):
                        if( bs1 < bs2 and (bs1,bs2) in sitesConnections ):
                            #neighboring.append( (bs1,bs2) )
                            neighboring.append( (i+1,j+1) )
                            connectedSites[bs1] = 1
                            connectedSites[bs2] = 1

                connectedSites = list( connectedSites.keys() )

                #--------------------------------------------------------------------
                # Reactant
                species = len(connectedSites)*[ "" ]
                for i,bs in enumerate(connectedSites):
                    if( bs in attachedMolecule[idReactant].keys() ):
                        species[i] = attachedMolecule[idTS][bs]

                clusterReactant = Cluster( site_types=tuple([ labels[j] for j in connectedSites ]),
                                           neighboring=neighboring,
                                           species=SpeciesList( [ Species(f+"*",1) for f in species ] ),
                                           multiplicity=2,
                                           cluster_energy=state2Energy[idReactant] )
                #--------------------------------------------------------------------

                #--------------------------------------------------------------------
                # Product
                species = len(connectedSites)*[ "" ]
                for i,bs in enumerate(connectedSites):
                    if( bs in attachedMolecule[idProduct].keys() ):
                        species[i] = attachedMolecule[idTS][bs]

                clusterProduct = Cluster( site_types=tuple([ labels[j] for j in connectedSites ]),
                                          neighboring=neighboring,
                                          species=SpeciesList( [ Species(f+"*",1) for f in species ] ),
                                          multiplicity=2,
                                          cluster_energy=state2Energy[idReactant] )
                #--------------------------------------------------------------------

                #--------------------------------------------------------------------
                # Reaction
                activationEnergy = state2Energy[idTS]-state2Energy[idReactant]

                reaction = ElementaryReaction( site_types=tuple([ labels[j] for j in connectedSites ]),
                                               neighboring=neighboring,
                                               initial=clusterReactant,
                                               final=clusterProduct,
                                               reversible=True,
                                               pre_expon=1e+13,
                                               pe_ratio=0.676,
                                               activation_energy=activationEnergy )

                self.mechanism.append( reaction )
                #--------------------------------------------------------------------
