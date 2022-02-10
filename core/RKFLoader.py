import os
import sys

from .Species import *
from .SpeciesList import *
from .Cluster import *
from .ElementaryReaction import *
from .ClusterExpansion import *
from .Mechanism import *
from .Lattice import *

__all__ = ['RKFLoader']

class RKFLoader:

    def __init__( self, results ):
        """
        Creates a new RKFLoader object

        :parm results
        """
        self.clusterExpansio = None
        self.mechanism = None
        self.lattice = None

        self.__deriveLatticeAndMechanism( results )


    def __deriveLatticeAndMechanism( self, results ):
        """
        Parses the .rkf file from AMS. Basically it loads the energy landscape and the binding-sites lattice.

        :parm results
        """
        import scm.plams

        eV = 0.0367493088244753
        angs = 1.88972612456506

        self.clusterExpansion = ClusterExpansion()
        self.mechanism = Mechanism()

        rkf_skeleton = results.get_rkf_skeleton()

        nLatticeVectors = results.readrkf("Molecule", "nLatticeVectors")
        latticeVectors = results.readrkf("Molecule", "LatticeVectors")
        latticeVectors = [ [latticeVectors[3*i+j]/angs for j in range(nLatticeVectors) ] for i in range(nLatticeVectors) ]
        regions = results.readrkf("Molecule", "EngineAtomicInfo").split("\0")

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
        toSites = results.readrkf("BindingSites", "ToSites")
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
        attachedMolecule = {}   # attachedMolecule[idState][idSite]

        # Loop over the binding sites to load the binding sites for each local minima
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
                    if( regions[j] != "region="+referenceRegion ):
                        adsorbate.add_atom( atom )

                adsorbate.guess_bonds()
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

        # Each TS defines an ElementaryReaction and at the same time it defines
        # two Clusters from reactants and products.

        # Loop over the TSs to find the species
        for idState in range(nStates):
            if( isTS[idState] ):
                idTS = idState

                # Locates the reactant and product
                idReactant = reactants[idTS]
                idProduct = products[idTS]
                prefactorR = prefactorsFromReactant[idTS]
                prefactorP = prefactorsFromProduct[idTS]
                #print( "idReactant : ", idReactant )
                #print( " idProduct : ", idProduct )

                # Filters the connection specifically for this TS
                neighboring = []
                connectedSites = {}
                for i,bs1 in enumerate(state2BindingSites[idTS]):
                    for j,bs2 in enumerate(state2BindingSites[idTS]):
                        #if( bs1 < bs2 and (bs1,bs2) in sitesConnections ):
                        if( bs1 < bs2
                            and ( (bs1 in fromSites and bs2 in toSites)
                                or (bs1 in toSites and bs2 in fromSites) ) ):
                            #neighboring.append( (bs1,bs2) )
                            neighboring.append( (i,j) )
                            connectedSites[bs1] = 1
                            connectedSites[bs2] = 1

                connectedSites = list( connectedSites.keys() )

                #--------------------------------------------------------------------
                # Reactant
                speciesNames = len(connectedSites)*[ "" ]
                for i,bs in enumerate(connectedSites):
                    if( bs in attachedMolecule[idReactant].keys() ):
                        speciesNames[i] = attachedMolecule[idTS][bs]

                site_types = [ labels[j] for j in connectedSites ]
                species = SpeciesList( [ Species(f+"*",1) for f in speciesNames ] )

                # This section remove the empty adsorption sites which are not needed for clusters
                site_types_cluster = []
                neighboring_cluster = []
                species_cluster = []
                for i in range(len(site_types)):
                    if( not len(speciesNames[i]) == 0 ):
                        site_types_cluster.append( site_types[i] )
                        species_cluster.append( species[i] )
                        for pair in neighboring:
                            if( i not in pair ):
                                neighboring_cluster.append(pair)

                clusterReactant = Cluster( site_types=site_types_cluster,
                                           neighboring=neighboring_cluster,
                                           species=species_cluster,
                                           multiplicity=1,
                                           cluster_energy=state2Energy[idReactant]-energyReference )

                speciesReactant = SpeciesList( [ Species(f+"*",1) for f in speciesNames ] )

                #--------------------------------------------------------------------
                # Product
                speciesNames = len(connectedSites)*[ "" ]
                for i,bs in enumerate(connectedSites):
                    if( bs in attachedMolecule[idProduct].keys() ):
                        speciesNames[i] = attachedMolecule[idTS][bs]

                site_types = [ labels[j] for j in connectedSites ]
                species = SpeciesList( [ Species(f+"*",1) for f in speciesNames ] )

                # This section remove the empty adsorption sites which are not needed for clusters
                site_types_cluster = []
                neighboring_cluster = []
                species_cluster = []
                for i in range(len(site_types)):
                    if( not len(speciesNames[i]) == 0 ):
                        site_types_cluster.append( site_types[i] )
                        species_cluster.append( species[i] )
                        for pair in neighboring:
                            if( i not in pair ):
                                neighboring_cluster.append(pair)

                clusterProduct = Cluster( site_types=site_types_cluster,
                                          neighboring=neighboring_cluster,
                                          species=species_cluster,
                                          multiplicity=1,
                                          cluster_energy=state2Energy[idReactant]-energyReference )

                speciesProduct = SpeciesList( [ Species(f+"*",1) for f in speciesNames ] )

                #--------------------------------------------------------------------
                # Reaction
                activationEnergy = state2Energy[idTS]-state2Energy[idReactant]

                reaction = ElementaryReaction( site_types=[ labels[j] for j in connectedSites ],
                                               neighboring=neighboring,
                                               initial=speciesReactant,
                                               final=speciesProduct,
                                               reversible=True,
                                               pre_expon=prefactorR,
                                               pe_ratio=prefactorR/prefactorP,
                                               activation_energy=activationEnergy )

                self.clusterExpansion.extend( [clusterReactant, clusterProduct] )
                self.mechanism.append( reaction )

        # Loop over the Fragmented states to find the species and reactions
        for idFState in range(nFStates):
            energy = fStatesEnergy[idFState]
            nFragments = fStatesNFragments[idFState]
            composition = fStatesComposition[idFState]

            # Loop over the associated connected states
            for idState in fStatesConnections[idFState]:
                prefactorAdsorption = fStatesAdsorptionPrefactors[idFState][idState]
                prefactorDesorption = fStatesDesorptionPrefactors[idFState][idState]

                # Filters the connection specifically for this state
                neighboring = []
                connectedSites = {}
                for i,bs1 in enumerate(state2BindingSites[idState]):
                    # Each binding sites in the molecule automatically contributes
                    connectedSites[bs1] = 1

                    # Check binding sites connected in the same molecule
                    for j,bs2 in enumerate(state2BindingSites[idState]):
                        if( bs1 < bs2
                            and ( (bs1 in fromSites and bs2 in toSites)
                                or (bs1 in toSites and bs2 in fromSites) ) ):
                            #neighboring.append( (bs1,bs2) )
                            neighboring.append( (i,j) )
                            connectedSites[bs1] = 1
                            connectedSites[bs2] = 1

                connectedSites = list( connectedSites.keys() )

                #--------------------------------------------------------------------
                # State
                speciesNames = len(connectedSites)*[ "" ]
                for i,bs in enumerate(connectedSites):
                    if( bs in attachedMolecule[idState].keys() ):
                        speciesNames[i] = attachedMolecule[idState][bs]

                clusterState = Cluster( site_types=[ labels[j] for j in connectedSites ],
                                        neighboring=neighboring,
                                        species=SpeciesList( [ Species(f+"*",1) for f in speciesNames ] ),
                                        multiplicity=1,
                                        cluster_energy=state2Energy[idState]-energyReference )

                speciesState = SpeciesList( [ Species(f+"*",1) for f in speciesNames ] )

                #--------------------------------------------------------------------
                # Fragmented State
                speciesNames = [ "*" for f in speciesNames ]
                for idFragment in composition:
                    if( fragmentsRegions[idFragment] == "active" ):
                        mol = results.get_molecule("Molecule", file=fragmentsFileNames[idFragment])
                        speciesNames.append( mol.get_formula() )

                speciesFState = SpeciesList( [ Species(f) for f in speciesNames ] )

                #--------------------------------------------------------------------
                # Reaction
                activationEnergy = 0.0 #TODO Here we are assuming that there is no a TS between the fragmented state and the state.

                # X_gas <--> X*
                reaction = ElementaryReaction( site_types=[ labels[j] for j in connectedSites ],
                                               neighboring=neighboring,
                                               initial=speciesFState,
                                               final=speciesState,
                                               reversible=True,
                                               pre_expon=prefactorAdsorption,
                                               pe_ratio=prefactorAdsorption/prefactorDesorption,
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

            if( first is None or second is None ): continue

            # (1,1):"northeast",  <<< #TODO I don't understand this case
            # (1,-1):"southeast"  <<< #TODO I don't understand this case

            neighboring_structure[i] = [first,second]

        self.lattice = Lattice( cell_vectors=[ [v[0],v[1]] for v in latticeVectors[0:2] ], # We omit the z-axis
                                repeat_cell=(1,1), # Default value.
                                site_types=labels,
                                site_coordinates=coordsFrac,
                                neighboring_structure=neighboring_structure)


    def replace_site_types_names( self, site_types_old, site_types_new ):
        """
        Replaces the site types names

        *   ``site_types_old`` -- List of strings containing the old site_types to be replaced
        *   ``site_types_new`` -- List of strings containing the new site_types which would replace old site_types_old.
        """
        assert( len(site_types_old) == len(site_types_new) )

        self.lattice.replace_site_types_names( site_types_old, site_types_new )
        self.mechanism.replace_site_types_names( site_types_old, site_types_new )
        self.clusterExpansion.replace_site_types_names( site_types_old, site_types_new )
