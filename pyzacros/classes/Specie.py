class Specie:

    ###
    # @brief Initialize the :class:`Specie`
    ##
    def __init__( self, symbol, dentation=0, energy=0.0 ):

        self.symbol = symbol         # e.g. H2*
        self.dentation = dentation   # e.g. 2
        self.energy = energy         # e.g. 0.0

        if( len(symbol) > 1 and symbol.find("*") != -1 and dentation == 0 ):
            msg  = "### ERROR ### Specie.__init__.\n"
            msg += "Inconsistent symbol and dentation\n"
            raise NameError(msg)

        if( dentation == 0 ):
            self.energy = None

    ###
    # @brief Translates the cluster to a string
    ##
    def __str__( self ):
        output  = self.symbol
        return output

    ###
    # @brief
    ##
    def is_adsorbed( self ):
        return ( self.symbol.find("*") != -1 )

    ###
    # @brief
    ##
    def is_gas( self ):
        return ( not self.is_adsorbed() )

    ###
    # @brief
    ##
    @staticmethod
    def test():
        print( "---------------------------------------------------" )
        print( ">>> Testing Specie class" )
        print( "---------------------------------------------------" )

        # Adsorbed specie
        myAdsorbedSpecie = Specie( "H2*", dentation=1 )
        print( myAdsorbedSpecie )

        # Gas specie
        myGasSpecie = Specie( "H2", energy=0.0 )
        print( myGasSpecie )

        # Free adsorption site
        myAdsorptionFreeSite = Specie( "*" )
        print( myAdsorptionFreeSite )
