"""
Module containing the Settings class.
"""

import scm.plams

__all__ = ['Settings']

class Settings( scm.plams.Settings ):
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

        for option in ['snapshots', 'process_statistics', 'species_numbers']:
            if( option in self ):
                    pair = self[option]

                    if( len(pair) != 2 ):
                        msg  = "### ERROR ### keyword "+option+" in settings."
                        msg += "              Its value should be a pair (key,value)."
                        msg += "              Possible options for key:  'event', 'elemevent', 'time',       'logtime', 'realtime'"
                        msg += "              Possible options for value:  <int>,       <int>, <real>, (<real>,<real>),     <real>"
                        raise NameError(msg)

                    key,value = pair

                    if( key == 'logtime' ):
                        if( len(value) != 2 ):
                            msg  = "### ERROR ### keyword '"+option+" on "+key+"' in settings."
                            msg += "              Its value should be a pair of reals (<real>,<real>)."
                            raise NameError(msg)

                        output += "%-20s"%option + "      " + "on "+ key + "       " + str(float(value[1])) + "  " + str(float(value[2])) + "\n"
                    elif( key == 'event' or key == 'elemevent' ):
                        output += "%-20s"%option + "      " + "on "+ key + "       " + str(int(value)) + "\n"
                    else:
                        output += "%-20s"%option + "      " + "on "+ key + "       " + str(float(value)) + "\n"

        if( 'event_report' in self ): output += "event_report      " + str(self.get(('event_report')))+"\n"
        if( 'max_steps' in self ): output += "max_steps         " + str(self.get(('max_steps')))+"\n"
        if( 'max_time' in self ): output += "max_time          " + str(self.get(('max_time')))+"\n"
        if( 'wall_time' in self ): output += "wall_time         " + str(self.get(('wall_time')))+"\n"

        return output
