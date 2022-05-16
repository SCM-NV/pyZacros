import os
import sys
import numpy

from .Species import *
from .SpeciesList import *
from .Cluster import *
from .ElementaryReaction import *
from .ClusterExpansion import *
from .Mechanism import *
from .Lattice import *

__all__ = ['RKFLoader']

class RKFLoader:

    def __init__( self, results=None ):
        """
        Creates a new RKFLoader object

        :parm results
        """
        self.clusterExpansion = ClusterExpansion()
        self.mechanism = Mechanism()
        self.lattice = None

        if( results is not None ):
            self.__deriveLatticeAndMechanism( results )


    def __deriveLatticeAndMechanism( self, results ):
        """
        Parses the .rkf file from AMS. Basically it loads the energy landscape and the binding-sites lattice.

        :parm results
        """
        import scm.plams
        import networkx as nx
        #import matplotlib.pyplot as plt

        eV = 0.0367493088244753
        angs = 1.88972612456506

        self.clusterExpansion = ClusterExpansion()
        self.mechanism = Mechanism()

        rkf_skeleton = results.get_rkf_skeleton()

        nLatticeVectors = results.readrkf("Molecule", "nLatticeVectors")
        latticeVectors = results.readrkf("Molecule", "LatticeVectors")
        latticeVectors = [ [latticeVectors[3*i+j]/angs for j in range(nLatticeVectors) ] for i in range(nLatticeVectors) ]
        regions = results.readrkf("InputMolecule", "EngineAtomicInfo").split("\0")

        nStates = results.readrkf("EnergyLandscape", "nStates")
        fileNames = results.readrkf("EnergyLandscape", "fileNames").replace(".rkf","").split("\0")
        counts = results.readrkf("EnergyLandscape", "counts")
        isTS = results.readrkf("EnergyLandscape", "isTS")
        reactants = results.readrkf("EnergyLandscape", "reactants")
        products = results.readrkf("EnergyLandscape", "products")
        prefactorsFromReactant = results.readrkf("EnergyLandscape", "prefactorsFromReactant")
        prefactorsFromProduct = results.readrkf("EnergyLandscape", "prefactorsFromProduct")

        # Fix ids from Fortran to python
        reactants = [ max(0,idState-1) for idState in reactants ]
        products = [ max(0,idState-1) for idState in products ]

        nFragments = 0
        if( "nFragments" in rkf_skeleton["EnergyLandscape"] ):
            nFragments = results.readrkf("EnergyLandscape", "nFragments")
            fragmentsEnergies = results.readrkf("EnergyLandscape", "fragmentsEnergies")
            fragmentsRegions = results.readrkf("EnergyLandscape", "fragmentsRegions").split("\0")
            fragmentsFileNames = results.readrkf("EnergyLandscape", "fragmentsFileNames").replace(".rkf","").split("\0")

        nFStates = 0
        if( "nFStates" in rkf_skeleton["EnergyLandscape"] ):
            nFStates = results.readrkf("EnergyLandscape", "nFStates")

            fStatesEnergy = nFStates*[ None ]
            fStatesNFragments = nFStates*[ None ]
            fStatesComposition = nFStates*[ None ]
            fStatesNConnections = nFStates*[ None ]
            fStatesConnections = nFStates*[ None ]
            fStatesAdsorptionPrefactors = nFStates*[ None ]
            fStatesDesorptionPrefactors = nFStates*[ None ]

            for i in range(nFStates):
                fStatesEnergy[i] = results.readrkf("EnergyLandscape", "fStatesEnergy("+str(i+1)+")")
                fStatesNFragments[i] = results.readrkf("EnergyLandscape", "fStatesNFragments("+str(i+1)+")")
                fStatesComposition[i] = results.readrkf("EnergyLandscape", "fStatesComposition("+str(i+1)+")")
                fStatesNConnections[i] = results.readrkf("EnergyLandscape", "fStatesNConnections("+str(i+1)+")")
                fStatesConnections[i] = results.readrkf("EnergyLandscape", "fStatesConnections("+str(i+1)+")")
                fStatesAdsorptionPrefactors[i] = results.readrkf("EnergyLandscape", "fStatesAdsorptionPrefactors("+str(i+1)+")")
                fStatesDesorptionPrefactors[i] = results.readrkf("EnergyLandscape", "fStatesDesorptionPrefactors("+str(i+1)+")")

                if type(fStatesComposition[i]) != list: fStatesComposition[i] = [ fStatesComposition[i] ]
                if type(fStatesConnections[i]) != list: fStatesConnections[i] = [ fStatesConnections[i] ]
                if type(fStatesAdsorptionPrefactors[i]) != list: fStatesAdsorptionPrefactors[i] = [ fStatesAdsorptionPrefactors[i] ]
                if type(fStatesDesorptionPrefactors[i]) != list: fStatesDesorptionPrefactors[i] = [ fStatesDesorptionPrefactors[i] ]

                # Fix ids from Fortran to python
                fStatesComposition[i] = [ max(0,idFragment-1) for idFragment in fStatesComposition[i] ]
                fStatesConnections[i] = [ max(0,idState-1) for idState in fStatesConnections[i] ]

        nSites = results.readrkf("BindingSites", "nSites")
        referenceRegion = results.readrkf("BindingSites", "ReferenceRegionLabel").strip()
        labels = results.readrkf("BindingSites", "Labels").split()
        coords = results.readrkf("BindingSites", "Coords")
        coords = [ [coords[3*i+j]/angs for j in range(3) ] for i in range(nSites) ]
        coordsFrac = results.readrkf("BindingSites", "CoordsFrac")
        coordsFrac = [ [coordsFrac[3*i+j] for j in range(3) ] for i in range(nSites) ]
        nConnections = results.readrkf("BindingSites", "nConnections")
        fromSites = results.readrkf("BindingSites", "FromSites")
        if type(fromSites) != list: fromSites = [ fromSites ]
        toSites = results.readrkf("BindingSites", "ToSites")
        if type(toSites) != list: toSites = [ toSites ]
        latticeDisplacements = results.readrkf("BindingSites", "LatticeDisplacements")
        latticeDisplacements = [ [latticeDisplacements[nLatticeVectors*i+j] for j in range(nLatticeVectors) ] for i in range(nConnections) ]
        nParentStates = results.readrkf("BindingSites", "nParentStates")
        parentStatesRaw = results.readrkf("BindingSites", "ParentStates")
        parentAtomsRaw = results.readrkf("BindingSites", "ParentAtoms")

        energyReference = 0.0 if nFStates==0 else min(fStatesEnergy)/eV

        # Fix ids from Fortran to python
        fromSites = [ max(0,idSite-1) for idSite in fromSites ]
        toSites = [ max(0,idSite-1) for idSite in toSites ]
        parentStatesRaw = [ max(0,i-1) for i in parentStatesRaw ]

        assert( len(fromSites) == len(toSites) )

        latticeGraph = nx.Graph()
        for i in range(len(fromSites)):
            latticeGraph.add_edge( fromSites[i], toSites[i] )

        latticeSPaths = dict(nx.all_pairs_shortest_path(latticeGraph))

        def getLatticeRxnSubgraph( bs_from, bs_to ):
            path = []
            for bs1 in bs_from:
                for bs2 in bs_to:
                    path.extend( latticeSPaths[bs1][bs2] )

            return latticeGraph.subgraph( path )

        #G1 = getLatticeRxnSubgraph( [4, 7], [8, 11] )

        #subax1 = plt.subplot(121)
        #nx.draw(latticeGraph, with_labels=True, font_weight='bold')
        #subax2 = plt.subplot(122)
        #nx.draw(G1, with_labels=True, font_weight='bold')
        #plt.show()

        #exit(-1)

        # It is not neccessary for fix the parentAtomsRaw, because PLAMS
        # uses also 1-based indices for its atoms
        #parentAtomsRaw = [ max(0,i-1) for i in parentAtomsRaw ]

        state2Molecule = nStates*[ None ]
        state2Energy = nStates*[ None ]
        for i,fileName in enumerate(fileNames):
            mol = results.get_molecule("Molecule", file=fileNames[i])
            amsResults = results.read_rkf_section("AMSResults", file=fileNames[i])

            state2Molecule[i] = mol
            state2Energy[i] = amsResults["Energy"]/eV

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
        attachedMoleculeData = {}   # attachedMoleculeData[idState][idSite]

        # Loop over the binding sites to load the binding sites for each local minima
        # Notice that the parent-states of the binding sites are always local minima
        for idSite in range(nSites):

            # Loop over the parent states of each binding site
            for i,idState in enumerate(parentStates[idSite]):
                if( state2BindingSites[ idState ] is None ):
                    state2BindingSites[ idState ] = []
                    attachedMoleculeData[ idState ] = {}

                state2BindingSites[ idState ].append( idSite )

                #-------------------------------------------------------------------
                # This block finds the attached molecule to the binding site idSite
                attachedAtom = parentAtoms[idSite][i]

                adsorbate = scm.plams.Molecule()
                for j,atom in enumerate(state2Molecule[idState]):
                    if( regions[j] != "region="+referenceRegion ):
                        adsorbate.add_atom( atom )

                adsorbate.guess_bonds()
                adsorbateMols = adsorbate.separate()

                loc = 0
                for sMol in adsorbateMols:
                    for atom in sMol:
                        r1 = numpy.array(atom.coords)
                        r2 = numpy.array(state2Molecule[idState][attachedAtom].coords)

                        if( all( abs(r1-r2) < 1e-6 ) ):
                            attachedMoleculeData[idState][idSite] = { 'formula':sMol.get_formula(),
                                                                      'cm':numpy.array(sMol.get_center_of_mass()),
                                                                      'mol':sMol }
                            loc = 1
                            break
                    if( loc == 1 ):
                        break
                #-------------------------------------------------------------------

        # Loop over the TSs to load their binding sites
        # Notice that the previous loop didn't include any TS
        # Here we defined attached molecules to a TS as the union of both the molecules attached to its reactants and products
        for idState in range(nStates):
            if( not isTS[idState] ): continue

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

            attachedMoleculeData[idState] = { **attachedMoleculeData[idReactant], **attachedMoleculeData[idProduct] }

        def getProperties( idState ):

            speciesNames = len(G1_nodes)*[ "" ]
            entityNumber = len(G1_nodes)*[ -1 ]
            for i,bs1 in enumerate(G1_nodes):
                if( bs1 in attachedMoleculeData[idState].keys() ):
                    speciesName1 = attachedMoleculeData[idState][bs1]['formula']
                    centerOfMass1 = attachedMoleculeData[idState][bs1]['cm']
                    speciesNames[i] = speciesName1

                    for j,bs2 in enumerate(G1_nodes):
                        if( j<=i ): continue

                        if( bs2 in attachedMoleculeData[idState].keys() ):
                            speciesName2 = attachedMoleculeData[idState][bs2]['formula']
                            centerOfMass2 = attachedMoleculeData[idState][bs2]['cm']

                            if( speciesName1 == speciesName2
                                and numpy.linalg.norm( centerOfMass1-centerOfMass2 ) < 0.5 ):
                                    entityNumber[i] = max(entityNumber)+1
                                    entityNumber[j] = entityNumber[i]

                if( entityNumber[i] == -1 ):
                    entityNumber[i] = max(entityNumber)+1

            denticity = len(speciesNames)*[1]
            if entityNumber.count(-1) != len(G1_nodes):
                denticity = [ entityNumber.count(entityNumber[i]) if entityNumber[i] != -1 else 1 for i in range(len(speciesNames)) ]
            species = SpeciesList( [ Species(f+"*"*denticity[i],denticity[i]) for i,f in enumerate(speciesNames) ] )

            return species,entityNumber

        def getPropertiesForCluster( species, entityNumber ):
            # This section remove the empty adsorption sites which are not needed for clusters
            data = {}
            data['site_types'] = []
            data['entity_number'] = []
            data['neighboring'] = []
            data['species'] = []

            nonEmptySites = []
            for i,bs in enumerate(G1_nodes):
                if( len(species[i].symbol.replace('*','')) != 0 ):
                    nonEmptySites.append(bs)

            if len(nonEmptySites) > 1:

                path = []
                for bs1 in nonEmptySites:
                    for bs2 in nonEmptySites:
                        if( bs1 != bs2 ):
                            path.extend( G1_shortest_paths[bs1][bs2] )

                G2 = G1.subgraph( path )
                G2_nodes = list(G2.nodes())
                G2_edges = [ [G2_nodes.index(pair[0]),G2_nodes.index(pair[1])] for pair in G2.edges() ]

                for bs in G2.nodes():
                    old_id = G1_nodes.index(bs)
                    data['site_types'].append( site_types[old_id] )
                    data['entity_number'].append( entityNumber[old_id] )
                    data['species'].append( species[old_id] )

                data['entity_number'] = [ data['entity_number'][i]-min(data['entity_number']) for i in range(len(data['entity_number'])) ]
                data['neighboring'] = G2_edges

            else:
                data['site_types'].append( site_types[0] )
                data['entity_number'].append( entityNumber[0] )
                data['species'].append( species[0] )
                data['neighboring'] = []

            return data

        # Loop over the TSs to find the species
        # Each TS defines an ElementaryReaction and at the same time it defines
        # two Clusters from reactants and products.
        for idState in range(nStates):
            if( isTS[idState] ):
                idTS = idState

                # We only accept complete TSs
                if( reactants[idTS] == 0 or products[idTS] == 0 ):
                    continue

                # Locates the reactant and product
                idReactant = reactants[idTS]
                idProduct = products[idTS]
                prefactorR = prefactorsFromReactant[idTS]
                prefactorP = prefactorsFromProduct[idTS]

                # Filters the connection specifically for this TS
                G1 = getLatticeRxnSubgraph( state2BindingSites[idReactant], state2BindingSites[idProduct] )
                G1_nodes = sorted(list(G1.nodes()))
                G1_edges = [ [G1_nodes.index(pair[0]),G1_nodes.index(pair[1])] for pair in G1.edges() ]
                G1_shortest_paths = dict(nx.all_pairs_shortest_path(G1))

                site_types = [ labels[j] for j in G1_nodes ]

                #--------------------------------------------------------------------
                # Reactant
                speciesReactant, entityNumber = getProperties( idReactant )
                cluster_data = getPropertiesForCluster( speciesReactant, entityNumber )

                clusterReactant = Cluster( site_types=cluster_data['site_types'],
                                           entity_number=cluster_data['entity_number'],
                                           neighboring=cluster_data['neighboring'],
                                           species=cluster_data['species'],
                                           multiplicity=1,
                                           cluster_energy=state2Energy[idReactant]-energyReference )

                entityNumberReactant = entityNumber

                #--------------------------------------------------------------------
                # Product
                speciesProduct,entityNumber = getProperties( idProduct )
                cluster_data = getPropertiesForCluster( speciesProduct, entityNumber )

                clusterProduct = Cluster( site_types=cluster_data['site_types'],
                                          entity_number=cluster_data['entity_number'],
                                          neighboring=cluster_data['neighboring'],
                                          species=cluster_data['species'],
                                          multiplicity=1,
                                          cluster_energy=state2Energy[idReactant]-energyReference )

                entityNumberProduct = entityNumber

                #--------------------------------------------------------------------
                # Reaction
                entityNumberReactant = entityNumberReactant if entityNumberReactant.count(-1) != len(entityNumberReactant) else None
                entityNumberProduct = entityNumberProduct if entityNumberProduct.count(-1) != len(entityNumberProduct) else None
                activationEnergy = state2Energy[idTS]-state2Energy[idReactant]

                pe_ratio = prefactorR/prefactorP
                reversible = True if pe_ratio > 1e-6 else False

                reaction = ElementaryReaction( site_types=site_types,
                                               initial_entity_number=entityNumberReactant,
                                               final_entity_number=entityNumberProduct,
                                               neighboring=G1_edges,
                                               initial=speciesReactant,
                                               final=speciesProduct,
                                               reversible=reversible,
                                               pre_expon=prefactorR,
                                               pe_ratio=pe_ratio,
                                               activation_energy=activationEnergy )

                #self.clusterExpansion.extend( [clusterReactant, clusterProduct] )
                self.mechanism.append( reaction )

        # Loop over the Fragmented states to find the species and reactions
        for idFState in range(nFStates):
            energy = fStatesEnergy[idFState]
            nFragments = fStatesNFragments[idFState]
            composition = fStatesComposition[idFState]

            # Loop over the associated connected states
            for pos,idState in enumerate(fStatesConnections[idFState]):
                prefactorAdsorption = fStatesAdsorptionPrefactors[idFState][pos]
                prefactorDesorption = fStatesDesorptionPrefactors[idFState][pos]

                G1 = getLatticeRxnSubgraph( state2BindingSites[idState], state2BindingSites[idState] )
                G1_nodes = sorted(list(G1.nodes()))
                G1_edges = [ [G1_nodes.index(pair[0]),G1_nodes.index(pair[1])] for pair in G1.edges() ]
                G1_shortest_paths = dict(nx.all_pairs_shortest_path(G1))

                site_types = [ labels[j] for j in G1_nodes ]

                #--------------------------------------------------------------------
                # State
                speciesState, entityNumber = getProperties( idState )
                cluster_data = getPropertiesForCluster( speciesState, entityNumber )

                clusterState = Cluster( site_types=cluster_data['site_types'],
                                        entity_number=cluster_data['entity_number'],
                                        neighboring=cluster_data['neighboring'],
                                        species=cluster_data['species'],
                                        multiplicity=1,
                                        cluster_energy=state2Energy[idState]-energyReference )

                #--------------------------------------------------------------------
                # Fragmented State
                speciesNames = [ "*" for f in cluster_data['site_types'] ]
                for idFragment in composition:
                    if( fragmentsRegions[idFragment] == "active" ):
                        mol = results.get_molecule("Molecule", file=fragmentsFileNames[idFragment])
                        speciesNames.append( mol.get_formula() )

                speciesFState = SpeciesList( [ Species(f) for f in speciesNames ] )

                #--------------------------------------------------------------------
                # Reaction
                activationEnergy = 0.0 #TODO Here we are assuming that there is no a TS between the fragmented state and the state.

                # X_gas <--> X*
                pe_ratio = prefactorAdsorption/prefactorDesorption
                reversible = True if pe_ratio > 1e-6 else False

                reaction = ElementaryReaction( site_types=cluster_data['site_types'],
                                               final_entity_number=cluster_data['entity_number'],
                                               neighboring=cluster_data['neighboring'],
                                               initial=speciesFState,
                                               final=cluster_data['species'],
                                               reversible=reversible,
                                               pre_expon=prefactorAdsorption,
                                               pe_ratio=pe_ratio,
                                               activation_energy=activationEnergy )

                self.clusterExpansion.extend( [clusterState] )
                self.mechanism.append( reaction )

        #--------------------------------------------------------------------
        # Generation of the KMCLattice
        assert( len(latticeVectors) >= 2 )

        neighboring_structure = nConnections*[ None ]
        for i in range(nConnections):
            ld = latticeDisplacements[i]

            first = None
            if( ld[0] >= 0 and ld[1] >= 0 ):
                first = (fromSites[i],toSites[i])
            else:
                first = (toSites[i],fromSites[i])
                ld = [ abs(v) for v in ld ]

            second = None
            if( tuple(ld[0:2]) == (0,0) ):
                second = Lattice.SELF
            elif( tuple(ld[0:2]) == (0,1) ):
                second = Lattice.NORTH
            elif( tuple(ld[0:2]) == (1,0) ):
                second = Lattice.EAST
            elif( tuple(ld[0:2]) == (1,1) ):
                second = Lattice.NORTHEAST
            else:
                raise NameError("Unknown case for LD="+str(ld[0:2]))

            if( first is None or second is None ): continue

            # (1,1):"northeast",  <<< #TODO I don't understand this case
            # (1,-1):"southeast"  <<< #TODO I don't understand this case

            neighboring_structure[i] = [first,second]

        # Here we omit the z-axis. In the future, we should make a 2D projection of
        # the 3D lattice instead. This is necessary to be able to study adsorption on nanoclusters.
        self.lattice = Lattice( cell_vectors=[ [v[0],v[1]] for v in latticeVectors[0:2] ],
                                repeat_cell=(1,1), # Default value.
                                site_types=labels,
                                site_coordinates=coordsFrac,
                                neighboring_structure=neighboring_structure)


    def replace_site_types( self, site_types_old, site_types_new ):
        """
        Replaces the site types names

        *   ``site_types_old`` -- List of strings containing the old site_types to be replaced
        *   ``site_types_new`` -- List of strings containing the new site_types which would replace old site_types_old.
        """
        assert( len(site_types_old) == len(site_types_new) )

        self.lattice.replace_site_types( site_types_old, site_types_new )
        self.mechanism.replace_site_types( site_types_old, site_types_new )
        self.clusterExpansion.replace_site_types( site_types_old, site_types_new )


    @staticmethod
    def merge( rkf_loaders ):
        """
        Merges a list of rkf_loader into a single one

        *   ``rkf_loaders`` -- List of rkf_loader items to merge
        """
        final_loader = RKFLoader()

        for loader in rkf_loaders:
            for cluster in loader.clusterExpansion:
                final_loader.clusterExpansion.append( cluster )

            for elementaryStep in loader.mechanism:
                final_loader.mechanism.append( elementaryStep )

            if final_loader.lattice is None:
                final_loader.lattice = loader.lattice
            else:
                final_loader.lattice.extend( loader.lattice )

            #firstTime = False
            #for lattice in loader.lattice:
                #if firstTime:
                    #final_loader.cell_vectors

        #self.cell_vectors = None
        #self.site_types = None
        #self.site_coordinates = None
        #self.nearest_neighbors = None

        return final_loader



