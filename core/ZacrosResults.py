"""Module containing the ZacrosResults class."""

import os
import stat

import numpy
import scipy
import scipy.stats
import scm.plams

from .Lattice import *
from .SpeciesList import *
from .ClusterExpansion import *
from .Mechanism import *
from .LatticeState import *
from .Settings import *

__all__ = ['ZacrosResults']

class ZacrosResults( scm.plams.Results ):
    """
    A Class for handling Zacros Results.
    """

    _filenames = {
        'general': 'general_output.txt',
        'history': 'history_output.txt',
        'lattice': 'lattice_output.txt',
        'procstat': 'procstat_output.txt',
        'specnum': 'specnum_output.txt',
        'restart': 'restart.inf',
        'err': 'std.err',
        'out': 'std.out'}


    def get_zacros_version(self):
        """
        Return the zacros's version from the 'general_output.txt' file.
        """
        if( self.job.restart is None ):
            lines = self.grep_file(self._filenames['general'], pattern='ZACROS')

            if( len(lines) > 0 ):
                zversion = lines[0].split()[2]
            else:
                lines = self.grep_file(self._filenames['restart'], pattern='Version')
                zversion = float(lines[0].split()[1])/1e5
        else:
            lines = self.grep_file(self._filenames['restart'], pattern='Version')
            zversion = float(lines[0].split()[1])/1e5
        return float(zversion)


    def get_reaction_network(self):
        """
        Return the reactions from the 'general_output.txt' file.
        """
        lines = self.get_file_chunk(self._filenames['general'], begin="Reaction network:", end="Finished reading mechanism input.")

        reaction_network = {}
        for line in lines:
            if( not line.strip() or line.find("A(Tini)") == -1 ): continue
            reaction_network[ line.split()[1].replace(':','') ] = line[line.find("Reaction:")+len("Reaction:"):].strip().replace('  ',' ')

        return reaction_network


    def provided_quantities(self):
        """
        Return the provided quantities from the ``specnum_output.txt`` file in a form of a dictionary.
        Below is shown an example of the ``specnum_output.txt`` for a zacros calculation.

        .. code-block:: none

            Entry   Nevents        Time   Temperature       Energy   O*  CO*     O2     CO   CO2
                1         0   0.000E+00   5.00000E+02   -4.089E+01   11   12      0      0     0
                2        88   1.000E-01   5.00000E+02   -7.269E+01   22   17    -21    -36    31
                3       176   2.000E-01   5.00000E+02   -9.139E+01   29   19    -41    -71    64
                4       247   3.000E-01   5.00000E+02   -1.041E+02   34   20    -57    -99    91

        For this example, this function will return:

        .. code-block:: python

            {
               "Entry":[1, 2, 3, 4],
               "Nevents":[0, 88, 176, 247],
               "Time":[0.000E+00, 1.000E-01, 2.000E-01, 3.000E-01],
               "Temperature":[5.00000E+02, 5.00000E+02, 5.00000E+02, 5.00000E+02],
               "Energy":[-4.089E+01, -7.269E+01, -9.139E+01, -1.041E+02],
               "O*":[11, 22, 29, 34],
               "CO*":[12, 17, 19, 20],
               "O2":[0, -21, -41, -57],
               "CO":[0, -36, -71, -99],
               "CO2":[0, 31, 64, 91]
            }
        """
        quantities = None
        if( self.job.restart is None ):
            lines = self.awk_file(self._filenames['specnum'],script='(NR==1){print $0}')
            names = lines[0].split()

            quantities = {}
            for name in names:
                quantities[name] = []
        else:
            quantities = self.job.restart.results.provided_quantities()
            names = list(quantities.keys())

        if( self.job.restart is None ):
            lines = self.awk_file(self._filenames['specnum'],script='(NR>1){print $0}')
        else:
            lines = self.awk_file(self._filenames['specnum'],script='{print $0}')

        for line in lines:
            for i,token in enumerate(line.split()):
                # Specific conversion rules
                cases = {
                    "Time"        : lambda sv: float(sv),
                    "Temperature" : lambda sv: float(sv),
                    "Energy"      : lambda sv: float(sv)
                }

                # Notice that by default values are considered integers
                value = cases.get( names[i], lambda sv: int(sv) )( token.strip() )
                quantities[ names[i] ].append( value )

        return quantities


    def number_of_lattice_sites(self):
        """
        Return the number of lattice sites from the 'general_output.txt' file.
        """
        zversion = self.get_zacros_version()

        if( self.job.restart is not None ):
            nsites = self.job.restart.results.number_of_lattice_sites()
        else:
            if( zversion >= 2.0 and zversion < 3.0 ):
                lines = self.grep_file(self._filenames['general'], pattern='Number of lattice sites:')
                nsites = lines[0][ lines[0].find('Number of lattice sites:')+len("Number of lattice sites:"): ]
            elif( zversion >= 3.0 ):
                lines = self.grep_file(self._filenames['general'], pattern='Total number of lattice sites:')
                nsites = lines[0][ lines[0].find('Total number of lattice sites:')+len("Total number of lattice sites:"): ]
            else:
                raise Exception( "Error: Zacros version "+str(zversion)+" not supported!" )

            nsites = int(nsites)

        return nsites


    def gas_species_names(self):
        """
        Return the gas species names from the 'general_output.txt' file.
        """
        output = []

        lines = self.grep_file(self._filenames['general'], pattern='Gas species names:')

        if( len(lines) != 0 ):
            output = lines[0][ lines[0].find('Gas species names:')+len("Gas species names:"): ].split()

        if( self.job.restart is not None ):
            output.extend( self.job.restart.results.gas_species_names() )

        return output


    def surface_species_names(self):
        """
        Return the surface species names from the 'general_output.txt' file.
        """
        output = []

        lines = self.grep_file(self._filenames['general'], pattern='Surface species names:')

        if( len(lines) != 0 ):
            return lines[0][ lines[0].find('Surface species names:')+len("Surface species names:"): ].split()

        if( self.job.restart is not None ):
            output.extend( self.job.restart.results.surface_species_names() )

        return output

    def site_type_names(self):
        """
        Return the site types from the 'general_output.txt' file.
        """
        zversion = self.get_zacros_version()

        if( zversion >= 2.0 and zversion < 3.0 ):
            lines = self.get_file_chunk(self._filenames['general'], begin="Site type names and number of sites of that type:",
                                            end='Maximum coordination number:')
        elif( zversion >= 3.0 ):
            lines = self.get_file_chunk(self._filenames['general'], begin="Site type names and total number of sites of that type:",
                                            end='Maximum coordination number:')
        else:
            raise Exception( "Error: Zacros version "+str(zversion)+" not supported!" )

        site_types = []
        for line in lines:
            if( not line.strip() ): continue
            site_types.append( line.split()[0] )

        return site_types


    def number_of_snapshots(self):
        """
        Return the number of configurations from the 'history_output.txt' file.
        """
        lines = self.grep_file(self._filenames['history'], pattern='configuration')
        nconf = len(lines)

        if( self.job.restart is not None ):
            nconf = self.job.restart.results.number_of_snapshots() + nconf

        return nconf


    def number_of_process_statistics(self):
        """
        Return the number of process statistics from the 'procstat_output.txt' file.
        """
        lines = self.grep_file(self._filenames['procstat'], pattern='configuration')
        nconf = len(lines)

        if( self.job.restart is not None ):
            nconf = self.job.restart.results.number_of_process_statistics() + nconf

        return nconf


    def elementary_steps_names(self):
        """
        Return the names of elementary steps from the 'procstat_output.txt' file.
        """
        if( self.job.restart is None ):
            lines = self.grep_file(self._filenames['procstat'], pattern='Overall')
            names = lines[0][ lines[0].find('Overall')+len("Overall"): ].split()
        else:
            names = self.job.restart.results.elementary_steps_names()

        return names


    def lattice_states(self, last=None):
        """
        Return the configurations from the 'history_output.txt' file.
        """
        output = []

        number_of_lattice_sites = self.number_of_lattice_sites()
        gas_species_names = self.gas_species_names()
        surface_species_names = self.surface_species_names()

        total_number_of_snapshots = self.number_of_snapshots()

        prev_total_number_of_snapshots = 0
        number_of_snapshots_to_load = total_number_of_snapshots

        llast = number_of_snapshots_to_load
        if( last is not None ): llast = last

        if( self.job.restart is not None ):
            prev_total_number_of_snapshots = self.job.restart.results.number_of_snapshots()
            number_of_snapshots_to_load = total_number_of_snapshots-prev_total_number_of_snapshots

        if( number_of_snapshots_to_load-llast < 0 ):
            if( self.job.restart is not None ):
                output = self.job.restart.results.lattice_states( last=abs(number_of_snapshots_to_load-llast) )
            else:
                raise Exception("\n### ERROR ### Trying to load more snapshots ("+str(llast)+") than available ("+str(total_number_of_snapshots)+")")

        surface_species = len(surface_species_names)*[None]
        for i,sname in enumerate(surface_species_names):
            for sp in self.job.mechanism.surface_species():
                if( sname == sp.symbol ):
                    surface_species[i] = sp

            if( surface_species[i] is None ):
                for sp in self.job.cluster_expansion.surface_species():
                    if( sname == sp.symbol ):
                        surface_species[i] = sp
        surface_species = SpeciesList( surface_species )

        lines = self.grep_file(self._filenames['history'], pattern='configuration', options="-A"+str(number_of_lattice_sites))
        lines = [line for line in lines if line != "--"]
        for nconf in range(max(0,number_of_snapshots_to_load-llast),number_of_snapshots_to_load):
            start = nconf*(number_of_lattice_sites+1)
            end = (nconf+1)*(number_of_lattice_sites+1)
            conf_lines = lines[start:end]

            lattice_state = None
            lattice_state_buffer = {} # key=adsorbate_number
            for nline,line in enumerate(conf_lines):
                tokens = line.split()

                if( nline==0 ):
                    assert tokens[0] == "configuration"

                    configuration_number = int(tokens[1])
                    number_of_events = int(tokens[2])
                    time = float(tokens[3])
                    temperature = float(tokens[4])
                    energy = float(tokens[5])

                    add_info = {"number_of_events":number_of_events, "time":time,
                                "temperature":temperature, "energy":energy}
                    lattice_state = LatticeState( self.job.lattice, surface_species, add_info=add_info )
                else:
                    site_number = int(tokens[0])-1 # Zacros uses arrays indexed from 1
                    adsorbate_number = int(tokens[1])
                    species_number = int(tokens[2])-1 # Zacros uses arrays indexed from 1
                    dentation = int(tokens[3])

                    if( species_number > -1 ): # In pyzacros -1 means empty site (0 for Zacros)
                        if( adsorbate_number not in lattice_state_buffer ):
                            lattice_state_buffer[adsorbate_number] = [ [site_number], species_number, dentation ]
                        else:
                            lattice_state_buffer[adsorbate_number][0].append( site_number )
                            if( dentation > lattice_state_buffer[adsorbate_number][2] ):
                                lattice_state_buffer[adsorbate_number][2] = dentation

            for key,item in lattice_state_buffer.items():
                if( len(item[0]) != item[2] ):
                    msg  = "Format error reading lattice state. Species' dentation is not compatible with the number of associated binding sites.\n"
                    msg += ">> adsorbate_number="+str(key)+", site_number="+str(site_number)+"\n"
                    msg += ">> species="+str(surface_species[item[1]])+", dentation="+str(dentation)+"\n"
                    raise Exception( msg )
                lattice_state.fill_site( item[0], surface_species[item[1]], update_species_numbers=False )

            if( lattice_state is not None ):
                lattice_state._updateSpeciesNumbers()

            output.append( lattice_state )

        return output


    def last_lattice_state(self):
        """
        Return the last configuration from the 'history_output.txt' file.
        """
        return self.lattice_states(last=1)[0]


    def average_coverage(self, last=5):
        """
        Returns a dictionary with the average coverage fractions using the last ``last`` lattice states, e.g., ``{ "CO*":0.32, "O*":0.45 }``
        """

        surface_species_names = self.surface_species_names()

        acf = {}
        for sspecies in surface_species_names:
            acf[sspecies] = 0.0

        #for lattice_state in self.lattice_states(last=last):
            #fractions = lattice_state.coverage_fractions()

            #for sspecies in surface_species_names:
                #acf[sspecies] += fractions[sspecies]/last

        provided_quantities = self.provided_quantities()
        n_items = len(provided_quantities['Entry'])
        nmol_total = n_items*[0]

        for i in reversed(range(n_items)):
            if i==n_items-last-1: break

            for sspecies in surface_species_names:
                acf[sspecies] += provided_quantities[sspecies][i]

        for sspecies in surface_species_names:
            acf[sspecies] /= self.job.lattice.number_of_sites()*last

        return acf


    def plot_lattice_states(self, data, pause=-1, show=True, ax=None, close=False, time_perframe=0.5, file_name=None):
        """
        Uses matplotlib to visualize the lattice states as an animation

        *   ``data`` -- List of LatticeState objects to plot
        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``time_perframe`` -- Sets the time interval between frames in seconds.
        *   ``file_name`` -- Saves the figures to the file ``file_name-<id>`` (the corresponding id on the list replaces the ``<id>``). The format is inferred from the extension, and by default, ``.png`` is used.

        """
        if( type(data) == LatticeState ):
            data.plot( show=show, pause=pause, ax=ax, close=close, file_name=file_name )
        if( type(data) == list ):
            try:
                import matplotlib.pyplot as plt
            except ImportError as e:
                return # module doesn't exist, deal with it.

            if( ax is None ):
                fig,ax = plt.subplots()

            plt.rcParams["figure.autolayout"] = True
            for i,ls in enumerate(data):
                ifile_name = None
                if( file_name is not None ):
                    prefix,ext = os.path.splitext(file_name)
                    ifile_name = prefix+"-"+"%05d"%i+ext

                ax.cla()
                ls.plot( show=show, pause=time_perframe, ax=ax, close=False, file_name=ifile_name )

            if( show ):
                if( pause == -1 ):
                    plt.show()
                else:
                    plt.pause( pause )

            if( close ):
                plt.close("all")


    def plot_molecule_numbers(self, species_name, pause=-1, show=True, ax=None, close=False,
                                file_name=None, normalize_per_site=False, derivative=False):
        """
        Uses matplotlib to visualize the Molecule Numbers an animation

        *   ``species_name`` -- List of species names to show, e.g., ``["CO*", "CO2"]``
        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing. This can be used for crude animation.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``file_name`` -- Saves the figure to the file ``file_name``. The format is inferred from the extension, and by default, ``.png`` is used.
        *   ``normalize_per_site`` -- Divides the molecule numbers by the total number of sites in the lattice.
        *   ``derivative`` -- Plots the first derivative.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            return # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        plt.rcParams["figure.autolayout"] = True
        provided_quantities = self.provided_quantities()

        COLORS = ['r', 'g', 'b', 'm']

        ax.set_xlabel('t (s)')

        if( normalize_per_site ):
            if( derivative ):
                ax.set_ylabel('Derivative of the Molecule Numbers per Site')
            else:
                ax.set_ylabel('Molecule Numbers per Site')
        else:
            if( derivative ):
                ax.set_ylabel('Derivative of the Molecule Numbers')
            else:
                ax.set_ylabel('Molecule Numbers')

        x = provided_quantities["Time"]
        for i,spn in enumerate(species_name):
            if( normalize_per_site ):
                y = numpy.array(provided_quantities[spn])/self.number_of_lattice_sites()
            else:
                y = numpy.array(provided_quantities[spn])

            if( derivative ):
                y = numpy.gradient(y, x)

            ax.step( x, y, where='post', color=COLORS[i], label=spn)

        ax.legend(loc='best')

        if( file_name is not None ):
            plt.savefig( file_name )

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

        if( close ):
            plt.close("all")


    def get_process_statistics(self):
        """
        Return the statistics from the 'procstat_output.txt' file in a form of a list of dictionaries.
        Below is shown an example of the ``procstat_output.txt`` for a zacros calculation.

        .. code-block:: none

                Overall        CO_ads  O2_react_ads        CO_oxi
          configuration     1             0          0.00
                  0.000         0.000         0.000         0.000
                      0             0             0             0
          configuration     2           250          0.01
                  0.039         0.043         0.044         0.000
                    250           108           118            24

        For this example, this function will return:

        .. code-block:: python

            [
              {
                'configuration_number': 1,
                'total_number_of_events': 0,
                'time': 0.0,
                'average_waiting_time': {
                                          'CO_ads': 0.0,
                                          'O2_react_ads': 0.0,
                                          'CO_oxi': 0.0
                                        },
                'number_of_events': {
                                      'CO_ads': 0,
                                      'O2_react_ads': 0,
                                      'CO_oxi': 0
                                    },
                'occurence_frequency': {
                                         'CO_ads': 0.0,
                                         'O2_react_ads': 0.0,
                                         'CO_oxi': 0.0
                                       }
              },
              {
                'configuration_number': 2,
                'total_number_of_events': 250,
                'time': 0.01,
                'average_waiting_time': {
                                          'CO_ads': 0.043
                                          'O2_react_ads': 0.044
                                          'CO_oxi': 0.0
                                        },
                'number_of_events': {
                                      'CO_ads': 108,
                                      'O2_react_ads': 118,
                                      'CO_oxi': 24
                                    },
                'occurence_frequency': {
                                         'CO_ads': 10800.0,
                                         'O2_react_ads': 11800.0,
                                         'CO_oxi': 2400.0
                                       }
              }
            ]

        The ``occurence_frequency`` is calculated as ``number_of_events``/``time``.
        """
        output = []

        prev_number_of_process_statistics = 0
        number_of_process_statistics = self.number_of_process_statistics()

        if( self.job.restart is None ):
            lines = self.grep_file(self._filenames['procstat'], pattern='Overall')
            elementary_steps_names = lines[0][ lines[0].find('Overall')+len("Overall"): ].split()
        else:
            prev_number_of_process_statistics = self.job.restart.results.number_of_process_statistics()
            elementary_steps_names = self.job.restart.results.elementary_steps_names()
            output = self.job.restart.results.get_process_statistics()

        all_lines = self.grep_file(self._filenames['procstat'], pattern='configuration', options="-A2")
        all_lines = [line for line in all_lines if line != "--"]
        for nconf in range(number_of_process_statistics-prev_number_of_process_statistics):
            lines = all_lines[nconf*3:(nconf+1)*3]

            procstat_state = {}
            pos = 0
            for nline,line in enumerate(lines):
                tokens = line.split()

                if( nline==0 ):
                    assert tokens[0] == "configuration"

                    configuration_number = int(tokens[1])
                    total_number_of_events = int(tokens[2])
                    time = float(tokens[3])

                    procstat_state["configuration_number"] = configuration_number
                    procstat_state["total_number_of_events"] = total_number_of_events
                    procstat_state["time"] = time

                elif( nline==1 ):
                    assert len(tokens)-1 == len(elementary_steps_names)

                    average_waiting_time = {}
                    for i,k in enumerate(elementary_steps_names):
                        average_waiting_time[k] = float(tokens[i+1])

                    procstat_state["average_waiting_time"] = average_waiting_time

                elif( nline==2 ):
                    assert len(tokens)-1 == len(elementary_steps_names)

                    number_of_events = {}
                    occurence_frequency = {}
                    for i,k in enumerate(elementary_steps_names):
                        number_of_events[k] = int(tokens[i+1])

                        if( procstat_state["time"] > 0.0 ):
                            occurence_frequency[k] = number_of_events[k]/procstat_state["time"]
                        else:
                            occurence_frequency[k] = 0.0

                    procstat_state["number_of_events"] = number_of_events
                    procstat_state["occurence_frequency"] = occurence_frequency

                else:
                    raise Exception( "Error: Wrong format in file specnum_output.txt" )

                pos += 1

            output.append( procstat_state )


        return output


    def __plot_process_statistics(self, data, key, log_scale=False, pause=-1, show=True, ax=None, close=False, xmax=None, file_name=None):
        """
        Plots data as a histogram
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            return # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        plt.rcParams["figure.autolayout"] = True

        provided_quantities = self.provided_quantities()

        ax.set_title('t $\in$ [0.0,{:.3g}] s'.format(data["time"]))
        ax.set_xlabel(key)

        keys = list(data[key].keys())
        idkeys_sorted = sorted(enumerate(keys), key=lambda x: x[1])

        keys = [ k for i,k in idkeys_sorted ]
        data_sorted = [ list(data[key].values())[i] for i,k in idkeys_sorted ]

        y_pos = len(keys)*[None]
        j = 0
        for i in range(len(keys)):
            if( i==0 ):
                y_pos[i] = j
            else:
                if( keys[i].replace('_fwd','').replace('_rev','') != keys[i-1].replace('_fwd','').replace('_rev','') ):
                    j += 1

                y_pos[i] = j

        COLORS = ['r', 'b', 'g', 'm']
        color = len(y_pos)*[COLORS[0]]

        j = 0
        for i in range(1,len(y_pos)):
            if( y_pos[i] == y_pos[i-1] ):
                y_pos[i] += 0.15
                y_pos[i-1] -= 0.15
                color[i] = COLORS[j]
                color[i-1] = COLORS[j+1]

        ax.barh(y_pos, data_sorted, align='center', height=0.25, color=color)

        maxval = max(data_sorted)
        if( xmax is not None ):
            maxval = xmax

        if( log_scale ):
            ax.set_xlim((1e0,1.2*maxval))
            plt.xscale("log")
        else:
            ax.set_xlim((0,1.05*maxval))

        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_yticks(y_pos)
        ax.set_yticklabels(keys)
        plt.tight_layout()

        if( file_name is not None ):
            plt.savefig( file_name )

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

        if( close ):
            plt.close("all")


    def plot_process_statistics(self, data, key, log_scale=False, pause=-1, show=True, ax=None, close=False, file_name=None):
        """
        Uses matplotlib to visualize the process statistics an animation

        *   ``data`` -- List of process statistics to plot. See function :func:`~scm.pyzacros.ZacrosResults.get_process_statistics`.
        *   ``key`` -- Key to plot, e.g., ``'average_waiting_time'``, ``'average_waiting_time'``. See function :func:`~scm.pyzacros.ZacrosResults.get_process_statistics`.
        *   ``log_scale`` -- Use log scale for the x axis.
        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``file_name`` -- Saves the figures to the file ``file_name-<id>`` (the corresponding id on the list replaces the ``<id>``). The format is inferred from the extension, and by default, ``.png`` is used.

        """
        if( type(data) == dict ):
            self.__plot_process_statistics( data, key, log_scale=log_scale, pause=pause, show=show,
                                            close=close, file_name=file_name )
        if( type(data) == list ):
            try:
                import matplotlib.pyplot as plt
            except ImportError as e:
                return # module doesn't exist, deal with it.

            if( ax is None ):
                fig,ax = plt.subplots()

            maxval = -1e8
            for idata in data:
                if( max(idata[key].values()) > maxval ):
                    maxval = max(idata[key].values())

            for i,idata in enumerate(data):
                ifile_name = None
                if( file_name is not None ):
                    prefix,ext = os.path.splitext(file_name)
                    ifile_name = prefix+"-"+"%05d"%i+ext

                ax.cla()
                self.__plot_process_statistics( idata, key, log_scale=log_scale, pause=0.5, show=show, ax=ax,
                                                close=False, xmax=maxval, file_name=ifile_name )

            if( show ):
                if( pause == -1 ):
                    plt.show()
                else:
                    plt.pause( pause )

            if( close ):
                plt.close("all")


    #--------------------------------------------------------------
    # Function to compute the rate of production using the
    # Batch-Means-Stopping method.
    # Original author: Mauro Bracconi (mauro.bracconi@polimi.it)
    # Evaluation of the steady state is inspired by this publication:
    #   Hashemi et al., J.Chem. Phys. 144, 074104 (2016)
    #--------------------------------------------------------------
    @staticmethod
    def __compute_rate( t_vect, spec, n_sites, n_batch=20, confidence=0.99 ):

        # Batch means stopping implementation
        t_vect = numpy.array(t_vect)
        prod_mol = numpy.array(spec)/n_sites

        # Define batch length
        lt = int(len(t_vect)/n_batch)
        n_batch = min( len(t_vect), lt )

        # Compute TOF in each batch
        ratet = numpy.empty(n_batch)
        for i in range(n_batch):
            if ( i != n_batch-1 ) :
                ratet[i] = numpy.polyfit(t_vect[lt*i:lt*(i+1)],prod_mol[lt*i:lt*(i+1)],1)[0]
            else:
                ratet[i] = numpy.polyfit(t_vect[lt*i:-1],prod_mol[lt*i:-1],1)[0]

        # Exclude first batch
        rate = ratet[1:]

        # Compute average and CI
        rate_av, se = numpy.mean(rate), scipy.stats.sem(rate)
        rate_CI = se * scipy.stats.t._ppf( (1.0+confidence)/2.0, len(rate) - 1.0 )
        ratio = numpy.abs(rate_CI)/(numpy.abs(rate_av)+1e-8)

        if ( ratio<1.0-confidence ):
            return ( rate_av,rate_CI,ratio, True )
        else:
            #return ( rate_av,rate_CI,ratio, False )
            return ( rate[-1],rate_CI,ratio, False )


    def turnover_frequency(self, nbatch=20, confidence=0.99, species_name=None, provided_quantities=None):
        """
        Returns the TOF (mol/sec/site) calculated by the batch-means stopping method. See Hashemi et al., J.Chem. Phys. 144, 074104 (2016)

        *   ``nbatch`` -- Number of batches to use.
        *   ``confidence`` -- Confidence level to use in the criterion to determine if the steady-state was reached.

        The simulation output is divided into an ensemble of contiguous batches where the TOF is computed.
        The average value and the standard deviation of the TOF ensemble are evaluated as follows:

        .. math::

           <TOF> = \\frac{1}{n}\\sum_{i=1}^n TOF_i  \\qquad  \\sigma_{TOF}\\sqrt{\\frac{1}{n-1}\\sum_{i=1}^n\\left(TOF_i-<TOF>\\right)}

        where :math:`n = \\text{nbatch}`. Confidence intervals are estimated to assess the steady-state behavior of the simulation:

        .. math::

           <TOF>\\pm t_{n-1,1-\\frac{\\delta}{2}}\\frac{\\sigma_{TOF}}{\\sqrt{n}}

        The function returns True when the steady-state is reached. This happens if the following equation is satisfied:

        .. math::

           t_{n-1,1-\\frac{\\delta}{2}}\\frac{\\sigma_{TOF}}{\\sqrt{n}} \lt \epsilon

        Here the convergence criteria is :math:`\epsilon=1-\\text{confidence}`

        """
        values = {}
        errors = {}
        ratios = {}
        converged = {}

        lprovided_quantities = provided_quantities
        if provided_quantities is None:
            lprovided_quantities = self.provided_quantities()

        for sn in self.gas_species_names():

            nMolsVec = lprovided_quantities[sn]

            if sum(numpy.abs(lprovided_quantities[sn])) > 0:
                aver,ci,ratio,conv = ZacrosResults.__compute_rate( lprovided_quantities["Time"], lprovided_quantities[sn],
                                                                    self.number_of_lattice_sites(), nbatch, confidence )
                values[sn] = aver
                errors[sn] = ci
                ratios[sn] = ratio
                converged[sn] = conv
            else:
                values[sn] = 0.0
                errors[sn] = 0.0
                ratios[sn] = 0.0
                converged[sn] = True

        if species_name is None:
            return values,errors,ratios,converged
        else:
            return values[species_name],errors[species_name],ratios[species_name],converged[species_name]


    @staticmethod
    def _average_provided_quantities( provided_quantities_list, key_column_name, columns_name=None ):

        if len(provided_quantities_list) == 0:
            msg  = "### ERROR ### ZacrosResults._average_provided_quantities\n"
            msg += ">> provided_quantities_list parameter should eb a list with at least one item\n"
            raise Exception( msg )

        nexp = len(provided_quantities_list)
        npoints = len(provided_quantities_list[0][key_column_name])

        if columns_name is None:
            columns_name = provided_quantities_list[0].keys()

        for provided_quantities in provided_quantities_list:
            for name in columns_name:
                if len(provided_quantities[name]) != npoints:
                    msg  = "### ERROR ### ZacrosResults._average_provided_quantities\n"
                    msg += ">> provided_quantities_list contains items with different sizes\n"
                    raise Exception( msg )

        average = {}

        average[key_column_name] = npoints*[0.0]
        for name in columns_name:
            average[name] = npoints*[0.0]

        for i in range(npoints):
            average[key_column_name][i] = provided_quantities_list[0][key_column_name][i]

            for k in range(nexp):
                if k>0 and provided_quantities_list[k][key_column_name][i] != provided_quantities_list[0][key_column_name][i]:
                    msg  = "### ERROR ### ZacrosResults._average_provided_quantities\n"
                    msg += ">> Reference column has different values for each item\n"
                    raise Exception( msg )

            for name in columns_name:
                if name == key_column_name: continue
                for k in range(nexp):
                    average[name][i] += provided_quantities_list[k][name][i]
                average[name][i] /= float(nexp)

        return average

