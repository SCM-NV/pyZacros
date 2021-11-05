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
        for sp in copy_self:
            if( sp not in self.data ):
                self.data.append( sp )

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
        for i,sp in enumerate(self):
            if( sp.is_adsorbed() ):
                adsorbedSpecies.append(i)

                if( sp.symbol == "*" ):
                    containsEmptySite = True
            else:
                gasSpecies.append(i)

        output = ""

        if( len(gasSpecies) > 0 ):
            output = "n_gas_species    "+str(len(gasSpecies))+"\n"

            output += "gas_specs_names   "
            for i in gasSpecies:
                output += " %12s"%self[i].symbol
            output += "\n"

            output += "gas_energies      "
            for i in gasSpecies:
                output += " %12.5e"%self[i].gas_energy
            output += "\n"

            output += "gas_molec_weights "
            for i in gasSpecies:
                output += " %12.5e"%self[i].mass()
            output += "\n"

        effAdsorbedSpecies = -1
        if( containsEmptySite ):
            effAdsorbedSpecies = len(adsorbedSpecies)-1
        else:
            effAdsorbedSpecies = len(adsorbedSpecies)


        if( effAdsorbedSpecies > 0 ):
            output += "n_surf_species    "+str(effAdsorbedSpecies)+"\n"

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

        for sp in self:
            if( sp.is_gas() ):
                output.append( sp )

        return SpeciesList( output )


    def surface_species(self) -> list:
        """Returns the adsorbed species."""
        output = []

        for sp in self:
            if( sp.is_adsorbed() ):
                output.append( sp )

        return SpeciesList( output )


    def mass( self, entity_numbers ) -> float:
        """
        Returns the total mass as the sum of the all species based on the most common isotope in Da
        """
        mass = 0.0
        mapped_entity = {}
        for i,sp in enumerate(self.surface_species()):
            if( entity_numbers[i] not in mapped_entity ):
                mass += sp.mass()
            mapped_entity[ entity_numbers[i] ] = 1

        for i,sp in enumerate(self.gas_species()):
            mass += sp.mass()

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


    @staticmethod
    def default_entity_numbers( nsites, species ):
        """
        Calculates the entity numbers assuming that ...
        """
        entity_number = nsites*[ None ]

        id_map = {}
        for i in range(nsites):
            if( i==0 ):
                id_map[ species[i] ] = i
            else:
                if( species[i] not in id_map ):
                    id_map[ species[i] ] = max( id_map.values() ) + 1
                else:
                    if( species[0:i+1].count(species[i]) > species[i].denticity ):
                        id_map[ species[i] ] = max( id_map.values() ) + 1

            entity_number[i] = id_map[ species[i] ]

        return entity_number
