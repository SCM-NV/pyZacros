import os
import re

__all__ = ['OutputFilesParser']


class OutputFilesParser:
    EOF = "EOF$$"

    def __init__( self, resultsDir ):
        """
        Creates a new OutputFilesParser object

        :parm results
        """
        if( not os.path.isdir(resultsDir) ):
            msg  = "### ERROR ### OutputFilesParser.__init__.\n"
            msg += "              Results directory "+resultsDir+" not found\n"
            raise NameError(msg)

        self.__general_output = resultsDir+"/general_output.txt"
        if( not os.path.isfile(self.__general_output) ):
            msg  = "### ERROR ### OutputFilesParser.__init__.\n"
            msg += "              Results file "+self.__general_output+" not found\n"
            raise NameError(msg)

        self.__history_output = resultsDir+"/history_output.txt"
        if( not os.path.isfile(self.__history_output) ):
            msg  = "### ERROR ### OutputFilesParser.__init__.\n"
            msg += "              Results file "+self.__history_output+" not found\n"
            raise NameError(msg)

        self.__lattice_output = resultsDir+"/lattice_output.txt"
        if( not os.path.isfile(self.__lattice_output) ):
            msg  = "### ERROR ### OutputFilesParser.__init__.\n"
            msg += "              Results file "+self.__lattice_output+" not found\n"
            raise NameError(msg)

        self.__procstat_output = resultsDir+"/procstat_output.txt"
        if( not os.path.isfile(self.__procstat_output) ):
            msg  = "### ERROR ### OutputFilesParser.__init__.\n"
            msg += "              Results file "+self.__procstat_output+" not found\n"
            raise NameError(msg)

        self.__specnum_output = resultsDir+"/specnum_output.txt"
        if( not os.path.isfile(self.__specnum_output) ):
            msg  = "### ERROR ### OutputFilesParser.__init__.\n"
            msg += "              Results file "+self.__specnum_output+" not found\n"
            raise NameError(msg)

        # Options from general_output.txt
        self.random_seed = None
        self.temperature = None
        self.pressure = None
        self.n_gas_species = None
        self.gas_specs_names = None
        self.gas_energies = None
        self.gas_molec_weights = None
        self.gas_molar_fracs = None
        self.n_surf_species = None
        self.surf_specs_names = None
        self.surf_specs_dent = None
        self.max_steps = None
        self.max_time = None
        self.wall_time = None

        self.__loadGeneralOutput()
        #self.__loadHistoryOutput()
        #self.__loadLatticeOutput()
        #self.__loadProcsStatOutput()
        #self.__loadSpecNumOutput()


    def __str__( self ):
        """
        Translates the object to a string
        """
        output = ""

        for k,v in self.__dict__.items():
            if( str(k).find("_") > 1 ): # Do not print private attributes
                output += str(k)+" = "+str(v)+"\n"

        return output


    @staticmethod
    def getBlockFrom( text, begin, end=None, lineFilter=".*", pos=-1 ):
        locatedBegin=False
        locatedEnd=False

        previousBlock = ""
        previousHeader = ""
        previousFooter = ""

        selectedBlock = ""
        selectedHeader = ""
        footer = ""

        if( len(text) == 0 ):
            return ( None, selectedHeader, footer, 0 )

        lines = text.splitlines()

        nBlock=0
        nLine=0
        for line in lines:

            if( locatedBegin==True ):

                if( end == None or nLine+1 == len(lines) ):
                    selectedBlock = selectedBlock+line

                    footer = ""

                    locatedBegin = False
                    locatedEnd = True

                    break

                elif( re.match( end, line ) ):
                    # Esta linea lo que busca es quitar el ultimo
                    # cambio de linea adicionado por el comando
                    # selectedBlock = selectedBlock+line+"\n"
                    # que esta mas abajo
                    selectedBlock = selectedBlock[:-1]
                    footer = line

                    locatedBegin = False
                    locatedEnd = True

                    if( pos == nBlock  ):
                        break
                    else:
                        nBlock += 1

                elif( re.match( lineFilter, line ) ):
                        selectedBlock = selectedBlock+line+"\n"

            if( re.match( begin, line ) ):
                locatedBegin = True
                locatedEnd = False
                previousBlock = selectedBlock
                previousHeader = selectedHeader
                selectedHeader = line
                selectedBlock = ""

            nLine += 1

        # Solo para el caso en que no se solicite una posicion especifica del bloque
        # se actualizara el numero de bloques
        if( pos == -1 ):
            numberOfBlocks = nBlock
        else:
            numberOfBlocks = -1

        if( locatedEnd ):
            return ( selectedBlock, selectedHeader, footer, numberOfBlocks )
        else:
            return ( previousBlock, previousHeader, footer, numberOfBlocks )


    def __loadGeneralOutput( self ):
        iFile = open( self.__general_output, "r" )
        fileContent = iFile.read()
        iFile.close()

        content,_,_,_ = OutputFilesParser.getBlockFrom( fileContent, "Simulation setup:", end="Finished reading simulation input.", lineFilter=".*[a-z]+[:].*" )

        def set_max_steps( sv ):
            if( sv.find("maximum allowed value") != -1 ):
                self.max_steps = "inf"
            else:
                self.max_steps = int(sv)

        cases = {
            "Random sequence with seed"     : lambda sv: setattr(self,"random_seed",int(sv)),
            "Temperature"                   : lambda sv: setattr(self,"temperature",float(sv)),
            "Pressure"                      : lambda sv: setattr(self,"pressure", float(sv)),
            "Number of gas species"         : lambda sv: setattr(self,"n_gas_species", int(sv)),
            "Gas species names"             : lambda sv: setattr(self,"gas_specs_names", [ v for v in sv.split("#")[0].split() ]),
            "Gas species energies"          : lambda sv: setattr(self,"gas_energies", [ float(v) for v in sv.split("#")[0].split() ]),
            "Gas species molecular weights" : lambda sv: setattr(self,"gas_molec_weights", [ float(v) for v in sv.split("#")[0].split() ]),
            "Gas species molar fractions"   : lambda sv: setattr(self,"gas_molar_fracs", [ float(v) for v in sv.split("#")[0].split() ]),
            "Number of surface species"     : lambda sv: setattr(self,"n_surf_species", int(sv)),
            "Surface species names"         : lambda sv: setattr(self,"surf_specs_names", [ v for v in sv.split("#")[0].split() ]),
            "Surface species dentation"     : lambda sv: setattr(self,"surf_specs_dent", [ int(v) for v in sv.split("#")[0].split() ]),
            "Maximum number of steps"       : lambda sv: set_max_steps(sv),
            "Max simulated time"            : lambda sv: setattr(self,"max_time", float(sv)),
            "Allowed walltime in seconds"   : lambda sv: setattr(self,"wall_time", int(sv))
        }

        for line in content.splitlines():
            tokens = line.split(":")
            cases.get(tokens[0].strip(), lambda sv: print("Key didn't match a case. File: "+self.__general_output))( tokens[1].strip() )

        #print(">>>>>>>>>>")
        #content,_,_,_ = OutputFilesParser.getBlockFrom( fileContent, "Simulation setup:", end="Finished reading simulation input.", lineFilter=".*every.*" )
        #for line in content.splitlines():
            #tokens = line.split("every")
            #print(tokens)


    def __loadHistoryOutput( self ):
        raise NameError("Loading file "+self.__history_output+" is not implemented yet!")


    def __loadLatticeOutput( self ):
        raise NameError("Loading file "+self.__lattice_output+" is not implemented yet!")


    def __loadProcsStatOutput( self ):
        raise NameError("Loading file "+self.__procstat_output+" is not implemented yet!")


    def __loadSpecNumOutput( self ):
        raise NameError("Loading file "+self.__specnum_output+" is not implemented yet!")
        pass
