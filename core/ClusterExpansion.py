from collections import UserList

from .SpeciesList import *

__all__ = ['ClusterExpansion']

class ClusterExpansion( UserList ):
    """
    Creates a new ClusterExpansion object which is formally a list of Clusters. It implements all python list operations.

    *   ``data`` -- List of Clusters to initially include.
    """

    def __init__(self, data=[]):
        super(ClusterExpansion, self).__init__( data )

        # Duplicates are automatically removed.
        copy_data = self.data

        self.data = []
        for cl in copy_data:
            if( cl not in self.data ):
                self.data.append( cl )


    def append(self, item):
        """
        Appends a cluster to the end of the sequence. Appends a cluster to the end of the sequence. Notice that duplicate items are not accepted. In case of duplicity, the new cluster is just ignored.
        """
        self.insert( len(self), item )


    def extend(self, other):
        """
        Extend sequence by appending elements from the iterable

        *   ``other`` --
        """
        for item in other:
            self.append( item )


    def insert(self, i, item):
        """
        Inserts item to the list at the i-th index.

        *   ``i`` -- The index where ``item`` needs to be inserted.
        *   ``item`` --  The cluster to be inserted in the list.
        """
        for cl in self:
            if( cl.label() == item.label() ):
                return

        super(ClusterExpansion, self).insert(i, item)


    def __str__(self):
        """
        Translates the object to a string in Zacros input files format.
        """
        output  = "energetics\n\n"

        for cl in self:
            output += str(cl)+"\n\n"

        output += "end_energetics"

        return output


    def gas_species(self):
        """Returns the gas species."""
        species = []

        for cl in self:
            species.extend( cl.gas_species() )

        species = SpeciesList( species )
        species.remove_duplicates()
        return species


    def surface_species(self):
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


    def replace_site_types( self, site_types_old, site_types_new ):
        """
        Replaces the site types names

        *   ``site_types_old`` -- List of strings containing the old site_types to be replaced
        *   ``site_types_new`` -- List of strings containing the new site_types which would replace old site_types_old.
        """
        assert( len(site_types_old) == len(site_types_new) )

        for cl in self:
            cl.replace_site_types( site_types_old, site_types_new )


    def find( self, label ):
        """
        Returns the list of clusters where the substring ``label`` is found in the clusters' label
        """
        return [cl for cl in self if cl.label().find(label) != -1]


    def find_one( self, label ):
        """
        Returns the first cluster where the substring ``label`` is found in the cluster's label
        """
        return next(cl for cl in self if cl.label().find(label) != -1)
