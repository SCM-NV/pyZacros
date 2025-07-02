"""Module containing the ZacrosParametersScanJob class."""

import os
import copy
import shutil
import numpy
from collections import OrderedDict
from typing import Optional

import scm.plams

from .ZacrosJob import *
from .ZacrosSteadyStateJob import *
from .ParametersBase import *

__all__ = ["ZacrosParametersScanJob", "ZacrosParametersScanResults"]


class ZacrosParametersScanResults(scm.plams.Results):
    """
    A Class for handling ZacrosParametersScanJob Results.
    """

    def indices(self):
        """
        Returns the indices to get access to the children results.

        Example of use:

        .. code-block:: python

           for i,idx in enumerate(results.indices()):
               print( results.children_results( child_id=idx ).history( pos=-1 )['max_time'] )

        """
        return self.job._indices

    def children_results(self, child_id=None):
        """
        Returns the children results in a dictionary form.

        Example of use:

        .. code-block:: python

           for i,idx in enumerate(results.indices()):
               print( results.children_results( child_id=idx ).history( pos=-1 )['max_time'] )

        """
        if child_id is None:
            output = {}

            for pos, idx in enumerate(self.job._indices):
                output[idx] = self.job.children[idx].results

            return output
        else:
            return self.job.children[child_id].results

    def turnover_frequency(self, nbatch=20, confidence=0.99, ignore_nbatch=1, update=None):
        """
        Return a list with values related to the calculation of the turnover frequency for the gas species.

        *   ``nbatch`` -- Number of batches to use.
        *   ``confidence`` -- Confidence level to use in the criterion to determine if the steady-state was reached.
        *   ``ignore_nbatch`` -- Number of batches to ignore during the averaging in the calculation of the TOF.
        *   ``update`` -- List with dictionary items to be updated with the output values.

        The following example illustrates the structure of one element of the output list:

        .. code-block:: python

           {'x_CO': 0.1,
            'x_O2': 0.9,
            'turnover_frequency': {'CO': -0.017600, 'O2': -0.014926, 'CO2': 0.017600},
            'turnover_frequency_error': {'CO': 0.018148, 'O2': 0.015503, 'CO2': 0.018148},
            'turnover_frequency_converged': {'CO': False, 'O2': False, 'CO2': False}}

        """

        if update:
            output = update
        else:
            output = []

        for pos, idx in enumerate(self.job._indices):
            params = self.job._parameters_values[idx]

            if pos == 0 and isinstance(self.job.children[idx], ZacrosSteadyStateJob):
                nbatch = self.job.children[idx].nbatch
                confidence = self.job.children[idx].confidence
                ignore_nbatch = self.job.children[idx].ignore_nbatch

            TOFs, errors, ratio, converged = self.job.children[idx].results.turnover_frequency(
                nbatch=nbatch, confidence=confidence, ignore_nbatch=ignore_nbatch
            )

            if update:
                output[pos]["turnover_frequency"] = TOFs
                output[pos]["turnover_frequency_error"] = errors
                output[pos]["turnover_frequency_ratio"] = ratio
                output[pos]["turnover_frequency_converged"] = converged
            else:
                output.append(
                    {
                        **params,
                        "turnover_frequency": TOFs,
                        "turnover_frequency_error": errors,
                        "turnover_frequency_converged": converged,
                    }
                )

        return output

    def average_coverage(self, last=5, update=None):
        """
        Return a list with values related to the calculation of the average coverage for the adsorbed species.
        Each element of the output list is a dictionary with the average coverage fractions using the last ``last``
        lattice states, for example:

        .. code-block:: python

           {'x_CO': 0.1,
            'x_O2': 0.9,
            'average_coverage': { "CO*":0.32, "O*":0.45 }}

        """

        if update:
            output = update
        else:
            output = []

        for pos, idx in enumerate(self.job._indices):
            params = self.job._parameters_values[idx]
            acf = self.job.children[idx].results.average_coverage(last=last)

            if update:
                output[pos]["average_coverage"] = acf
            else:
                output.append({**params, "average_coverage": acf})

        return output


class ZacrosParametersScanJob(scm.plams.MultiJob):
    """
    Creates a new ZacrosParametersScanJob object. This class is a job that is a container for other jobs, called children jobs and
    it is an extension of the `PLAMS.MultiJob <../../plams/components/jobs.html#multijobs>`_. Children are copies of a reference
    job ``reference``. However, just before they are run, their corresponding Settings are altered accordingly to the rules
    defined through the ``Parameters`` object ``parameters``.

    *   ``reference`` -- Reference job. It must be :ref:`ZacrosJob <zacrosjob>` or :ref:`ZacrosSteadyStateJob <zacrossteadystatejob>` kind object.
    *   ``parameters`` -- ``Parameters`` object containing the parameters' specifications.
    *   ``name`` -- A string containing the name of the job. All zacros input and output files are stored in a folder with this name. If not supplied, the default name is ``plamsjob``.
    """

    class Parameter(ParameterBase):
        """
        Creates a new Parameter object specifically tailored for ZacrosParametersScanJob
        """

        def __init__(self, name_in_settings, kind, values):
            super().__init__(self, name_in_settings, kind, values)

    class Parameters(ParametersBase):
        """
        Creates a new Parameters object specifically tailored for ZacrosParametersScanJob
        """

        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)

    _result_type = ZacrosParametersScanResults

    def __init__(self, reference, parameters=None, **kwargs):
        scm.plams.MultiJob.__init__(self, children=OrderedDict(), **kwargs)

        self._indices = None
        self._parameters_values = None

        if isinstance(reference, ZacrosJob):
            self._indices, self._parameters_values, settings_list = parameters._generator(
                reference.settings, parameters
            )
        elif isinstance(reference, ZacrosSteadyStateJob):
            self._indices, self._parameters_values, settings_list = parameters._generator(
                reference._reference.settings, parameters
            )
        else:
            msg = "\n### ERROR ### ZacrosParametersScanJob.__init__.\n"
            msg += "              Parameter 'reference' should be a ZacrosJob or ZacrosSteadyStateJob object.\n"
            raise Exception(msg)

        for i, (idx, settings_idx) in enumerate(settings_list.items()):

            new_name = "ps_cond" + "%03d" % i

            if isinstance(reference, ZacrosJob):

                job = ZacrosJob(
                    settings=settings_idx,
                    lattice=reference.lattice,
                    mechanism=reference.mechanism,
                    cluster_expansion=reference.cluster_expansion,
                    initial_state=reference.initial_state,
                    restart=reference.restart,
                    name=new_name,
                )

            elif isinstance(reference, ZacrosSteadyStateJob):

                new_reference = copy.copy(reference._reference)
                new_reference.settings = settings_idx
                job = ZacrosSteadyStateJob(
                    settings=reference.settings,
                    reference=new_reference,
                    parameters=reference._parameters,
                    name=new_name,
                )

            self.children[idx] = job

    def run(
        self,
        jobrunner: Optional[scm.plams.JobRunner] = None,
        jobmanager: Optional[scm.plams.JobRunner] = None,
        **kwargs,
    ) -> scm.plams.Results:
        # Check the zacros executable is available before running, and raise an error if not
        ZacrosJob._check_zacros_executable()
        return super().run(jobrunner, jobmanager, **kwargs)

    def check(self):
        return all([job.ok() for job in self.children.values()])

    @staticmethod
    def zipGenerator(reference_settings, parameters):
        """
        This function combines the values of the parameters one-to-one following the order as they were defined

        *   ``reference_settings`` -- ``Settings`` object to be used as a reference.
        *   ``parameters`` -- ``Parameters`` object containing the parameters' specifications.

        Example of use:

        .. code-block:: python

            params = pz.ZacrosParametersScanJob.Parameters()
            params.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.0, 1.0, 0.25) )
            params.add( 'x_O2', 'molar_fraction.O2', lambda p: 1.0-p['x_CO'] )
            params.set_generator( pz.ZacrosParametersScanJob.zipGenerator )
            print(params)

        The code above will generate the following output that lists the final values for the parameters:

        .. code-block:: none

            0: {'x_CO': 0.0, 'x_O2': 1.0}
            1: {'x_CO': 0.25, 'x_O2': 0.75}
            2: {'x_CO': 0.5, 'x_O2': 0.5}
            3: {'x_CO': 0.75, 'x_O2': 0.25}
        """
        return ZacrosParametersScanJob.Parameters.zipGenerator(reference_settings, parameters)

    @staticmethod
    def meshgridGenerator(reference_settings, parameters):
        """
        This function combines the values of the parameters creating an `n-`dimensional rectangular grid,
        being `n` the number of parameters. Meshgrid generator is inspired by ``numpy.meshgrid`` function.

        *   ``reference_settings`` -- ``Settings`` object to be used as a reference.
        *   ``parameters`` -- ``Parameters`` object containing the specifications of the parameters.

        Example of use:

        .. code-block:: python

            params = pz.ZacrosParametersScanJob.Parameters()
            params.add( 'x_CO', 'molar_fraction.CO', numpy.arange(0.0, 1.0, 0.4) )
            params.add( 'x_O2', 'molar_fraction.O2', numpy.arange(0.0, 1.0, 0.4) )
            params.add( 'x_N2', 'molar_fraction.N2', lambda p: 0.11+p['x_CO']+p['x_O2'] )
            params.set_generator( pz.ZacrosParametersScanJob.meshgridGenerator )
            print(params)

        The code above will generate the following output that lists the final values for the parameters:

        .. code-block:: none

           (0, 0): {'x_CO': 0.0, 'x_O2': 0.0, 'x_N2': 0.11}
           (0, 1): {'x_CO': 0.4, 'x_O2': 0.0, 'x_N2': 0.51}
           (0, 2): {'x_CO': 0.8, 'x_O2': 0.0, 'x_N2': 0.91}
           (1, 0): {'x_CO': 0.0, 'x_O2': 0.4, 'x_N2': 0.51}
           (1, 1): {'x_CO': 0.4, 'x_O2': 0.4, 'x_N2': 0.91}
           (1, 2): {'x_CO': 0.8, 'x_O2': 0.4, 'x_N2': 1.31}
           (2, 0): {'x_CO': 0.0, 'x_O2': 0.8, 'x_N2': 0.91}
           (2, 1): {'x_CO': 0.4, 'x_O2': 0.8, 'x_N2': 1.31}
           (2, 2): {'x_CO': 0.8, 'x_O2': 0.8, 'x_N2': 1.71}
        """

        independent_params = []
        for name, item in parameters.items():
            if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                independent_params.append(item.values)
                if len(item.values) == 0:
                    msg = "\n### ERROR ### ZacrosParametersScanJob.meshgridGenerator().\n"
                    msg += "              All parameter in 'generator_parameters' should be lists with at least one element.\n"
                    raise Exception(msg)

        mesh = numpy.meshgrid(*independent_params, sparse=False)

        indices = [tuple(idx) for idx in numpy.ndindex(mesh[0].shape)]
        parameters_values = {}
        settings_list = {}

        for idx in indices:
            settings_idx = reference_settings.copy()

            params = {}
            for i, (name, item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.INDEPENDENT:
                    value = mesh[i][idx]
                    eval("settings_idx" + item.name2setitem().replace("$var_value", str(value)))
                    params[name] = value

            for i, (name, item) in enumerate(parameters.items()):
                if item.kind == ZacrosParametersScanJob.Parameter.DEPENDENT:
                    value = item.values(params)
                    eval("settings_idx" + item.name2setitem().replace("$var_value", str(value)))
                    params[name] = value

            parameters_values[idx] = params
            settings_list[idx] = settings_idx

        return indices, parameters_values, settings_list
