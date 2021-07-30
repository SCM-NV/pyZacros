import copy
from collections import UserList

from .Species import *

__all__ = ['SpeciesList']

class SpeciesList(UserList):

    def __init__( self, data=[] ):
        super(SpeciesList, self).__init__( data )
        self.__label = None
        self.__updateLabel()


    def remove_duplicates(self):
        """
        Remove duplicates
        """
        copy_self = copy.deepcopy(self.data)

        self.data = []
        for s in copy_self:
            if( s not in self.data ):
                self.data.append( s )

        self.__updateLabel()


    def __hash__(self):
        """
        Returns a hash based on the label
        """
        return hash(self.__label)


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """

        gasSpecies = []
        adsorbedSpecies = []
        containsEmptySite = False
        for i,s in enumerate(self):
            if( s.is_adsorbed() ):
                adsorbedSpecies.append(i)

                if( s.symbol == "*" ):
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


    def gas_species(self) -> list:
        """Returns the gas species."""
        output = []

        for s in self:
            if( s.is_gas() ):
                output.append( s )

        return SpeciesList( output )


    def adsorbed_species(self) -> list:
        """Returns the adsorbed species."""
        output = []

        for s in self:
            if( s.is_adsorbed() ):
                output.append( s )

        return SpeciesList( output )


    def species(self) -> list:
        """Returns the adsorbed species."""
        return self.adsorbed_species()


    def mass( self ) -> float:
        """
        Returns the total mass as the sum of the all species based on the most common isotope in Da
        """
        mass = 0.0
        for s in self:
            mass += s.mass()

        return mass


    def __updateLabel( self ):
        """
        Updates the attribute 'label'
        """
        self.__label = ""
        for i in range(len(self)):
            self.__label += self[i].symbol
            if(i != len(self)-1):
                self.__label += ","


    def label( self ) -> str:
        """
        Returns the label of the cluster
        """
        if( self.label is None ):
            self.__updateLabel()

        return self.__label
