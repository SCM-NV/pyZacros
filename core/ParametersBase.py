import numpy
from .Settings import *

class ParameterBase:
    """
    Creates a new ParameterBase object.
    """
    INDEPENDENT = 0
    DEPENDENT = 1

    def __init__(self, name_in_settings, kind, values):
        self.name_in_settings = name_in_settings
        self.kind = kind
        self.values = values


    def name2setitem(self, dummy_var='$var_value'):
        """
        Converts the attribute ``name_in_settings`` in a string that may be combined with the
        python ``eval`` function to set new items in ``Settings`` objects.

        As an example let's assume that ``name_in_settings=="section.molar_fraction.CO"``. This
        function should return "['section']['molar_fraction'].__setitem__('CO','$var_value')".
        Thus, it can be combined with the python ``eval`` function as follows:

        .. code-block:: python

            >>> sett = Settings()
            >>> param = ParameterBase( 'temperature', INDEPENDENT,3.0 )
            >>> value = 3.0
            >>> eval('sett'+param.name2setitem().replace('$var_value',str(value)))
            >>> print(sett)
            section:
                    molar_fraction:
                                CO:      3.0

        This is just a tricky way to do ``sett.section.molar_fraction.CO = 3.0``, but it is
        particularly convenient in some punctual cases.
        """
        tokens = self.name_in_settings.split('.')
        output = ""
        for i,token in enumerate(tokens):
            if i != len(tokens)-1:
                output += "[\'"+token+"\']"
        return output+".__setitem__(\'"+tokens[-1]+"\',"+dummy_var+")"


class ParametersBase(dict):
    """
    Creates a new ParametersBase object which is used to modify parameters in :ref:`Settings <settings>` objects.

    Example:
        parameters = ParametersBase()
        parameters.add( 'x_CO', 'molar_fraction.CO', [0.40, 0.50] )
        parameters.add( 'x_O2', 'molar_fraction.O2', lambda params: 1.0-params['x_CO'] )
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self._generator = ParametersBase.zipGenerator


    def __str__(self):
        """
        Translates the object to a string
        """
        output = ""
        for index,values in self.values().items():
            output += str(index)+": "+str(values)+"\n"

        return output


    def add(self, name, name_in_settings, values):
        """
        Adds a new parameter
        *   ``name`` -- String to be used as a key  to identify the new parameter to add.
        *   ``name_in_settings`` -- String with the name of the parameter as it is in the target ``Settings`` object,
            e.g., `'temperature'` to modify the value of `settings.temperature`,
            or 'scaling.species_numbers' to modify the value of `settings.scaling.species_numbers`.
        *   ``values`` -- Possible values to consider for this parameter. It can be a one-dimensional array
            (``list`` or ``numpy.ndarray``), or a python lambda function (``lambda params: expression( params )``).
            If it is an array, the parameter is considered ``INDEPENDENT``; otherwise, if it is a lambda function,
            it is considered ``DEPENDENT``. In the latter case, possible values rest on the values of other parameters,
            which can be accessed through the lambda function parameter ``params``.
        """
        if type(values) not in [list,numpy.ndarray] and not callable(values):
            msg  = "\n### ERROR ### ParametersBase.add.\n"
            msg += "              Parameter 'values' should be a 'list', 'numpy.ndarray', or a 'lambda function'.\n"
            raise Exception(msg)

        kind = None
        if type(values) in [list,numpy.ndarray]:
            kind = ParameterBase.INDEPENDENT
        elif callable(values):
            kind = ParameterBase.DEPENDENT

        self.__setitem__( name, ParameterBase( name_in_settings, kind, values ) )


    def set_generator(self, generator):
        self._generator = generator


    def values(self):
        settings = Settings()
        indices,parameters_values,settings_list = self._generator( settings, self )

        return parameters_values


    @staticmethod
    def zipGenerator( reference_settings, parameters ):

        independent_params = []
        size = None
        for name,item in parameters.items():
            if item.kind == ParameterBase.INDEPENDENT:
                independent_params.append( item.values )
                if size is None:
                    size = len(item.values)
                elif size != len(item.values):
                    msg  = "\n### ERROR ### ParametersBase.zipGenerator().\n"
                    msg += "              All parameter in 'generator_parameters' should be lists of the same size.\n"
                    raise Exception(msg)

        if size == 0:
            msg  = "\n### ERROR ### ParametersBase.zipGenerator().\n"
            msg += "              All parameter in 'generator_parameters' should be lists with at least one element.\n"
            raise Exception(msg)

        indices = list( range(size) )
        parameters_values = {}
        settings_list = {}

        for idx in indices:
            settings_idx = reference_settings.copy()

            params = {}
            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ParameterBase.INDEPENDENT:
                    value = independent_params[i][idx]
                    eval('settings_idx'+item.name2setitem().replace('$var_value',str(value)))
                    params[name] = value

            for i,(name,item) in enumerate(parameters.items()):
                if item.kind == ParameterBase.DEPENDENT:
                    value = item.values(params)
                    eval('settings_idx'+item.name2setitem().replace('$var_value',str(value)))
                    params[name] = value

            parameters_values[idx] = params
            settings_list[idx] = settings_idx

        return indices,parameters_values,settings_list
