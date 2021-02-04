"""Module containing the InitalState class."""
import random

from pyzacros.classes.ElementaryReaction import ElementaryReaction
from pyzacros.classes.Species import Species
from pyzacros.classes.Lattice import Lattice
from typing import List


class InitialState:
    """
    InitialState class that represents the initial coating of the surface.

    By default a KMC simulation in Zacros is initialized with an empty lattice.
    """

    def __init__(self, lattice: Lattice, mechanism: List[ElementaryReaction]):
        """
        Create a new InitialState object.

        :parm mechanism: Mechanism containing the mechanisms involved in the
                        calculation.
        :parm lattice: Lattice containing the lattice to be used during the
                       calculation.
        """
        self.lattice = lattice
        self.mechanism = mechanism
        self.filledSitesPerSpecies = {}

        # TODO We need to make a way to check if a lattice is compatible
        # with the mechanism.

    def empty(self):
        """Return true if the initial state is empty."""
        return(len(self.filledSitesPerSpecies) > 0)

    def fillSites(self, site_name: str, species: Species, coverage:  float):
        """
        Fill the sites of the surface slab.

        :param site_name: String of the site name of the slab to be covered.

        :param species: Species instance to fill in the site_name of the slab.

        :param coverage: The coverage of the surface.
        """
        effSpecies = None
        if not (isinstance(species, Species)):
            msg = "### ERROR ### InitialState.fillSites.\n"
            msg += "             Inconsistent type for species. It should be\n"
            msg += "             a Species instance.\n"
            raise NameError(msg)
        else:
            effSpecies = species

        if(effSpecies.denticity > 1):
            msg = "### ERROR ### InitialState.fillSites.\n"
            msg += "             Species with denticity > 1 are not yet\n"
            msg += "             supported\n"
            raise NameError(msg)

        # Makes a list of the filled sites
        filledSites = []
        for key, value in self.filledSitesPerSpecies.items():
            filledSites.extend(value)

        filledSitesPerSpecies = {}
        nx = self.lattice.repeat_cell[0]
        ny = self.lattice.repeat_cell[1]

        nSitesOfThisKind = 0
        k = 1  # Zacros starts in 1
        for i in range(nx):
            for j in range(ny):
                for idSite, sname in enumerate(self.lattice.site_types):

                    if(sname == site_name):
                        if(effSpecies not in filledSitesPerSpecies):
                            filledSitesPerSpecies[effSpecies] = []

                        if(k not in filledSites):
                            filledSitesPerSpecies[effSpecies].append(k)
                            filledSites.append(k)

                        nSitesOfThisKind += 1

                    k += 1

        nSitesToKeep = round(nSitesOfThisKind*coverage)

        # Removes elements according with the coverage
        for key, value in filledSitesPerSpecies.items():
            random.shuffle(filledSitesPerSpecies[key])

            while(len(filledSitesPerSpecies[key]) > nSitesToKeep):
                filledSitesPerSpecies[key].pop()

        # Removes empty sites per species
        toRemove = []
        for key, value in filledSitesPerSpecies.items():
            if(len(filledSitesPerSpecies[key]) == 0):
                toRemove.append(key)

        for key in toRemove:
            filledSitesPerSpecies.pop(key)

        # Updates self.__filledSitesPerSpecies
        for key, value in filledSitesPerSpecies.items():
            if(key in self.filledSitesPerSpecies):
                self.filledSitesPerSpecies[key].extend(value)
            else:
                self.filledSitesPerSpecies[key] = value

            self.filledSitesPerSpecies[key] = sorted(
                 self.filledSitesPerSpecies[key])

    def fillAllSites(self, site_name, species):
        """Fill all the sites."""
        self.fillSites(site_name, species, coverage=1.0)