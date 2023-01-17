"""Module containing the ZacrosSteadyStateJob class."""

import os
import shutil
import copy
import numpy
from collections import OrderedDict

import scm.plams

from .Settings import *
from .ZacrosJob import *
from .ZacrosResults import *
from .ParametersBase import *

__all__ = ['ZacrosSteadyStateJob', 'ZacrosSteadyStateResults']


class ZacrosSteadyStateResults( scm.plams.Results ):
    """
    A Class for handling ZacrosSteadyStateJob Results.
    """

    def history(self, pos=None):
        """
        Returns a list of properties related with the history of the calculation.
        Each element of the history includes the maximum amount of time
        (referred to as ``max_steps``, ``max_time``, or ``wall_time``) used in that iteration
        as well as three numbers related to the turnover frequency calculation: the value itself
        (referred to as ``turnover frequency``), its error (referred to as ``turnover frequency error``),
        and a flag (referred to as ``turnover frequency converged``) that denotes whether or not the calculation has converged.

        Example of an item of the returned history list:

        .. code-block:: python

           {'turnover_frequency': {'CO': -0.75409, 'O2': -0.39222, 'CO2': 0.75498},
            'turnover_frequency_error': {'CO': 0.11055, 'O2': 0.06458, 'CO2': 0.11099},
            'converged': {'CO': False, 'O2': False, 'CO2': False},
            'max_time': 20.0}
        """
        if pos is not None:
            return self.job._history[pos]
        else:
            return self.job._history


    def niterations(self):
        """
        Returns the current number of iterations executed
        """
        return self.job.niterations


    def nreplicas(self):
        """
        Returns the number of replicas used
        """
        return self.job.nreplicas


    def children_results(self, iteration=None, replica=None):
        """
        Returns a list of the children's results or the results for a specific iteration or replica if requested.
        """
        if iteration is None and replica is None:
            output = []

            for i in range(len(self.job.children)):
                output.append( self.job.children[i].results )

            return output
        elif iteration is not None and replica is None:
            output = []

            for j in range(len(self.job.nreplicas)):
                output.append( self.job.children[iteration*self.job.nreplicas+j].results )

            return output
        elif iteration is not None and replica is not None:
            return self.job.children[iteration*self.job.nreplicas+replica].results
        else:
            msg  = "\n### ERROR ### ZacrosSteadyStateResults.children_results().\n"
            msg += "                Wrong parameters combination.\n"
            raise Exception(msg)


    def get_zacros_version(self):
        """
        Returns the zacros's version from the 'general_output.txt' file.
        """
        return self.job.children[-1].results.get_zacros_version()


    def get_reaction_network(self):
        """
        Returns the reactions from the 'general_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.get_reaction_network()


    def provided_quantities(self):
        """
        Returns the provided quantities headers from the ``specnum_output.txt`` file in a list associated to the last children.
        """
        return self.job.children[-1].results.provided_quantities()


    def number_of_lattice_sites(self):
        """
        Returns the number of lattice sites from the 'general_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.number_of_lattice_sites()


    def gas_species_names(self):
        """
        Returns the gas species names from the 'general_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.gas_species_names()


    def surface_species_names(self):
        """
        Returns the surface species names from the 'general_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.surface_species_names()


    def site_type_names(self):
        """
        Returns the site types from the 'general_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.site_type_names()


    def number_of_snapshots(self):
        """
        Returns the number of configurations from the 'history_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.number_of_snapshots()


    def number_of_process_statistics(self):
        """
        Returns the number of process statistics from the 'procstat_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.number_of_process_statistics()


    def elementary_steps_names(self):
        """
        Returns the names of elementary steps from the 'procstat_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.elementary_steps_names()


    def lattice_states(self, last=None):
        """
        Returns the configurations from the 'history_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.lattice_states(last=last)


    def last_lattice_state(self):
        """
        Returns the last configuration from the 'history_output.txt' file associated to the last children.
        """
        return self.job.children[-1].results.last_lattice_state()


    def average_coverage(self, last=5):
        """
        Returns a dictionary with the average coverage fractions using the last ``last`` lattice states, e.g., ``{ "CO*":0.32, "O*":0.45 }``.
        It makes an average on the number of replicas if they were requested.
        """

        acf = {}

        for i in range(self.job.nreplicas):
            prev = self.job.children[i-self.job.nreplicas]

            lacf = prev.results.average_coverage(last=last)

            for k,v in lacf.items():
                if k not in acf:
                    acf[k] = v/self.job.nreplicas
                else:
                    acf[k] += v/self.job.nreplicas

        return acf


    def plot_lattice_states(self, data, pause=-1, show=True, ax=None, close=False, time_perframe=0.5, file_name=None):
        """
        Uses Matplotlib to create an animation of the lattice states associated to the last children.

        *   ``data`` -- List of LatticeState objects to plot
        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``time_perframe`` -- Sets the time interval between frames in seconds.
        *   ``file_name`` -- Saves the figures to the file ``file_name-<id>`` (the corresponding id on the list replaces the ``<id>``). The format is inferred from the extension, and by default, ``.png`` is used.
        """
        self.job.children[-1].results.plot_lattice_states(data=data, pause=pause, show=show, ax=ax, close=close,
                                                    time_perframe=time_perframe, file_name=file_name)


    def plot_molecule_numbers(self, species_name, pause=-1, show=True, ax=None, close=False,
                                file_name=None, normalize_per_site=False, derivative=False):
        """
        uses Matplotlib to create an animation of the Molecule Numbers associated to the last children.

        *   ``species_name`` -- List of species names to show, e.g., ``["CO*", "CO2"]``
        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing. This can be used for crude animation.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``file_name`` -- Saves the figure to the file ``file_name``. The format is inferred from the extension, and by default, ``.png`` is used.
        *   ``normalize_per_site`` -- Divides the molecule numbers by the total number of sites in the lattice.
        *   ``derivative`` -- Plots the first derivative.
        """
        self.job.children[-1].results.plot_molecule_numbers(species_name=species_name, pause=pause, show=show, ax=ax, close=close,
                                                        file_name=file_name, normalize_per_site=normalize_per_site, derivative=derivative)


    def get_process_statistics(self):
        """
        Returns the statistics from the 'procstat_output.txt' file in a form of a list of dictionaries associated to the last children.
        """
        return self.job.children[-1].results.get_process_statistics()


    def plot_process_statistics(self, data, key, log_scale=False, pause=-1, show=True, ax=None, close=False, file_name=None):
        """
        Uses Matplotlib to create an animation of the process statistics associated to the last children.

        *   ``data`` -- List of process statistics to plot. See function :func:`~scm.pyzacros.ZacrosResults.get_process_statistics`.
        *   ``key`` -- Key to plot, e.g., ``'average_waiting_time'``, ``'average_waiting_time'``. See function :func:`~scm.pyzacros.ZacrosResults.get_process_statistics`.
        *   ``log_scale`` -- Use log scale for the x axis.
        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``file_name`` -- Saves the figures to the file ``file_name-<id>`` (the corresponding id on the list replaces the ``<id>``). The format is inferred from the extension, and by default, ``.png`` is used.
        """
        self.job.children[-1].results.plot_process_statistics(data=data, key=key, log_scale=log_scale, pause=pause, show=show, ax=ax,
                                                        close=close, file_name=file_name)


    def turnover_frequency(self, nbatch=None, confidence=None, ignore_nbatch=None, species_name=None):

        if nbatch is None: nbatch = self.job.nbatch
        if confidence is None: confidence = self.job.confidence
        if ignore_nbatch is None: ignore_nbatch = self.job.ignore_nbatch

        provided_quantities_list = []

        for i in range(self.job.nreplicas):
            prev = self.job.children[i-self.job.nreplicas]
            provided_quantities_list.append( prev.results.provided_quantities() )

        aver_provided_quantities = ZacrosResults._average_provided_quantities( provided_quantities_list, 'Time' )

        # This case happens only when the surface gets quickly poisoned; in one iteration.
        # In that case we use only the last values to estimate the TOF
        if self.job._surface_poisoned and self.job.niterations == 1:
            ignore_nbatch = nbatch-2

        TOF,error,ratio,conv = prev.results.turnover_frequency( nbatch=nbatch, confidence=confidence,
                                                                ignore_nbatch=ignore_nbatch,
                                                                provided_quantities=aver_provided_quantities )

        if species_name is None:
            return TOF,error,ratio,conv
        else:
            return TOF[species_name],error[species_name],ratio[species_name],conv[species_name]


class ZacrosSteadyStateJob( scm.plams.MultiJob ):
    """
    Create a new ZacrosSteadyStateJob object. ``ZacrosSteadyStateJob`` class represents a job that is a container for other jobs, called children jobs, which must be :ref:`ZacrosJobs <zacrosjob>` or :ref:`ZacrosSteadyStateJob <zacrossteadystatejob>` kind objects. This class is an extension of the PLAMS MultiJob class. So it inherits all its powerful features, e.g., being executed locally or submitted to some external queueing system transparently or executing jobs in parallel with a predefined dependency structure. See all configure possibilities on the PLAMS MultiJob class documentation in this link: `PLAMS.MultiJob <../../plams/components/jobs.html#multijobs>`_.

    The ``ZacrosSteadyStateJob`` class constructor requires a Settings object to set the parameters for the Steady-State calculation. The rest of the parameters related to the Zacros calculation ( e.g., lattice, mechanism, and the cluster expansion Hamiltonian ) are provided indirectly through a reference job ``reference`` from which the calculation ``Settings`` is taken to be replicated through its children. Children are initially copies of the reference job. However, just before they are run, their corresponding Settings are altered accordingly to the rules defined through a ``Parameters`` object provided in the constructor.

    The following are the available parameters to be modified in the ``Settings`` object.

    .. code-block:: python

       settings.turnover_frequency.nbatch = 20
       settings.turnover_frequency.confidence = 0.99
       settings.turnover_frequency.ignore_nbatch = 1

       settings.scaling.enabled = 'F'
       settings.scaling.partial_equilibrium_index_threshold = 0.1
       settings.scaling.upper_bound = 100
       settings.scaling.max_steps = None
       settings.scaling.max_time = None
       settings.scaling.species_numbers = None
       settings.scaling.nevents_per_timestep = None
    """

    _result_type = ZacrosSteadyStateResults


    class Parameter(ParameterBase):
        """
        Creates a new Parameter object specifically tailored for ZacrosSteadyStateJob
        """

        def __init__(self, name_in_settings, kind, values):
            super().__init__(self, name_in_settings, kind, values)


    class Parameters(ParametersBase):
        """
        Creates a new Parameters object specifically tailored for ZacrosSteadyStateJob
        """

        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)


    def __init__(self, reference, parameters, settings=Settings(), **kwargs):
        scm.plams.MultiJob.__init__(self, settings=settings, **kwargs)

        self._reference = reference

        size = None

        if parameters._generator.__name__ != "zipGenerator":
            msg  = "\n### ERROR ### ZacrosSteadyStateJob.__init__().\n"
            msg += "              The only generator allowed is the zipGenerator.\n"
            raise Exception(msg)

        for name,item in parameters.items():
            if size is None:
                size = len(item.values)
            elif size != len(item.values):
                msg  = "\n### ERROR ### ZacrosSteadyStateJob.__init__().\n"
                msg += "              All parameter in 'parameters' should be lists of the same size.\n"
                raise Exception(msg)

        if size == 0:
            msg  = "\n### ERROR ### ZacrosSteadyStateJob.__init__().\n"
            msg += "              All parameter in 'parameters' should be lists with at least one element.\n"
            raise Exception(msg)

        self._parameters = parameters

        if not isinstance(reference,ZacrosJob):
            msg  = "\n### ERROR ### ZacrosSteadyStateJob.__init__.\n"
            msg += "              Parameter 'reference' must be a ZacrosJob object.\n"
            raise Exception(msg)

        # We don't need the indices because we are sure that the generator is the zipGenerator
        _,self._parameters_values,self._parameters_settings = parameters._generator( reference.settings, parameters )

        self._scaling = False
        self._scaling_status = 'not_requested'
        self._scaling_factors = None

        self.max_iterations = len(parameters[list(parameters.keys())[0]].values)
        self.niterations = 0
        self._history = []
        self._surface_poisoned = False

        self.nbatch = 20
        self.confidence = 0.99
        self.ignore_nbatch = 1
        self.nreplicas = 1
        self.scaling_partial_equilibrium_index_threshold = 0.1
        self.scaling_upper_bound = 100
        self.scaling_max_steps = None
        self.scaling_max_time = None
        self.scaling_species_numbers = None
        self.scaling_nevents_per_timestep = None
        self._new_timestep = None

        self.nreplicas = self.settings.get('nreplicas', default=self.nreplicas)

        if 'turnover_frequency' in self.settings:
            self.nbatch = self.settings.turnover_frequency.get('nbatch', default=self.nbatch)
            self.confidence = self.settings.turnover_frequency.get('confidence', default=self.confidence)
            self.ignore_nbatch = self.settings.turnover_frequency.get('ignore_nbatch', default=self.ignore_nbatch)

        # Scaling pre-exponential terms parameters
        if 'scaling' in self.settings:
            self._scaling = self.settings.scaling.get('enabled', default=self._scaling)
            if type(self._scaling) == str \
                and ( self._scaling.upper() == 'T' or self._scaling.upper() == 'TRUE'
                    or self._scaling.upper() == 'Y' or self._scaling.upper() == 'Yes' ):
                        self._scaling_status = 'requested'
            if type(self._scaling) == bool and self._scaling :
                self._scaling_status = 'requested'

            self.scaling_partial_equilibrium_index_threshold = self.settings.scaling.get('partial_equilibrium_index_threshold', default=self.scaling_partial_equilibrium_index_threshold)
            self.scaling_upper_bound = self.settings.scaling.get('upper_bound', default=self.scaling_upper_bound)
            self.scaling_max_steps = self.settings.scaling.get('max_steps', default=self.scaling_max_steps)
            self.scaling_max_time = self.settings.scaling.get('max_time', default=self.scaling_max_time)
            self.scaling_species_numbers = self.settings.scaling.get('species_numbers', default=self.scaling_species_numbers)
            self.scaling_nevents_per_timestep = self.settings.scaling.get('nevents_per_timestep', default=self.scaling_nevents_per_timestep)

        scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: Using nbatch="+str(self.nbatch)+
                        ",confidence="+str(self.confidence)+",ignore_nbatch="+str(self.ignore_nbatch)+",nreplicas="+str(self.nreplicas))

        # These parameters a needed to make ZacrosSteadyStateJob compatible with ZacrosJob
        self.lattice = reference.lattice
        self.mechanism = reference.mechanism
        self.cluster_expansion = reference.cluster_expansion
        self.initial_state = reference.initial_state


    def __steady_state_step(self):

        if self.niterations >= self.max_iterations:
            scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: MAX ITERATIONS REACHED")
            return None

        if len(self.children) > 0:
            prev = None
            provided_quantities_list = []

            for i in range(self.nreplicas):
                prev = self.children[i-self.nreplicas]
                prev.ok()

            # This case happens only when the surface gets quickly poisoned; in less than one iteration.
            # In that case we use only the last values to estimate the TOF
            ignore_nbatch = self.ignore_nbatch

            for i in range(self.nreplicas):
                prev = self.children[i-self.nreplicas]

                if not prev.ok():
                    if len(self.children) > self.nreplicas:
                        if prev.restart_aborted():
                            scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: RESTART ABORTED")
                            poisoned_job = self.children.pop(i-self.nreplicas)
                            scm.plams.delete_job( poisoned_job )
                            scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: JOB REMOVED")
                            self._surface_poisoned = True
                            self.niterations -= 1
                    elif len(self.children) > 2*self.nreplicas:
                        prevprev = self.children[i-2*self.nreplicas]
                        if prevprev.surface_poisoned():
                            scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: SURFACE POISONED")
                            poisoned_job = self.children.pop(i-self.nreplicas)
                            scm.plams.delete_job( poisoned_job )
                            scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: JOB REMOVED")
                            self._surface_poisoned = True
                            self.niterations -= 1
                    else:
                        scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: FAILED")

                    return None

                TOF,error,ratio,conv = prev.results.turnover_frequency( nbatch=self.nbatch, confidence=self.confidence,
                                                                        ignore_nbatch=ignore_nbatch )

                if self.nreplicas > 1:
                    scm.plams.log("   Replica #%d"%i )
                    scm.plams.log("   %10s"%"species"+"%15s"%"TOF"+"%15s"%"error"+"%15s"%"ratio"+"%10s"%"conv?")
                    for s in prev.results.gas_species_names():
                        scm.plams.log("   %10s"%s+"%15.5f"%TOF[s]+"%15.5f"%error[s]+"%15.5f"%ratio[s]+"%10s"%conv[s])

                provided_quantities_list.append( prev.results.provided_quantities() )

            aver_provided_quantities = ZacrosResults._average_provided_quantities( provided_quantities_list, 'Time' )

            TOF,error,ratio,conv = prev.results.turnover_frequency( nbatch=self.nbatch, confidence=self.confidence,
                                                                        ignore_nbatch=ignore_nbatch,
                                                                        provided_quantities=aver_provided_quantities )

            if self.nreplicas > 1: scm.plams.log("   Average" )
            scm.plams.log("   %10s"%"species"+"%15s"%"TOF"+"%15s"%"error"+"%15s"%"ratio"+"%10s"%"conv?")
            for s in prev.results.gas_species_names():
                scm.plams.log("   %10s"%s+"%15.5f"%TOF[s]+"%15.5f"%error[s]+"%15.5f"%ratio[s]+"%10s"%conv[s])

            history_i = { 'turnover_frequency':TOF,
                          'turnover_frequency_error':error,
                          'converged':conv }

            for i,(name,item) in enumerate(self._parameters.items()):
                history_i[name] = self._parameters_values[self.niterations-1][name]

            self._history.append( history_i )

            if all(conv.values()):
                scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: CONVERGENCE REACHED. DONE!")
                return None
            else:
                scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: NO CONVERGENCE REACHED YET")

        # Here we apply the scaling factors
        mechanism = copy.deepcopy(self._reference.mechanism)
        if self._scaling_factors is not None:
            for i,rxn in enumerate(mechanism):
                old = rxn.pre_expon
                rxn.pre_expon *= self._scaling_factors[i]

        lparallel = []
        for i in range(self.nreplicas):
            prev = None if len(self.children)==0 else self.children[i-self.nreplicas]

            lsettings = self._parameters_settings[self.niterations].copy()
            lsettings.random_seed = lsettings.get('random_seed',default=0) + i

            if self.nreplicas > 1:
                name = self.name+"_ss_iter"+"%03d"%self.niterations+"_rep"+"%03d"%i
            else:
                name = self.name+"_ss_iter"+"%03d"%self.niterations

            new_child = ZacrosJob( settings=lsettings,
                                   lattice=self._reference.lattice,
                                   mechanism=mechanism,
                                   cluster_expansion=self._reference.cluster_expansion,
                                   name=name,
                                   restart=prev )

            lparallel.append( new_child )

        self.niterations += 1

        return lparallel


    #--------------------------------------------------------------
    # Function to compute the scaling factors of the mechanisms
    # pre-exponential factors.
    # Original author: Mauro Bracconi (mauro.bracconi@polimi.it)
    # Reference:
    #    M. Núñez, T. Robie, and D. G. Vlachosa
    #    Acceleration and sensitivity analysis of lattice kinetic
    #    Monte Carlo simulations using parallel processing and rate
    #    constant rescaling
    #    J. Chem. Phys. 147, 164103 (2017)
    #    https://doi.org/10.1063/1.4998926
    #--------------------------------------------------------------
    @staticmethod
    def __scaling_factors( mechanism, process_statistics, quasieq_th=0.1, delta=100 ) :

        # kMC rate scaling
        freq = numpy.zeros(len(mechanism)*2)
        value = list(process_statistics[-1]['number_of_events'].values())

        cont = 0
        for i,step in enumerate(mechanism):
            if(step.reversible):
                freq[2*i] = value[cont]
                freq[2*i+1] = value[cont+1]
                cont = cont+2
            else:
                freq[2*i] = value[cont]
                freq[2*i+1] = 0
                cont = cont+1

        # Forward & backward
        fwq = freq[0::2]
        bkd = freq[1::2]
        # Net & total
        net = fwq - bkd
        tot = fwq + bkd

        # Define fast and slow reactions
        fast_rxn = []
        slow_rxn = []
        PE_vec = []
        kind_vec = []
        for i in range(len(tot)):
            if tot[i] == 0:
                slow_rxn.append(i)
                PE_vec.append( 0.0 ) # TODO Check this case
                kind_vec.append( 'slow' )
            else:
                PE = float(net[i]) / tot[i]
                PE_vec.append( PE )
                if numpy.abs(PE) < quasieq_th:
                    fast_rxn.append(i)
                    kind_vec.append( 'fast' )
                else:
                    slow_rxn.append(i)
                    kind_vec.append( 'slow' )

        slow_f = [1.]
        for i in slow_rxn:
            slow_f.append(tot[i])

        slow_scale = numpy.max(slow_f)

        delta_sdf = numpy.ones(len(tot))
        for i in fast_rxn:
            Nf = tot[i] / float(slow_scale)

            delta_sdf[i] = numpy.min([1.0, delta / Nf ])

        return delta_sdf,PE_vec,kind_vec


    def __scaling_factors_step_start(self):

        sufix = ""
        if self.scaling_max_steps is not None: sufix += ",max_steps="+str(self.scaling_max_steps)
        if self.scaling_max_time is not None: sufix += ",max_time="+str(self.scaling_max_time)
        if self.scaling_species_numbers is not None: sufix += ",species_numbers="+str(self.scaling_species_numbers)

        scm.plams.log("JOB "+self._full_name()+" Scaling: Using partial_equilibrium_index_threshold="+str(self.scaling_partial_equilibrium_index_threshold)+
                        ",upper_bound="+str(self.scaling_upper_bound)+sufix)

        lsettings = self._reference.settings.copy()

        # This section is just to be sure that processes statistics (which
        # are needed for the scaling) are available for at least the last
        # step of the simulation
        ok = False

        if self.scaling_max_steps is not None:
            lsettings['process_statistics'] = ('event', self.scaling_max_steps)
            lsettings['max_steps'] = self.scaling_max_steps
            ok = True

        if self.scaling_max_time is not None:
            lsettings['process_statistics'] = ('time', self.scaling_max_time)
            lsettings['max_time'] = self.scaling_max_time
            ok = True

        if self.scaling_species_numbers is not None:
            lsettings['species_numbers'] = self.scaling_species_numbers

        if not ok:
            if 'max_steps' in lsettings and lsettings.max_steps != 'infinity':
                lsettings['process_statistics'] = ('event', lsettings.max_steps)
                ok = True

            if 'max_time' in lsettings:
                lsettings['process_statistics'] = ('time', lsettings.max_time)
                ok = True

            if not ok:
                msg  = "\n### ERROR ### ZacrosSteadyStateJob.__scaling_factors_step_start.\n"
                msg += "                process_statistics section is needed in settings object.\n"
                raise Exception(msg)

        for name,item in self._parameters.items():
            value = item.values[0]
            eval('lsettings'+item.name2setitem().replace('$var_value',str(value)))

        new_child = ZacrosJob( settings=lsettings,
                               lattice=self._reference.lattice,
                               mechanism=self._reference.mechanism,
                               cluster_expansion=self._reference.cluster_expansion,
                               name=self.name+"_ss_scaling" )

        self._scaling_status = 'started'

        return [ new_child ]


    def __scaling_factors_step_end(self):

        prev = self.children[-1]
        prev.ok()

        process_statistics = prev.results.get_process_statistics()

        if self.scaling_nevents_per_timestep is not None:
            time = process_statistics[-1]['time']
            nevents = process_statistics[-1]['total_number_of_events']

            self._new_timestep = (time/nevents)*self.scaling_nevents_per_timestep

        sf,PE,kind = self.__scaling_factors( self._reference.mechanism,
                                             process_statistics,
                                             quasieq_th=self.scaling_partial_equilibrium_index_threshold,
                                             delta=self.scaling_upper_bound )

        scm.plams.log("  "+" %5s"%"id"+" %10s"%"PE"+" %8s"%"kind"+" %15s"%"orig_pexp"+" %15s"%"sf"+" %15s"%"new_pexp"+"    label")

        self._scaling_factors = []
        for i,rxn in enumerate(self._reference.mechanism):
            old = rxn.pre_expon
            new = old*sf[i]
            self._scaling_factors.append( sf[i] )

            scm.plams.log("  "+" %5d"%i+" %10.5f"%PE[i]+" %8s"%kind[i]+" %15.5e"%old+" %15.5e"%sf[i]+" %15.5e"%new+"    "+rxn.label())

        self._scaling_status = 'finished'

        scaling_job = self.children.pop()
        #scm.plams.delete_job( scaling_job )


    def new_children(self):
        """
        """

        if self._scaling and self._scaling_status != 'finished':
            if self._scaling_status == 'requested':
                return self.__scaling_factors_step_start()
            elif self._scaling_status == 'started':
                self.__scaling_factors_step_end()

        return self.__steady_state_step()


    def check(self):
        """
        Look for the normal termination signal in the output. Note, that it does not mean your calculation was successful!
        """
        if self._surface_poisoned:
            return True
        else:
            return all(self._history[-1]['converged'].values())

