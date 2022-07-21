"""Module containing the ZacrosMultiJob class."""

import numpy
from collections import OrderedDict

import scm.plams

from .ZacrosJob import *

__all__ = ['ZacrosMultiJob', 'ZacrosMultiResults']


class ZacrosMultiResults( scm.plams.Results ):
    """
    A Class for handling ZacrosMulti Results.
    """

    def turnover_frequency(self, nbatch=20, confidence=0.99, update=None):
        if update:
            output = update
        else:
            output = []

        for pos,idx in enumerate(self.job._indices):
            params = self.job._parameters_values[idx]
            TOFs,_,_ = self.job.children[idx].results.turnover_frequency( nbatch=nbatch, confidence=confidence )

            if update:
                output[pos]['turnover_frequency'] = TOFs
            else:
                output.append( {**params, 'turnover_frequency':TOFs} )

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


class ZacrosMultiJob( scm.plams.MultiJob ):
    """
    Create a new ZacrosMultiJob object.

    *   ``lattice`` -- Lattice containing the lattice to be used during the calculation.
    *   ``mechanism`` -- Mechanism containing the mechanisms involed in the calculation.
    *   ``cluster_expansion`` -- ClusterExpansion containing the list of Clusters to use during the simulation.
    *   ``initial_state`` -- Initial state of the system. By default the simulation will use an empty lattice.
    *   ``settings`` -- Settings containing the parameters of the Zacros calculation.
    *   ``name`` -- A string containing the name of the job. All zacros input and output files are stored in a folder with this name. If not supplied, the default name is ``plamsjob``.
    *   ``restart`` -- ZacrosMultiJob object from which the calculation will be restarted
    """

    _result_type = ZacrosMultiResults

    class Parameter:
        INDEPENDENT = 0
        DEPENDENT = 1

        def __init__(self, name_in_settings, values):
            self.name_in_settings = name_in_settings

            self.values = values
            if type(values) not in [list,numpy.ndarray] and not callable(values):
                msg  = "\n### ERROR ### ZacrosMultiJob.Parameter.__init__.\n"
                msg += "              Parameter 'values' should be a 'list', 'numpy.ndarray', or 'function'.\n"
                raise Exception(msg)

            self.kind = None
            if type(values) in [list,numpy.ndarray]:
                self.kind = ZacrosMultiJob.Parameter.INDEPENDENT
            elif callable(values):
                self.kind = ZacrosMultiJob.Parameter.DEPENDENT


    def __init__(self, settings, lattice, mechanism, cluster_expansion, initial_state=None, restart=None, parameters=None, **kwargs):
        scm.plams.MultiJob.__init__(self, children=OrderedDict(), **kwargs)

        self._indices = None
        self._parameters_values = None

        if parameters is None or len(parameters) == 0:
            msg  = "\n### ERROR ### ZacrosMultiJob.__init__.\n"
            msg += "              Parameter 'parameters' is required.\n"
            raise Exception(msg)

        independent_params = []
        for name,item in parameters.items():
            if type(item) is not ZacrosMultiJob.Parameter:
                msg  = "\n### ERROR ### ZacrosMultiJob.__init__.\n"
                msg += "              Parameter 'parameters' should be a list of ZacrosMultiJob.Parameter objects.\n"
                raise Exception(msg)

            if item.kind == ZacrosMultiJob.Parameter.INDEPENDENT:
                independent_params.append( item.values )

        mesh = numpy.meshgrid( *independent_params, sparse=False )

        def name2dict( name ):
            tokens = name.split('.')
            output = ""
            for i,token in enumerate(tokens):
                if i != len(tokens)-1:
                    output += "[\'"+token+"\']"
            return output+".__setitem__(\'"+tokens[-1]+"\',$var_value)"

        self._indices = [ tuple(idx) for idx in numpy.ndindex(mesh[0].shape) ]
        self._parameters_values = {}

        for idx in self._indices:
            settings_i = settings.copy()

            params = {}
            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosMultiJob.Parameter.INDEPENDENT:
                    value = mesh[i][idx]
                    eval('settings_i'+name2dict(item.name_in_settings).replace('$var_value',str(value)))
                    params[name] = value

            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ZacrosMultiJob.Parameter.DEPENDENT:
                    value = item.values(params)
                    eval('settings_i'+name2dict(item.name_in_settings).replace('$var_value',str(value)))
                    params[name] = value

            self.children[idx] = ZacrosJob(settings=settings_i, lattice=lattice, mechanism=mechanism, \
                                            cluster_expansion=cluster_expansion, initial_state=initial_state, restart=restart)

            self._parameters_values[idx] = params

