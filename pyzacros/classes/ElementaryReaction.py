from Cluster import *

class ElementaryReaction:

    ###
    # @brief Initialize the :class:`ElementaryReaction`
    ##
    def __init__( self, label, site_types, neighboring, initial, final,
                    reversible=True, pre_expon=0.0, pe_ratio=0.0, activ_eng=0.0 ):

        self.label = label             # e.g. H2_recomb
        self.site_types = site_types   # e.g. ( "f", "f" )
        self.neighboring = neighboring # e.g. [ (1,2) ]
        self.initial = initial         # e.g. ( a, b )
        self.final = final             # e.g. ( c, d )
        self.reversible = reversible   # e.g. True
        self.pre_expon = pre_expon     # e.g. 1e+13
        self.pe_ratio = pe_ratio       # e.g. 0.676
        self.activ_eng = activ_eng     # e.g. 0.200

        self.sites = len(site_types)

        if( self.sites != len(initial) or len(initial) != len(final) ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent dimensions for sites, initial or final\n"
            raise NameError(msg)

        if( type(initial) != Cluster or type(final) != Cluster ):
            msg  = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent type for initial or final\n"
            raise NameError(msg)

    ###
    # @brief Translates the cluster to a string
    ##
    def __str__( self ):
        if( self.reversible ):
            output  = "reversible_step " + self.label +"\n"
        else:
            output  = "step " + self.label +"\n"

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
                output += "    "+str(i+1)+" "+self.initial.specie[i].symbol+" 1"+"\n"

            output += "  final"+"\n"
            for i in range(len(self.final)):
                output += "    "+str(i+1)+" "+self.final.specie[i].symbol+" 1"+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])+" "
            output += "\n"

        output += "  pre_expon "+("%e"%self.pre_expon)+"\n"
        output += "  pe_ratio "+str(self.pe_ratio)+"\n"
        output += "  activ_eng "+str(self.activ_eng)+"\n"
        output += "end_step"

        return output

    ###
    # @brief
    ##
    @staticmethod
    def test():
        print( "---------------------------------------------------" )
        print( ">>> Testing ElementaryReaction class" )
        print( "---------------------------------------------------" )

        s0 = Specie( "*" )      # Empty adsorption site
        s1 = Specie( "H*", 1 )  # H adsorbed with dentation 1
        s2 = Specie( "H2*", 1 ) # H2 adsorbed with dentation 1

        myCluster1 = Cluster( "H*(f)-H*(f)",
                                site_types=( "f", "f" ),
                                neighboring=[ (1,2) ],
                                specie=( s1, s1 ),
                                multiplicity=2,
                                energy=0.1 )

        myCluster2 = Cluster( "H2*(f)-*(f)",
                                site_types=( "f", "f" ),
                                neighboring=[ (1,2) ],
                                specie=( s2, s0 ),
                                multiplicity=2,
                                energy=0.1 )

        myReaction = ElementaryReaction( "H*(f)-H*(f)<-->H2*(f)-*(f)",
                                           site_types=( "f", "f" ),
                                           neighboring=[ (1,2) ],
                                           initial=myCluster1,
                                           final=myCluster2,
                                           reversible=True,
                                           pre_expon=1e+13,
                                           pe_ratio=0.676,
                                           activ_eng = 0.2 )

        print( myReaction )
