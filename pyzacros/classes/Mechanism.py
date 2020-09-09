import os
import sys

from .ElementaryReaction import *

class Mechanism(list):

    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output = "mechanism"+"\n"
        for i in range(len(self)):
            output += str(self[i])
            if( i != len(self)-1 ):
                output += "\n"
        output += "\n"
        output += "end_mechanism"

        return output


    def deriveMechanisms( self, results ):
        """
        The next lines feed self%state2BindingSites.
        The binding sites for the reactants or products are already defined
        The binding sites for a TS are the union of the ones from its reactants and products

        TS ----> R --> bsR1, bsR2, ...
            |
            +--> P --> bsP1, bsP2, ...
        """
        import scm.plams

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

        # It is not neccessary for fix the parentAtomsRaw, because PLAMS
        # uses also 1-based indices for its atoms
        #parentAtomsRaw = [ max(0,i-1) for i in parentAtomsRaw ]

        # parentStates and parentAtoms elements are actually vectors for each binding site
        # Here I split the vectors in that way
        parentStates = nSites*[ None ]
        parentAtoms = nSites*[ None ]
        for idSite in range(nSites):
            idStart = sum(nParentStates[0:idSite])
            idEnd = sum(nParentStates[0:idSite])+nParentStates[idSite]

            parentStates[idSite] = parentStatesRaw[idStart:idEnd]
            parentAtoms[idSite] = parentAtomsRaw[idStart:idEnd]

        #--------------------------------------------------------------------------------------
        # The next lines feed the array state2BindingSites.
        # The binding sites for the reactants or products are already defined
        # The binding sites for a TS are the union of the ones from its reactants and products
        #
        # TS ----> R --> bsR1, bsR2, ...
        #     |
        #     +--> P --> bsP1, bsP2, ...
        #--------------------------------------------------------------------------------------

        # Loop over the all states to initialize the elements of state2BindingSites
        state2IsTS = nStates*[ False ]
        for idState in range(nStates):
            if( isTS[idState] ):
                state2IsTS[idState] = True

        state2BindingSites = nStates*[ None ]
        state2BondedAtoms = nStates*[ None ] # Contains pairs (idAtom,idState). The atom of a given state.

        # Loop over the binding sites to load the binding sites for local minima
        for idSite in range(nSites):
            # Loop over the parent states of each binding site
            for i,idState in enumerate(parentStates[idSite]):
                if( state2BindingSites[ idState ] is None ):
                    state2BindingSites[ idState ] = []
                    state2BondedAtoms[ idState ] = []

                state2BindingSites[ idState ].append( idSite )
                state2BondedAtoms[ idState ].append( (parentAtoms[idSite][i],idState) )

        # Loop over the TSs to load their binding sites
        for idState in range(nStates):
            if( isTS[idState] ):
                idReactant = reactants[idState]
                idProduct = products[idState]

                # Loop over the binding sites of the reactant
                for i,idSite in enumerate(state2BindingSites[idReactant]):
                    if( state2BindingSites[ idState ] is None ):
                        state2BindingSites[ idState ] = []
                        state2BondedAtoms[ idState ] = []

                    state2BindingSites[ idState ].append( idSite )
                    state2BondedAtoms[ idState ].append( (parentAtoms[idReactant][i],idReactant) )

                # Loop over the binding sites of the products
                for i,idSite in enumerate(state2BindingSites[idProduct]):
                    if( state2BindingSites[ idState ] is None ):
                        state2BindingSites[ idState ] = []
                        state2BondedAtoms[ idState ] = []

                    state2BindingSites[ idState ].append( idSite )
                    state2BondedAtoms[ idState ].append( (parentAtoms[idProduct][i],idProduct) )

        # Loop over the TSs to find the connections
        state2SiteConnections = nStates*[ None ]
        for idState in range(nStates):
            if( isTS[idState] ):

                for idSite1 in state2BindingSites[idState]:
                    for idSite2 in state2BindingSites[idState]:
                        if( idSite2 <= idSite1 ):
                            continue

                        for l in range(nConnections):
                            if( ( fromSites[l] == idSite1 and toSites[l] == idSite2 ) or
                                ( fromSites[l] == idSite2 and toSites[l] == idSite1 ) ):

                                if( state2SiteConnections[idState] is None ):
                                    state2SiteConnections[idState] = []

                                state2SiteConnections[idState].append( (idSite1,idSite2) )

        ## Loop over the TSs to find the species
        state2Species = nStates*[ None ]
        for idState in range(nStates):
            if( isTS[idState] ):
                idReactant = reactants[idState]
                idProduct = products[idState]

                # Reactants >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                mol = results.get_molecule("Molecule", file=fileNames[idReactant])

                adsorbate = scm.plams.Molecule()
                for j,atom in enumerate(mol):
                    if( regions[j] == "region="+adsorbateLabel ):
                        adsorbate.add_atom( atom )

                adsorbateMols = adsorbate.separate()

                for idAtom,idStateParent in state2BondedAtoms[idState]:
                    if( idReactant == idStateParent ): # >> The state is the same mol
                        for sMol in adsorbateMols:
                            for atom in sMol:
                                if( all( [ abs(atom.coords[i]-mol[idAtom].coords[i]) < 1e-6 ] ) ):
                                    if( state2Species[ idState ] is None ):
                                        state2Species[ idState ] = []
                                    state2Species[idState].append( adsorbate.get_formula() )

                # Products >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                mol = results.get_molecule("Molecule", file=fileNames[idProduct])

                adsorbate = scm.plams.Molecule()
                for j,atom in enumerate(mol):
                    if( regions[j] == "region="+adsorbateLabel ):
                        adsorbate.add_atom( atom )

                adsorbateMols = adsorbate.separate()

                for idAtom,idStateParent in state2BondedAtoms[idState]:
                    if( idProduct == idStateParent ): # >> The state is the same mol
                        for sMol in adsorbateMols:
                            for atom in sMol:
                                if( all( [ abs(atom.coords[i]-mol[idAtom].coords[i]) < 1e-6 ] ) ):
                                    if( state2Species[ idState ] is None ):
                                        state2Species[ idState ] = []
                                    state2Species[idState].append( adsorbate.get_formula() )

        for idState in range(nStates):
            if( isTS[idState] ):
                print(">>>>>>>>>> Cluster" , idState, "<<<<<<<<<<")
                print("self.site_types  = ", [ labels[j] for j in state2BindingSites[idState] ])
                print("self.neighboring = ", state2SiteConnections[idState])
                print("self.species     = ", state2Species[idState])

#! !         >>>>>>>>>> Elementary Reaction <<<<<<<<<<
#! !         self.site_types = site_types   # e.g. [ "f", "f" ]
#! !         self.neighboring = neighboring # e.g. [ (1,2) ]
#! !         self.initial = initial: Cluster
#! !         self.final = final: Cluster
#! !         self.reversible = reversible
#! !         self.pre_expon = pre_expon
#! !         self.pe_ratio = pe_ratio
#! !         self.activation_energy = activation_energy     # e.g. 0.200
#!
#! !         >>>>>>>>>> Cluster <<<<<<<<<<
#! !         self.site_types = site_types                  # e.g. ( "f", "f" )
#! !         self.neighboring = neighboring                # e.g. [ (1,2) ]
#! !         self.species = species                        # e.g. ( Species("H*",1), Species("H*",1) )
#! !         self.gas_species = gas_species                # e.g. ( Species("H2") )
#! !         self.multiplicity = multiplicity              # e.g. 2
#! !         self.cluster_energy = cluster_energy          # Units eV

    #def fromAMS( self, amsResultsDirName: str="ams.results" ):
    #def fromAMS( self, result: scm.plams.Results ):
    def fromAMS( self, results ):
        """
        Loads the mechanism from a AMS results object

        :parm amsResultsDirName: str. Stablishes the file name of the rkf file to load
        :parm results: str. xxxx
        """
        # Tries to use PLAMS from AMS
        AMSHOME = os.getenv("AMSHOME")
        if( AMSHOME is not None ):
            if( AMSHOME+"/scripting" not in sys.path ):
                sys.path.append( AMSHOME+"/scripting" )

        # If AMS is not available, it tries to load the package from PYTHONPATH
        try:
            import scm.plams
        except ImportError:
            raise Exception( "Package scm.plams is required!" )

        scm.plams.init()

        print("\n-------------------------------------")
        print(" Results")
        print("-------------------------------------\n")

        nStates = results.readrkf("EnergyLandscape", "nStates")
        fileNames = results.readrkf("EnergyLandscape", "fileNames").replace(".rkf","").split()
        counts = results.readrkf("EnergyLandscape", "counts")
        isTS = results.readrkf("EnergyLandscape", "isTS")
        reactants = results.readrkf("EnergyLandscape", "reactants")
        products = results.readrkf("EnergyLandscape", "products")

        #print("nStates = ", nStates)
        #print("fileNames = ", fileNames)
        #print("counts = ", counts)
        #print("isTS = ", isTS)
        #print("reactants = ", reactants)
        #print("products = ", products)

        for i,fileName in enumerate(fileNames):
            mol = results.get_molecule("Molecule", file=fileNames[i])
            skeleton = results.get_rkf_skeleton( file=fileNames[i] )
            amsResults = results.read_rkf_section("AMSResults", file=fileNames[i])
            vibrations = results.read_rkf_section("Vibrations", file=fileNames[i])
            #print("Id = ", i)
            #print("Energy = ", amsResults["Energy"])
            #print("Frequencies = ", vibrations["Frequencies[cm-1]"])
            #print(mol)

        nSites = results.readrkf("BindingSites", "nSites")
        AdsorbateLabel = results.readrkf("BindingSites", "AdsorbateLabel")
        Labels = results.readrkf("BindingSites", "Labels")
        AverEnergy = results.readrkf("BindingSites", "AverEnergy")
        StdevEnergy = results.readrkf("BindingSites", "StdevEnergy")
        Coords = results.readrkf("BindingSites", "Coords")
        nConnections = results.readrkf("BindingSites", "nConnections")
        FromSites = results.readrkf("BindingSites", "FromSites")
        ToSites = results.readrkf("BindingSites", "ToSites")
        LatticeDisplacements = results.readrkf("BindingSites", "LatticeDisplacements")
        nParentStates = results.readrkf("BindingSites", "nParentStates")
        ParentStates = results.readrkf("BindingSites", "ParentStates")

        self.deriveMechanisms( results )

        scm.plams.finish()
