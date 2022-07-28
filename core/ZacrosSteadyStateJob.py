"""Module containing the ZacrosSteadyStateJob class."""

import os
import shutil
import numpy
from collections import OrderedDict

import scm.plams

from .ZacrosJob import *

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
    def average_coverage(self, last=5): return self.job.children[-1].results.average_coverage(last=last)
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


    def __init__(self, reference, generator_parameters, **kwargs):
        scm.plams.MultiJob.__init__(self, settings=reference.settings, **kwargs)

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

        self.lattice = reference.lattice
        self.mechanism = reference.mechanism
        self.cluster_expansion = reference.cluster_expansion
        self.initial_state = reference.initial_state
        self.restart = reference.restart

        self._reference = reference
        self._generator_parameters = generator_parameters

        self.max_iterations = len(generator_parameters[list(generator_parameters.keys())[0]].values)
        self._n_iterations = 0
        self._history = []
        self._surface_poisoned = False


    @staticmethod
    def __name2dict( name ):
        tokens = name.split('.')
        output = ""
        for i,token in enumerate(tokens):
            if i != len(tokens)-1:
                output += "[\'"+token+"\']"
        return output+".__setitem__(\'"+tokens[-1]+"\',$var_value)"


    def new_children(self):

        if self._n_iterations >= self.max_iterations:
            scm.plams.log("JOB "+self.name+" Steady State Convergence: MAX ITERATIONS REACHED")
            return None

        prev = None
        if len(self.children) > 0:
            prev = self.children[-1]

            if not prev.ok():
                if len(self.children) > 1:
                    scm.plams.log("JOB "+self.name+" Steady State Convergence: SURFACE POISONED")
                    prevprev = self.children[-2]
                    if prevprev.surface_poisoned():
                        self.children.pop()
                    self._surface_poisoned = True
                else:
                    scm.plams.log("JOB "+self.name+" Steady State Convergence: FAILED")
                return None

            TOF,error,conv = prev.results.turnover_frequency()

            history_i = { 'turnover_frequency':TOF,
                          'turnover_frequency_error':error,
                          'converged':conv }

            for name,item in self._generator_parameters.items():
                history_i[name] = item.values[self._n_iterations-1]

            self.lattice = prev.lattice
            self.mechanism = prev.mechanism
            self.cluster_expansion = prev.cluster_expansion
            self.initial_state = prev.initial_state
            self.restart = prev.restart

            self._history.append( history_i )

            if all(conv.values()):
                scm.plams.log("JOB "+self.name+" Steady State Convergence: OPTIMIZATION CONVERGED. DONE!")
                return None

        lsettings = self._reference.settings.copy()

        params = {}
        for name,item in self._generator_parameters.items():
            value = item.values[self._n_iterations]
            eval('lsettings'+ZacrosSteadyStateJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))
            params[name] = value

        new_child = ZacrosJob( settings=lsettings,
                               lattice=self._reference.lattice,
                               mechanism=self._reference.mechanism,
                               cluster_expansion=self._reference.cluster_expansion,
                               name=self.name+"_ss_iter"+"%03d"%self._n_iterations,
                               restart=prev )

        self._n_iterations += 1

        return [ new_child ]


    def check(self):
        """
        Look for the normal termination signal in the output. Note, that it does not mean your calculation was successful!
        """
        if self._surface_poisoned:
            return True
        else:
            return all(self._history[-1]['converged'].values())

