"""
Module containing the Settings class.
"""

import scm.plams

__all__ = ['Settings']

class Settings( scm.plams.Settings ):
    """
    Automatic multi-level dictionary. Subclass of the PLAMS class `scm.plams.Settings <../../plams/components/settings.html>`_. This dictionary can contain any kind of information stored in key-value pairs. Be aware that no check of the rightness of the key/values is done at this level. This object is used just as a container. The verification of the physical meaning of the key-value pairs is done at the ZacrosJob class. The following is an example of use adapted to zacros:

    .. code:: python

        sett = Settings()
        sett.random_seed = 953129
        sett.temperature = 500.0
        sett.pressure = 1.0
        sett.snapshots = ('time', 0.1)
        sett.process_statistics = ('time', 0.1)
        sett.species_numbers = ('time', 0.1)
        sett.event_report = 'off'
        sett.max_steps = 'infinity'
        sett.max_time = 1.0
    """

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)


    def __str__( self ):
        """
        Translates the object to a string
        """
        output  = ""

        if( 'random_seed' in self ): output += "random_seed     " + "%10s"%self.get('random_seed')+"\n"
        output += "temperature     " + "%10s"%self.get('temperature')+"\n"
        output += "pressure        " + "%10s"%self.get('pressure')+"\n\n"

        for option in ['snapshots', 'process_statistics', 'species_numbers', 'energetics_lists', 'process_lists']:
            if( option in self ):
                    pair = self[option]
                    add = None

                    if( pair[0] in ['event', 'elemevent', 'time', 'logtime', 'realtime'] ):

                        # e.g. sett.snapshots = ('time', 1e1*dt)
                        if( len(pair) == 2 ):
                            key,value = pair

                        # e.g. sett.on_sites_seeding_reportevent_report = ('time', 1e1*dt, 'on')
                        elif(
                            len(pair) == 3
                            and pair[2] in ['on', 'off']
                        ):
                            key,value,add = pair[0],pair[1],pair[2]

                        # e.g. sett.snapshots = ('logtime', 1e1*dt, 0.1)
                        elif( len(pair) == 3 ):
                            key,value = pair[0],(pair[1],pair[2])

                        # e.g. sett.on_sites_seeding_reportevent_report = ('logtime', 1e-08*dt, 1.5, 'on')
                        elif(
                            len(pair) == 4
                            and pair[3] in ['on', 'off']
                        ):
                            key,value,add = pair[0],(pair[1],pair[2]),pair[3]

                        # e.g. sett.process_lists = ('time', 1e1*dt, 'select_event_type', [1,2])
                        elif(
                            len(pair) == 4
                            and pair[2] in ['select_cluster_type', 'select_event_type']
                            and type(pair[3]) == list
                        ):
                            key,value,add = pair[0],pair[1],(pair[2],pair[3])

                        # e.g. sett.process_lists = ('logtime', 1e-08*dt, 1.5, 'select_event_type', [1,2])
                        elif(
                            len(pair) == 5
                            and pair[3] in ['select_cluster_type', 'select_event_type']
                            and type(pair[4]) == list
                        ):
                            key,value,add = pair[0],(pair[1],pair[2]),(pair[3],pair[4])

                    else:
                        msg  = "\n### ERROR ### keyword "+option+" in settings.\n"
                        msg += "              Its value should be a pair (key,value[,value1]).\n"
                        msg += "              Possible options for key:  'event', 'elemevent', 'time',       'logtime', 'realtime'\n"
                        msg += "              Possible options for value:  <int>,       <int>, <real>, (<real>,<real>),     <real>\n"
                        msg += "              Given value: "+str(pair)+"\n"
                        raise NameError(msg)

                    if( key == 'logtime' ):
                        if( len(value) != 2 ):
                            msg  = "\n### ERROR ### keyword '"+option+" on "+key+"' in settings.\n"
                            msg += "              Its value should be a pair of reals (<real>,<real>).\n"
                            msg += "              Given value: "+str(value)+"\n"
                            raise NameError(msg)

                        output += "%-20s"%option + "      " + "on "+ key + "       " + str(float(value[0])) + "  " + str(float(value[1]))
                    elif( key == 'event' or key == 'elemevent' ):
                        output += "%-20s"%option + "      " + "on "+ key + "       " + str(int(value))
                    else:
                        output += "%-20s"%option + "      " + "on "+ key + "       " + str(float(value))

                    if( add is not None ):
                        if( type(add) == tuple and type(add[1]) == list ):
                            output += "%20s"%add[0] + "      " + " ".join([str(v) for v in add[1]])

                    output += "\n"

        if( 'on_sites_seeding_report' in self ): output += "on_sites_seeding_report         " + str(self.get(('on_sites_seeding_report')))+"\n"
        if( 'event_report' in self ): output += "event_report         " + str(self.get(('event_report')))+"\n"

        if( 'max_steps' in self ): output += "max_steps         " + str(self.get(('max_steps')))+"\n"
        if( 'max_time' in self ): output += "max_time          " + str(self.get(('max_time')))+"\n"
        if( 'wall_time' in self ): output += "wall_time         " + str(self.get(('wall_time')))+"\n"

        if( 'override_array_bounds' in self ): output += "override_array_bounds         " + str(self.get(('override_array_bounds')))+"\n"

        return output
