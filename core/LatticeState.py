import math
import random

from .Species import *
from .SpeciesList import *
from .Lattice import *

__all__ = ['LatticeState']

class LatticeState:
    """
    LatticeState class that represents a state for a Zacros simulation.

    *   ``lattice`` --
    *   ``surface_species`` --
    *   ``initial`` --
    *   ``add_info`` --
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
        for sp in self.surface_species:
            self.__speciesNumbers[sp] = 0


    def __str__(self):
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
                output += "  #   - "+sp.symbol+"  "+str(nsites)+"\n"

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


    def empty(self):
        """
        Returns true if the state is empty
        """
        return ( len(self.__adsorbed_on_site) == self.__adsorbed_on_site.count(None) )


    def number_of_filled_sites(self):
        """
        Returns number of filled sites on the lattice
        """
        return len(self.__adsorbed_on_site)


    def _updateSpeciesNumbers(self):
        for sp in self.surface_species:
            self.__speciesNumbers[sp] = 0

        for sp in self.__adsorbed_on_site:
            if( sp is None ): continue

            if( sp not in self.__speciesNumbers ):
                self.__speciesNumbers[sp] = 1
            else:
                self.__speciesNumbers[sp] += 1


    def fill_site(self, site_number, species, update_species_numbers=True):
        """
        Fills the ``site_number`` site with the species ``species``

        *   ``site_number`` --
        *   ``species`` --
        *   ``update_species_numbers`` --
        """
        lSpecies = None
        if( isinstance(species, str) ):
            for sp in self.surface_species:
                if( sp.symbol == species ):
                    lSpecies = sp
                    break
        elif( isinstance(species, Species) ):
            lSpecies = species

        if( isinstance(site_number,int) ):
            site_number = [site_number]

        if( not ( isinstance(site_number,list) or isinstance(site_number,tuple) ) ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              Inconsistent values for species denticity and dimensions of site_number\n"
            msg += "              denticity>1 but site_number is not an instance of list or tuple\n"
            raise NameError(msg)

        if( len(site_number) != lSpecies.denticity ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              Inconsistent values for species denticity and dimensions of site_number\n"
            msg += "              site_number should have the `denticity` number of elements\n"
            raise NameError(msg)

        if( any([self.__adsorbed_on_site[site] is not None for site in site_number]) ):
            msg  = "### ERROR ### LatticeState.fill_site.\n"
            msg += "              site is already filled\n"
            raise NameError(msg)

        connected = [site_number[0]]
        to_check = [site_number[0]]
        while( to_check and len(connected) < lSpecies.denticity ):
            new_check = []
            for site in to_check:
                new_check.extend(list(filter(lambda x: x in site_number and x not in connected and x not in to_check,self.lattice.nearest_neighbors[site])))
            to_check = list(set(new_check))
            connected.extend(to_check)

        if( len(connected) != lSpecies.denticity ):
             msg  = "### ERROR ### LatticeState.fill_site.\n"
             msg += "              sites are not neighboring\n"
             raise NameError(msg)

        fvalues = list(filter(lambda x: x is not None,self.__entity_number))
        entity_number = max(fvalues)+1 if len(fvalues)>0 else 0

        for site in site_number:
            self.__adsorbed_on_site[site] = lSpecies
            self.__entity_number[site] = entity_number

        if( update_species_numbers ):
            self._updateSpeciesNumbers()


    def fill_sites_random(self, site_name, species, coverage, neighboring=None):
        """
        Fills the named sites ``site_name`` randomly with the species ``species`` by keeping a
        coverage given by ``coverage``. Coverage is defined relative to the available empty sites.
        Neighboring can be specified if the sites are not neighboring linearly, but are branched
        or cyclical.

        *   ``site_name`` --
        *   ``species`` --
        *   ``coverage`` --
        *   ``neighboring`` --
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

        if ( isinstance(site_name, str) or isinstance(site_name, int) ):
            site_name = [site_name]

        if ( lSpecies.denticity != len(site_name) ):
            msg = "### ERROR ### LatticeState.fill_sites_random.\n"
            msg += "             Inconsistent amount of site_name with species denticity\n"
            raise NameError(msg)

        neighboring_order = []
        if ( lSpecies.denticity > 1 ):
            if ( neighboring == None ):
                neighboring = [[x-1,x] for x in range(1,lSpecies.denticity)]
                neighboring_order = range(lSpecies.denticity)
            else:
                connected = [0]
                to_check = [0]
                # We need to check if the sites are neighboring, and generate an ordering to generate the subgraphs from the site_names
                # E.g. when denticity == 3 and neighboring=[[0,2],[1,2]], it should generate as site_name[0], site_name[2], site_name[1]
                while ( to_check and len(connected) < lSpecies.denticity ):
                    new_check = []
                    for site in to_check:
                        neighbor_pairs = list(filter(lambda x: site in x,neighboring))
                        neighbors = [x[0] if x[1] == site else x[1] for x in neighbor_pairs]
                        new_check.extend(list(filter(lambda x: x not in connected and x not in to_check,neighbors)))
                    to_check = list(set(new_check))
                    connected.extend(to_check)
                if( len(connected) != lSpecies.denticity ):
                    msg = "### ERROR ### LatticeState.fill_sites_random.\n"
                    msg += "             neighboring sites not connected.\n"
                    raise NameError(msg)
                neighboring_order = connected
                neighboring = [[x[0],x[1]] if connected.index(x[0]) < connected.index(x[1]) else [x[1],x[0]] for x in neighboring]

        total_available_conf = []

        empty_sites = list(filter(lambda x: self.__adsorbed_on_site[x] is None and self.lattice.site_types[x] == site_name[0],range(self.lattice.number_of_sites())))
        for site_number_i in empty_sites:
            available_conf = [[site_number_i]]
            for identicity in neighboring_order[1:]:
                new_conf = []
                neighbors = list(filter(lambda x: x[1] == identicity, neighboring))
                for conf in available_conf:
                    nearest_neighbors = [self.lattice.nearest_neighbors[conf[neighboring_order.index(x[0])]] for x in neighbors]
                    if (not nearest_neighbors):
                        continue
                    nearest_neighbors = set.intersection(*map(set,nearest_neighbors))
                    new_conf.extend([conf + [x] for x in list(filter(lambda x:
                                    self.__adsorbed_on_site[x] is None and
                                    x not in conf and
                                    self.lattice.site_types[x] == site_name[identicity],
                                    nearest_neighbors))])
                available_conf = new_conf
            total_available_conf.extend(available_conf)

        target_sites = set([item for sublist in total_available_conf for item in sublist])
        n_sites_to_fill = round(len(target_sites)*coverage)
        random.shuffle( total_available_conf )

        filled_sites = {}
        available_conf = []
        for conf in total_available_conf:
            if( len(filled_sites) >= n_sites_to_fill ):
                break

            if any((site in filled_sites for site in conf)):
                continue

            for site in conf:
                filled_sites[ site ] = True
            available_conf.append( conf )

        fvalues = list(filter(lambda x: x is not None,self.__entity_number))
        entity_number = max(fvalues)+1 if len(fvalues)>0 else 0
        for conf in available_conf:
            for site_number in conf:
                self.__adsorbed_on_site[site_number] = lSpecies
                self.__entity_number[site_number] = entity_number
            entity_number += 1

        self._updateSpeciesNumbers()

        if (lSpecies not in self.__speciesNumbers):
            return 0.0
        actual_coverage = self.__speciesNumbers[lSpecies]/len(target_sites)
        return actual_coverage


    def fill_all_sites( self, site_name, species ):
        """
        Fills all available named sites ``site_name`` with the species ``species``.

        *   ``site_name`` --
        *   ``species`` --
        """
        self.fill_sites_random( site_name, species, coverage=1.0 )


    def coverage_fractions(self):
        """
        Returns a dictionary with the coverage fractions
        """
        fractions = {}
        for sp in self.surface_species:
            fractions[sp.symbol] = 0.0

        for sp,nsites in self.__speciesNumbers.items():
            fractions[sp.symbol] = float(nsites)/self.lattice.number_of_sites()

        return fractions


    def plot(self, pause=-1, show=True, ax=None, close=False, show_sites_ids=False, file_name=None):
        """
        Uses matplotlib to visualize the lattice state

        *   ``pause`` --
        *   ``show`` --
        *   ``ax`` --
        *   ``close`` --
        *   ``show_sites_ids`` --
        *   ``file_name`` --
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
        self.lattice.plot( show=False, ax=ax, color='0.8', show_sites_ids=show_sites_ids )

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

            if( len(xvalues)>0 ):
                #ax.scatter(xvalues, yvalues, color=colors[i], marker=markers[imarkers[i]], s=100, zorder=4, label=sym_i)
                #ax.scatter(xvalues, yvalues, color=colors[i], marker=markers[imarkers[i]], s=100/5, zorder=4, label=sym_i)
                ax.scatter(xvalues, yvalues, color=colors[i], marker=markers[imarkers[i]],
                           s=450/math.sqrt(len(self.lattice.site_coordinates)), zorder=4, label=sym_i)

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

        if( file_name is not None ):
            plt.savefig( file_name )

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")
