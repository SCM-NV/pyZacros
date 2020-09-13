"""Module containing the KMCJob class."""

from .SpeciesList import SpeciesList
from .Mechanism import Mechanism
from .Lattice import Lattice
from subprocess import Popen
from .KMCSettings import KMCSettings
from pyzacros.utils.setting_utils import check_settings
from pyzacros.utils.find_utils import find_KMCPaths


class KMCJob:
    """Job class that represents a chemical species."""

    def __init__(self, settings: KMCSettings, lattice: Lattice,
                 mechanism: Mechanism):
        """
        Create a new Job object.

        :parm settings: KMCSettings containing the parameters of the Zacros
                        calculation.
        :parm mechanism: Mechanism containing the mechanisms involed in the
                        calculation.
        :parm lattice: Lattice containing the lattice to be used during the
                       calculation.
        """
        check_settings(settings)

        self.settings = settings
        self.mechanism = mechanism
        self.lattice = lattice
        self.__speciesList = SpeciesList()
        self.__gasSpeciesList = SpeciesList()
        self.__updateSpeciesList()

        self.__clustersList = []
        self.__updateClustersList()

    def __str__(self) -> str:
        """Translate the object to a string."""
        output = ""

        output += "---------------------------"+"\n"
        output += "simulation_input.dat"+"\n"
        output += "---------------------------"+"\n"
        output += self.simulationInput()

        output += "\n"
        output += "---------------------------"+"\n"
        output += "lattice_input.dat"+"\n"
        output += "---------------------------"+"\n"
        output += self.latticeInput()

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

    def run(self):
        """Execute the KMC engine."""
        (path_to_engine, working_path) = find_KMCPaths(self.settings)
        self.writeInputFiles(directory=working_path)
        print("Running engine:")
        Popen([path_to_engine], cwd=working_path, shell=True)
        return

    def simulationInput(self) -> str:
        """Return a string with the content of simulation_input.dat ."""
        output = "random_seed\t" + \
                 str(self.settings.get(('random_seed')))+"\n"
        output += "temperature\t" + \
                  str(self.settings.get(('temperature')))+"\n"
        output += "pressure\t" + \
                  str(self.settings.get(('pressure')))+"\n"

        output += str(self.__gasSpeciesList)+"\n"
        output += str(self.__speciesList)+"\n"

        output += self.print_optional_sett(opt_sett='snapshots')
        output += self.print_optional_sett(opt_sett='process_statistics')
        output += self.print_optional_sett(opt_sett='species_numbers')

        output += "event_report\t" + \
                  str(self.settings.get(('event_report')))+"\n"
        output += "max_steps\t" + \
                  str(self.settings.get(('max_steps')))+"\n"
        output += "max_time\t" + \
                  str(self.settings.get(('max_time')))+"\n"
        output += "max_time\t" + \
                  str(self.settings.get(('max_time')))+"\n"
        return output

    def print_optional_sett(self, opt_sett: str) -> str:
        """Give back the printing of an time/event/logtime setting."""
        dictionary = self.settings.as_dict()

        if 'time' in str(dictionary[opt_sett]):
            output = opt_sett + "\t" + "on time \t" + \
                     str(dictionary[opt_sett][1]) + "\n"
        if 'event' in str(dictionary[opt_sett]):
            output = opt_sett + "\t" + "on event\n"
        # becuase the order, it will overwrite time:
        if 'logtime' in str(dictionary[opt_sett]):
            output = opt_sett + "\t" + "on logtime\t" + \
                    str(dictionary[opt_sett][1]) + "\t" + \
                    str(dictionary[opt_sett][2]) + "\n"
        return output

    def latticeInput(self) -> str:
        """Return a string with the content of the lattice_input.dat file."""
        output = str(self.lattice)
        return output

    def energeticsInput(self) -> str:
        """Return a string with the content of the energetics_input.dat file."""
        output = "energetics"+"\n"
        for cluster in self.__clustersList:
            output += str(cluster)+"\n"
        output += "end energetics"

        return output

    def mechanismInput(self) -> str:
        """
        Returns a string with the content of the mechanism_input.dat file
        """
        output = str(self.mechanism)

        return output

    def writeInputFiles(self, directory: str):
        """
        Write KMC inputs files to disk.

        :parm directory: Directory where the Zacros will be printed.
        :type directory: str, required.
        """
        with open(directory+"/simulation_input.dat", "w") as f:
            f.write(self.simulationInput())
        with open(directory+"/lattice_input.dat", "w") as f:
            f.write(self.latticeInput())
        with open(directory+"/energetics_input.dat", "w") as f:
            f.write(self.energeticsInput())
        with open(directory+"/mechanism_input.dat", "w") as f:
            f.write(self.mechanismInput())

    def __updateSpeciesList(self):
        """
        Update self.__speciesList and self.__gasSpeciesList from self.mechanism.

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

