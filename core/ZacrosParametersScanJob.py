"""Module containing the ZacrosParametersScanJob class."""

import os
import copy
import shutil
import numpy
from collections import OrderedDict

import scm.plams

from .ZacrosJob import *
from .ZacrosSteadyStateJob import *

__all__ = ['ZacrosParametersScanJob', 'ZacrosParametersScanResults']


class ZacrosParametersScanResults( scm.plams.Results ):
    """
    A Class for handling ZacrosMulti Results.
    """
    def indices(self):
        return self.job._indices


    def turnover_frequency(self, nbatch=20, confidence=0.99, update=None):
        if update:
            output = update
        else:
            output = []

        for pos,idx in enumerate(self.job._indices):
            params = self.job._parameters_values[idx]
            TOFs,errors,ratio,converged = self.job.children[idx].results.turnover_frequency( nbatch=nbatch, confidence=confidence )

            if update:
                output[pos]['turnover_frequency'] = TOFs
                output[pos]['turnover_frequency_error'] = errors
                output[pos]['turnover_frequency_ratio'] = ratio
                output[pos]['turnover_frequency_converged'] = converged
            else:
                output.append( {**params, 'turnover_frequency':TOFs, 'turnover_frequency_error':errors,
                                    'turnover_frequency_converged':converged} )

        return output


    def average_coverage(self, last=5, update=None):
        if update:
            output = update
        else:
            output = []

        for pos,idx in enumerate(self.job._indices):
            params = self.job._parameters_values[idx]
            acf = self.job.children[idx].results.average_coverage( last=last )

            if update:
                output[pos]['average_coverage'] = acf
            else:
                output.append( {**params, 'average_coverage':acf} )

        return output


class ZacrosParametersScanJob( scm.plams.MultiJob ):
    """
    Create a new ZacrosParametersScanJob object.
    """

    _result_type = ZacrosParametersScanResults


    class Parameter:
        INDEPENDENT = 0
        DEPENDENT = 1

        def __init__(self, name_in_settings, values):
            self.name_in_settings = name_in_settings

            self.values = values
            if type(values) not in [list,numpy.ndarray] and not callable(values):
                msg  = "\n### ERROR ### ZacrosParametersScanJob.Parameter.__init__.\n"
                msg += "              Parameter 'values' should be a 'list', 'numpy.ndarray', or 'function'.\n"
                raise Exception(msg)

            self.kind = None
            if type(values) in [list,numpy.ndarray]:
                self.kind = ZacrosParametersScanJob.Parameter.INDEPENDENT
            elif callable(values):
                self.kind = ZacrosParametersScanJob.Parameter.DEPENDENT


    def __init__(self, reference, generator=None, generator_parameters=None, **kwargs):
        scm.plams.MultiJob.__init__(self, children=OrderedDict(), **kwargs)

        if generator is not None:
            if len(generator_parameters) == 0:
                msg  = "\n### ERROR ### ZacrosParametersScanJob.__init__.\n"
                msg += "              Parameter 'generator_parameters' is required if 'generator' different than None\n"
                raise Exception(msg)

            for name,item in generator_parameters.items():
                if type(item) is not ZacrosParametersScanJob.Parameter:
                    msg  = "\n### ERROR ### ZacrosParametersScanJob.__init__.\n"
                    msg += "              Parameter 'generator_parameters' should be a list of ZacrosParametersScanJob.Parameter objects.\n"
                    raise Exception(msg)

        self._indices = None
        self._parameters_values = None

        if isinstance(reference,ZacrosJob):
            self._indices,self._parameters_values,settings_list = generator( reference.settings, generator_parameters )
        elif isinstance(reference,ZacrosSteadyStateJob):
            self._indices,self._parameters_values,settings_list = generator( reference._reference.settings, generator_parameters )
        else:

            msg  = "\n### ERROR ### ZacrosParametersScanJob.__init__.\n"
            msg += "              Parameter 'reference' should be a ZacrosJob or ZacrosSteadyStateJob object.\n"
            raise Exception(msg)

        for i,(idx,settings_idx) in enumerate(settings_list.items()):

            new_name = self.name+"_ps_cond"+"%03d"%i

            if isinstance(reference,ZacrosJob):

                job = ZacrosJob( settings=settings_idx, lattice=reference.lattice, mechanism=reference.mechanism, \
                                cluster_expansion=reference.cluster_expansion, initial_state=reference.initial_state, \
                                restart=reference.restart, name=new_name )

            elif isinstance(reference,ZacrosSteadyStateJob):

                new_reference = copy.copy(reference._reference)
                new_reference.settings = settings_idx
                job = ZacrosSteadyStateJob( settings=reference.settings, reference=new_reference,
                                            generator_parameters=reference._generator_parameters,
                                            name=new_name, scaling=reference._scaling )

            self.children[ idx ] = job


    def check(self):
        return all([job.ok() for job in self.children.values()])


    @staticmethod
    def __name2dict( name ):
        tokens = name.split('.')
        output = ""
        for i,token in enumerate(tokens):
            if i != len(tokens)-1:
                output += "[\'"+token+"\']"
        return output+".__setitem__(\'"+tokens[-1]+"\',$var_value)"


    @staticmethod
    def meshGenerator( settings, parameters ):

        independent_params = []
        for name,item in parameters.items():
            if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                independent_params.append( item.values )
                if len(item.values) == 0:
                    msg  = "\n### ERROR ### ZacrosParametersScanJob.meshGenerator().\n"
                    msg += "              All parameter in 'generator_parameters' should be lists with at least one element.\n"
                    raise Exception(msg)

        mesh = numpy.meshgrid( *independent_params, sparse=False )

        indices = [ tuple(idx) for idx in numpy.ndindex(mesh[0].shape) ]
        parameters_values = {}
        settings_list = {}

        for idx in indices:
            settings_idx = settings.copy()

            params = {}
            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                    value = mesh[i][idx]
                    eval('settings_idx'+ZacrosParametersScanJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))
                    params[name] = value

            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.DEPENDENT:
                    value = item.values(params)
                    eval('settings_idx'+ZacrosParametersScanJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))
                    params[name] = value

            parameters_values[idx] = params
            settings_list[idx] = settings_idx

        return indices,parameters_values,settings_list


    @staticmethod
    def zipGenerator( settings, parameters ):

        independent_params = []
        size = None
        for name,item in parameters.items():
            if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                independent_params.append( item.values )
                if size is None:
                    size = len(item.values)
                elif size != len(item.values):
                    msg  = "\n### ERROR ### ZacrosParametersScanJob.zipGenerator().\n"
                    msg += "              All parameter in 'generator_parameters' should be lists of the same size.\n"
                    raise Exception(msg)

        if size == 0:
            msg  = "\n### ERROR ### ZacrosParametersScanJob.zipGenerator().\n"
            msg += "              All parameter in 'generator_parameters' should be lists with at least one element.\n"
            raise Exception(msg)

        indices = list( range(size) )
        parameters_values = {}
        settings_list = {}

        for idx in indices:
            settings_idx = settings.copy()

            params = {}
            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                    value = independent_params[i][idx]
                    eval('settings_idx'+ZacrosParametersScanJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))
                    params[name] = value

            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.DEPENDENT:
                    value = item.values(params)
                    eval('settings_idx'+ZacrosParametersScanJob.__name2dict(item.name_in_settings).replace('$var_value',str(value)))
                    params[name] = value

            parameters_values[idx] = params
            settings_list[idx] = settings_idx

        return indices,parameters_values,settings_list
