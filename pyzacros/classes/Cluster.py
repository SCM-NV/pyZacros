from .Species import *
"""Module containing the Species Class"""


class Cluster:


"""Initialize the :class:`Cluster`"""
    def __init__( self, label: str, site_types: tuple, neighboring: list, species: tuple=(),
                    multiplicity: int=0, energy: float=0.000 ):
        """
        Creates a new Cluster object

        :parm label: str
        :parm site_types: tuple
        :parm neighboring: list
        :parm species: tuple
        :parm multiplicity: int
        :parm energy: float
        """
        self.label = label                            # e.g. "H-H_f-f" #TODO This label should be automatically generated in the future
        self.site_types = site_types                  # e.g. ( "f", "f" )
        self.neighboring = neighboring                # e.g. [ (1,2) ]
        self.species = species                        # e.g. ( Species("H*",1), Species("H*",1) )
        self.multiplicity = multiplicity              # e.g. 2
        self.energy = energy                          # Units eV

        self.sites = len(site_types)

        if( len(species) != self.sites ):
            msg  = "### ERROR ### Cluster.__init__.\n"
            msg += "Inconsistent dimensions for species or site_types\n"
            raise NameError(msg)


    def __len__( this ) -> int:
        """
        Returns the number of species inside the cluster
        """
        return len(this.species)


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output  = "cluster " + self.label +"\n"

        if( self.sites != 0 ):
            output += "  sites " + str(self.sites)+"\n"

            output += "  neighboring "
            for i in range(len(self.neighboring)):
                output += str(self.neighboring[i][0])+"-"+str(self.neighboring[i][1])
                if( i != len(self.neighboring)-1 ):
                    output += " "
            output += "\n"

            output += "  lattice_state"+"\n"
            for i in range(len(self.species)):
                output += "    "+str(i+1)+" "+self.species[i].symbol+" "+str(self.species[i].denticity)+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])
                if( i != len(self.site_types)-1 ):
                    output += " "
            output += "\n"

            output += "  graph_multiplicity "+str(self.multiplicity)+"\n"

        output += "  cluster_eng "+str(self.energy)+"\n"
        output += "end_cluster"

        return output


    @staticmethod
    def test():
        """
        Tests the main methods of the object
        """
        print( "---------------------------------------------------" )
        print( ">>> Testing Cluster class" )
        print( "---------------------------------------------------" )
        myCluster = Cluster( "H*(f)-H*(f)",
                            site_types=( "f", "f" ),
                            neighboring=[ (1,2) ],
                            species=( Species("H*",1), Species("H*",1) ),
                            multiplicity=2,
                            energy = 0.1 )

        print( myCluster )

        output = str(myCluster)
        expectedOutput = """\
cluster H*(f)-H*(f)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster\
"""
        assert( output == expectedOutput )
