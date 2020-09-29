"""Module containing the ElementaryReaction class."""

from typing import List
from collections import Counter
from pyzacros.classes.Species import Species


class ElementaryReaction:

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

        :parm site_types: list
        :parm neighboring: list
        :parm initial: List[Species]
        :parm final: List[Species]
        :parm reversible: bool
        :parm pre_expon: float
        :parm pe_ratio: float
        :parm activation_energy: float
        """
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

        # Check deniticies:
        initial_total_denticity = 0
        final_total_denticity = 0
        for i in self.initial:
            if (i.symbol != "*" and i.is_adsorbed()):
                initial_total_denticity += i.denticity
        for i in self.final:
            if (i.symbol != "*" and i.is_adsorbed()):
                final_total_denticity += i.denticity
        if (initial_total_denticity > self.sites
           or final_total_denticity > self.sites):
            msg = "### ERROR ### ElementaryReaction.__init__.\n"
            msg += "Inconsistent dimensions for sites, initial or final.\n"
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

        :rparam reaction_label: Label of the elementary reaction.
        :rtype: String.
        """
        reaction_label = ""
        # FIXME reaction label is not as complex as it was before
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

    def __str__(self) -> str:
        """Translate the object to a string."""
        if(self.reversible):
            output = "reversible_step " + self.label() + "\n"
        else:
            output = "step " + self.label() + "\n"

        if (len(count_gas_species(self.initial)) != 0
           or len(count_gas_species(self.final)) != 0):

            output += "  gas_reacs_prods "

            gas_species_freqs = Counter([s for s
                                        in count_gas_species(self.initial)])
            i = 0
            for symbol, freq in gas_species_freqs.items():
                output += symbol+" "+str(-freq) + " "
                if (i != len(gas_species_freqs)-1):
                    output += " "
                i += 1

            gas_species_freqs = Counter([s for s
                                        in count_gas_species(self.final)])
            i = 0
            for symbol, freq in gas_species_freqs.items():
                output += symbol+" "+str(freq) + " "
                if(i != len(gas_species_freqs)-1):
                    output += " "
                i += 1
            output += "\n"

        if(self.sites != 0):
            output += "  sites " + str(self.sites)+"\n"
            if self.neighboring is not None:
                output += "  neighboring "
                for i in range(len(self.neighboring)):
                    output += str(self.neighboring[i][0]) + \
                             "-"+str(self.neighboring[i][1])
                    if(i != len(self.neighboring)-1):
                        output += " "
                output += "\n"

        # Print initial and final blocks:
            output += "  initial"+"\n"
            i = 1
            for species in self.initial:
                if species.is_adsorbed():
                    output += "\t" + str(i) + "\t" + str(species) + "\t" \
                            + str(species.denticity)
                    i += 1
                    output += "\n"

            output += "  final"+"\n"
            i = 1
            for species in self.final:
                if species.is_adsorbed():
                    output += "\t" + str(i) + "\t" + str(species) + "\t" \
                            + str(species.denticity)
                    i += 1
                    output += "\n"

            output += "  site_types "
            for i in range(len(self.site_types)):
                output += str(self.site_types[i])
                if(i != len(self.site_types)-1):
                    output += " "
            output += "\n"

        output += "  pre_expon "+("%e"%self.pre_expon)+"\n"
        if self.reversible is True:
            output += "  pe_ratio "+str(self.pe_ratio)+"\n"
        output += "  activ_eng "+str(self.activation_energy)+"\n"
        if self.reversible is True:
            output += "end_reversible_step"
        else:
            output += "end_step"

        return output


def count_gas_species(list_of_species: List[Species]) -> list:
    """Provide labels of gas species in a List[Species]."""
    list_gas_species = []
    for i in list_of_species:
        if i.is_gas():
            list_gas_species.append(i.symbol)
    return list_gas_species
