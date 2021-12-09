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


    def ok(self):
        """Check if the execution of the associated :attr:`job` was successful or not.
        See :meth:`Job.ok<scm.plams.core.basejob.Job.ok>` for more information."""
        return self.job.ok()


    def get_zacros_version(self):
        """
        Return the zacros's version from the 'general_output.txt' file.
        """
        if( self.job.restart is None ):
            lines = self.grep_file(self._filenames['general'], pattern='ZACROS')
            zversion = lines[0].split()[2]
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

                5       292   4.000E-01   5.00000E+02   -1.156E+02   39   20    -68   -116   108
                6       353   5.000E-01   5.00000E+02   -1.235E+02   43   19    -82   -139   132
                7       394   5.999E-01   5.00000E+02   -1.116E+02   35   24    -86   -160   148
                8       462   6.999E-01   5.00000E+02   -1.253E+02   37   31    -99   -191   172
                9       547   7.999E-01   5.00000E+02   -1.155E+02   35   27   -116   -223   208

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
                raise Exception("### ERROR ### Trying to load more snapshots ("+str(llast)+") than available ("+str(total_number_of_snapshots)+")")

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

        for nconf in range(max(0,number_of_snapshots_to_load-llast),number_of_snapshots_to_load):
            lines = self.grep_file(self._filenames['history'], pattern='configuration', options="-A"+str(number_of_lattice_sites)+" -m"+str(nconf+1))
            lines = lines[-number_of_lattice_sites-1:] # Equivalent to tail -n $number_of_lattice_sites+1

            lattice_state = None
            for nline,line in enumerate(lines):
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
                        lattice_state.fill_site( site_number, surface_species[species_number], update_species_numbers=False )

            if( lattice_state is not None ):
                lattice_state._updateSpeciesNumbers()

            output.append( lattice_state )

        return output


    def last_lattice_state(self):
        """
        Return the last configuration from the 'history_output.txt' file.
        """
        return self.lattice_states(last=1)[0]


    def plot_lattice_states(self, data, pause=-1, show=True, ax=None, close=False, time_perframe=0.5, file_name=None):
        """
        Uses matplotlib to visualize the lattice states as an animation

        *   ``data`` --
        *   ``pause`` --
        *   ``show`` --
        *   ``ax`` --
        *   ``close`` --
        *   ``time_perframe`` --
        *   ``file_name`` --
        """
        if( type(data) == LatticeState ):
            data.plot( show=True, pause=pause, ax=ax, file_name=file_name )
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
                ls.plot( show=True, pause=time_perframe, ax=ax, file_name=ifile_name )

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

        *   ``species_name`` --
        *   ``pause`` --
        *   ``show`` --
        *   ``ax`` --
        *   ``close`` --
        *   ``file_name`` --
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
                ax.set_ylabel('Molecule Numbers per Site')

        for i,spn in enumerate(species_name):
            if( normalize_per_site ):
                data = numpy.array(provided_quantities[spn])/self.number_of_lattice_sites()
            else:
                data = numpy.array(provided_quantities[spn])

            if( derivative ):
                data = numpy.gradient(data)

            ax.step( provided_quantities["Time"], data, where='post', color=COLORS[i], label=spn)

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
        Return the statistics from the 'specnum_output.txt' file.
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
                    raise( "Error: Wrong format in file specnum_output.txt" )

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

        ax.set_title('t $\in$ [0.000,{:.3f}] s'.format(data["time"]))
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

        *   ``data`` --
        *   ``key`` --
        *   ``log_scale`` --
        *   ``pause`` --
        *   ``show`` --
        *   ``ax`` --
        *   ``close`` --
        *   ``file_name`` --
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
    # Function to compute the rate of production
    # Original author: Mauro Bracconi (mauro.bracconi@polimi.it)
    # Evaluation of the steady state is inspired by this publication:
    #   Hashemi et al., J.Chem. Phys. 144, 074104 (2016)
    #--------------------------------------------------------------
    @staticmethod
    def __compute_rate( t_vect, spec, n_sites, n_batch=20, confidence=0.99 ):

        def time_search(t,tvec):
            ind_geq = 0
            while tvec[ind_geq] < t:
                ind_geq += 1

            ind_leq = len( tvec ) - 1
            while ind_leq>0 and tvec[ind_leq] > t:
                ind_leq -= 1
            low_frac = 1.0
            if not (ind_geq == ind_leq):
                low_frac = (tvec[ind_geq] - t) / (tvec[ind_geq] - tvec[ind_leq])
            return [ (ind_leq,ind_geq), (low_frac,1-low_frac)]

        t_vect = numpy.array(t_vect)
        prod_mol = numpy.array(spec)/n_sites

        n_batch = min( len(t_vect), int(len(t_vect)/n_batch) )
        dt_batch = t_vect[-1]/n_batch
        bin_edge = numpy.linspace(0,t_vect[-1],n_batch+1)

        rate = numpy.zeros( n_batch )

        for i in range(n_batch):
            idb_s = time_search( bin_edge[i], t_vect )
            idb_e = time_search( bin_edge[i+1], t_vect )

            pp_s = idb_s[1][0] * prod_mol[idb_s[0][0]] + idb_s[1][1] * prod_mol[idb_s[0][1]]
            pp_e = idb_e[1][0] * prod_mol[idb_e[0][0]] + idb_e[1][1] * prod_mol[idb_e[0][1]]
            rate[i] = (pp_e-pp_s)/dt_batch

        rate = rate[1:]
        rate_av, se = numpy.mean(rate), scipy.stats.sem(rate)

        rate_CI = se * scipy.stats.t._ppf((1+confidence)/2.0, n_batch - 1)

        if ( rate_CI/(rate_av+1e-8)<1.0-confidence ):
            return ( rate_av,rate_CI,rate_CI/(rate_av+1e-8), True )
        else:
            return ( rate_av,rate_CI,rate_CI/(rate_av+1e-8), False )


    def get_TOFs(self, nbatch=20, confidence=0.99):
        """
        Returns the TOF (mol/sec/site) calculated by the batch method

        *   ``nbatch`` --
        *   ``confidence`` --
        """
        values = {}
        errors = {}
        converged = {}

        provided_quantities = self.provided_quantities()

        for sn in self.gas_species_names():

            nMolsVec = provided_quantities[sn]

            aver,ci,ratio,conv = ZacrosResults.__compute_rate( provided_quantities["Time"], provided_quantities[sn],
                                                                self.number_of_lattice_sites(), nbatch, confidence )
            values[sn] = aver
            errors[sn] = ci
            converged[sn] = conv

        return values,errors,converged
