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
        self.__entity_number = lattice.number_of_sites()*[ None ]
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

        processed_entity_number = {}
        for id_site,sp in enumerate(self.__adsorbed_on_site):
            if( sp is not None and self.__entity_number[id_site] not in processed_entity_number ):
                entity_pos = [ str(i+1) for i,v in enumerate(self.__entity_number) if v==self.__entity_number[id_site] ]

                if( len(entity_pos)>0 ):
                    output += "  seed_on_sites "+sp.symbol+" "+' '.join(entity_pos)+"\n"

                    processed_entity_number[ self.__entity_number[id_site] ] = 1

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


    def fill_site( self, site_number, species ):
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

        if( lSpecies.denticity == 1 and not isinstance(site_number,int) ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              Inconsistent values for species denticity and dimensions of site_number\n"
            msg += "              denticity==1 but site_number is not an integer\n"
            raise NameError(msg)

        if( lSpecies.denticity > 1 and not ( isinstance(site_number,list) or isinstance(site_number,tuple) ) ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              Inconsistent values for species denticity and dimensions of site_number\n"
            msg += "              denticity>1 but site_number is not an instance of list or tuple\n"
            raise NameError(msg)

        if( lSpecies.denticity > 1 and ( isinstance(site_number,list) or isinstance(site_number,tuple) ) and len(site_number) != lSpecies.denticity ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              Inconsistent values for species denticity and dimensions of site_number\n"
            msg += "              site_number should have the `denticity` number of elements\n"

        if( lSpecies.denticity > 2 ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              Species with denticity > 2 are not supported yet\n"
            raise NameError(msg)

        if( lSpecies.denticity == 1 ):

            self.__adsorbed_on_site[site_number] = lSpecies
            fvalues = list(filter(lambda x: x is not None,self.__entity_number))
            self.__entity_number[site_number] = max(fvalues)+1 if len(fvalues)>0 else 0

        elif( lSpecies.denticity == 2 ):

            if( site_number[0] not in self.lattice.nearest_neighbors[site_number[1]] and
                site_number[1] not in self.lattice.nearest_neighbors[site_number[0]] ):
                msg  = "### ERROR ### LatticeState.fill_site.\n"
                msg += "              site "+str(site_number[0])+" is not neighboring site "+str(site_number[1])+"\n"
                raise NameError(msg)

            if( self.__adsorbed_on_site[site_number[0]] is None and
                self.__adsorbed_on_site[site_number[1]] is None ):

                self.__adsorbed_on_site[site_number[0]] = lSpecies
                self.__adsorbed_on_site[site_number[1]] = lSpecies
                fvalues = list(filter(lambda x: x is not None,self.__entity_number))
                self.__entity_number[site_number[0]] = max(fvalues)+1 if len(fvalues)>0 else 0
                self.__entity_number[site_number[1]] = self.__entity_number[site_number[0]]
            else:
                msg  = "### ERROR ### LatticeState.fill_site.\n"
                msg += "              site "+str(site_number[0])+" or site "+str(site_number[1])+" is already filled\n"
                raise NameError(msg)

        #print("     final __adsorbed_on_site = ",[ s.symbol if s is not None else "__" for s in self.__adsorbed_on_site ])
        #print("     final __entity_number    = ",[ "%4s"%v if v is not None else "__" for v in  self.__entity_number ])

        self.__updateSpeciesNumbers()


    def fill_sites_random( self, site_name, species, coverage ):
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
            msg  = "### ERROR ### LatticeState.fill_sites_random.\n"
            msg += "              Inconsistent type for species. It should be type str or Species\n"
            raise NameError(msg)

        if( lSpecies.denticity > 2 ):
            msg  = "### ERROR ### LatticeState.fill_sites_random.\n"
            msg += "              Species with denticity > 2 are not supported yet\n"
            raise NameError(msg)

        if( lSpecies.denticity == 1 ):

            target_sites = []
            total_available_conf = []
            for site_number in range(self.lattice.number_of_sites()):
                if( self.__adsorbed_on_site[site_number] is None and
                    self.lattice.site_types[site_number] == site_name ):
                    total_available_conf.append( site_number )
                    target_sites.append( site_number )

        elif( lSpecies.denticity == 2 ):
            target_sites = {}
            total_available_conf = {}

            for site_number_i in range(self.lattice.number_of_sites()):
                for site_number_j in self.lattice.nearest_neighbors[site_number_i]:

                    if( self.__adsorbed_on_site[site_number_i] is None and
                        self.__adsorbed_on_site[site_number_j] is None and
                        site_number_i not in target_sites and
                        site_number_j not in target_sites and
                        ( self.lattice.site_types[site_number_i] == site_name[0] or
                            self.lattice.site_types[site_number_j] == site_name[1] ) and
                        ( self.lattice.site_types[site_number_i] == site_name[1] or
                            self.lattice.site_types[site_number_j] == site_name[0] ) ):

                            if( site_number_i < site_number_j ):
                                total_available_conf[ (site_number_i,site_number_j) ] = 1
                            else:
                                total_available_conf[ (site_number_j,site_number_i) ] = 1
                            target_sites[ site_number_i ] = 1
                            target_sites[ site_number_j ] = 1

            target_sites = list( target_sites.keys() )
            target_sites.sort()
            total_available_conf = list( total_available_conf.keys() )

        n_sites_to_fill = round(len(target_sites)*coverage)

        random.shuffle( total_available_conf )

        filled_sites = {}
        available_conf = []
        for item in total_available_conf:
            if( len(filled_sites) >= n_sites_to_fill ):
                break

            if( lSpecies.denticity == 1 ):
                filled_sites[ item ] = 1
            elif( lSpecies.denticity == 2 ):
                filled_sites[ item[0] ] = 1
                filled_sites[ item[1] ] = 1

            available_conf.append( item )

        #print("filled_sites = ", list(filled_sites.keys()))
        #print("available_conf = ", self.lattice.number_of_sites(), n_sites_to_fill, available_conf)

        fvalues = list(filter(lambda x: x is not None,self.__entity_number))
        entity_number = max(fvalues)+1 if len(fvalues)>0 else 0
        for site_number in available_conf:
            if( lSpecies.denticity == 1 ):
                self.__adsorbed_on_site[site_number] = lSpecies
                self.__entity_number[site_number] = entity_number
                #print("   filling sites", site_number, "with", entity_number)
                #print("     current __adsorbed_on_site = ",[ s.symbol if s is not None else "__" for s in self.__adsorbed_on_site ])
                #print("     current __entity_number    = ",[ "%4s"%v if v is not None else "__" for v in  self.__entity_number ])
                entity_number += 1
            elif( lSpecies.denticity == 2 ):
                self.__adsorbed_on_site[site_number[0]] = lSpecies
                self.__adsorbed_on_site[site_number[1]] = lSpecies
                self.__entity_number[site_number[0]] = entity_number
                self.__entity_number[site_number[1]] = entity_number
                #print("   filling sites", site_number, "with", entity_number)
                #print("     current __adsorbed_on_site = ",[ s.symbol if s is not None else "__" for s in self.__adsorbed_on_site ])
                #print("     current __entity_number    = ",[ "%4s"%v if v is not None else "__" for v in  self.__entity_number ])
                entity_number += 1

        self.__updateSpeciesNumbers()

        if( type(site_name) is str ):
            nsites = self.lattice.site_types.count(site_name)
        elif( type(site_name) is list or type(site_name) is tuple ):
            nsites = sum([ self.lattice.site_types.count(st) for st in site_name ])

        actual_coverage = self.__speciesNumbers[lSpecies.symbol]/len(target_sites)

        #print("   filling nsites", site_number, "with", lSpecies.symbol)
        #print("     final __adsorbed_on_site = ",[ s.symbol if s is not None else "__" for s in self.__adsorbed_on_site ])
        #print("     final __entity_number    = ",[ "%4s"%v if v is not None else "__" for v in  self.__entity_number ])
        #print("     actual_coverage = ", actual_coverage)

        return actual_coverage


    def fill_all_sites( self, site_name, species ):
        """
        Fill all the sites
        """
        self.fill_sites_random( site_name, species, coverage=1.0 )


    def plot(self, pause=-1, show=True, ax=None, close=False, show_sites_ids=False):
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

        if( self.add_info is not None ):
            ax.set_title("t = {:.3f} s".format(self.add_info.get("time")))

        #--------------------------------
        # Plots the lattice
        #--------------------------------
        self.lattice.plot( show=False, ax=ax, color='0.5', show_sites_ids=show_sites_ids )

        #--------------------------------
        # Plots the species
        #--------------------------------
        site_types = list(set(self.lattice.site_types))
        for i,sym_i in enumerate([item.symbol for item in items]):

            if( all([sym is None for sym in symbols]) ): continue

            xvalues = []
            yvalues = []
            imarkers = []
            for (x,y),site_type,sym in zip(self.lattice.site_coordinates,self.lattice.site_types,symbols):
                if( sym == sym_i ):
                    xvalues.append( x )
                    yvalues.append( y )

                    lSpecies = None
                    for sp in self.surface_species:
                        if( sp.symbol == sym_i ):
                            lSpecies = sp
                            break

                    imarkers.append( site_types.index(site_type) )

            ax.scatter(xvalues, yvalues, color=colors[i], marker=markers[imarkers[i]], s=100, zorder=4, label=sym_i)

        #-------------------------------------------------
        # Plots the links for species with denticity > 1
        #-------------------------------------------------
        for id_site,sp in enumerate(self.__adsorbed_on_site):
            if( sp is not None ):
                entity_pos = [ i for i,v in enumerate(self.__entity_number) if v==self.__entity_number[id_site] ]

                if( len(entity_pos)>0 ):
                    for id_site_2 in self.lattice.nearest_neighbors[id_site]:
                        if( id_site_2 in entity_pos ):
                            coords_i = self.lattice.site_coordinates[id_site]
                            coords_j = self.lattice.site_coordinates[id_site_2]
                            ax.plot([coords_i[0],coords_j[0]],
                                    [coords_i[1],coords_j[1]],
                                    color=colors[items.index(sp)], linestyle='solid', linewidth=5, zorder=4)

        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")
