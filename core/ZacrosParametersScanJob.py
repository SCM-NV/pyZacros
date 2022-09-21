"""Module containing the ZacrosParametersScanJob class."""

import os
import copy
import shutil
import numpy
from collections import OrderedDict

import scm.plams

from .ZacrosJob import *
from .ZacrosSteadyStateJob import *
from .ParametersBase import *

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

            if pos==0 and isinstance(self.job.children[idx],ZacrosSteadyStateJob):
                nbatch = self.job.children[idx].nbatch
                confidence = self.job.children[idx].confidence

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
    Creates a new ZacrosParametersScanJob object. This class is a job that is a container for other jobs, called children jobs and
    it is an extension of the `PLAMS.MultiJob <../../plams/components/jobs.html#multijobs>`_. Children are copies of a reference
    job ``reference``. However, just before they are run, their corresponding Settings are altered accordingly to the rules
    defined through a ``Parameter`` object provided using the parameters ``generator`` and ``generator_parameters``.

    *   ``reference`` -- Reference job. It must be :ref:`ZacrosJobs <zacrosjob>` or :ref:`ZacrosSteadyStateJob <zacrossteadystatejob>` kind object.
    *   ``generator`` --
    *   ``generator_parameters`` -- Mechanism containing the mechanisms involed in the calculation.
    *   ``name`` -- A string containing the name of the job. All zacros input and output files are stored in a folder with this name. If not supplied, the default name is ``plamsjob``.
    """

    class Parameter(ParameterBase):
        def __init__(self, name_in_settings, kind, values):
            super().__init__(self, name_in_settings, kind, values)

    class Parameters(ParametersBase):
        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)


    _result_type = ZacrosParametersScanResults


    def __init__(self, reference, parameters=None, **kwargs):
        scm.plams.MultiJob.__init__(self, children=OrderedDict(), **kwargs)

        self._indices = None
        self._parameters_values = None

        if isinstance(reference,ZacrosJob):
            self._indices,self._parameters_values,settings_list = parameters._generator( reference.settings, parameters )
        elif isinstance(reference,ZacrosSteadyStateJob):
            self._indices,self._parameters_values,settings_list = parameters._generator( reference._reference.settings, parameters )
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
                                            parameters=reference._parameters,
                                            name=new_name, scaling=reference._scaling )

            self.children[ idx ] = job


    def check(self):
        return all([job.ok() for job in self.children.values()])


    @staticmethod
    def zipGenerator( reference_settings, parameters ):
        return ZacrosParametersScanJob.Parameters.zipGenerator( reference_settings, parameters )


    @staticmethod
    def meshgridGenerator( reference_settings, parameters ):
        """
        This function is used to create a rectangular
        grid out of N given one-dimensional arrays representing the Cartesian indexing or Matrix
        indexing. Meshgrid function is somewhat inspired from MATLAB.

        *   ``reference_settings`` --
        *   ``parameters`` --
        """

        independent_params = []
        for name,item in parameters.items():
            if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                independent_params.append( item.values )
                if len(item.values) == 0:
                    msg  = "\n### ERROR ### ZacrosParametersScanJob.meshgridGenerator().\n"
                    msg += "              All parameter in 'generator_parameters' should be lists with at least one element.\n"
                    raise Exception(msg)

        mesh = numpy.meshgrid( *independent_params, sparse=False )

        indices = [ tuple(idx) for idx in numpy.ndindex(mesh[0].shape) ]
        parameters_values = {}
        settings_list = {}

        for idx in indices:
            settings_idx = reference_settings.copy()

            params = {}
            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                    value = mesh[i][idx]
                    eval('settings_idx'+item.name2setitem().replace('$var_value',str(value)))
                    params[name] = value

            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.DEPENDENT:
                    value = item.values(params)
                    eval('settings_idx'+item.name2setitem().replace('$var_value',str(value)))
                    params[name] = value

            parameters_values[idx] = params
            settings_list[idx] = settings_idx

        return indices,parameters_values,settings_list
