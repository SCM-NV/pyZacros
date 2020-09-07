import os
import sys

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


    #def fromAMS( self, amsResultsDirName: str="ams.results" ):
    #def fromAMS( self, result: scm.plams.Results ):
    def fromAMS( self, results ):
        """
        Loads the mechanism from a AMS results object

        :parm amsResultsDirName: str. Stablishes the file name of the rkf file to load
        :parm results: str. xxxx
        """
        AMSHOME = os.getenv("AMSHOME")
        if( AMSHOME == None ):
            print( "### Error ###: Environment variable AMSHOME not found !!!" )
            quit()
        if( AMSHOME+"/scripting" not in sys.path ): sys.path.append( AMSHOME+"/scripting" )

        import scm.plams

        scm.plams.init()

        if( not results.job.ok() ):
            print("### ERROR ### AMS results object was correctly generated")
            raise

        print("\n-------------------------------------")
        print(" Results")
        print("-------------------------------------\n")

        nStates = results.readrkf("EnergyLandscape", "nStates")
        fileNames = results.readrkf("EnergyLandscape", "fileNames").replace(".rkf","").split()
        counts = results.readrkf("EnergyLandscape", "counts")
        isTS = results.readrkf("EnergyLandscape", "isTS")
        reactants = results.readrkf("EnergyLandscape", "reactants")
        products = results.readrkf("EnergyLandscape", "products")

        print("nStates = ", nStates)
        print("fileNames = ", fileNames)
        print("counts = ", counts)
        print("isTS = ", isTS)
        print("reactants = ", reactants)
        print("products = ", products)

        for i,fileName in enumerate(fileNames):
            mol = results.get_molecule("Molecule", file=fileNames[i])
            skeleton = results.get_rkf_skeleton( file=fileNames[i] )
            amsResults = results.read_rkf_section("AMSResults", file=fileNames[i])
            thermodynamics = results.read_rkf_section("Thermodynamics", file=fileNames[i])
            vibrations = results.read_rkf_section("Vibrations", file=fileNames[i])
            print("Id = ", i)
            print("Energy = ", amsResults["Energy"])
            print("Frequencies = ", vibrations["Frequencies[cm-1]"])
            print("ZeroPointEnergy = ", vibrations["ZeroPointEnergy"])
            print(mol)

        scm.plams.finish()
