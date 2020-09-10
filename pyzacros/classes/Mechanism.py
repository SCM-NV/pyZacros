from .ElementaryReaction import *

class Mechanism(list):

    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output = "mechanism"+"\n"
        for i in range(len(self)):
            output += str(self[i])
            if( i != len(self)-1 ):
                output += "\n"
        output += "\n"
        output += "end_mechanism"

        return output
