from .Species import *

class SpeciesList(list):

    def __str__( self ) -> str:
        """
        Translates the object to a string
        """

        gasSpecies = []
        adsorbedSpecies = []
        containsEmptySite = False

        for i,specie in enumerate(self):
            if( specie.is_adsorbed() ):
                adsorbedSpecies.append(i)

                if( specie.symbol == "*" ):
                    containsEmptySite = True
            else:
                gasSpecies.append(i)

        output = ""

        if( len(gasSpecies) > 0 ):
            output = "n_gas_species "+str(len(gasSpecies))+"\n"

            output += "gas_specs_names   "
            for i in gasSpecies:
                output += "%10s"%self[i].symbol
            output += "\n"

            output += "gas_energies      "
            for i in gasSpecies:
                output += "%10s"%self[i].gas_energy
            output += "\n"

            output += "gas_molec_weights "
            for i in gasSpecies:
                output += "%10s"%self[i].mass()
            output += "\n"
        else:
            output = "n_gas_species "+str(0)+"\n"

        effAdsorbedSpecies = -1
        if( containsEmptySite ):
            effAdsorbedSpecies = len(adsorbedSpecies)-1
        else:
            effAdsorbedSpecies = len(adsorbedSpecies)

        if( effAdsorbedSpecies > 0 ):
            output += "n_surf_species "+str(effAdsorbedSpecies)+"\n"

            output += "surf_specs_names  "
            for i in adsorbedSpecies:
                if( self[i].symbol != "*" ):
                    output += "%10s"%self[i].symbol
            output += "\n"

            output += "surf_specs_dent   "
            for i in adsorbedSpecies:
                if( self[i].symbol != "*" ):
                    output += "%10s"%self[i].denticity

        return output
