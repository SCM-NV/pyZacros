from ElementaryReaction import *

class Mechanism(list):

    ###
    # @brief Initialize the :class:`Mechanism`
    ##
    #def __init__( self ):


    ###
    # @brief Translates the cluster to a string
    ##
    def __str__( self ):
        output = "mechanism"+"\n"
        for i in range(len(self)):
            output += str(self[i])
            if( i != len(self)-1 ):
                output += "\n"
        output += "\n"
        output += "end_mechanism"

        return output

    ###
    # @brief
    ##
    @staticmethod
    def test():
        print( "---------------------------------------------------" )
        print( ">>> Testing Mechanism class" )
        print( "---------------------------------------------------" )

        s0 = Specie( "*" )      # Empty adsorption site
        s1 = Specie( "H*", 1 )  # H adsorbed with dentation 1
        s2 = Specie( "H2*", 1 ) # H2 adsorbed with dentation 1
        s3 = Specie( "H2*", 2 ) # H2 adsorbed with dentation 1

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

        myCluster3 = Cluster( "H2*(f,f)",
                                site_types=( "f", "f" ),
                                neighboring=[ (1,2) ],
                                specie=( s3, s3 ),  # <<< @TODO This is not correct
                                multiplicity=2,
                                energy=0.1 )

        myReaction1 = ElementaryReaction( "H*(f)-H*(f)<-->H2*(f)-*(f)",
                                            site_types=( "f", "f" ),
                                            neighboring=[ (1,2) ],
                                            initial=myCluster1,
                                            final=myCluster2,
                                            reversible=True,
                                            pre_expon=1e+13,
                                            pe_ratio=0.676,
                                            activ_eng = 0.2 )

        myReaction2 = ElementaryReaction( "H2*(f,f)<-->H2*(f)-*(f)",
                                            site_types=( "f", "f" ),
                                            neighboring=[ (1,2) ],
                                            initial=myCluster3,
                                            final=myCluster2,
                                            reversible=True,
                                            pre_expon=1e+13,
                                            pe_ratio=0.676,
                                            activ_eng = 0.2 )

        myMechanism = Mechanism()
        myMechanism.append( myReaction1 )
        myMechanism.append( myReaction2 )

        print( myMechanism )

        print( "---------------------------------------------------" )

