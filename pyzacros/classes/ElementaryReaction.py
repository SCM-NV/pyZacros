from collections import Counter
from .Cluster import *

class ElementaryReaction:

    def __init__( self, site_types: list, neighboring: list, initial: Cluster, final: Cluster,
                    reversible: bool=True, pre_expon: float=0.0, pe_ratio: float=0.0, activation_energy: float=0.0 ):
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

        if( self.sites != len(initial) or len(initial) != len(final) ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent dimensions for sites, initial or final\n"
            raise NameError(msg)

        if( type(initial) != Cluster or type(final) != Cluster ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent type for initial or final\n"
            raise NameError(msg)

        self.__label = None
        self.__updateLabel()


    def __updateLabel( self ):
        """
        Updates the attribute 'label'
        """
        if( self.reversible ):
            self.__label = self.initial.label()+"<-->"+self.final.label()
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
            output += "  gas_species "

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

        if( self.sites != 0 ):
            output += "  sites " + str(self.sites)+"\n"

            output += "  neighboring "
            for i in range(len(self.neighboring)):
                output += str(self.neighboring[i][0])+"-"+str(self.neighboring[i][1])
                if( i != len(self.neighboring)-1 ):
                    output += " "
            output += "\n"

            output += "  initial"+"\n"
            for i in range(len(self.initial)):
                output += "    "+str(i+1)+" "+self.initial.species[i].symbol+" 1"+"\n"

            output += "  final"+"\n"
            for i in range(len(self.final)):
                output += "    "+str(i+1)+" "+self.final.species[i].symbol+" 1"+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])
                if( i != len(self.site_types)-1 ):
                    output += " "
            output += "\n"

        output += "  pre_expon "+("%e"%self.pre_expon)+"\n"
        output += "  pe_ratio "+str(self.pe_ratio)+"\n"
        output += "  activ_eng "+str(self.activation_energy)+"\n"
        output += "end_step"

        return output


    @staticmethod
    def test():
        """
        Tests the main methods of the object
        """
        print( "---------------------------------------------------" )
        print( ">>> Testing ElementaryReaction class" )
        print( "---------------------------------------------------" )

        s0 = Species( "*" )      # Empty adsorption site
        s1 = Species( "H*", 1 )  # H adsorbed with dentation 1
        s2 = Species( "H2*", 1 ) # H2 adsorbed with dentation 1

        myCluster1 = Cluster( site_types=( "f", "f" ),
                              neighboring=[ (1,2) ],
                              species=( s1, s1 ),
                              multiplicity=2,
                              cluster_energy=0.1 )

        myCluster2 = Cluster( site_types=( "f", "f" ),
                              neighboring=[ (1,2) ],
                              species=( s2, s0 ),
                              multiplicity=2,
                              cluster_energy=0.1 )

        myReaction1 = ElementaryReaction( site_types=( "f", "f" ),
                                         neighboring=[ (1,2) ],
                                         initial=myCluster1,
                                         final=myCluster2,
                                         reversible=True,
                                         pre_expon=1e+13,
                                         pe_ratio=0.676,
                                         activation_energy=0.2 )

        print( myReaction1 )

        output = str(myReaction1)
        expectedOutput = """\
reversible_step H*-f,H*-f:(1,2)<-->H2*-f,*-f:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_step\
"""
        assert( output == expectedOutput )

        s3 = Species( "H2", gas_energy=0.0 ) # H2(gas)

        myCluster3 = Cluster( site_types=( "f", "f" ),
                              neighboring=[ (1,2) ],
                              species=[ s0, s0 ],
                              gas_species=[ s3 ],
                              multiplicity=2,
                              cluster_energy=0.1 )

        myReaction2 = ElementaryReaction( site_types=( "f", "f" ),
                                          neighboring=[ (1,2) ],
                                          initial=myCluster1,
                                          final=myCluster3,
                                          reversible=False,
                                          pre_expon=1e+13,
                                          pe_ratio=0.676,
                                          activation_energy = 0.2 )

        print( myReaction2 )

        output = str(myReaction2)
        expectedOutput = """\
step H*-f,H*-f:(1,2)-->*-f,*-f:H2:(1,2)
  gas_species H2 1
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 * 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_step\
"""
        assert( output == expectedOutput )
