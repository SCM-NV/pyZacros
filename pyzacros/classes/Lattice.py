# -*- PLT@NLeSC(2020) -*-                                                             
"""Module containing the Lattice class."""


class Lattice():
    """
    **summary line** Lattice class defining the KMC surface slab.

    :parm lattice_type: Allows the user to construct a lattice by giving
                        information about the unit cell.
    :type lattice_type: str, required.

    :parm cell_vectors: Define the unit vectors.
    :type cell_vectors: tuple, required.

    :parm repeat_cell: The number of repetitions of the unit cell in the
                       directions of unit vectors.
    :type repeat_cell: tuple, required.

    :parm n_cell_sites: The total number of sites (of any site type) in the
                        unit cell.
    :type n_cell_sites: int, required.

    :parm n_site_types: The number of different site types.
    :type n_site_types: int, required.

    :parm site_type_names: The names of the different site types.
    :type site_type_names: tuple, required.

    :parm site_types: The site types for each of the different sites of
                      the unit cell.
    :type site_types: tuple, required.

    :parm site_coordinates: Pairs of real numbers specifying the
                            “fractional coordinates” of each site
                             in the unit cell.
    :type site_coordinates: tuple, required.
    
    :parm neighboring_structure: Defines a neighboring structure block.
    :type neighboring_structure: tuple, required.
    """

    def __init__(self, lattice_type: str,
                 cell_vectors: tuple,
                 repeat_cell: tuple,
                 n_cell_sites: int,
                 n_site_types: int,
                 site_type_names: tuple,
                 site_types: tuple,
                 site_coordinates: tuple,
                 neighboring_structure: tuple):
        """Initialize the Lattice class."""
        self.lattice_type = lattice_type
        self.cell_vectors = cell_vectors
        self.repeat_cell = repeat_cell
        self.n_cell_sites = n_cell_sites
        self.n_site_types = n_site_types
        self.site_type_names = site_type_names
        self.site_types = site_types
        self.site_coordinates = site_coordinates
        self.neighboring_structure = neighboring_structure

    def __str__(self) -> str:
        """Translate the object to a string."""
        output = "lattice"+"\t"+self.lattice_type+"\n"

        output += "cell_vectors"
        for i in range(2):
            output += "\n"
            for j in range(2):
                output += "\t"+str(self.cell_vectors[i][j])

        output += "\nrepeat_cell\t"
        output += str(str(self.repeat_cell)[1:-1]).replace(',', '')

        output += "\nn_cell_sites\t"+str(self.n_cell_sites)

        output += "\nn_site_types\t"+str(self.n_site_types)

        output += "\nsite_type_names\t" \
                  + str(' '.join(str(x) for x in self.site_type_names))

        output += "\nsite_types\t" \
                  + str(' '.join(str(x) for x in self.site_types))

        output += "\nsite_coordinates"
        for i in range(self.n_cell_sites):
            output += "\n"
            for j in range(2):
                output += "\t"+str(self.site_coordinates[i][j])

        output += "\nneighboring_structure"
        for i in range(len(self.neighboring_structure)):
            output += "\n"
            output += "\t"+str(' '.join(str(self.neighboring_structure[i][j])
                               for j in range(2)))
        output += "\nend_neighboring_structure"
        output += "\nend_lattice"

        return output
