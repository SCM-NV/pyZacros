from collections import UserList
from pyzacros.classes.SpeciesList import SpeciesList
from .ElementaryReaction import *

class Mechanism(UserList):

    def __init__( self, data=[] ):
        super(Mechanism, self).__init__( data )

        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()
        self.__updateSpeciesList()

        self.__clustersList = []
        self.__updateClustersList()


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output = "mechanism"+"\n\n"
        for i in range(len(self)):
            output += str(self[i])
            if( i != len(self)-1 ):
                output += "\n\n"
        output += "\n"
        output += "end_mechanism"

        return output


    def __updateSpeciesList(self):
        """
        Update self.__speciesList and self.__gasSpeciesList.

        Duplicates are automatically removed.
        """
        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()

        for reaction in self:
            self.__speciesList.extend( reaction.initial.species )
            self.__speciesList.extend( reaction.final.species )
            self.__gasSpeciesList.extend( reaction.initial.gas_species )
            self.__gasSpeciesList.extend( reaction.final.gas_species )

        # Remove duplicates
        self.__speciesList = SpeciesList(dict.fromkeys(self.__speciesList))
        self.__gasSpeciesList = SpeciesList(dict.fromkeys(self.__gasSpeciesList))


    def __updateClustersList( self ):
        """
        Updates self.__clustersList.
        Duplicates are automatically removed.
        """

        self.__clustersList = []

        for reaction in self:
            self.__clustersList.append( reaction.initial )
            self.__clustersList.append( reaction.final )

        # Remove duplicates
        self.__clustersList = list(dict.fromkeys(self.__clustersList))
        self.__clustersList = list(dict.fromkeys(self.__clustersList))


    def species( self ):
        """
        Returns the species list. Updates self.__speciesList if needed.
        """
        if( len(self.__speciesList) == 0 ):
            self.__updateSpeciesList()

        return self.__speciesList


    def gasSpecies( self ):
        """
        Returns the gas species list. Updates self.__gasSpeciesList if needed.
        """
        if( len(self.__gasSpeciesList) == 0 ):
            self.__updateSpeciesList()

        return self.__gasSpeciesList


    def clusters( self ):
        """
        Returns the clusters list. Updates self.__clustersList if needed.
        """
        if( len(self.__clustersList) == 0 ):
            self.__updateClustersList()

        return self.__clustersList
