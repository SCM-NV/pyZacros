from collections import Counter
from .SpeciesList import SpeciesList

__all__ = ['ElementaryReaction']

class ElementaryReaction:

    def __init__(self,
                 site_types: list,
                 initial: SpeciesList,
                 final: SpeciesList,
                 neighboring: list = None,
                 reversible: bool = True,
                 pre_expon: float = 0.0,
                 pe_ratio: float = 0.0,
                 activation_energy: float = 0.0,
                 label: str = None):
        """
        Creates a new ElementaryReaction object

        :parm site_types: list
        :parm neighboring: list
        :parm initial: SpeciesList. Gas species have to be at the end of the list
        :parm final: SpeciesList. Gas species have to be at the end of the list
        :parm reversible: bool
        :parm pre_expon: float
        :parm pe_ratio: float
        :parm activation_energy: float
        """

        if( ( type(initial) != SpeciesList and type(initial) != list )
            or ( type(final) != SpeciesList and type(final) != list ) ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent type for initial or final\n"
            raise NameError(msg)

        self.site_types = site_types   # e.g. [ "f", "f" ]
        self.neighboring = neighboring # e.g. [ (1,2) ]
        self.initial = initial
        if( type(initial) == list ): self.initial = SpeciesList(initial)
        self.final = final
        if( type(final) == list ): self.final = SpeciesList(final)
        self.reversible = reversible
        self.pre_expon = pre_expon
        self.pe_ratio = pe_ratio
        self.activation_energy = activation_energy     # e.g. 0.200

        self.sites = len(site_types)

        if( self.sites != sum([s.denticity for s in self.initial])
           or self.sites != sum([s.denticity for s in self.final]) ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent dimensions for sites, initial or final\n"
            raise NameError(msg)

        if( abs( self.initial.mass() - self.final.mass() ) > 1e-6 ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              The mass is not conserved during the reaction\n"
            msg += "              mass(initial)="+str(self.initial.mass())+",mass(final)="+str(self.final.mass())
            raise NameError(msg)

        self.__userLabel = label
        self.__label = None
        self.__updateLabel()


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


    @staticmethod
    def __getSpeciesListFullName( species, site_types ):
        label = ""

        for i in range(len(species)):
            label += species[i].symbol+"-"
            for j in range(species[i].denticity):
                label += site_types[i]
                if(j != species[i].denticity-1):
                    label += "-"
            if(i != len(species)-1):
                label += ","

        return label


    def __updateLabel( self ):
        """
        Updates the attribute 'label'
        """
        if( self.__userLabel is not None ):
            self.__label = self.__userLabel
            return

        initialLabel = ElementaryReaction.__getSpeciesListFullName( self.initial.adsorbed_species(), self.site_types )

        if( len(self.initial.gas_species()) > 0 ):
            initialLabel += ":" + SpeciesList(self.initial.gas_species()).label()

        finalLabel = ElementaryReaction.__getSpeciesListFullName( self.final.adsorbed_species(), self.site_types )

        if( len(self.final.gas_species()) > 0 ):
            finalLabel += ":" + SpeciesList(self.final.gas_species()).label()

        self.__label = ""

        if( self.reversible ):
            # Reaction labels in lexicographical order
            if( initialLabel > finalLabel ):
                self.__label = initialLabel+"<-->"+finalLabel
            else:
                self.__label = finalLabel+"<-->"+initialLabel
        else:
            self.__label = initialLabel+"-->"+finalLabel

        # For neighboring nodes are sorted
        if self.neighboring is not None:
            self.__label += ";"
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
        if( self.label is None ):
            self.__updateLabel()

        return self.__label


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        if( self.reversible ):
            output  = "reversible_step " + self.__label +"\n"
        else:
            output  = "step " + self.__label +"\n"

        initial_gas_species = SpeciesList( self.initial.gas_species() )
        final_gas_species = SpeciesList( self.final.gas_species() )

        if( len(initial_gas_species) != 0 or len(final_gas_species) != 0 ):
            output += "  gas_reacs_prods "

            gas_species_freqs = Counter( [ s.symbol for s in initial_gas_species ] )

            i=0
            for symbol,freq in gas_species_freqs.items():
                output += symbol+" "+str(-freq)
                if( i != len(gas_species_freqs)-1 ):
                    output += " "
                i += 1

            gas_species_freqs = Counter( [ s.symbol for s in final_gas_species ] )

            i=0
            for symbol,freq in gas_species_freqs.items():
                output += symbol+" "+str(freq)
                if( i != len(gas_species_freqs)-1 ):
                    output += " "
                i += 1

            output += "\n"

        if(self.sites != 0):
            output += "  sites " + str(self.sites)+"\n"
            if self.neighboring is not None:
                output += "  neighboring "
                for i in range(len(self.neighboring)):
                    output += str(self.neighboring[i][0]) + \
                             "-"+str(self.neighboring[i][1])
                    if(i != len(self.neighboring)-1):
                        output += " "
                output += "\n"

            output += "  initial"+"\n"
            for i in range(len(self.initial)):
                for j in range(self.initial[i].denticity):
                    output += "    "+str(i+1)+" "+self.initial[i].symbol+" "+str(j+1)+"\n"

            output += "  final"+"\n"
            for i in range(len(self.final)):
                for j in range(self.final[i].denticity):
                    output += "    "+str(i+1)+" "+self.final[i].symbol+" "+str(j+1)+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])
                if(i != len(self.site_types)-1):
                    output += " "
            output += "\n"

        output += "  pre_expon "+("%.3e"%self.pre_expon)+"\n"
        if self.reversible is True:
            output += "  pe_ratio "+("%.3f"%self.pe_ratio)+"\n"
        output += "  activ_eng "+("%.3f"%self.activation_energy)+"\n"
        if self.reversible is True:
            output += "end_reversible_step"
        else:
            output += "end_step"

        return output

