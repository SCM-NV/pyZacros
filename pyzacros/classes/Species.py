class Species:
    """
    Species class that represents a chemical species
    """

    def __init__( self, symbol: str, denticity: int=0, gas_energy: float=0.0 ):
        """
        Creates a new Species object

        :parm symbol: str. Species' symbol. If symbol contains the
          character '*', it is considered an adsorbed species. Otherwise
          it si considered a gas species. e.g. H2*
        :parm denticity: int, Species' denticity e.g. 2
        :parm gas_energy: float, Species' gas energy e.g. 0.0
        """
        self.symbol = symbol
        self.denticity = denticity
        self.gas_energy = gas_energy

        if( len(symbol) > 1 and symbol.find("*") != -1 and denticity == 0 ):
            msg  = "### ERROR ### Species.__init__.\n"
            msg += "Inconsistent symbol and denticity\n"
            raise NameError(msg)

        if( symbol.find("*") == -1 and denticity != 0 ):
            msg  = "### ERROR ### Species.__init__.\n"
            msg += "Denticity given for a gas species\n"
            msg += "Did you forget to add * in the species label?\n"
            raise NameError(msg)

        # If specie is gas the energy is undefined
        if( denticity > 0 ):
            self.gas_energy = None


    def __eq__( self, other ):
        """
        Returns True if both objects have the same symbol. Otherwise returns False
        """
        if( self.symbol == other.symbol ):
            return True
        else:
            return False


    def __hash__(self):
        """
        Returns a hash based on the symbol
        """
        return hash(self.symbol)


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output  = self.symbol
        return output


    def is_adsorbed( self ) -> bool:
        """
        Returns True if the name of the species has the character '*'
        """
        return ( self.symbol.find("*") != -1 )


    def is_gas( self ) -> bool:
        """
        Returns True if the name of the species has no the character '*'
        """
        return ( not self.is_adsorbed() )
