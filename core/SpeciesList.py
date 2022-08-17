import copy
from collections import UserList

from .Species import *

__all__ = ['SpeciesList']

class SpeciesList(UserList):
    """
    Creates a new SpeciesList object which is formally a list of Species. It implements all python list operations.

    *   ``data`` -- List of Species to initially include.
    """

    def __init__( self, data=[] ):
        super(SpeciesList, self).__init__( data )
        self.__label = None
        self.__updateLabel()


    def __hash__(self):
        """
        Returns a hash based on the label
        """
        return hash(self.__label)


    def __str__( self ):
        """
        Translates the object to a string
        """

        gasSpecies = []
        adsorbedSpecies = []
        for i,sp in enumerate(self):
            if( sp.is_adsorbed() ):
                if( sp.symbol != "*" and sp.symbol != "**" and sp.symbol != "***" and sp.symbol != "****" ):
                    adsorbedSpecies.append(i)
            else:
                gasSpecies.append(i)

        output = ""

        if( len(gasSpecies) > 0 ):
            output = "n_gas_species    "+str(len(gasSpecies))+"\n"

            output += "gas_specs_names   "
            for i in gasSpecies:
                output += " %20s"%self[i].symbol
            output += "\n"

            output += "gas_energies      "
            for i in gasSpecies:
                output += " %20.10e"%self[i].gas_energy
            output += "\n"

            output += "gas_molec_weights "
            for i in gasSpecies:
                output += " %20.10e"%self[i].mass()
            output += "\n"

        if( len(adsorbedSpecies) > 0 ):
            output += "n_surf_species    "+str(len(adsorbedSpecies))+"\n"

            output += "surf_specs_names  "
            for i in adsorbedSpecies:
                if( self[i].symbol != "*" and self[i].symbol != "**" and self[i].symbol != "***" and self[i].symbol != "****" ):
                    output += "%10s"%self[i].symbol
            output += "\n"

            output += "surf_specs_dent   "
            for i in adsorbedSpecies:
                if( self[i].symbol != "*" and self[i].symbol != "**" and self[i].symbol != "***" and self[i].symbol != "****" ):
                    output += "%10s"%self[i].denticity

        return output


    def gas_species(self):
        """Returns the gas species."""
        output = []

        for sp in self:
            if( sp.is_gas() ):
                output.append( sp )

        return SpeciesList( output )


    def surface_species(self):
        """Returns the adsorbed species."""
        output = []

        for sp in self:
            if( sp.is_adsorbed() ):
                output.append( sp )

        return SpeciesList( output )


    def mass( self, entity_numbers ):
        """
        Returns the total mass as the sum of its all species in Da.

        *   ``entity_numbers`` -- Avoids double counting of the species if they belong to the same entity.
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


    def label( self ):
        """
        Returns the label of the cluster
        """
        if( self.label is None ):
            self.__updateLabel()

        return self.__label


    def remove_duplicates(self):
        """
        Removes duplicate species. Two species are considered the same if they have the same symbol.
        """
        copy_self = copy.deepcopy(self.data)

        self.data = []
        for sp in copy_self:
            if( sp not in self.data ):
                self.data.append( sp )

        self.__updateLabel()


    @staticmethod
    def default_entity_numbers( nsites, species ):
        """
        Calculates the list of entity numbers assuming that species with the same symbol belong to the same entity.

        *   ``nsites`` --
        *   ``species`` --
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
