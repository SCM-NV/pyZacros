from .settings import *
from .SpeciesList import *
from .Mechanism import *
#from .Lattice import *

class Job:
    """
    Job class that represents a chemical species
    """

    #def __init__( self, settings: Settings, mechanism: Mechanism, lattice: Lattice ):
    def __init__( self, mechanism: Mechanism ):
        """
        Creates a new Job object

        :parm settings: Settings. Stablishes the parameters of the Zacros calculation
        :parm mechanism: Mechanism: Stablished the mechanisms involed in the calculation
        :parm lattice: Lattice.Stablished the lattice to be used during the calculation
        """
        #self.settings = settings
        self.mechanism = mechanism
        #self.lattice = lattice

        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()
        self.__updateSpeciesList()


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output = ""
        output += "--------------------------------"+"\n"
        output += "simulation_input.dat"+"\n"
        output += "--------------------------------"+"\n"
        output += str(self.__gasSpeciesList)
        output += "\n"
        output += str(self.__speciesList)
        return output


    def __updateSpeciesList( self ):

        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()

        for reaction in self.mechanism:
            print("Hola = ", reaction.initial.species)
            self.__speciesList.extend( reaction.initial.species )
            self.__speciesList.extend( reaction.final.species )
            self.__gasSpeciesList.extend( reaction.initial.gas_species )
            self.__gasSpeciesList.extend( reaction.final.gas_species )

        # Remove duplicates
        self.__speciesList = SpeciesList(dict.fromkeys(self.__speciesList))
        self.__gasSpeciesList = SpeciesList(dict.fromkeys(self.__gasSpeciesList))


    @staticmethod
    def test():
        """
        Tests the main methods of the object
        """
        print( "---------------------------------------------------" )
        print( ">>> Testing Job class" )
        print( "---------------------------------------------------" )

        s0 = Species( "*" )      # Empty adsorption site
        s1 = Species( "H*", 1 )  # H adsorbed with dentation 1
        s2 = Species( "H2*", 1 ) # H2 adsorbed with dentation 1
        s3 = Species( "H2", gas_energy=0.0 ) # H2(gas)

        myCluster1 = Cluster( site_types=( "f", "f" ),
                              neighboring=[ (1,2) ],
                              species=SpeciesList( [ s1, s1 ] ),
                              multiplicity=2,
                              cluster_energy=0.1 )

        myCluster2 = Cluster( site_types=( "f", "f" ),
                              neighboring=SpeciesList( [ (1,2) ] ),
                              species=[ s2, s0 ],
                              multiplicity=2,
                              cluster_energy=0.1 )

        myCluster3 = Cluster( site_types=( "f", "f" ),
                              neighboring=[ (1,2) ],
                              species=SpeciesList( [ s0, s0 ] ),
                              gas_species=[ s3 ],
                              multiplicity=2,
                              cluster_energy=0.1 )

        myReaction1 = ElementaryReaction( site_types=( "f", "f" ),
                                          neighboring=[ (1,2) ],
                                          initial=myCluster1,
                                          final=myCluster2,
                                          reversible=True,
                                          pre_expon=1e+13,
                                          pe_ratio=0.676,
                                          activation_energy = 0.2 )

        myReaction2 = ElementaryReaction( site_types=( "f", "f" ),
                                          neighboring=[ (1,2) ],
                                          initial=myCluster2,
                                          final=myCluster3,
                                          reversible=False,
                                          pre_expon=1e+13,
                                          pe_ratio=0.676,
                                          activation_energy = 0.2 )

        myMechanism = Mechanism()
        myMechanism.append( myReaction1 )
        myMechanism.append( myReaction2 )

        myJob = Job( myMechanism )
        print(myJob)

        #output = str(myMechanism)
        #expectedOutput = """\
#mechanism
#reversible_step H*-f,H*-f:(1,2)<-->H2*-f,*-f:(1,2)
  #sites 2
  #neighboring 1-2
  #initial
    #1 H* 1
    #2 H* 1
  #final
    #1 H2* 1
    #2 * 1
  #site_types f f
  #pre_expon 1.000000e+13
  #pe_ratio 0.676
  #activ_eng 0.2
#end_step
#reversible_step H2*-f,H2*-f:(1,2)<-->H2*-f,*-f:(1,2)
  #sites 2
  #neighboring 1-2
  #initial
    #1 H2* 1
    #2 H2* 1
  #final
    #1 H2* 1
    #2 * 1
  #site_types f f
  #pre_expon 1.000000e+13
  #pe_ratio 0.676
  #activ_eng 0.2
#end_step
#end_mechanism\
#"""
        #assert( output == expectedOutput )
