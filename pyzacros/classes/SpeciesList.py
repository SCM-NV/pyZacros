from .Species import *

class SpeciesList(list):

    def __str__( self ) -> str:
        """
        Translates the object to a string
        """

        gasSpecies = []
        adsorbedSpecies = []

        for i,specie in enumerate(self):
            if( specie.is_adsorbed() ):
                adsorbedSpecies.append(i)
            else:
                gasSpecies.append(i)

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
            #output += "%10s"%self[i].mass
            output += "%10s"%"XXX" # @TODO We need a database with the molecular weights
        output += "\n"

        output += "\n"
        output += "n_surf_species "+str(len(adsorbedSpecies))+"\n"  #TODO Remove the * species

        output += "surf_specs_names  "
        for i in adsorbedSpecies:
            output += "%10s"%self[i].symbol
        output += "\n"

        output += "surf_specs_dent   "
        for i in adsorbedSpecies:
            output += "%10s"%self[i].denticity

        return output
