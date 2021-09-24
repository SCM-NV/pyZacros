import chemparse

__all__ = ['Species']

class Species:
    """
    Species class that represents a chemical species
    """

    # Mass of the most common isotope in Da
    __ATOMIC_MASS = {
        "H":1.0078,
        "HE":4.0026,
        "LI":7.0160,
        "BE":9.0122,
        "B":11.0093,
        "C":12.0000,
        "N":14.0031,
        "O":15.9949,
        "F":18.9984,
        "NE":19.9924,
        "NA":22.9898,
        "MG":23.9850,
        "AL":26.9815,
        "SI":27.9769,
        "P":30.9738,
        "S":31.9721,
        "CL":34.9689,
        "AR":39.9624,
        "K":38.9637,
        "CA":39.9626,
        "SC":44.9559,
        "TI":47.9479,
        "V":50.9440,
        "CR":51.9405,
        "MN":54.9380,
        "FE":55.9349,
        "CO":58.9332,
        "NI":57.9353,
        "CU":62.9296,
        "ZN":63.9291,
        "GA":68.9256,
        "GE":73.9212,
        "AS":74.9216,
        "SE":79.9165,
        "BR":78.9183,
        "KR":83.9115,
        "RB":84.9118,
        "SR":87.9056,
        "Y":88.9058,
        "ZR":89.9047,
        "NB":92.9064,
        "RH":102.9055,
        "AG":106.9051,
        "IN":114.9039,
        "SB":120.9038,
        "I":126.9045,
        "CS":132.9055,
        "BA":137.9052,
        "LA":138.9064,
        "CE":139.9054,
        "PR":140.9077,
        "EU":152.9212,
        "TB":158.9254,
        "HO":164.9303,
        "TM":168.9342,
        "LU":174.9408,
        "HF":179.9466,
        "TA":180.9480,
        "RE":186.9558,
        "OS":191.9615,
        "IR":192.9629,
        "AU":196.9666,
        "TL":204.9744,
        "PB":207.9767,
        "BI":208.9804,
        "TH":232.0381,
        "PA":231.0359,
        "U":238.0508
    }

    FROM_SYMBOL = -1
    SURFACE = 0
    GAS = 1

    def __init__(self, symbol, denticity = FROM_SYMBOL,
                 gas_energy = None, kind = FROM_SYMBOL, mass = FROM_SYMBOL ):
        """
        Creates a new Species object.

        :parm symbol: str. Species' symbol. If symbol contains the
          character '*', it is considered an adsorbed species. Otherwise
          it si considered a gas species. e.g. H2*
        :parm denticity: int, Species' denticity e.g. 2
        :parm gas_energy: float, Species' gas energy e.g. 0.0
        """
        self.symbol = symbol
        self.gas_energy = gas_energy

        self.denticity = denticity
        if( denticity == Species.FROM_SYMBOL ):
            self.denticity = symbol.count("*")

        self.kind = kind
        if( kind == Species.FROM_SYMBOL ):
            if(len(self.symbol) > 1 and self.symbol.find("*") != -1 and self.denticity == 0):
                msg = "### ERROR ### Species.__init__.\n"
                msg += "Inconsistent symbol and denticity\n"
                raise NameError(msg)

            if(self.symbol.find("*") == -1 and self.denticity != 0):
                msg  = "### ERROR ### Species.__init__.\n"
                msg += "Denticity given for a gas species\n"
                msg += "Did you forget to add * in the species label?\n"
                raise NameError(msg)

            self.kind = Species.GAS
            if( self.symbol.find("*") != -1 ):
                self.kind = Species.SURFACE

        if( self.kind != Species.GAS and self.gas_energy is not None ):
            msg  = "### ERROR ### Species.__init__.\n"
            msg += "Parameter gas_energy cannot be associated with a surface species\n"
            raise NameError(msg)

        if( self.kind == Species.GAS and self.gas_energy is None ):
            self.gas_energy = 0.0

        self.__composition = chemparse.parse_formula( symbol.replace("*","") )

        if( mass == Species.FROM_SYMBOL ):
            if( not all( [ key.upper() in Species.__ATOMIC_MASS.keys() for key in self.__composition.keys() ] ) ):
                msg  = "### ERROR ### Species.__init__.\n"
                msg += "Wrong format for species symbol\n"
                raise NameError(msg)

            self.__mass = 0.0
            for s,n in self.__composition.items():
                self.__mass += n*Species.__ATOMIC_MASS[s.upper()]
        else:
            self.__mass = mass


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
        return ( self.kind == Species.SURFACE )


    def is_gas( self ) -> bool:
        """
        Returns True if the name of the species has no the character '*'
        """
        return ( self.kind == Species.GAS )


    def composition( self ) -> dict:
        """
        Returns a dictionary containing the number of atoms of each kind
        """
        return self.__composition


    def mass( self ) -> float:
        """
        Returns the mass of the species based on the most common isotope in Da
        """
        return self.__mass
