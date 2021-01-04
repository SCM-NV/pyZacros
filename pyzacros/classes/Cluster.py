"""Module containing the Cluster class."""
from typing import List
from pyzacros.classes.Species import Species


class Cluster:
    """Cluster class."""
    # TODO insert 2NN and 3NN interactions.

    def __init__(self, site_types: list,
                 species: List[Species],
                 neighboring: list = None,
                 multiplicity: int = 1, 
                 cluster_energy: float = 0.000):
        """
        Create a new Cluster object.

        :param site_types: list
        :param neighboring: list
        :param species: list
        :param multiplicity: int
        :param cluster_energy: float
        """
        self.site_types = site_types                  # e.g. [ "f", "f" ]
        self.neighboring = neighboring                # e.g. [ (1,2) ]
        self.species = species                        # e.g. [ Species("H*",1), Species("H*",1) ]
        self.multiplicity = multiplicity              # e.g. 2
        self.cluster_energy = cluster_energy          # Units eV

        if(sum(s.denticity for s in self.species) != len(self.site_types)):
            msg = "### ERROR ### Cluster.__init__.\n"
            msg += "Inconsistent dimensions for species or site_types\n"
            raise NameError(msg)

    def __eq__(self, other):
        """Return True if both objects have the same label."""
        if(self.label == other.label):
            return True
        else:
            return False

    def __hash__(self):
        """Return a hash based on the label."""
        return hash(self.__label)

    def label(self) -> str:
        """Return the label of the cluster."""
        cluster_label = ""
        if len(self.species) == 1:
            cluster_label += self.species[0].symbol.replace("*", "") + "_point"
        elif len(self.species) == 2:
            cluster_label += self.species[0].symbol.replace("*", "")
            cluster_label += "-"
            cluster_label += self.species[1].symbol.replace("*", "")
            cluster_label += "_1NN"
        # TODO include 2NN and 3NN labeling.
        return cluster_label

    def mass(self) -> float:
        """Return the mass of the cluster in Da."""
        return self.__mass
