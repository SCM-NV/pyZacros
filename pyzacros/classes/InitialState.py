import math
import random

from .Species import *
from .Lattice import *
from .Mechanism import *

class InitialState:
    """
    InitialState class that represents the initial state for a Zacros simulation.
    By default a KMC simulation in Zacros is initialized with an empty lattice.
    """

    def __init__(self, lattice: Lattice, mechanism: Mechanism):
        """
        Creates a new InitialState object.

        :parm mechanism: Mechanism containing the mechanisms involed in the
                        calculation.
        :parm lattice: Lattice containing the lattice to be used during the
                       calculation.
        """
        self.lattice = lattice
        self.mechanism = mechanism
        self.__filledSitesPerSpecies = {}

        # #TODO We need to make a way to check if a lattice is compatible with the mechanism

    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output  = "initial_state"+"\n"

        for species,id_sites in self.__filledSitesPerSpecies.items():
            for i,id_site in enumerate(id_sites):
                output += "  seed_on_sites "+species.symbol+" "+str(id_site)+"\n"

        output += "end_initial_state"

        return output


    def empty( self ):
        """
        Returns true if the initial state is empty
        """
        return ( len(__filledSitesPerSpecies) > 0 )


    def fillSites( self, site_name, species, coverage ):
        """
        Fill the sites
        """
        effSpecies = None
        if( isinstance(species, str) ):
            for sp in self.mechanism.species():
                if( sp.symbol == species ):
                    effSpecies = sp
                    break

        elif( isinstance(species, Species) ):
            effSpecies = species

        else:
            msg  = "### ERROR ### InitialState.fillSites.\n"
            msg += "              Inconsistent type for species. It should be type str or Species\n"
            raise NameError(msg)

        if( effSpecies.denticity > 1 ):
            msg  = "### ERROR ### InitialState.fillSites.\n"
            msg += "              Species with denticity > 1 are not yet supported\n"
            raise NameError(msg)

        # Makes a list of the filled sites
        filledSites = []
        for key,value in self.__filledSitesPerSpecies.items():
            filledSites.extend( value )

        filledSitesPerSpecies = {}
        nx = self.lattice.repeat_cell[0]
        ny = self.lattice.repeat_cell[1]

        nSitesOfThisKind = 0
        k = 1 # Zacros starts in 1
        for i in range(nx):
            for j in range(ny):
                for idSite,sname in enumerate(self.lattice.site_types):

                    if( sname == site_name ):
                        if( effSpecies not in filledSitesPerSpecies ):
                            filledSitesPerSpecies[effSpecies] = []

                        if( k not in filledSites ):
                            filledSitesPerSpecies[effSpecies].append(k)
                            filledSites.append(k)

                        nSitesOfThisKind += 1

                    k += 1

        nSitesToKeep = round(nSitesOfThisKind*coverage)

        # Removes elements according with the coverage
        for key,value in filledSitesPerSpecies.items():
            random.shuffle( filledSitesPerSpecies[key] )

            while( len(filledSitesPerSpecies[key]) > nSitesToKeep ):
                filledSitesPerSpecies[key].pop()

        # Removes empty sites per species
        toRemove = []
        for key,value in filledSitesPerSpecies.items():
            if( len(filledSitesPerSpecies[key]) == 0 ):
                toRemove.append( key )

        for key in toRemove:
            filledSitesPerSpecies.pop( key )

        # Updates self.__filledSitesPerSpecies
        for key,value in filledSitesPerSpecies.items():
            if( key in self.__filledSitesPerSpecies ):
                self.__filledSitesPerSpecies[key].extend(value)
            else:
                self.__filledSitesPerSpecies[key] = value

            self.__filledSitesPerSpecies[key] = sorted(self.__filledSitesPerSpecies[key])


    def fillAllSites( self, site_name, species ):
        """
        Fill all the sites
        """
        self.fillSites( site_name, species, coverage=1.0 )
