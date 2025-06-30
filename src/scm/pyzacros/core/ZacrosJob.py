"""Module containing the ZacrosJob class."""

#### WAIT FOR NEXT FIX VERSION, THEN LOAD SHOULD WORK PROPERLY, REVERT CHANGES TO DATA FILES, THINK ABOUT HOW TO HANDLE EXCEPTION ####



import os
import stat
import shutil

import scm.plams

from .ZacrosResults import *
from .Species import *
from .SpeciesList import *
from .Lattice import *
from .Cluster import *
from .ClusterExpansion import *
from .ElementaryReaction import *
from .Mechanism import *
from .Settings import *

__all__ = ["ZacrosJob", "ZacrosExecutableNotFoundError"]


class ZacrosExecutableNotFoundError(Exception):
    """Exception raised if zacros executable is not found in path

    Attributes:
        command -- zacros command
    """

    def __init__(self, command):
        super().__init__("Zacros executable (" + command + ") not found in $PATH")


class ZacrosJob(scm.plams.SingleJob):
    """
    Create a new ZacrosJob object.

    *   ``lattice`` -- Lattice containing the lattice to be used during the calculation.
    *   ``mechanism`` -- Mechanism containing the mechanisms involed in the calculation.
    *   ``cluster_expansion`` -- ClusterExpansion containing the list of Clusters to use during the simulation.
    *   ``initial_state`` -- Initial state of the system. By default the simulation will use an empty lattice.
    *   ``settings`` -- Settings containing the parameters of the Zacros calculation.
    *   ``name`` -- A string containing the name of the job. All zacros input and output files are stored in a folder with this name. If not supplied, the default name is ``plamsjob``.
    *   ``restart`` -- ZacrosJob object from which the calculation will be restarted
    """

    _command = os.environ["AMSBIN"] + "/zacros" if "AMSBIN" in os.environ else "zacros.x"
    _result_type = ZacrosResults
    _filenames = {
        "simulation": "simulation_input.dat",
        "lattice": "lattice_input.dat",
        "energetics": "energetics_input.dat",
        "mechanism": "mechanism_input.dat",
        "state": "state_input.dat",
        "restart": "restart.inf",
        "run": "slurm.run",
        "err": "std.err",
        "out": "std.out",
    }

    def __init__(self, lattice, mechanism, cluster_expansion, initial_state=None, restart=None, **kwargs):

        def check_molar_fraction(settings=Settings, species_list=SpeciesList):
            """
            Check if molar_fraction labels are compatible with Species labels.

            It also sets defaults molar_fractions 0.000.

            :parm settings: Settings object with the main settings of the
                            KMC calculation.
            """
            list_of_species = [sp.symbol for sp in species_list.gas_species()]
            section = settings.molar_fraction

            if "molar_fraction" in settings:

                # Check if the molar fraction is assigned to a gas species:
                for key in settings.molar_fraction.keys():
                    if key not in list_of_species:
                        msg = "\n### ERROR ### check_molar_fraction_labels.\n"
                        msg += "molar fraction defined for a non-gas species."
                        raise NameError(msg)

                # Set default molar_fraction = 0.00 to the rest of gas species.
                for key in list_of_species:
                    if key not in settings.keys():
                        section += {key: 0.000}
            else:
                for key in list_of_species:
                    section += {key: 0.000}

        if "settings" not in kwargs:
            msg = "\n### ERROR ### ZacrosJob.__init__.\n"
            msg += "                Parameter 'settings' is required by the ZacrosJob constructor.\n"
            raise NameError(msg)

        if "molecule" in kwargs:
            print("Warning: parameter 'molecule' is not used by the ZacrosJob constructor'")
            del kwargs["molecule"]

        scm.plams.SingleJob.__init__(self, molecule=None, **kwargs)

        self.lattice = lattice
        self.mechanism = mechanism
        if type(mechanism) == list:
            self.mechanism = Mechanism(mechanism)

        # if( set(map(type, self.mechanism.site_types_set())) == {int} )

        if not self.mechanism.site_types_set().issubset(self.lattice.site_types_set()):
            msg = "\n### ERROR ### ZacrosJob.__init__.\n"
            msg += "              Inconsistent site types found between lattice and mechanism.\n"
            msg += "              lattice=" + str(self.lattice.site_types_set()) + "\n"
            msg += "              mechanism=" + str(self.mechanism.site_types_set()) + "\n"
            raise NameError(msg)

        self.cluster_expansion = cluster_expansion
        if type(cluster_expansion) == list:
            self.cluster_expansion = ClusterExpansion(cluster_expansion)

        if not self.cluster_expansion.site_types_set().issubset(self.lattice.site_types_set()):
            msg = "\n### ERROR ### ZacrosJob.__init__.\n"
            msg += "              Inconsistent site types found between lattice and cluster_expansion.\n"
            msg += "              lattice=" + str(self.lattice.site_types_set()) + "\n"
            msg += "              cluster_expansion=" + str(self.cluster_expansion.site_types_set()) + "\n"
            raise NameError(msg)

        self.initial_state = initial_state

        self._restart_file_content = None
        self.restart = None

        if restart is not None:
            self.restart = restart
            restart_file = os.path.join(restart.path, ZacrosJob._filenames["restart"])
            with open(restart_file, "r") as depFile:
                self._restart_file_content = depFile.readlines()

        check_molar_fraction(self.settings, self.mechanism.gas_species())

        self._executable_path = shutil.which(self._command)

    def get_input(self):
        """
        It should generate the Zacros input file. But Zacros has several
        input files. So, we discourage using this function.
        On the other side, this function is also used as a hash to
        represent the job univocally. Because of that, we just return
        its string representation which contains all input files concatenated.
        """
        return str(self)

    def get_simulation_input(self):
        """
        Return a string with the content of simulation_input.dat.
        """

        def get_molar_fractions(settings, species_list):
            """
            Get molar fractions using the correct order of list_gas_species.

            :parm settings: Settings object with the main settings of the
                            KMC calculation.

            :parm species_list: SpeciesList object containing the species
                                    information.

            :rparm list_of_molar_fractions: Simple list of molar fracions.
            """
            # We must be sure that the order of return list is the same as
            # the order of the labels printed by SpeciesList.
            # For that:

            # 1- Generate a total_list of tuples with (atomic label,
            #    molar_fraciton):
            list_of_labels = []
            list_of_molar_fractions = []
            dic_test = settings.as_dict()
            for i, j in dic_test.items():
                if i == "molar_fraction":
                    for key in sorted(j.keys()):
                        list_of_labels.append(key)
                        list_of_molar_fractions.append(j[key])
            total_list = list(zip(list_of_labels, list_of_molar_fractions))

            # 2- Match the tota_tuple to the "good" ordering of the
            # species_list:
            list_of_molar_fractions.clear()
            tuple_tmp = [i[0] for i in total_list]
            molar_tmp = [i[1] for i in total_list]
            for i in [sp.symbol for sp in species_list.gas_species()]:
                for j, k in enumerate(tuple_tmp):
                    if i == k:
                        list_of_molar_fractions.append(molar_tmp[j])
            return list_of_molar_fractions

        output = str(self.settings) + "\n"

        gasSpecies = self.mechanism.gas_species()
        gasSpecies.extend(self.cluster_expansion.gas_species())
        gasSpecies.remove_duplicates()

        if len(gasSpecies) == 0:
            output += "n_gas_species    " + str(len(gasSpecies)) + "\n\n"
        else:
            output += str(gasSpecies)

        molar_frac_list = get_molar_fractions(self.settings, gasSpecies)

        surfaceSpecies = self.mechanism.species()
        surfaceSpecies.extend(self.cluster_expansion.surface_species())
        surfaceSpecies.remove_duplicates()

        if len(molar_frac_list) > 0:
            output += "gas_molar_fracs   " + "".join([" %20.10e" % elem for elem in molar_frac_list]) + "\n\n"
        output += str(surfaceSpecies) + "\n"

        output += "\n"
        output += "finish"
        return output

    def get_lattice_input(self):
        """
        Return a string with the content of the lattice_input.dat file.
        """
        return str(self.lattice)

    def get_energetics_input(self):
        """
        Return a string with the content of the energetics_input.dat file.
        """
        return str(self.cluster_expansion)

    def get_mechanism_input(self):
        """
        Returns a string with the content of the mechanism_input.dat file
        """
        return str(self.mechanism)

    def get_initial_state_input(self):
        """
        Returns a string with the content of the state_input.dat file
        """
        output = ""
        if self.initial_state is not None:
            output = str(self.initial_state)
        return output

    def get_restart_input(self):
        """
        Returns a string with the content of the restart.inf file
        """
        output = ""
        if self._restart_file_content is not None:
            for line in self._restart_file_content:
                output += line
        return output

    def check(self):
        """
        Look for the normal termination signal in the output. Note, that it does not mean your calculation was successful!
        """
        try:
            lines = self.results.grep_file(self.results._filenames["general"], pattern="> Normal termination <")
            return len(lines) > 0
        except scm.plams.FileError:
            return False

    def surface_poisoned(self):
        """
        Returns true in the case the "Warning code 801002" is find in the output.
        """
        lines = self.results.grep_file(
            self.results._filenames["general"],
            pattern="Warning code 801002 .* this may indicate that the surface is poisoned",
        )
        return len(lines) > 0

    def restart_aborted(self):
        """
        Returns true in the case the "Restart aborted:" is find in the output.
        """
        lines = self.results.grep_file(self.results._filenames["general"], pattern="Restart aborted:")
        return len(lines) > 0

    def get_runscript(self):
        """
        Generate a runscript for slurm

        ``name`` is taken from the class attribute ``_command``. ``-n`` flag is added if ``settings.runscript.nproc`` exists. ``[>jobname.out]`` is used based on ``settings.runscript.stdout_redirect``.
        """
        if self._executable_path is None:
            raise ZacrosExecutableNotFoundError(self._command)

        s = self.settings.runscript

        ret = "#!/bin/bash\n"
        ret += "\n"
        ret += "export OMP_NUM_THREADS=" + str(s.get("nproc", 1))
        ret += "\n"
        ret += self._executable_path

        if self._restart_file_content is not None and "restart" in self.settings:
            if "max_time" in self.settings["restart"]:
                ret += " --max_time=" + str(self.settings.restart.max_time)
            if "max_steps" in self.settings["restart"]:
                ret += " --max_steps=" + str(self.settings.restart.max_steps)
            if "wall_time" in self.settings["restart"]:
                ret += " --wall_time=" + str(self.settings.restart.wall_time)

        if s.stdout_redirect:
            ret += ' >"{}"'.format(ZacrosJob._filenames["out"])
        ret += "\n"

        return ret

    def _get_ready(self):
        """
        Create inputs and runscript files in the job folder.
        Filenames correspond to entries in the `_filenames` attribute
        """
        simulation = os.path.join(self.path, ZacrosJob._filenames["simulation"])
        lattice = os.path.join(self.path, ZacrosJob._filenames["lattice"])
        energetics = os.path.join(self.path, ZacrosJob._filenames["energetics"])
        mechanism = os.path.join(self.path, ZacrosJob._filenames["mechanism"])
        state = os.path.join(self.path, ZacrosJob._filenames["state"])
        restart = os.path.join(self.path, ZacrosJob._filenames["restart"])

        runfile = os.path.join(self.path, ZacrosJob._filenames["run"])
        # err = os.path.join(self.path, ZacrosJob._filenames['err'])
        # out = os.path.join(self.path, ZacrosJob._filenames['out'])

        with open(simulation, "w") as inp:
            inp.write(self.get_simulation_input())

        with open(lattice, "w") as inp:
            inp.write(self.get_lattice_input())

        with open(energetics, "w") as inp:
            inp.write(self.get_energetics_input())

        with open(mechanism, "w") as inp:
            inp.write(self.get_mechanism_input())

        if self.initial_state is not None:
            with open(state, "w") as inp:
                inp.write(self.get_initial_state_input())

        if self._restart_file_content is not None:
            with open(restart, "w") as inp:
                inp.write(self.get_restart_input())

        with open(runfile, "w") as run:
            run.write(self.get_runscript())

        os.chmod(runfile, os.stat(runfile).st_mode | stat.S_IEXEC)

    def __str__(self):
        """
        Translate the object to a string.
        """
        output = ""

        output += "---------------------------------------------------------------------" + "\n"
        output += ZacrosJob._filenames["simulation"] + "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += self.get_simulation_input()

        output += "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += ZacrosJob._filenames["lattice"] + "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += self.get_lattice_input()

        output += "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += ZacrosJob._filenames["energetics"] + "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += self.get_energetics_input()

        output += "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += ZacrosJob._filenames["mechanism"] + "\n"
        output += "---------------------------------------------------------------------" + "\n"
        output += self.get_mechanism_input()

        if self.initial_state is not None:
            output += "\n"
            output += "---------------------------------------------------------------------" + "\n"
            output += ZacrosJob._filenames["state"] + "\n"
            output += "---------------------------------------------------------------------" + "\n"
            output += self.get_initial_state_input()

        if self._restart_file_content is not None:
            output += "\n"
            output += "---------------------------------------------------------------------" + "\n"
            output += ZacrosJob._filenames["restart"] + "\n"
            output += "---------------------------------------------------------------------" + "\n"
            for line in self._restart_file_content:
                output += line

        return output

    @staticmethod
    def __recreate_simulation_input(path):
        """
        Recreates the simulation input for the corresponding job based on file 'simulation_input.dat' present in the job folder.
        This method is used by :func:~scm.pyzacros.ZacrosJob.load_external.
        Returns a :func:~scm.pyzacros.Settings object.
        """
        sett = Settings()

        with open(path + "/" + ZacrosJob._filenames["simulation"], "r") as inp:
            file_content = inp.readlines()
        file_content = [line for line in file_content if line.strip()]  # Removes empty lines

        for line in file_content:
            tokens = line.split()

            if len(tokens) < 2:
                continue

            def process_scheme(sv):
                if sv[1] == "event":
                    if len(sv) < 3:
                        return sv[1], 1
                    else:
                        return sv[1], int(sv[2])
                elif sv[1] == "elemevent":
                    return sv[1], int(sv[2])
                elif sv[1] == "time":
                    return sv[1], float(sv[2])
                elif sv[1] == "logtime":
                    return sv[1], float(sv[2]), float(sv[3])
                elif sv[1] == "realtime":
                    return sv[1], float(sv[2])
                else:
                    raise Exception(
                        "Error: Keyword "
                        + str(sv)
                        + " in file "
                        + ZacrosJob._filenames["simulation"]
                        + " is not supported!"
                    )

            # Specific conversion rules
            cases = {
                "random_seed": lambda sv: sett.setdefault("random_seed", int(sv[0])),
                "temperature": lambda sv: sett.setdefault("temperature", float(sv[0])),
                "pressure": lambda sv: sett.setdefault("pressure", float(sv[0])),
                "n_gas_species": lambda sv: sett.setdefault("n_gas_species", int(sv[0])),
                "gas_specs_names": lambda sv: sett.setdefault("gas_specs_names", sv),
                "gas_energies": lambda sv: sett.setdefault("gas_energies", [float(a) for a in sv]),
                "gas_molec_weights": lambda sv: sett.setdefault("gas_molec_weights", [float(a) for a in sv]),
                "gas_molar_fracs": lambda sv: sett.setdefault("gas_molar_fracs", [float(a) for a in sv]),
                "n_surf_species": lambda sv: sett.setdefault("n_surf_species", int(sv[0])),
                "surf_specs_names": lambda sv: sett.setdefault("surf_specs_names", sv),
                "surf_specs_dent": lambda sv: sett.setdefault("surf_specs_dent", [int(a) for a in sv]),
                "snapshots": lambda sv: sett.setdefault("snapshots", process_scheme(sv)),
                "process_statistics": lambda sv: sett.setdefault("process_statistics", process_scheme(sv)),
                "species_numbers": lambda sv: sett.setdefault("species_numbers", process_scheme(sv)),
                "event_report": lambda sv: sett.setdefault("event_report", sv[0]),
                "max_steps": lambda sv: sett.setdefault("max_steps", sv[0] if sv[0] == "infinity" else int(sv[0])),
                "max_time": lambda sv: sett.setdefault("max_time", float(sv[0])),
                "wall_time": lambda sv: sett.setdefault("wall_time", int(sv[0])),
                "override_array_bounds": lambda sv: sett.setdefault("override_array_bounds", " ".join(sv)),
            }
            value = cases.get(tokens[0], lambda sv: None)(tokens[1:])

            if value is None:
                raise Exception(
                    "Error: Keyword "
                    + tokens[0]
                    + " in file "
                    + ZacrosJob._filenames["simulation"]
                    + " is not supported!"
                )

        if sett.get("gas_molar_fracs") is not None:
            # Special case molar_fractions
            sett["molar_fraction"] = {}
            for i, spn in enumerate(sett["gas_specs_names"]):
                sett["molar_fraction"][spn] = sett["gas_molar_fracs"][i]
            del sett["gas_molar_fracs"]

        return sett

    @staticmethod
    def __recreate_lattice_input(path):
        """
        Recreates the lattice input for the corresponding job based on file 'lattice_input.dat' present in the job folder.
        This method is used by :func:~scm.pyzacros.ZacrosJob.load_external.
        Returns a :func:~scm.pyzacros.Lattice object.
        """
        return Lattice(fileName=path + "/" + ZacrosJob._filenames["lattice"])

    @staticmethod
    def __recreate_energetics_input(path, gas_species, surface_species):
        """
        Recreates the energetics input for the corresponding job based on file 'energetics_input.dat' present in the job folder.
        This method is used by :func:~scm.pyzacros.ZacrosJob.load_external.
        Returns a list of :func:~scm.pyzacros.Cluster objects.
        """
        return ClusterExpansion(
            fileName=path + "/" + ZacrosJob._filenames["energetics"], surface_species=surface_species
        )

    @staticmethod
    def __recreate_mechanism_input(path, gas_species, surface_species):
        """
        Recreates the mechanism input for the corresponding job based on file 'mechanism_input.dat' present in the job folder.
        This method is used by :func:~scm.pyzacros.ZacrosJob.load_external.
        Returns a :func:~scm.pyzacros.Mechanism object.
        """
        return Mechanism(
            fileName=path + "/" + ZacrosJob._filenames["mechanism"],
            gas_species=gas_species,
            surface_species=surface_species,
        )

    @staticmethod
    def __recreate_initial_state_input(lattice):
        """
        Recreates the initial state input for the corresponding job based on file 'initial_state_input.dat' present in the job folder.
        This method is used by :func:~scm.pyzacros.ZacrosJob.load_external.
        Returns a :func:~scm.pyzacros.LatticeState object
        """
        raise Exception("Error: __recreate_initial_state_input function is not implmented yet!")
        lattice_state = LatticeState()
        return lattice_state

    @classmethod
    def load_external(cls, path, settings=None, finalize=False, restart=None):
        """
        Loads an "external job," a Zacros calculation that either was or was not managed by pyZacros. All input and output files produced during the calculation should be placed in one folder, and *path* should be the path to this folder. The name of the folder is used as the job name. Example:

        .. code-block:: python

           import scm.pyzacros as pz
           job = ZacrosJob.load_external( path="plams_workdir/plamsjob" )
           print(job)

        *   ``path`` -- Path to the folder containing input and output files to restore.
        *   ``settings`` -- The Settings object for the calculation (``self.settings``) is loaded automatically from the path ``path``. However, by using this option ``self.settings`` will be replaced by ``settings``.
        *   ``finalize`` -- If ``finalize`` is ``False``, the status of the returned job is *copied* and results will be restored too. Otherwise, results will not be restored, so the job will need to be executed again.
        *   ``restart`` -- Selects the ``ZacrosJob`` to restart from
        """
        if not os.path.isdir(path):
            raise FileNotFoundError("Path {} does not exist, cannot load from it.".format(path))

        path = os.path.abspath(path)
        jobname = os.path.basename(path)

        sett = ZacrosJob.__recreate_simulation_input(path)

        gas_species = SpeciesList()
        for i in range(len(sett["gas_specs_names"])):
            gas_species.append(
                Species(
                    symbol=sett["gas_specs_names"][i],
                    gas_energy=sett["gas_energies"][i],
                    kind=Species.GAS,
                    mass=sett["gas_molec_weights"][i],
                )
            )

        surface_species = SpeciesList()
        surface_species.append(Species("*", 1))  # Empty adsorption site
        for i in range(len(sett["surf_specs_names"])):
            surface_species.append(
                Species(symbol=sett["surf_specs_names"][i], denticity=sett["surf_specs_dent"][i], kind=Species.SURFACE)
            )

        lattice = ZacrosJob.__recreate_lattice_input(path)
        cluster_expansion = ZacrosJob.__recreate_energetics_input(path, gas_species, surface_species)
        mechanism = ZacrosJob.__recreate_mechanism_input(path, gas_species, surface_species)
        initial_state = None  # TODO

        job = cls(
            settings=sett,
            lattice=lattice,
            mechanism=mechanism,
            cluster_expansion=cluster_expansion,
            initial_state=initial_state,
            name=jobname,
        )

        job.path = path
        job.status = "copied"
        job.results.collect()

        if finalize:
            job._finalize()

        job.restart = restart

        return job
