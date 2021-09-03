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

    def __init__(self, lattice, surface_species, initial=True, add_info=None):
        """
        Creates a new LatticeState object.
        """
        self.lattice = lattice
        self.add_info = add_info

        if( type(surface_species) != SpeciesList and type(surface_species) != list ):
            msg  = "### ERROR ### LatticeState.__init__.\n"
            msg += "              Inconsistent type for surface_species\n"
            raise NameError(msg)

        self.surface_species = surface_species
        if( type(surface_species) == list ):
            self.surface_species = SpeciesList(surface_species)

        if( len( self.surface_species.gas_species() ) > 0 ):
            msg  = "### ERROR ### LatticeState.__init__.\n"
            msg += "              LatticeState doesn't accept gas surface_species\n"
            raise NameError(msg)

        self.initial = initial

        self.__adsorbed_on_site = lattice.number_of_sites()*[ None ]
        self.__speciesNumbers = {}


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        if( self.initial ):
            output  = "initial_state"+"\n"
        else:
            output  = "state"+"\n"

        if( self.surface_species is not None ): output += "  # species "+(" ".join([sp.symbol for sp in self.surface_species]))+"\n"

        if( len(self.__speciesNumbers) > 0 ):
            output += "  # species_numbers\n"
            for sp,nsites in self.__speciesNumbers.items():
                output += "  #   - "+sp+"  "+str(nsites)+"\n"

        for id_site,sp in enumerate(self.__adsorbed_on_site):
            if( sp is not None ):
                output += "  seed_on_sites "+sp.symbol+" "+str(id_site+1)+"\n"

        if( self.initial ):
            output += "end_initial_state"
        else:
            output += "end_state"

        return output


    def empty( self ):
        """
        Returns true if the state is empty
        """
        return ( len(self.__adsorbed_on_site) == self.__adsorbed_on_site.count(None) )


    def __updateSpeciesNumbers( self ):
        self.__speciesNumbers = {}
        for sp in self.__adsorbed_on_site:
            if( sp is None ): continue

            if( sp.symbol not in self.__speciesNumbers ):
                self.__speciesNumbers[sp.symbol] = 1
            else:
                self.__speciesNumbers[sp.symbol] += 1


    def fillSite( self, site_number, species ):
        """
        Fill the site_number state with the species species
        """
        lSpecies = None
        if( isinstance(species, str) ):
            for sp in self.surface_species:
                if( sp.symbol == species ):
                    lSpecies = sp
                    break
        elif( isinstance(species, Species) ):
            lSpecies = species

        self.__adsorbed_on_site[site_number] = lSpecies
        self.__updateSpeciesNumbers()


    def fillSitesRandom( self, site_name, species, coverage ):
        """
        Fill the sites
        """
        lSpecies = None
        if( isinstance(species, str) ):
            for sp in self.surface_species:
                if( sp.symbol == species ):
                    lSpecies = sp
                    break
        elif( isinstance(species, Species) ):
            lSpecies = species

        else:
            msg  = "### ERROR ### LatticeState.fillSitesRandom.\n"
            msg += "              Inconsistent type for species. It should be type str or Species\n"
            raise NameError(msg)

        if( lSpecies.denticity > 1 ):
            msg  = "### ERROR ### LatticeState.fillSitesRandom.\n"
            msg += "              Species with denticity > 1 are not yet supported\n"
            raise NameError(msg)

        available_sites = []
        for site_number in range(self.lattice.number_of_sites()):
            if( self.__adsorbed_on_site[site_number] is None and self.lattice.site_types[site_number] == site_name ):
                available_sites.append( site_number )

        n_sites_to_fill = round(len(available_sites)*coverage)

        random.shuffle( available_sites )
        available_sites = available_sites[0:n_sites_to_fill]

        for site_number in available_sites:
            self.__adsorbed_on_site[site_number] = lSpecies

        self.__updateSpeciesNumbers()


    def fillAllSites( self, site_name, species ):
        """
        Fill all the sites
        """
        self.fillSitesRandom( site_name, species, coverage=1.0 )


    def plot(self, pause=-1, show=True, ax=None, close=False):
        """
        Uses matplotlib to visualize the lattice state
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            return  # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        #markers = ['o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'd']
        markers = ['o', 's', 'v', '^']
        colors = ['r', 'g', 'b', 'm']

        symbols = [sp if sp is None else sp.symbol for sp in self.__adsorbed_on_site]

        items = list(filter(None.__ne__, set(self.__adsorbed_on_site)))

        ax.set_title("t = {} s".format(self.add_info.get("time")))
        self.lattice.plot( show=False, ax=ax, color='0.5' )

        for i,sym_i in enumerate([item.symbol for item in items]):

            if( all([sym is None for sym in symbols]) ): continue

            xvalues = [ x for (x,y),sym in zip(self.lattice.site_coordinates,symbols) if sym==sym_i ]
            yvalues = [ y for (x,y),sym in zip(self.lattice.site_coordinates,symbols) if sym==sym_i ]

            ax.scatter(xvalues, yvalues, color=colors[i], marker=markers[i], s=100, zorder=4, label=sym_i)

        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")
