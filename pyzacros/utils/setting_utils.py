# -*- PLT@NLeSC(2020) -*-
"""
Module containing utilities to check and map objects.
"""
from pyzacros.classes.KMCSettings import KMCSettings


def check_settings(settings=KMCSettings):
    """
    Check KMCSettings, load defaults if necessary.

    :parm settings: KMCSettings object with the main settings of the
                    KMC calculation.
    :type settings: KMCSettings, required.
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
