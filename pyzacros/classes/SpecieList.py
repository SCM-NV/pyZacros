from Specie import *

class SpecieList(list):

    ###
    # @brief Initialize the :class:`SpecieList`
    ##
    #def __init__( self ):


    ###
    # @brief Translates the Specie to a string
    ##
    def __str__( self ):
        gasSpecie = []
        adsorbedSpecie = []

        for i,specie in enumerate(self):
            if( specie.is_adsorbed() ):
                adsorbedSpecie.append(i)
            else:
                gasSpecie.append(i)

        output = "n_gas_species "+str(len(gasSpecie))+"\n"

        output += "gas_specs_names   "
        for i in gasSpecie:
            output += "%10s"%self[i].symbol
        output += "\n"

        output += "gas_energies      "
        for i in gasSpecie:
            output += "%10s"%self[i].energy
        output += "\n"

        output += "gas_molec_weights "
        for i in gasSpecie:
            #output += "%10s"%self[i].mass
            output += "%10s"%"XXX" # @TODO We need a database with the molecular weights
        output += "\n"

        output += "\n"
        output += "n_surf_species "+str(len(adsorbedSpecie))+"\n"

        output += "surf_specs_names  "
        for i in adsorbedSpecie:
            output += "%10s"%self[i].symbol
        output += "\n"

        output += "surf_specs_dent   "
        for i in adsorbedSpecie:
            output += "%10s"%self[i].dentation

        return output

    ###
    # @brief
    ##
    @staticmethod
    def test():
        print( "---------------------------------------------------" )
        print( ">>> Testing SpecieList class" )
        print( "---------------------------------------------------" )

        # Adsorbed specie
        myAdsorbedSpecie1 = Specie( "H2*", dentation=1 )
        print( myAdsorbedSpecie1 )

        myAdsorbedSpecie2 = Specie( "O2*", dentation=1 )
        print( myAdsorbedSpecie2 )

        # Gas specie
        myGasSpecie1 = Specie( "H2", energy=0.0 )
        print( myGasSpecie1 )

        # Gas specie
        myGasSpecie2 = Specie( "O2", energy=0.0 )
        print( myGasSpecie2 )

        # Free adsorption site
        myFreeAdsorptionSite = Specie( "*" )
        print( myFreeAdsorptionSite )
        print( "" )

        mySpecieList = SpecieList()
        mySpecieList.append( myAdsorbedSpecie1 )
        mySpecieList.append( myAdsorbedSpecie2 )
        mySpecieList.append( myGasSpecie1 )
        mySpecieList.append( myGasSpecie2 )
        mySpecieList.append( myFreeAdsorptionSite )

        print(mySpecieList)
