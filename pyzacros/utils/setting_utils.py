# -*- PLT@NLeSC(2020) -*-
"""Module containing utilities to check and map objects."""
from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Species import Species
from typing import List


def check_settings(settings=KMCSettings, species_list=List[Species]):
    """
    Check KMCSettings, load defaults if necessary.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.

    :parm species_list: List of species contained in the Mechanism.
    """
    # This list contains the defaults for KMCSettings, please modify
    # them as you wish.
    # They will NOT overwrite settings provided by user.
    tmp = KMCSettings(
        {'KMCEngine': {'name': 'Zacros'},
         'snapshots': ('time', 0.0005),
         'process_statistics': ('time', 0.0005),
         'species_numbers': ('time', 0.0005),
         'event_report': 'off',
         'max_steps': 'infinity',
         'max_time': 250.0,
         'wall_time': 10})
    # Soft merge of the settings:
    settings.soft_update(tmp)
    # Molar fractions were introduced as KMCSettings, here they are checked:
    check_molar_fraction(settings, species_list)


def check_molar_fraction(settings=KMCSettings,
                         species_list=List[Species]):
    """
    Check if molar_fraction labels are compatible with Species labels.

    It also sets defaults molar_fractions 0.000.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.

    :parm species_list: A List of Species to be check.
    """
    label_list = get_species_labels(species_list)
    sett_keys = settings.as_dict()
    try:
        sett_keys = list(sett_keys["molar_fraction"])
    except KeyError:
        print("### ERROR ### check_molar_fraction_labels.\n"
              "No molar fractions defined.")
        raise
    # Check if the molar fraction is assigned to a gas species:
    for i in sett_keys:
        if i not in label_list:
            msg = "### ERROR ### check_molar_fraction_labels.\n"
            msg += "molar fraction defined for a non-gas species."
            raise NameError(msg)
    # Set default molar_fraction = 0.00 to the rest of gas species.
    for i in label_list:
        if i not in sett_keys:
            tmp = KMCSettings({'molar_fraction': {i: 0.000}})
            # Soft merge of the settings:
            settings.soft_update(tmp)


def get_molar_fractions(settings=KMCSettings,
                        species_list=List[Species]) -> list:
    """
    Get molar fractions of a List[Species] in the same order as species_list.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.

    :parm species_list: A List of Species.

    :return molar_fraction_list: Simple list of molar fracions.
    """
    # We must be sure that the order of return list is the same as
    # the order of the labels printed by SpeciesList.
    # For that:

    # 1- Generate a total_list of tuples with (atomic label,
    #    molar_fraction):
    label_list = []
    molar_fraction_list = []
    dic_test = settings.as_dict()
    for i, j in dic_test.items():
        if i == "molar_fraction":
            for key in sorted(j.keys()):
                label_list.append(key)
                molar_fraction_list.append(j[key])
    total_list = list(zip(label_list, molar_fraction_list))

    # 2- Match the total_tuple to the "good" ordering of the
    # species_list:
    molar_fraction_list.clear()
    tuple_tmp = [i[0] for i in total_list]
    molar_tmp = [i[1] for i in total_list]
    for i in get_species_labels(species_list):
        for j, k in enumerate(tuple_tmp):
            if i == k:
                molar_fraction_list.append(molar_tmp[j])
    return molar_fraction_list


def get_denticity(species_list=List[Species]) -> list:
    """
    Get denticy of a List[Species].

    :parm species_list: A List of Species.

    :return denticity_list: Simple list of denticities.
    """
    check_list(species_list, "Species")
    denticity_list = []
    for ij in species_list:
        if ij.denticity:
            denticity_list.append(ij.denticity)
    return denticity_list


def get_all_species(reaction_list=List[ElementaryReaction]) -> List[Species]:
    """
    Return the list of species in a List of ElementaryReactions.

    :return: List[Species] of all the species, including redundancies.
    """
    check_list(reaction_list, "ElementaryReaction")
    species_list = []
    for ij in reaction_list:
        for kl in ij.initial + ij.final:
            species_list.append(kl)
    return species_list


def get_species(reaction_list=List[ElementaryReaction])\
                       -> List[Species]:
    """
    Return the list of unique species in a List of ElementaryReactions.

    :param reaction_list: A List[ElementaryReaction] to be checked.

    :return: List[Species] of all the unique species, excluding redundancies.
    """
    check_list(reaction_list, "ElementaryReaction")
    unique_species = list(set(get_all_species(reaction_list)))
    return order_list_of_species(unique_species)


def get_unique_reactions(reaction_list=List[ElementaryReaction])\
                               -> List[ElementaryReaction]:
    """
    Return the list of unique species in a List of ElementaryReactions.

    :param reaction_list: A List[ElementaryReaction] to be checked.

    :return: List[ElementaryReactions] without redundancies.
    """
    check_list(reaction_list, "ElementaryReaction")
    return(order_list_of_reactions(list(set(reaction_list))))


def get_gas_species(species_list=List[Species]) -> List[Species]:
    """
    Return only gas species from a List[Species].

    :param List[Species]: Input List[Species].

    :return List[Species]: Outputs the list with only gas Species.
    """
    check_list(species_list, "Species")
    gas_species_list = []
    for ij in species_list:
        if ij.is_gas():
            gas_species_list.append(ij)
    return gas_species_list


def get_adsorbed_species(species_list=List[Species]) -> List[Species]:
    """
    Return only adsorbed species from a List[Species].

    Warning! Empty sites "*" will be EXCLUDED from the output list.

    :param List[Species]: Input List[Species].

    :return List[Species]: Outputs the list with only gas Species.
    """
    check_list(species_list, "Species")
    adsorbed_species_list = []
    for ij in species_list:
        if ij.is_adsorbed() and ij.symbol != "*":
            adsorbed_species_list.append(ij)
    return adsorbed_species_list


def get_species_labels(species_list=List[Species]) -> list:
    """
    Return a list of the List[Species] labels.

    :param List[Species]: Input List[Species].

    :return list: list with labels.
    """
    label_list = []
    for ij in species_list:
        label_list.append(ij.symbol)
    return label_list


def check_list(list_to_check=List, type_of_object=str):
    """
    Check the content of a List[] object.

    :param list_to_check: List[] object to check.

    :param type of_object: String to compare.
    """
    for i in list_to_check:
        if type_of_object not in str(type(i)):
            msg = "### ERROR ### check_list in function setting_utils.py\n"
            msg += "Wrong arguments passed to List[] object.\n"
            raise ValueError(msg)
    return


def order_list_of_species(list_to_order=List[Species]) -> List[Species]:
    """
    Orders a List of Species according to Species.symbols.

    :param list_to_order: List[Species] to order.

    :return: List[Species] with elements ordered by alphabetical order symbols.
    """
    list_to_order.sort(key=lambda x: x.symbol)
    return list_to_order


def order_list_of_reactions(list_to_order=List[ElementaryReaction]) \
                           -> List[ElementaryReaction]:
    """
    Orders a List of ElementaryReactions according ElementaryReaction.label.

    :param list_to_order: List[ElementaryReaction] to order.

    :return: List[ElementaryReaction] with elements ordered
    by alphabetical order symbols.
    """
    list_to_order.sort(key=lambda x: x.label())
    return list_to_order
