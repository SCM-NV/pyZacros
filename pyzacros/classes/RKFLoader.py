import os
import sys

from .Species import *
from .Mechanism import *
from .Lattice import *

class RKFLoader:

    def __init__( self, results ):
        """
        Creates a new RKFLoader object

        :parm results
        """
        self.mechanism = None
        self.lattice = None

        self.__deriveLatticeAndMechanism( results )


    def __deriveLatticeAndMechanism( self, results ):  # @TODO results -> scm.plams.Results
        """
        The next lines feed self%state2BindingSites.
        The binding sites for the reactants or products are already defined
        The binding sites for a TS are the union of the ones from its reactants and products

        TS ----> R --> bsR1, bsR2, ...
            |
            +--> P --> bsP1, bsP2, ...
        """
        import scm.plams

        eV = 0.0367493088244753
        angs = 1.88972612456506

        self.mechanism = Mechanism()

        nLatticeVectors = results.readrkf("Molecule", "nLatticeVectors")
        latticeVectors = results.readrkf("Molecule", "LatticeVectors")
        latticeVectors = [ [latticeVectors[3*i+j]/angs for j in range(nLatticeVectors) ] for i in range(nLatticeVectors) ]
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
        labels = results.readrkf("BindingSites", "Labels")
        labels = labels.split()
        coords = results.readrkf("BindingSites", "Coords")
        coords = [ [coords[3*i+j]/angs for j in range(3) ] for i in range(nSites) ]
        nConnections = results.readrkf("BindingSites", "nConnections")
        fromSites = results.readrkf("BindingSites", "FromSites")
        toSites = results.readrkf("BindingSites", "ToSites")
        latticeDisplacements = results.readrkf("BindingSites", "LatticeDisplacements")
        latticeDisplacements = [ [latticeDisplacements[3*i+j] for j in range(3) ] for i in range(nConnections) ]
        nParentStates = results.readrkf("BindingSites", "nParentStates")
        parentStatesRaw = results.readrkf("BindingSites", "ParentStates")
        parentAtomsRaw = results.readrkf("BindingSites", "ParentAtoms")

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
                        #if( bs1 < bs2 and (bs1,bs2) in sitesConnections ):
                        if( bs1 < bs2
                            and ( (bs1 in fromSites and bs2 in toSites)
                                or (bs1 in toSites and bs2 in fromSites) ) ):
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

                clusterReactant = Cluster( site_types=[ labels[j] for j in connectedSites ],
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

                clusterProduct = Cluster( site_types=[ labels[j] for j in connectedSites ],
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
        # Remove duplicated reactions in the mechanism
        self.mechanism = Mechanism(dict.fromkeys(self.mechanism))

        #--------------------------------------------------------------------
        # Generation of the KMCLattice
        assert( len(latticeVectors) >= 2 )

        neighboring_structure = nConnections*[ None ]
        for i in range(nConnections):
            ld = latticeDisplacements[i]

            first = "Unknown"
            if( ld[0] > 0 and ld[1] > 0 ):
                first = str(fromSites[i]+1)+"-"+str(toSites[i]+1)
            else:
                first = str(toSites[i]+1)+"-"+str(fromSites[i]+1)
                ld = [ abs(v) for v in ld ]

            second = "Unknown"
            if( tuple(ld[0:2]) == (0,0) ):
                second = "self"
            elif( tuple(ld[0:2]) == (0,1) ):
                second = "north"
            elif( tuple(ld[0:2]) == (1,0) ):
                second = "east"

            # (1,1):"northeast",  <<< #TODO I don't understand this case
            # (1,-1):"southeast"  <<< #TODO I don't understand this case

            neighboring_structure[i] = [first,second]

        site_type_names = list(set(labels))
        site_type_names.sort()

        self.lattice = Lattice(
                            lattice_type="periodic_cell",
                            cell_vectors=latticeVectors,
                            repeat_cell=[1, 1], # Default value.
                            n_cell_sites=nSites,
                            n_site_types=len(site_type_names),
                            site_type_names=site_type_names,
                            site_types=labels,
                            site_coordinates=coords,
                            neighboring_structure=neighboring_structure)
