import os
from collections import UserList

from .SpeciesList import *
from .Cluster import *

__all__ = ['ClusterExpansion']

class ClusterExpansion( UserList ):
    """
    Creates a new ClusterExpansion object which is formally a list of Clusters. It implements all python list operations.

    *   ``data`` -- List of Clusters to initially include.
    *   ``fileName`` -- Path to the zacros file name to load the cluster expansion, typically ``energetics_input.dat``
    *   ``surface_species`` -- Surface species. It is required if the option ``fileName`` was used.
    """

    def __init__(self, data=[], fileName=None, surface_species=None ):
        super(ClusterExpansion, self).__init__( data )

        if fileName is not None:
            if surface_species is not None:
                self.__fromZacrosFile( fileName, surface_species )
            else:
                raise Exception( "Error: Parameter surface_species is required to load the ClusterExpansion from a zacros input file" )

        # Duplicates are automatically removed.
        copy_data = self.data

        self.data = []
        for cl in copy_data:
            if( cl not in self.data ):
                self.data.append( cl )


    def __fromZacrosFile(self, fileName, surface_species):
        """
        Creates a Mechanism from a Zacros input file energetics_input.dat
        """
        if not os.path.isfile( fileName ):
            raise Exception( "Trying to load a file that doen't exist: "+fileName )

        with open( fileName, "r" ) as inp:
            file_content = inp.readlines()
        file_content = [line.split("#")[0] for line in file_content if line.split("#")[0].strip()] # Removes empty lines and comments

        nline = 0
        while( nline < len(file_content) ):
            tokens = file_content[nline].split()

            if( tokens[0].lower() == "cluster" ):
                parameters = {}

                if( len(tokens) < 2 ):
                    raise Exception( "Error: Format inconsistent in section cluster. Label not found!" )

                parameters["label"] = tokens[1]

                nline += 1

                while( nline < len(file_content) ):
                    tokens = file_content[nline].split()

                    if( tokens[0] == "end_cluster" ):
                        break

                    def process_neighboring( sv ):
                        output = []
                        for pair in sv:
                            a,b = pair.split("-")
                            output.append( (int(a)-1,int(b)-1) )
                        return output

                    def process_site_types( sv ):
                        output = []
                        for i in range(len(sv)):
                            if( sv[i].isdigit() ):
                              output.append( int(sv[i])-1 )
                            else:
                              output.append( sv[i] )
                        return output

                    def process_variant( sv ):
                        raise Exception( "ZacrosJob.__recreate_energetics_input. Option 'cluster%variant' is not supported yet!" )

                    cases = {
                        "sites" : lambda sv: parameters.setdefault("sites", int(sv[0])),
                        "site_types" : lambda sv: parameters.setdefault("site_types", process_site_types(sv)),
                        "graph_multiplicity" : lambda sv: parameters.setdefault("multiplicity", int(sv[0])),
                        "cluster_eng" : lambda sv: parameters.setdefault("energy", float(sv[0])),
                        "neighboring" : lambda sv: parameters.setdefault("neighboring", process_neighboring(sv)),
                        "variant" : lambda sv: parameters.setdefault("variant", process_variant(sv))
                    }
                    cases.get( tokens[0], lambda sv: None )( tokens[1:] )

                    if( tokens[0] == "lattice_state" ):
                        parameters["lattice_state"] = []

                        isites = 0
                        while( nline < len(file_content) ):
                            nline += 1
                            tokens = file_content[nline].split()

                            if( isites == parameters["sites"] ):
                                break

                            if( len(tokens) < 3 ):
                                raise Exception( "Error: Format inconsistent in section lattice_state!" )

                            if( tokens[0]+tokens[1]+tokens[2] != "&&&" ):
                                entity_number = int(tokens[0])-1
                                species_name = tokens[1]
                                dentate_number = int(tokens[2])

                                parameters["lattice_state"].append( [ entity_number, species_name, dentate_number ] )

                            isites += 1
                    else:
                        nline += 1

                parameters["species"] = []
                parameters["entity_number"] = []
                site_identate = {}
                for entity_number,species_name,dentate_number in parameters["lattice_state"]:
                    if( entity_number not in site_identate ):
                        site_identate[ entity_number ] = 0
                    else:
                        site_identate[ entity_number ] = site_identate[ entity_number ] + 1

                    #TODO Find a way to check consistency of dentate_number

                    loc_id = -1
                    for i,sp in enumerate(surface_species):
                        if( sp.symbol == species_name and site_identate[ entity_number ]+1 == dentate_number ):
                            loc_id = i
                            break

                    if( loc_id == -1 ):
                        raise Exception( "Error: Species "+species_name+" was not defined in the simulation_input.txt file!" )

                    parameters["species"].append( surface_species[loc_id] )
                    parameters["entity_number"].append( entity_number )

                del parameters["sites"]
                del parameters["lattice_state"]
                self.append( Cluster( **parameters ) )

            nline += 1


    def append(self, item):
        """
        Appends a cluster to the end of the sequence. Appends a cluster to the end of the sequence. Notice that duplicate items are not accepted. In case of duplicity, the new cluster is just ignored.
        """
        self.insert( len(self), item )


    def extend(self, other):
        """
        Extend sequence by appending elements from the iterable

        *   ``other`` -- Iterable with the clusters to extend the cluster expansion.
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
