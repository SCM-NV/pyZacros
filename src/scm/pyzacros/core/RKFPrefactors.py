import chemparse

__all__ = ['RKFPrefactors']

class RKFPrefactors:
    """
    Contains the information needed to calculate the prefactors based on kf files from an AMS calculation

    *   ``temperature`` --
    *   ``kf_initial`` --
    *   ``kf_final`` --

    Example

    kind = MEDIATED_BY_A_TRANSITION_STATE
    kf_initial = 'State-1_MIN.rkf'
    kf_final = 'State-4_TS_1-3.rkf'

    kind = NON_ACTIVATED_EXOTHERMIC_DESORPTION
    kf_initial = 'State-1_MIN.rkf'
    kf_final = ['Fragment-1.rkf', 'Fragment-2.rkf']

    kind = NON_ACTIVATED_EXOTHERMIC_ADSORPTION
    kf_initial = ['Fragment-1.rkf', 'Fragment-2.rkf']
    kf_final = None
    """

    UNSPECIFIED = -1
    MEDIATED_BY_A_TRANSITION_STATE = 0
    NON_ACTIVATED_EXOTHERMIC_ADSORPTION = 1
    NON_ACTIVATED_EXOTHERMIC_DESORPTION = 2

    def __init__(self, temperature=None, kind=None, kf_initial=None, kf_final=None ):
        """
        Creates a new RKFPrefactors object.
        """
        self.temperature = temperature
        self.kind = kind
        self.kf_initial = kf_initial
        self.kf_final = kf_final


    def __eq__( self, other ):
        """
        Returns True if both objects are the same (same temperature, and kf files)

        *   ``other`` --
        """
        if( type(other) == int and other == Species.UNSPECIFIED ):
            return False

        if( self.symbol == other.symbol ):
            return True
        else:
            return False


    def __hash__(self):
        """
        Returns a hash based on the symbol.
        """
        return hash(self.symbol)


    def __str__( self ):
        """
        Translates the object to a string
        """
        output  = self.symbol
        return output
