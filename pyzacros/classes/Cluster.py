from Specie import *

class Cluster:

    ###
    # @brief Initialize the :class:`Cluster`
    ##
    def __init__( self, label, sites, site_types, neighboring, specie=(),
                    multiplicity=0, energy=0.000 ):

        self.label = label                            # e.g. "H-H_f-f"
        self.sites = sites                            # e.g. 2
        self.site_types = site_types                  # e.g. ( "f", "f" )
        self.neighboring = neighboring                # e.g. "1-2"
        self.specie = specie                          # e.g. ( Specie("H*",1), Specie("H*",1) )
        self.multiplicity = multiplicity              # e.g. 2
        self.energy = energy                          # Units eV

        if( len(specie) != len(site_types) ):
            msg  = "### ERROR ### Cluster.__init__.\n"
            msg += "Inconsistent dimensions for specie or site_types\n"
            raise NameError(msg)

    ###
    # @brief
    ##
    def __len__( this ):
        return len(this.specie)

    ###
    # @brief Translates the cluster to a string
    ##
    def __str__( self ):
        output  = "cluster " + self.label +"\n"

        if( self.sites != 0 ):
            output += "  sites " + str(self.sites)+"\n"
            output += "  neighboring " + self.neighboring+"\n"

            output += "  lattice_state"+"\n"
            for i in range(len(self.specie)):
                output += "    "+str(i+1)+" "+self.specie[i].symbol+" "+str(self.specie[i].dentation)+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])+" "
            output += "\n"

            output += "  graph_multiplicity "+str(self.multiplicity)+"\n"

        output += "  cluster_eng "+str(self.energy)+"\n"
        output += "end_cluster"

        return output

    ###
    # @brief
    ##
    @staticmethod
    def test():
        print( "---------------------------------------------------" )
        print( ">>> Testing Cluster class" )
        print( "---------------------------------------------------" )
        myCluster = Cluster( "H*(f)-H*(f)",
                            sites=2,
                            site_types=( "f", "f" ),
                            neighboring="1-2",
                            specie=( Specie("H*",1), Specie("H*",1) ),
                            multiplicity=2,
                            energy = 0.1 )

        print( myCluster )

