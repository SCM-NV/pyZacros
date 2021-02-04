"""Module containing the ElementaryReaction class."""

from typing import List
from pyzacros.classes.Species import Species


class ElementaryReaction:
    """ElementaryReaction class."""

    def __init__(self,
                 site_types: list,
                 initial: List[Species],
                 final: List[Species],
                 neighboring: list = None,
                 reversible: bool = True,
                 pre_expon: float = 0.0,
                 pe_ratio: float = 0.0,
                 activation_energy: float = 0.0):
        """
        Create a new ElementaryReaction object.

        :param site_types: list, different odsorbing sites on the catalytic
                          surface.
        :param neighboring: list, connections between different unit cell
                           slab replicas.
        :param initial: List[Species], reactant species.
        :param final: List[Species], product species.
        :param reversible: bool, whether the reaction is reversible or not.
        :param pre_expon: float, Arrhenius prefactor.
        :param pe_ratio: float, ratio of forward over reverse pre-exponentials.
        :param activation_energy: float
        """
        # Define attributes an check masses and denticities:
        self.site_types = site_types    # e.g. [ "f", "f" ]
        self.neighboring = neighboring  # e.g. [ (1,2) ]
        self.initial = initial
        self.final = final
        self.reversible = reversible
        self.pre_expon = pre_expon
        self.pe_ratio = pe_ratio
        self.activation_energy = activation_energy     # e.g. 0.200
        self.sites = len(site_types)
        self._check_ElementaryReaction()

    def __eq__(self, other):
        """Return True if both objects have the same label. False otherwise."""
        if (self.label() == other.label()):
            return True
        else:
            return False

    def __hash__(self):
        """Return a hash based on the label."""
        return hash(self.label())

    def _check_ElementaryReaction(self):
        """Check types, denticity and masses of the ElementaryReaction."""
        # Check the types of initial and final arguments:
        if(type(self.initial) != list or type(self.final) != list):
            msg = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "initial or final states must be a list of Species.\n"
            raise NameError(msg)

        # Check denticities are not bigger than the site_types available, i.e.
        # we assume that all species have all the dents linked to the surface.
        initial_total_denticity = 0
        final_total_denticity = 0
        for i in self.initial:
            if i.is_adsorbed():
                initial_total_denticity += i.denticity
        for i in self.final:
            if i.is_adsorbed():
                final_total_denticity += i.denticity
        if (initial_total_denticity > self.sites
           or final_total_denticity > self.sites):
            msg = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "Inconsistency between the number of site_types and \n"
            msg += "the total denticity of initial or final species.\n"
            raise NameError(msg)

        # Check masses:
        initial_total_mass = 0.0
        final_total_mass = 0.0
        for i in self.initial:
            initial_total_mass += i.mass()
        for i in self.final:
            final_total_mass += i.mass()
        if(abs(initial_total_mass - final_total_mass) > 1e-6):
            msg = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "The mass is not conserved during the reaction:\n"
            msg += "mass(initial)="+str(initial_total_mass)+", \
            mass(final)="+str(final_total_mass)
            raise NameError(msg)

    def label(self) -> str:
        """
        Return the label of the ElementaryReaction.

        :return: A string with the label of the ElementaryReaction.
        """
        reaction_label = ""
        # FIXME reaction label is not as complex as
        # constructing the mechanisms from clusters.
        # I use the sense of the reactions, initial ---> final
        for i, species in enumerate(self.initial):
            reaction_label += str(species.symbol)
            if species.is_gas():
                reaction_label += str("(gas)")
            if i != (len(self.initial)-1):
                reaction_label += str("+")
        # Arrows:
        if(self.reversible):
            reaction_label += "<-->"
        else:
            reaction_label += "--->"
        # Final species:
        for i, species in enumerate(self.final):
            reaction_label += str(species.symbol)
            if species.is_gas():
                reaction_label += str("(gas)")
            if i != (len(self.final)-1):
                reaction_label += str("+")
        return reaction_label
