import os
from collections import UserList

from .SpeciesList import *
from .ElementaryReaction import *

__all__ = ['Mechanism']

class Mechanism( UserList ):
    """
    Creates a new Mechanism object. If no argument is given, the constructor creates a new empty mechanism.

    *   ``data`` -- List of elementary reactions to initialize the mechanism.
    *   ``fileName`` -- Path to the zacros file name to load the mechanism, typically ``mechanism_input.dat``
    *   ``gas_species`` -- Gas species. It is required if the option ``fileName`` was used.
    *   ``surface_species`` -- Surface species. It is required if the option ``fileName`` was used.
    """

    def __init__( self, data=[], fileName=None, gas_species=None, surface_species=None ):
        super(Mechanism, self).__init__( data )

        if fileName is not None:
            if gas_species is not None and surface_species is not None:
                self.__fromZacrosFile( fileName, gas_species, surface_species )
            else:
                raise Exception( "Error: Parameters gas_species and surface_species are requiered to load the Mechanism from a zacros input file" )

        # Duplicates are automatically removed.
        copy = self.data

        self.data = []
        for er in copy:
            if( er not in self.data ):
                self.data.append( er )


    def __fromZacrosFile(self, fileName, gas_species, surface_species):
        """
        Creates a Mechanism from a Zacros input file mechanism_input.dat
        """
        if not os.path.isfile( fileName ):
            raise Exception( "Trying to load a file that doen't exist: "+fileName )

        with open( fileName, "r" ) as inp:
            file_content = inp.readlines()
        file_content = [line.split("#")[0] for line in file_content if line.split("#")[0].strip()] # Removes empty lines and comments

        nline = 0
        while( nline < len(file_content) ):
            tokens = file_content[nline].split()

            if( tokens[0].lower() == "reversible_step" or tokens[0].lower() == "step" ):
                parameters = {}

                if( len(tokens) < 2 ):
                    raise Exception( "Error: Format inconsistent in section reversible_step/step. Label not found!" )

                parameters["label"] = tokens[1]

                if( tokens[0].lower() == "reversible_step" ):
                    parameters["reversible"] = True
                elif( tokens[0].lower() == "step" ):
                    parameters["reversible"] = False

                nline += 1

                while( nline < len(file_content) ):
                    tokens = file_content[nline].split()

                    if( tokens[0] == "end_reversible_step" or tokens[0] == "end_step" ):
                        break

                    def process_gas_reacs_prods( sv ):
                        output = []
                        for i in range(len(sv)-1):
                            output.append( (sv[i],int(sv[i+1])) )
                        return output

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

                    cases = {
                        "gas_reacs_prods" : lambda sv: parameters.setdefault("gas_reacs_prods", process_gas_reacs_prods(sv) ),
                        "sites" : lambda sv: parameters.setdefault("sites", int(sv[0])),
                        "neighboring" : lambda sv: parameters.setdefault("neighboring", process_neighboring(sv)),
                        "site_types" : lambda sv: parameters.setdefault("site_types", process_site_types(sv)),
                        "pre_expon" : lambda sv: parameters.setdefault("pre_expon", float(sv[0])),
                        "pe_ratio" : lambda sv: parameters.setdefault("pe_ratio", float(sv[0])),
                        "activ_eng" : lambda sv: parameters.setdefault("activation_energy", float(sv[0])),
                        "prox_factor" : lambda sv: parameters.setdefault("prox_factor", float(sv[0])),
                    }
                    cases.get( tokens[0], lambda sv: None )( tokens[1:] )

                    if( tokens[0] == "initial" ):
                        parameters["initial"] = []

                        site_identate = {}

                        isites = 0
                        while( nline < len(file_content) ):
                            nline += 1
                            tokens = file_content[nline].split()

                            if( isites == parameters["sites"] ):
                                break

                            if( len(tokens) < 3 ):
                                raise Exception( "Error: Format inconsistent in section reversible_step/step!" )

                            if( tokens[0]+tokens[1]+tokens[2] != "&&&" ):
                                entity_number = int(tokens[0])
                                species_name = tokens[1]
                                dentate_number = int(tokens[2])

                                loc_id = None
                                for i,sp in enumerate(surface_species):
                                    if( entity_number not in site_identate ):
                                        site_identate[ entity_number ] = 0

                                    #TODO Find a way to check consistency of dentate_number

                                    if( sp.symbol == species_name and site_identate[ entity_number ]+1 == dentate_number ):
                                        site_identate[ entity_number ] = site_identate[ entity_number ] + 1
                                        loc_id = i
                                        break

                                if( loc_id is None ):
                                    raise Exception( "Error: Species "+species_name+" not found! See mechanism initial: "+parameters["label"] )

                                parameters["initial"].append( surface_species[loc_id] )

                            isites += 1

                        if( "gas_reacs_prods" in parameters ):
                            for spn,k in parameters["gas_reacs_prods"]:
                                if( k == -1 ):

                                    loc_id = None
                                    for i,sp in enumerate(gas_species):
                                        if( spn == sp.symbol ):
                                            loc_id = i
                                            break

                                    if( loc_id is None ):
                                        raise Exception( "Error: Gas species "+species_name+" not found!" )

                                    parameters["initial"].append( gas_species[loc_id] )

                    if( tokens[0] == "final" ):
                        parameters["final"] = []

                        site_identate = {}

                        isites = 0
                        while( nline < len(file_content) ):
                            nline += 1
                            tokens = file_content[nline].split()

                            if( isites == parameters["sites"] ):
                                break

                            if( len(tokens) < 3 ):
                                raise Exception( "Error: Format inconsistent in section lattice_state!" )

                            if( tokens[0]+tokens[1]+tokens[2] != "&&&" ):
                                entity_number = int(tokens[0])
                                species_name = tokens[1]
                                dentate_number = int(tokens[2])

                                loc_id = None
                                for i,sp in enumerate(surface_species):
                                    if( entity_number not in site_identate ):
                                        site_identate[ entity_number ] = 0

                                    #TODO Find a way to check consistency of dentate_number

                                    if( sp.symbol == species_name and site_identate[ entity_number ]+1 == dentate_number ):
                                        site_identate[ entity_number ] = site_identate[ entity_number ] + 1
                                        loc_id = i
                                        break

                                if( loc_id is None ):
                                    raise Exception( "Error: Species "+species_name+" not found! See mechanism final: "+parameters["label"] )

                                parameters["final"].append( surface_species[loc_id] )

                            isites += 1

                        if( "gas_reacs_prods" in parameters ):
                            for spn,k in parameters["gas_reacs_prods"]:
                                if( k == 1 ):

                                    loc_id = None
                                    for i,sp in enumerate(gas_species):
                                        if( spn == sp.symbol ):
                                            loc_id = i
                                            break

                                    if( loc_id is None ):
                                        raise Exception( "Error: Gas species "+species_name+" not found!" )

                                    parameters["final"].append( gas_species[loc_id] )
                    else:
                        nline += 1

                del parameters["sites"]
                if( "gas_reacs_prods" in parameters ): del parameters["gas_reacs_prods"]

                rxn = ElementaryReaction( **parameters )

                self.append( rxn )

            nline += 1


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


    def replace_site_types( self, site_types_old, site_types_new ):
        """
        Replaces the site types names

        *   ``site_types_old`` -- List of strings containing the old site_types to be replaced
        *   ``site_types_new`` -- List of strings containing the new site_types which would replace old site_types_old.
        """
        assert( len(site_types_old) == len(site_types_new) )

        for erxn in self:
            erxn.replace_site_types( site_types_old, site_types_new )


    def find( self, label ):
        """
        Returns the list of reactions where the substring ``label`` is found in the reactions' label
        """
        return [rxn for rxn in self if rxn.label().find(label) != -1]


    def find_one( self, label ):
        """
        Returns the first reaction where the substring ``label`` is found in the reaction's label
        """
        return next(rxn for rxn in self if rxn.label().find(label) != -1)

