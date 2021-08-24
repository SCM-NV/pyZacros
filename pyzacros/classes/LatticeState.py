import math
import random

from .Species import *
from .SpeciesList import *
from .Lattice import *

__all__ = ['LatticeState']

class LatticeState:
    """
    LatticeState class that represents a state for a Zacros simulation.
    """

    def __init__(self, lattice, species):
        """
        Creates a new LatticeState object.
        """
        self.id = -1
        self.number_of_events = None
        self.time = None
        self.temperature = None
        self.energy = None
        self.lattice = lattice

        if( type(species) != SpeciesList and type(species) != list ):
            msg  = "### ERROR ### LatticeState.__init__.\n"
            msg += "              Inconsistent type for species\n"
            raise NameError(msg)

        self.species = species
        self.__filledSitesPerSpecies = {}
        self.__speciesNumbers = {}


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        if( self.id == -1 ):
            output  = "initial_state"+"\n"
        else:
            output  = "state"+"\n"

        if( self.id is not None and self.id != -1 ): output += "  # id "+str(self.id)+"\n"
        if( self.number_of_events is not None ): output += "  # number_of_events "+str(self.number_of_events)+"\n"
        if( self.time is not None ): output += "  # time "+"%.16e"%self.time+"\n"
        if( self.temperature is not None ): output += "  # temperature "+"%.16e"%self.temperature+"\n"
        if( self.energy is not None ): output += "  # energy "+"%.16e"%self.energy+"\n"

        if( self.species is not None ): output += "  # species "+(" ".join([sp.symbol for sp in self.species]))+"\n"

        if( len(self.__speciesNumbers) > 0 ):
            output += "  # species_numbers\n"
            for sp,nsites in self.__speciesNumbers.items():
                output += "  #   - "+sp.symbol+"  "+str(nsites)+"\n"

        for sp,id_sites in self.__filledSitesPerSpecies.items():
            for i,id_site in enumerate(id_sites):
                output += "  seed_on_sites "+sp.symbol+" "+str(id_site)+"\n"

        if( self.id == -1 ):
            output += "end_initial_state"
        else:
            output += "end_state"

        return output


    def empty( self ):
        """
        Returns true if the initial state is empty
        """
        return ( len(__filledSitesPerSpecies) > 0 )


    def __updateSpeciesNumbersFromFilledSitesPerSpecies( self ):
        for sp,fsites in self.__filledSitesPerSpecies.items():
            self.__speciesNumbers[sp] = len(fsites)


    def fillSites( self, site_name, species, coverage ):
        """
        Fill the sites
        """
        effSpecies = None
        if( isinstance(species, str) ):
            for sp in self.species:
                if( sp.symbol == species ):
                    effSpecies = sp
                    break

        elif( isinstance(species, Species) ):
            effSpecies = species

        else:
            msg  = "### ERROR ### LatticeState.fillSites.\n"
            msg += "              Inconsistent type for species. It should be type str or Species\n"
            raise NameError(msg)

        if( effSpecies.denticity > 1 ):
            msg  = "### ERROR ### LatticeState.fillSites.\n"
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

        self.__updateSpeciesNumbersFromFilledSitesPerSpecies()


    def fillAllSites( self, site_name, species ):
        """
        Fill all the sites
        """
        self.fillSites( site_name, species, coverage=1.0 )
