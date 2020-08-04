import os
from string import Template

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

        self.__simulationInputTemplate = Template( '''\
random_seed 10
temperature 380.0
pressure 2.00

$GAS_SPECIES
$SPECIES

snapshots on time 1e-5
process_statistics on time 1e-5
species_numbers on time 1e-5
event_report off
max_steps infinity
max_time 1.0e+2
wall_time 5000

finish\
''' )

        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()
        self.__updateSpeciesList()

        self.__clustersList = []
        self.__updateClustersList()


    def __str__( self ) -> str:
        """
        Translates the object to a string
        """
        output = ""

        output += "---------------------------"+"\n"
        output += "simulation_input.dat"+"\n"
        output += "---------------------------"+"\n"
        output += self.simulationInput()

        output += "\n"
        output += "---------------------------"+"\n"
        output += "lattice_input.dat"+"\n"
        output += "---------------------------"+"\n"
        #output += self.latticeInput()

        output += "\n"
        output += "---------------------------"+"\n"
        output += "energetics_input.dat"+"\n"
        output += "---------------------------"+"\n"
        output += self.energeticsInput()

        output += "\n"
        output += "---------------------------"+"\n"
        output += "mechanism_input.dat"+"\n"
        output += "---------------------------"+"\n"
        output += self.mechanismInput()

        return output


    def simulationInput( self ) -> str:
        """
        Returns a string with the content of the simulation_input.dat file
        """
        template = self.__simulationInputTemplate.safe_substitute(
                        GAS_SPECIES=str(self.__gasSpeciesList),
                        SPECIES=str(self.__speciesList))

        return template


    def latticeInput( self ) -> str:
        """
        Returns a string with the content of the lattice_input.dat file
        """
        msg  = "### ERROR ### Job.latticeInput().\n"
        msg += "              This function is not implemented yet!\n"
        raise NameError(msg)

        return ""


    def energeticsInput( self ) -> str:
        """
        Returns a string with the content of the energetics_input.dat file
        """
        output = "energetics"+"\n"
        for cluster in self.__clustersList:
            output += str(cluster)+"\n"
        output += "end energetics"

        return output


    def mechanismInput( self ) -> str:
        """
        Returns a string with the content of the mechanism_input.dat file
        """
        output = str(self.mechanism)

        return output


    def writeInputFiles( self, directory=".", parents=False ):
        """
        Write the Zacros inputs files to disk

        :parm directories: str. Directory where the Zacros input files are going to be saved
        :parm parents: bool. If True it will make parent directories as needed. Otherwise, an error will be raised.
        """
        if ( not os.path.exists( directory ) ):
            if( parents ):
                os.makedirs( directory )
            else:
                msg  = "### ERROR ### Job.writeInputFiles().\n"
                msg += "              The target directory '"+directory+"' doesn't exist!\n"
                raise NameError(msg)

        with open( directory+"/simulation_input.dat", "w") as f:
            f.write( self.simulationInput() )

        #with open( directory+"/"lattice_input.dat", "w") as f:
            #f.write( self.latticeInput() )

        with open( directory+"/energetics_input.dat", "w") as f:
            f.write( self.energeticsInput() )

        with open( directory+"/mechanism_input.dat", "w") as f:
            f.write( self.mechanismInput() )


    def __updateSpeciesList( self ):
        """
        Updates self.__speciesList and self.__gasSpeciesList from self.mechanism.
        Duplicates are automatically removed.
        """
        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()

        for reaction in self.mechanism:
            self.__speciesList.extend( reaction.initial.species )
            self.__speciesList.extend( reaction.final.species )
            self.__gasSpeciesList.extend( reaction.initial.gas_species )
            self.__gasSpeciesList.extend( reaction.final.gas_species )

        # Remove duplicates
        self.__speciesList = SpeciesList(dict.fromkeys(self.__speciesList))
        self.__gasSpeciesList = SpeciesList(dict.fromkeys(self.__gasSpeciesList))


    def __updateClustersList( self ):
        """
        Updates self.__clustersList from self.mechanism.
        Duplicates are automatically removed.
        """

        self.__clustersList = []

        for reaction in self.mechanism:
            self.__clustersList.append( reaction.initial )
            self.__clustersList.append( reaction.final )

        # Remove duplicates
        self.__clustersList = SpeciesList(dict.fromkeys(self.__clustersList))
        self.__clustersList = SpeciesList(dict.fromkeys(self.__clustersList))


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

        myJob.writeInputFiles()

        output = str(myJob)
        expectedOutput = """\
---------------------------
simulation_input.dat
---------------------------
random_seed 10
temperature 380.0
pressure 2.00

n_gas_species 1
gas_specs_names           H2
gas_energies             0.0
gas_molec_weights        XXX

n_surf_species 2
surf_specs_names          H*       H2*
surf_specs_dent            1         1

snapshots on time 1e-5
process_statistics on time 1e-5
species_numbers on time 1e-5
event_report off
max_steps infinity
max_time 1.0e+2
wall_time 5000

finish
---------------------------
lattice_input.dat
---------------------------

---------------------------
energetics_input.dat
---------------------------
energetics
cluster H*-f,H*-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H* 1
    2 H* 1
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster
cluster H2*-f,*-f:(1,2)
  sites 2
  neighboring 1-2
  lattice_state
    1 H2* 1
    2 * 0
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster
cluster *-f,*-f:H2:(1,2)
  # gas_species H2
  sites 2
  neighboring 1-2
  lattice_state
    1 * 0
    2 * 0
  site_types f f
  graph_multiplicity 2
  cluster_eng 0.1
end_cluster
end energetics
---------------------------
mechanism_input.dat
---------------------------
mechanism
reversible_step H*-f,H*-f:(1,2)<-->H2*-f,*-f:(1,2)
  sites 2
  neighboring 1-2
  initial
    1 H* 1
    2 H* 1
  final
    1 H2* 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_step
step H2*-f,*-f:(1,2)-->*-f,*-f:H2:(1,2)
  gas_species H2 1
  sites 2
  neighboring 1-2
  initial
    1 H2* 1
    2 * 1
  final
    1 * 1
    2 * 1
  site_types f f
  pre_expon 1.000000e+13
  pe_ratio 0.676
  activ_eng 0.2
end_step
end_mechanism\
"""
        assert( output == expectedOutput )
