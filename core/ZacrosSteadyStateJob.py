"""Module containing the ZacrosSteadyStateJob class."""

import os
import shutil
import numpy
from collections import OrderedDict

import scm.plams

from .Settings import *
from .ZacrosJob import *
from .ZacrosResults import *

__all__ = ['ZacrosSteadyStateJob', 'ZacrosSteadyStateResults']


class ZacrosSteadyStateResults( scm.plams.Results ):
    """
    A Class for handling ZacrosMulti Results.
    """
    def history(self):
        return self.job._history

    def get_zacros_version(self): return self.job.children[-1].results.get_zacros_version()
    def get_reaction_network(self): return self.job.children[-1].results.get_reaction_network()
    def provided_quantities(self): return self.job.children[-1].results.provided_quantities()
    def number_of_lattice_sites(self): return self.job.children[-1].results.number_of_lattice_sites()
    def gas_species_names(self): return self.job.children[-1].results.gas_species_names()
    def surface_species_names(self): return self.job.children[-1].results.surface_species_names()
    def site_type_names(self): return self.job.children[-1].results.site_type_names()
    def number_of_snapshots(self): return self.job.children[-1].results.number_of_snapshots()
    def number_of_process_statistics(self): return self.job.children[-1].results.number_of_process_statistics()
    def elementary_steps_names(self): return self.job.children[-1].results.elementary_steps_names()
    def lattice_states(self, last=None): return self.job.children[-1].results.lattice_states(last=last)
    def last_lattice_state(self): return self.job.children[-1].results.last_lattice_state()

    def average_coverage(self, last=5):

        acf = {}
        for i in range(self.job.nreplicas):
            prev = self.job.children[-(i+1)]

            lacf = prev.results.average_coverage(last=last)

            for k,v in lacf.items():
                if k not in acf:
                    acf[k] = v/self.job.nreplicas
                else:
                    acf[k] += v/self.job.nreplicas

        return acf

    def plot_lattice_states(self, data, pause=-1, show=True, ax=None, close=False, time_perframe=0.5, file_name=None):
        self.job.children[-1].results.plot_lattice_states(data=data, pause=pause, show=show, ax=ax, close=close,
                                                    time_perframe=time_perframe, file_name=file_name)
    def plot_molecule_numbers(self, species_name, pause=-1, show=True, ax=None, close=False,
                                file_name=None, normalize_per_site=False, derivative=False):
        self.job.children[-1].results.plot_molecule_numbers(species_name=species_name, pause=pause, show=show, ax=ax, close=close,
                                                        file_name=file_name, normalize_per_site=normalize_per_site, derivative=derivative)
    def get_process_statistics(self): return self.job.children[-1].results.get_process_statistics()
    def plot_process_statistics(self, data, key, log_scale=False, pause=-1, show=True, ax=None, close=False, file_name=None):
        self.job.children[-1].results.plot_process_statistics(data=data, key=key, log_scale=log_scale, pause=pause, show=show, ax=ax,
                                                        close=close, file_name=file_name)
    def turnover_frequency(self, nbatch=20, confidence=0.99, species_name=None):
        return self.job.children[-1].results.turnover_frequency(nbatch=nbatch, confidence=confidence, species_name=species_name)


class ZacrosSteadyStateJob( scm.plams.MultiJob ):
    """
    Create a new ZacrosSteadyStateJob object.
    """

    _result_type = ZacrosSteadyStateResults


    class Parameter:

        def __init__(self, name_in_settings, values):
            self.name_in_settings = name_in_settings

            self.values = values
            if type(values) not in [list,numpy.ndarray]:
                msg  = "\n### ERROR ### ZacrosSteadyStateJob.Parameter.__init__.\n"
                msg += "              Parameter 'values' should be a 'list' or 'numpy.ndarray'.\n"
                raise Exception(msg)


    def __init__(self, reference, generator_parameters, scaling=False, settings=Settings(), **kwargs):
        scm.plams.MultiJob.__init__(self, settings=settings, **kwargs)

        size = None
        for name,item in generator_parameters.items():
            if size is None:
                size = len(item.values)
            elif size != len(item.values):
                msg  = "\n### ERROR ### ZacrosSteadyStateJob.zipGenerator().\n"
                msg += "              All parameter in 'generator_parameters' should be lists of the same size.\n"
                raise Exception(msg)

        if size == 0:
            msg  = "\n### ERROR ### ZacrosSteadyStateJob.meshGenerator().\n"
            msg += "              All parameter in 'generator_parameters' should be lists with at least one element.\n"
            raise Exception(msg)

        self._reference = reference
        self._generator_parameters = generator_parameters
        self._scaling = scaling

        self._scaling_status = 'not_requested'
        if self._scaling: self._scaling_status = 'requested'

        self.max_iterations = len(generator_parameters[list(generator_parameters.keys())[0]].values)
        self._n_iterations = 0
        self._history = []
        self._surface_poisoned = False

        self.nbatch = 20
        self.confidence = 0.99
        self.nreplicas = 1
        self.partial_equilibrium_index_threshold = 0.1
        self.scaling_upper_bound = 100
        self.scaling_max_steps = None
        self.scaling_max_time = None

        self.nreplicas = self.settings.get('nreplicas', default=self.nreplicas)

        if 'turnover_frequency' in self.settings:
            self.nbatch = self.settings.turnover_frequency.get('nbatch', default=self.nbatch)
            self.confidence = self.settings.turnover_frequency.get('confidence', default=self.confidence)

        # Scaling pre-exponential terms parameters
        if 'scaling' in self.settings:
            self.partial_equilibrium_index_threshold = self.settings.scaling.get('partial_equilibrium_index_threshold', default=self.partial_equilibrium_index_threshold)
            self.scaling_upper_bound = self.settings.scaling.get('upper_bound', default=self.scaling_upper_bound)
            self.scaling_max_steps = self.settings.scaling.get('max_steps', default=self.scaling_max_steps)
            self.scaling_max_time = self.settings.scaling.get('max_time', default=self.scaling_max_time)

        scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: Using nbatch="+str(self.nbatch)+
                        ",confidence="+str(self.confidence)+",nreplicas="+str(self.nreplicas))

        # These parameters a needed to make ZacrosSteadyStateJob compatible with ZacrosJob
        self.lattice = reference.lattice
        self.mechanism = reference.mechanism
        self.cluster_expansion = reference.cluster_expansion
        self.initial_state = reference.initial_state


    @staticmethod
    def __name2dict( name ):
        tokens = name.split('.')
        output = ""
        for i,token in enumerate(tokens):
            if i != len(tokens)-1:
                output += "[\'"+token+"\']"
        return output+".__setitem__(\'"+tokens[-1]+"\',$var_value)"


    def __steady_state_step(self):

        if self._n_iterations >= self.max_iterations:
            scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: MAX ITERATIONS REACHED")
            return None

        if len(self.children) > 0:
            prev = None
            provided_quantities_list = []

            for i in range(self.nreplicas):
                prev = self.children[-(i+1)]
                prev.ok()

            for i in range(self.nreplicas):
                prev = self.children[-(i+1)]

                if not prev.ok():
                    if len(self.children) > 1:
                        prevprev = self.children[-(self.nreplicas-i)]
                        if prev.restart_aborted() or prevprev.surface_poisoned():
                            if prev.restart_aborted(): scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: RESTART ABORTED")
                            if prev.surface_poisoned(): scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: SURFACE POISONED")
                            poisoned_job = self.children.pop(-(i+1))
                            scm.plams.delete_job( poisoned_job )
                        self._surface_poisoned = True
                    else:
                        scm.plams.log("JOB "+prev._full_name()+" Steady State Convergence: FAILED")
                    return None

                TOF,error,ratios,conv = prev.results.turnover_frequency( nbatch=self.nbatch, confidence=self.confidence )

                if self.nreplicas>1:
                    scm.plams.log("   Replica #%d"%i )
                    scm.plams.log("   %10s"%"species"+"%15s"%"TOF"+"%15s"%"error"+"%15s"%"ratio"+"%10s"%"conv?")
                    for s in prev.results.gas_species_names():
                        scm.plams.log("   %10s"%s+"%15.5f"%TOF[s]+"%15.5f"%error[s]+"%15.5f"%ratios[s]+"%10s"%conv[s])

                provided_quantities_list.append( prev.results.provided_quantities() )

            aver_provided_quantities = ZacrosResults._average_provided_quantities( provided_quantities_list, 'Time' )

            TOF,error,ratios,conv = prev.results.turnover_frequency( nbatch=self.nbatch, confidence=self.confidence,
                                                                        provided_quantities=aver_provided_quantities )

            if self.nreplicas > 1: scm.plams.log("   Average" )
            scm.plams.log("   %10s"%"species"+"%15s"%"TOF"+"%15s"%"error"+"%15s"%"ratio"+"%10s"%"conv?")
            for s in prev.results.gas_species_names():
                scm.plams.log("   %10s"%s+"%15.5f"%TOF[s]+"%15.5f"%error[s]+"%15.5f"%ratios[s]+"%10s"%conv[s])

            history_i = { 'turnover_frequency':TOF,
                          'turnover_frequency_error':error,
                          'converged':conv }

            for name,item in self._generator_parameters.items():
                history_i[name] = item.values[self._n_iterations-1]

            self._history.append( history_i )

            if all(conv.values()):
                scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: CONVERGENCE REACHED. DONE!")
                return None
            else:
                scm.plams.log("JOB "+self._full_name()+" Steady State Convergence: NO CONVERGENCE REACHED YET")

        lparallel = []
        for i in range(self.nreplicas):
            prev = None if len(self.children)==0 else self.children[-(i+1)]
            lsettings = self._reference.settings.copy()

            lsettings.random_seed = lsettings.get('random_seed',default=0) + i

            for name,item in self._generator_parameters.items():
                value = item.values[self._n_iterations]
                eval('lsettings'+ZacrosSteadyStateJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))

            if self.nreplicas > 1:
                name = self.name+"_ss_iter"+"%03d"%self._n_iterations+"_rep"+"%03d"%i
            else:
                name = self.name+"_ss_iter"+"%03d"%self._n_iterations

            new_child = ZacrosJob( settings=lsettings,
                                   lattice=self._reference.lattice,
                                   mechanism=self._reference.mechanism,
                                   cluster_expansion=self._reference.cluster_expansion,
                                   name=name,
                                   restart=prev )

            lparallel.append( new_child )

        self._n_iterations += 1

        return lparallel


    #--------------------------------------------------------------
    # Function to compute the scaling factors of the mechanisms
    # pre-exponential factors.
    # Original author: Mauro Bracconi (mauro.bracconi@polimi.it)
    # Reference:
    #    M. Núñez, T. Robie, and D. G. Vlachosa
    #    Acceleration and sensitivity analysis of lattice kinetic Monte Carlo simulations using parallel processing and rate constant rescaling
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


    def __scaling_factors_step(self):

        sufix = ""
        if self.scaling_max_steps is not None: sufix += ",scaling_max_steps="+str(self.scaling_max_steps)
        if self.scaling_max_time is not None: sufix += ",scaling_max_time="+str(self.scaling_max_time)

        scm.plams.log("JOB "+self._full_name()+" Scaling: Using partial_equilibrium_index_threshold="+str(self.partial_equilibrium_index_threshold)+
                        ",scaling_upper_bound="+str(self.scaling_upper_bound)+sufix)

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

        if not ok:
            if 'max_steps' in lsettings and lsettings.max_steps != 'infinity':
                lsettings['process_statistics'] = ('event', lsettings.max_steps)
                ok = True

            if 'max_time' in lsettings:
                lsettings['process_statistics'] = ('time', lsettings.max_time)
                ok = True

            if not ok:
                msg  = "\n### ERROR ### ZacrosSteadyStateJob.__scaling_factors_step.\n"
                msg += "                process_statistics section is needed in settings object.\n"
                raise Exception(msg)

        for name,item in self._generator_parameters.items():
            value = item.values[0]
            eval('lsettings'+ZacrosSteadyStateJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))

        new_child = ZacrosJob( settings=lsettings,
                               lattice=self._reference.lattice,
                               mechanism=self._reference.mechanism,
                               cluster_expansion=self._reference.cluster_expansion,
                               name=self.name+"_ss_scaling" )

        self._scaling_status = 'started'

        return [ new_child ]


    def __scaling_factors_apply(self):

        prev = self.children[-1]
        prev.ok()

        sf,PE,kind = self.__scaling_factors( self._reference.mechanism,
                                             prev.results.get_process_statistics(),
                                             quasieq_th=self.partial_equilibrium_index_threshold,
                                             delta=self.scaling_upper_bound )

        scm.plams.log("  "+" %10s"%"PE"+" %8s"%"kind"+"    label")
        for i,rxn in enumerate(self._reference.mechanism):
            scm.plams.log("  "+" %10.5f"%PE[i]+" %8s"%kind[i]+"    "+rxn.label())

        scm.plams.log("  "+" %15s"%"orig_pexp"+" %15s"%"sf"+" %15s"%"new_pexp")
        for i,rxn in enumerate(self._reference.mechanism):
            old = rxn.pre_expon
            rxn.pre_expon *= sf[i]

            scm.plams.log("  "+" %15.5e"%old+" %15.5e"%sf[i]+" %15.5e"%rxn.pre_expon)

        self._scaling_status = 'finished'

        scaling_job = self.children.pop()
        scm.plams.delete_job( scaling_job )


    def new_children(self):

        if self._scaling and self._scaling_status != 'finished':
            if self._scaling_status == 'requested':
                return self.__scaling_factors_step()
            elif self._scaling_status == 'started':
                self.__scaling_factors_apply()

        return self.__steady_state_step()


    def check(self):
        """
        Look for the normal termination signal in the output. Note, that it does not mean your calculation was successful!
        """
        if self._surface_poisoned:
            return True
        else:
            return all(self._history[-1]['converged'].values())

