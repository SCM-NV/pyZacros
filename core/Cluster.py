from .Species import *
from .SpeciesList import SpeciesList

__all__ = ['Cluster']

class Cluster:

    def __init__(self, site_types: list,
                 species: SpeciesList,
                 entity_number: list = None,
                 neighboring: list = None,
                 multiplicity: int = 1,
                 cluster_energy: float = 0.000,
                 label: str = None):
        """
        Creates a new Cluster object

        :parm site_types: list
        :parm neighboring: list
        :parm species: list
        :parm multiplicity: int
        :parm cluster_energy: float
        """
        self.site_types = site_types                  # e.g. [ "f", "f" ]
        self.species = species                        # e.g. [ Species("H*",1), Species("H*",1) ]
        self.neighboring = neighboring                # e.g. [ (0,1) ]
        self.multiplicity = multiplicity              # e.g. 2
        self.cluster_energy = cluster_energy          # Units eV

        if( len(site_types) > len(species) ):
            msg  = "### ERROR ### Cluster.__init__.\n"
            msg += "Inconsistent dimensions for species or site_types\n"
            raise NameError(msg)

        self.sites = len(site_types)

        self.entity_number = entity_number
        if( entity_number is None ): self.entity_number = SpeciesList.default_entity_numbers( self.sites, self.species )

        #TODO Make a way to check denticity consistency
        #if( sum([s.denticity for s in self.species]) != self.sites ):
            #msg  = "### ERROR ### Cluster.__init__.\n"
            #msg += "Inconsistent dimensions for species or site_types\n"
            #raise NameError(msg)

        self.__userLabel = label
        self.__label = None
        self.__updateLabel()

        self.__mass = 0.0

        for item in species:
            self.__mass += item.mass()


    def __len__( self ) -> int:
        """
        Returns the number of species inside the cluster
        """
        return len(self.species)


    def __eq__( self, other ):
        """
        Returns True if both objects have the same label. Otherwise returns False
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


    def __updateLabel( self ):
        """
        Updates the attribute 'label'
        """
        if( self.__userLabel is not None ):
            self.__label = self.__userLabel
            return

        self.__label = ""
        for i in range(len(self.species)):
            self.__label += self.species[i].symbol
            self.__label += "_"+str(self.entity_number[i])
            self.__label += "-"
            self.__label += self.site_types[i]
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


    def label( self ) -> str:
        """
        Returns the label of the cluster
        """
        if( self.__label is None ):
            self.__updateLabel()

        return self.__label


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output  = "cluster " + self.__label +"\n"

        if( self.sites != 0 ):
            output += "  sites " + str(self.sites)+"\n"

            if self.neighboring is not None:
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

                if( site_identate[ self.entity_number[i] ] >= self.species[i].denticity ):
                    msg  = "### ERROR ### Cluster.__str__.\n"
                    msg += "Inconsistent of denticity value for "+self.species[i].symbol+"\n"
                    raise NameError(msg)

                output += "    "+str(self.entity_number[i]+1)+" "+self.species[i].symbol+" "+str(site_identate[self.entity_number[i]]+1)+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])
                if( i != len(self.site_types)-1 ):
                    output += " "
            output += "\n"

            output += "  graph_multiplicity "+str(self.multiplicity)+"\n"

        output += "  cluster_eng "+("%12.5e"%self.cluster_energy)+"\n"
        output += "end_cluster"

        return output


    def mass( self ) -> float:
        """
        Returns the mass of the cluster in Da
        """
        return self.__mass


    def gas_species(self) -> SpeciesList:
        """Returns the gas species."""
        species = []

        for sp in self.species:
            if( sp.kind == Species.GAS ):
                species.append( sp )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species


    def surface_species(self) -> SpeciesList:
        """Returns the surface species."""
        species = []

        for sp in self.species:
            if( sp.kind == Species.SURFACE ):
                species.append( sp )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species
