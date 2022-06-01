from .Species import *
from .SpeciesList import SpeciesList

__all__ = ['Cluster']

class Cluster:
    """
    Creates a new Cluster object. As in Zacros, each cluster is represented as a graph pattern, consisting of a collection of connected sites onto which surface species can bind. This pattern involves multi/mono-dentate species bound to neighboring sites of different types.

    *   ``species`` -- List of species bound to the sites, e.g. ``[ Species("H*",1), Species("H*",1) ]``
    *   ``site_types`` -- Specifies the name of the sites in the graph pattern representing the cluster. Notice that the order is essential and it should agree with the species option, e.g. ``['fcc','hcp']``.
    *   ``entity_number`` -- List of the molecular entities ids bound to each site. Notice that the order is essential and should agree with the site_types option. For example, if a bidentate species is bound to sites 1 and 2 ( ``species=[ Species("H**",2), Species("H**",2) ]`` ), both of these sites will have the same entity numbers, i.e. ``entity_number=[0,0]``. By default, the list of entity numbers is created by assuming that species with the same symbol belong to the same entity.
    *   ``neighboring`` -- Specifies the neighboring between sites, if more than one sites appear in the graph pattern, e.g. [ (0,1) ]
    *   ``multiplicity`` -- The multiplicity of the pattern, namely the number of times that the exact same pattern will be counted for a given lattice configuration.
    *   ``cluster_energy`` -- The energy contribution of the pattern in eV.
    *   ``label`` -- If None, a unique label is generated based on its composition.
    """

    def __init__(self, species,
                 site_types = None,
                 entity_number = None,
                 neighboring = None,
                 multiplicity = 1,
                 cluster_energy = 0.000,
                 label = None):
        """
        Creates a new Cluster object
        """
        self.species = species                        # e.g. [ Species("H*",1), Species("H*",1) ]
        self.sites = len([ sp for sp in species if sp == Species.UNSPECIFIED or sp.is_adsorbed() ])

        if( site_types is not None ):
            if( not ( all([ type(st)==int for st in site_types ]) or all([ type(st)==str for st in site_types ]) ) ):
                msg  = "\n### ERROR ### ElementaryReaction.__init__.\n"
                msg += "              Inconsistent type for site_types. It should be a list of int or str\n"
                raise NameError(msg)

            self.site_types = site_types              # e.g. [ "f", "f" ], [ 0, 0 ]
        else:
            self.site_types = self.sites*[ 0 ]

        self.neighboring = neighboring                # e.g. [ (0,1) ]
        self.multiplicity = multiplicity              # e.g. 2
        self.cluster_energy = cluster_energy          # Units eV

        self.entity_number = entity_number
        if( entity_number is None ): self.entity_number = SpeciesList.default_entity_numbers( self.sites, self.species )

        #TODO Make a way to check denticity consistency
        #if( sum([s.denticity for s in self.species]) != self.sites ):
            #msg  = "\n### ERROR ### Cluster.__init__.\n"
            #msg += "Inconsistent dimensions for species or site_types\n"
            #raise NameError(msg)

        self.__userLabel = label
        self.__label = None
        self.__updateLabel()

        self.__mass = 0.0

        for item in species:
            if( item != Species.UNSPECIFIED ):
                self.__mass += item.mass()


    def __len__(self):
        """
        Returns the number of species inside the cluster
        """
        return len(self.species)


    def __eq__(self, other):
        """
        Returns True if both objects have the same label. Otherwise returns False

        *   ``other`` --
        """
        if( self.__label == other.__label ):
            return True
        else:
            return False


    def __hash__(self):
        """
        Returns a hash based on the label
        """
        return hash(self.__label)


    def __updateLabel(self):
        """
        Updates the attribute 'label'
        """
        if( self.__userLabel is not None ):
            self.__label = self.__userLabel
            return

        self.__label = ""
        for i in range(len(self.species)):
            if( self.species[i] != Species.UNSPECIFIED ):
                self.__label += self.species[i].symbol
            else:
                self.__label += "&"

            if( len(self.entity_number)>1 ):
                self.__label += "_"+str(self.entity_number[i]+1)
            self.__label += "-"
            self.__label += str(self.site_types[i])
            if(i != len(self.species)-1):
                self.__label += ","

        if self.neighboring is not None:
            if(len(self.neighboring) > 0):
                self.__label += ":"

        # For neighboring nodes are sorted
        if self.neighboring is not None:
            for i in range(len(self.neighboring)):
                lNeighboring = list(self.neighboring[i])
                lNeighboring.sort()
                self.__label += str(tuple(lNeighboring)).replace(" ", "")
                if( i != len(self.neighboring)-1):
                    self.__label += ","


    def label(self):
        """
        Returns the label of the cluster
        """
        if( self.__label is None ):
            self.__updateLabel()

        return self.__label


    def __str__(self):
        """
        Translates the object to a string
        """
        output  = "cluster " + self.__label +"\n"

        if( self.sites != 0 ):
            output += "  sites " + str(self.sites)+"\n"

            if self.neighboring is not None and len(self.neighboring) > 0:
                output += "  neighboring "
                for i in range(len(self.neighboring)):
                    output += str(self.neighboring[i][0]+1)+"-"+str(self.neighboring[i][1]+1)
                    if( i != len(self.neighboring)-1 ):
                        output += " "
                output += "\n"

            site_identate = {}
            output += "  lattice_state"+"\n"
            for i in range(self.sites):
                if( self.entity_number[i] not in site_identate ):
                    site_identate[ self.entity_number[i] ] = 0
                else:
                    site_identate[ self.entity_number[i] ] = site_identate[ self.entity_number[i] ] + 1

                if( self.species[i] != Species.UNSPECIFIED ):
                    if( site_identate[ self.entity_number[i] ] >= self.species[i].denticity ):
                        msg  = "\n### ERROR ### Cluster.__str__.\n"
                        msg += "Inconsistent of denticity value for "+self.species[i].symbol+"\n"
                        raise NameError(msg)

                    output += "    "+str(self.entity_number[i]+1)+" "+self.species[i].symbol+" "+str(site_identate[self.entity_number[i]]+1)+"\n"
                else:
                    output += "    & & &\n"

            output += "  site_types "
            for i in range(len(self.site_types)):

                if( type(self.site_types[i]) == int ):
                    output += str(self.site_types[i]+1)
                elif( type(self.site_types[i]) == str ):
                    output += self.site_types[i]

                if( i != len(self.site_types)-1 ):
                    output += " "
            output += "\n"

            output += "  graph_multiplicity "+str(self.multiplicity)+"\n"

        output += "  cluster_eng "+("%12.5e"%self.cluster_energy)+"\n"
        output += "end_cluster"

        return output


    def mass(self):
        """
        Returns the mass of the cluster in Da
        """
        return self.__mass


    def gas_species(self):
        """Returns the gas species."""
        species = []

        for sp in self.species:
            if( sp != Species.UNSPECIFIED and sp.kind == Species.GAS ):
                species.append( sp )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species


    def surface_species(self):
        """Returns the surface species."""
        species = []

        for sp in self.species:
            if( sp != Species.UNSPECIFIED and sp.kind == Species.SURFACE ):
                species.append( sp )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species


    def site_types_set(self):
        """
        Returns the set of the sites types
        """
        return set(self.site_types)


    def replace_site_types( self, site_types_old, site_types_new ):
        """
        Replaces the site types names

        *   ``site_types_old`` -- List of strings containing the old site_types to be replaced
        *   ``site_types_new`` -- List of strings containing the new site_types which would replace old site_types_old.
        """
        assert( len(site_types_old) == len(site_types_new) )

        for i in range(len(site_types_old)):
            for j in range(len(self.site_types)):
                if( self.site_types[j] == site_types_old[i] ):
                    self.site_types[j] = site_types_new[i]

        self.__updateLabel()
