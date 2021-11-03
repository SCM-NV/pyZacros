from collections import UserList

from .SpeciesList import *

__all__ = ['ClusterExpansion']

class ClusterExpansion(UserList):

    def __init__( self, data=[] ):
        super(ClusterExpansion, self).__init__( data )

        # Duplicates are automatically removed.
        copy_data = self.data

        self.data = []
        for cl in copy_data:
            if( cl not in self.data ):
                self.data.append( cl )


    def append(self, item):
        """
        Append item to the end of the sequence
        """
        self.insert( len(self), item )


    def extend(self, other):
        """
        Extend sequence by appending elements from the iterable
        """
        for item in other:
            self.append( item )


    def insert(self, i, item):
        """
        Insert value before index
        """
        for erxn in self:
            if( erxn.label() == item.label() ):
                return

        super(ClusterExpansion, self).insert(i, item)


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output  = "energetics\n\n"

        for cluster in self:
            output += str(cluster)+"\n\n"

        output += "end_energetics"

        return output


    def gas_species(self) -> SpeciesList:
        """Returns the gas species."""
        species = []

        for cl in self:
            species.extend( cl.gas_species() )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species


    def surface_species(self) -> SpeciesList:
        """Returns the surface species."""
        species = []

        for cl in self:
            species.extend( cl.surface_species() )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species


    def site_types_set( self ):
        """
        Returns the set of the sites types
        """
        site_types = set()
        for cl in self:
            site_types.update( cl.site_types_set() )

        return site_types
