# -*- PLT@NLeSC(2020) -*-
"""
Module containing utilities to check and map objects.
"""
from pyzacros.classes.KMCSettings import KMCSettings
from pyzacros.classes.SpeciesList import SpeciesList


def check_settings(settings=KMCSettings, species_list=SpeciesList):
    """
    Check KMCSettings, load defaults if necessary.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.
    """
    # This list contains the defaults for KMCSettings, please modify
    # them as you wish.
    # They will NOT overwrite settings provided by user.
    check_molar_fraction(settings, species_list)
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


def check_molar_fraction(settings=KMCSettings,
                         species_list=SpeciesList):
    """
    Check if molar_fraction labels are compatible with Species labels.

    It also sets defaults molar_fractions 0.000.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.
    """
    list_of_species = species_list.gas_species_labels()
    sett_keys = settings.as_dict()
    sett_keys = list(sett_keys["molar_fraction"])
    # Check if the molar fraction is assigned to a gas species:
    for i in sett_keys:
        if i not in list_of_species:
            msg = "### ERROR ### check_molar_fraction_labels.\n"
            msg += "molar fraction defined for a non-gas species."
            raise NameError(msg)
    # Set default molar_fraction = 0.00 to the rest of gas species.
    for i in list_of_species:
        if i not in sett_keys:
            tmp = KMCSettings({'molar_fraction': {i: 0.000}})
            # Soft merge of the settings:
            settings.soft_update(tmp)


def get_molar_fractions(settings=KMCSettings,
                        species_list=SpeciesList) -> list:
    """
    Get molar fractions using the correct order of list_gas_species.

    :parm settings: KMCSettings object with the main settings of the
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
    for i in species_list.gas_species_labels():
        for j, k in enumerate(tuple_tmp):
            if i == k:
                list_of_molar_fractions.append(molar_tmp[j])
    return list_of_molar_fractions
