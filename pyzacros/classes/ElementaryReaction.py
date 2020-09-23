from collections import Counter
from .Cluster import Cluster


class ElementaryReaction:

    def __init__(self,
                 site_types: list,
                 initial: Cluster,
                 final: Cluster,
                 neighboring: list = None,
                 reversible: bool = True,
                 pre_expon: float = 0.0,
                 pe_ratio: float = 0.0,
                 activation_energy: float = 0.0):
        """
        Creates a new ElementaryReaction object

        :parm site_types: list
        :parm neighboring: list
        :parm initial: Cluster
        :parm final: Cluster
        :parm reversible: bool
        :parm pre_expon: float
        :parm pe_ratio: float
        :parm activation_energy: float
        """
        self.site_types = site_types   # e.g. [ "f", "f" ]
        self.neighboring = neighboring # e.g. [ (1,2) ]
        self.initial = initial
        self.final = final
        self.reversible = reversible
        self.pre_expon = pre_expon
        self.pe_ratio = pe_ratio
        self.activation_energy = activation_energy     # e.g. 0.200

        self.sites = len(site_types)

        if( self.sites != sum([s.denticity for s in initial.species])
           or self.sites != sum([s.denticity for s in final.species]) ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent dimensions for sites, initial or final\n"
            raise NameError(msg)

        if( type(initial) != Cluster or type(final) != Cluster ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent type for initial or final\n"
            raise NameError(msg)

        if( abs( initial.mass() - final.mass() ) > 1e-6 ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              The mass is not conserved during the reaction\n"
            msg += "              mass(initial)="+str(initial.mass())+",mass(final)="+str(final.mass())
            raise NameError(msg)

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


    def __updateLabel( self ):
        """
        Updates the attribute 'label'
        """
        if( self.reversible ):
            # Reaction labels in lexicographical order
            if( self.initial.label() > self.final.label() ):
                self.__label = self.initial.label()+"<-->"+self.final.label()
            else:
                self.__label = self.final.label()+"<-->"+self.initial.label()
        else:
            self.__label = self.initial.label()+"-->"+self.final.label()


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

        if( len(self.initial.gas_species) != 0 or len(self.final.gas_species) != 0 ):
            output += "  gas_reacs_prods "

            gas_species_freqs = Counter( [ s.symbol for s in self.initial.gas_species ] )

            i=0
            for symbol,freq in gas_species_freqs.items():
                output += symbol+" "+str(-freq)
                if( i != len(gas_species_freqs)-1 ):
                    output += " "
                i += 1

            gas_species_freqs = Counter( [ s.symbol for s in self.final.gas_species ] )

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
                for j in range(self.initial.species[i].denticity):
                    output += "    "+str(i+1)+" "+self.initial.species[i].symbol+" "+str(j+1)+"\n"

            output += "  final"+"\n"
            for i in range(len(self.final)):
                for j in range(self.final.species[i].denticity):
                    output += "    "+str(i+1)+" "+self.final.species[i].symbol+" "+str(j+1)+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])
                if(i != len(self.site_types)-1):
                    output += " "
            output += "\n"

        output += "  pre_expon "+("%e"%self.pre_expon)+"\n"
        if self.reversible is True:
            output += "  pe_ratio "+str(self.pe_ratio)+"\n"
        output += "  activ_eng "+str(self.activation_energy)+"\n"
        if self.reversible is True:
            output += "end_reversible_step"
        else:
            output += "end_step"
        return output

