from collections import UserList

from .SpeciesList import *

__all__ = ['Mechanism']

class Mechanism( UserList ):
    """
    Creates a new Mechanism object

    *   ``data`` --
    """

    def __init__( self, data=[] ):
        super(Mechanism, self).__init__( data )

        # Duplicates are automatically removed.
        copy = self.data

        self.data = []
        for er in copy:
            if( er not in self.data ):
                self.data.append( er )


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

        super(Mechanism, self).insert(i, item)


    def __str__( self ):
        """
        Translates the object to a string
        """
        output = "mechanism"+"\n\n"
        for i in range(len(self)):
            output += str(self[i])
            if( i != len(self)-1 ):
                output += "\n\n"
        output += "\n\n"
        output += "end_mechanism"

        return output


    def surface_species( self ):
        """
        Returns the surface species list.
        """
        species = SpeciesList()

        for erxn in self:
            for s in erxn.initial:
                if( s.is_adsorbed() ):
                    species.append( s )
            for s in erxn.final:
                if( s.is_adsorbed() ):
                    species.append( s )

        species.remove_duplicates()
        return species


    def gas_species( self ):
        """
        Returns the gas species list.
        """
        species = SpeciesList()

        for erxn in self:
            for s in erxn.initial:
                if( s.is_gas() ):
                    species.append( s )
            for s in erxn.final:
                if( s.is_gas() ):
                    species.append( s )

        species.remove_duplicates()
        return species


    def species(self):
        """Returns the adsorbed species."""
        return self.surface_species()


    def site_types_set( self ):
        """
        Returns the set of the sites types
        """
        site_types = set()
        for erxn in self:
            site_types.update( erxn.site_types_set() )

        return site_types
