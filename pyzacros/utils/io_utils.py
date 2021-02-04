# -*- PLT@NLeSC(2020) -*-
"""Module containing utilities to read/write data."""
from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.Lattice import Lattice
from pyzacros.classes.Cluster import Cluster
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.InitialState import InitialState
from pyzacros.utils.setting_utils import get_molar_fractions, get_denticity
from pyzacros.utils.setting_utils import get_species, get_species_labels
from pyzacros.utils.setting_utils import get_gas_species, get_adsorbed_species
from pyzacros.classes.Species import Species
from collections import Counter
from typing import List


def write_file_input(settings: KMCSettings = None,
                     lattice: Lattice = None,
                     mechanism: List[ElementaryReaction] = None,
                     cluster_expansions: List[Cluster] = None,
                     initial_state: InitialState = None):
    """
    Parse function to print input files.

    Depending on the arguments, it will call different printing functions.

    :param settings: KMC calculation settings.

    :param mechanism: A Reaction mechanism.
    """
    if settings and mechanism:
        output = write_simulation_input(settings, mechanism)
    elif lattice:
        output = write_lattice_input(lattice)
    elif mechanism:
        output = write_mechanism_input(mechanism)
    elif cluster_expansions:
        output = write_cluster_expansion_input(cluster_expansions)
    elif initial_state:
        output = write_initial_state(initial_state)
    else:
        msg = "### ERROR ### write_file_input function in io_utils.py\n"
        msg += "Wrong arguments passed to function.\n"
        raise ValueError(msg)
    return output


def write_simulation_input(settings: KMCSettings,
                           mechanism: List[ElementaryReaction]) -> str:
    """
    Return a string with the content of simulation_input.dat.

    :param settings: KMC calculation settings.

    :param mechanism: A Reaction mechanism.

    :return: String with the information to be printed in file.
    """
    # Get the Species info from Mechanism:
    species = get_species(mechanism)
    gas_species = get_gas_species(species)
    gas_species_labels = get_species_labels(gas_species)
    molar_frac_list = get_molar_fractions(settings, gas_species)
    adsorbed_species = get_adsorbed_species(species)
    adsorbed_species_labels = get_species_labels(adsorbed_species)
    denticity_list = get_denticity(adsorbed_species)

    # Print gas_phase species info:
    if(len(gas_species_labels) > 0):
        output = "n_gas_species"+"\t" + \
                  str(len(gas_species_labels))+"\n"
        output += "gas_specs_names  \t" + \
                  str('\t '.join(gas_species_labels))+"\n"
        output += "gas_molar_fracs \t" + \
                  "\t ".join([str(elem) for elem in molar_frac_list]) + "\n"
        output += "gas_energies \t"
        for i in gas_species:
            output += "\t" + str(i.gas_energy)
        output += "\n"
        output += "gas_molec_weights "
        for i in gas_species:
            output += "\t" + str(i.mass())
        output += "\n"
    output += "\n"

    # Print adsorbed species info:
    if(len(adsorbed_species_labels) > 0):
        output += "n_surf_species"+"\t"+str(len(adsorbed_species_labels))+"\n"
        output += "surf_specs_names  \t"
        output += str('\t '.join(adsorbed_species_labels))+"\n"
        output += "surf_specs_dent \t" + \
                  "\t ".join([str(elem) for elem in denticity_list]) + "\n"
    output += "\n"

    # Print general settings:
    output += print_settings(settings=settings)
    return output


def print_settings(settings=KMCSettings) -> str:
    """
    Print settings in the simulation_input.dat.

    :param settings: KMC calculation settings.

    :return: String with the information to be printed in file.
    """
    output = "random_seed\t" + \
             str(settings.get(('random_seed')))+"\n"
    output += "temperature\t" + \
              str(float(settings.get(('temperature'))))+"\n"
    output += "pressure\t" + \
              str(float(settings.get(('pressure'))))+"\n"
    output += "\n"
    output += print_optional_settings(settings=settings, opt_sett='snapshots')
    output += print_optional_settings(settings, opt_sett='process_statistics')
    output += print_optional_settings(settings, opt_sett='species_numbers')
    output += "event_report\t" + \
              str(settings.get(('event_report')))+"\n"
    output += "max_steps\t" + \
              str(settings.get(('max_steps')))+"\n"
    output += "max_time\t" + \
              str(settings.get(('max_time')))+"\n"
    output += "wall_time\t" + \
              str(settings.get(('wall_time')))+"\n"
    output += "\nfinish"
    return output


def print_optional_settings(settings: KMCSettings, opt_sett: str) -> str:
    """
    Give back the printing of an time/event/logtime KMCSetting.

    :param opt_sett: Option setting.

    :return: String with the correct format to be printed.
    """
    dictionary = settings.as_dict()
    if 'time' in str(dictionary[opt_sett]):
        output = opt_sett + "\t" + "on time \t" + \
                 str(float(dictionary[opt_sett][1])) + "\n"
    if 'event' in str(dictionary[opt_sett]):
        output = opt_sett + "\t" + "on event\n"
    # Because the order, it will overwrite time:
    if 'logtime' in str(dictionary[opt_sett]):
        output = opt_sett + "\t" + "on logtime\t" + \
                str(float(dictionary[opt_sett][1])) + "\t" + \
                str(float(dictionary[opt_sett][2])) + "\n"
    return output


def write_lattice_input(lattice=Lattice) -> str:
    """
    Return a string with the content of lattice_input.dat.

    :param lattice: A Lattice object.

    :return: String with the information to be printed in file.
    """
    output = "lattice"+" "+lattice.lattice_type+"\n"
    if lattice.default_lattice is not None:
        # The Lattice is given by default (read from .yaml):
        for i in range(4):
            output += str(lattice.default_lattice[i]) + " "
        output += "\nend_lattice"
    else:
        # The Lattice is provided by user:
        output += "cell_vectors"
        for i in range(2):
            output += "\n"
            for j in range(2):
                output += "  " + str(lattice.cell_vectors[i][j])
        output += "\nrepeat_cell "
        output += str(str(lattice.repeat_cell)[1:-1]).replace(',', '')
        output += "\nn_cell_sites " + str(lattice.n_cell_sites)
        output += "\nn_site_types " + str(lattice.n_site_types)
        output += "\nsite_type_names " \
                  + str(' '.join(str(x) for x in lattice.site_type_names))
        output += "\nsite_types " \
                  + str(' '.join(str(x) for x in lattice.site_types))
        output += "\nsite_coordinates"
        for i in range(lattice.n_cell_sites):
            output += "\n"
            for j in range(2):
                output += "\t" + str(lattice.site_coordinates[i][j])
        output += "\nneighboring_structure"
        for i in range(len(lattice.neighboring_structure)):
            output += "\n"
            output += "\t" + \
                      str('\t'.join(str(lattice.neighboring_structure[i][j])
                          for j in range(2)))
        output += "\nend_neighboring_structure"
        output += "\nend_lattice"
    return output


def write_mechanism_input(mechanism=List[ElementaryReaction]) -> str:
    """
    Return a string with the content of mechanism_input.dat.

    :param mechanism: A Mechanism object.

    :return: String with the information to be printed in file.
    """
#    gas_species = get_gas_species(get_species(mechanism))
    output = "mechanism"+"\n\n"
    # Main loop on the Elementary reactions of the mechanism:
    for index, ij in enumerate(mechanism):
        if ij.reversible is True:
            output += "reversible_step " + ij.label() + "\n"
        else:
            output += "step " + ij.label() + "\n"

        # Determine how many gas species are for each initial/final state of
        # the ij ElementaryReaction:
        initial_gas_species_labels = get_species_labels(
                                     get_gas_species(ij.initial))
        final_gas_species_labels = get_species_labels(
                                   get_gas_species(ij.final))

        # Print gas Species consumed/produced during the ij ElementaryReaction:
        if (len(initial_gas_species_labels) != 0
           or len(final_gas_species_labels) != 0):
            output += "  gas_reacs_prods "
            for kl in set(initial_gas_species_labels):
                output += kl + "  "\
                       + "-" + str(initial_gas_species_labels.count(kl))\
                       + "  "
            for kl in set(final_gas_species_labels):
                output += kl + "  "\
                       + str(final_gas_species_labels.count(kl))\
                       + "  "
            output += "\n"

        # Print sites and neighborings:
        if(ij.sites != 0):
            output += "  sites " + str(ij.sites)+"\n"
            if ij.neighboring is not None:
                output += "  neighboring "
                for kl in range(len(ij.neighboring)):
                    output += str(ij.neighboring[kl][0]) + \
                             "-"+str(ij.neighboring[kl][1])
                    if(kl != len(ij.neighboring)-1):
                        output += " "
                output += "\n"

        # Print initial and final blocks:
        output += "  initial"+"\n"
        index = 1
        for species in ij.initial:
            if species.is_adsorbed():
                output += "\t" + str(index) + "\t" + str(species.symbol)\
                       + "\t" + str(species.denticity) + "\n"
                index += 1
        output += "  final"+"\n"
        index = 1
        for species in ij.final:
            if species.is_adsorbed():
                output += "\t" + str(index) + "\t" + str(species.symbol)\
                       + "\t" + str(species.denticity) + "\n"
                index += 1

        # Print site_types if they are different:
        all_sites_are_the_same = False
        if len(ij.site_types) > 0:
            all_sites_are_the_same = \
                                ij.site_types.count(ij.site_types[0])\
                                == len(ij.site_types)
            if not all_sites_are_the_same:
                output += "  site_types "
                for kl in range(len(ij.site_types)):
                    output += str(ij.site_types[kl])
                    if(kl != len(ij.site_types)-1):
                        output += " "
                output += "\n"

        # Print pre-exponent and ratios:
        output += "  pre_expon " + str(ij.pre_expon)+"\n"
        if ij.reversible is True:
            output += "  pe_ratio " + str(ij.pe_ratio)+"\n"
        output += "  activ_eng " + str(ij.activation_energy)+"\n"
        if ij.reversible is True:
            output += "end_reversible_step\n"
        else:
            output += "end_step\n"
        output += "\n"

    output += "end_mechanism"
    return output


def write_cluster_expansion_input(cluster_expansions=List[Cluster]) -> str:
    """
    Return a string with the content of energetics_input.dat.

    :param mechanism: A List of Clusters.

    :return: String with the information to be printed in file.
    """
    output = "energetics \n"
    output += "\n"
    for ij in cluster_expansions:
        output += "cluster " + ij.label() + "\n"
        if(len(ij.site_types) != 0):
            output += "  sites " + str(len(ij.site_types))+"\n"
        if ij.neighboring is not None:
            output += "  neighboring "
            for i in range(len(ij.neighboring)):
                output += str(ij.neighboring[i][0]) + "-" \
                        + str(ij.neighboring[i][1])
                if(i != len(ij.neighboring)-1):
                    output += " "
            output += "\n"
        output += "  lattice_state"+"\n"
        for i in range(len(ij.species)):
            for j in range(ij.species[i].denticity):
                output += "    " + str(i+1) + " " \
                       + ij.species[i].symbol + " " + str(j+1) + "\n"
        output += "  site_types "
        for i in range(len(ij.site_types)):
            output += str(ij.site_types[i])
            if(i != len(ij.site_types)-1):
                output += " "
        output += "\n"

        output += "  graph_multiplicity "+str(ij.multiplicity)+"\n"

        output += "  cluster_eng   " + str(ij.cluster_energy) + "\n"
        output += "end_cluster\n"
        output += "\n"
    output += "end_energetics"
    return output


def write_initial_state(initial_state=InitialState) -> str:
    """
    Return a string with the content of state_input.dat.

    :param mechanism: An InitialState object.

    :return: String with the information to be printed in file.
    """
    output = "initial_state\n"
    for species, id_sites in initial_state.filledSitesPerSpecies.items():
        for i, id_site in enumerate(id_sites):
            output += "  seed_on_sites "+species.symbol+" "+str(id_site)+"\n"
    output += "end_initial_state"
    return output


def read_input_data(engine: str,
                    electronic_package: str = None,
                    path: str = None):
    """
    Search input files. In increasing hierarchical order.

    - Read engine standard input.
    - Read ab-initio output input.
    - Read formatted yaml or hdf5 files.

    :return: instantiation of PLAMS-like settings according for the input
             files read.
    """
    # 1. find engine standard files:
    #   list=find_input_files(enigne)                      ### find_utils.py
    #   map_settings(input_file_list, engine)              ### setting_utils.py

    # 2. if results from ab-initio code:
    #   find_input_files(electronic_pacakge)               ### find_utils.py
    #   map_settings(input_file_list, electronic_package)  ### setting_utils.py

    # 3. Always:
    #   find_input_files(yaml)                             ### find_utils.py
    #   map_settings(input_file_list, formatted_input)     ### setting_utils.py

    print("Hello world!")
    return

