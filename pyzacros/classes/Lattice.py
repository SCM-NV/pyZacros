# -*- PLT@NLeSC(2020) -*-                                                             
"""Module containing the Lattice class."""

from pyzacros.utils.io_utils import read_slab


class Lattice():
    """
    **summary line** Lattice class defining the KMC surface slab.

    :parm lattice_type: Allows the user to construct a lattice by giving
                        information about the unit cell.
    :type lattice_type: str, optional.

    :parm cell_vectors: Define the unit vectors.
    :type cell_vectors: tuple, optional.

    :parm repeat_cell: The number of repetitions of the unit cell in the
                       directions of unit vectors.
    :type repeat_cell: tuple, optional.

    :parm n_cell_sites: The total number of sites (of any site type) in the
                        unit cell.
    :type n_cell_sites: int, optional.

    :parm n_site_types: The number of different site types.
    :type n_site_types: int, optional.

    :parm site_type_names: The names of the different site types.
    :type site_type_names: tuple, optional.

    :parm site_types: The site types for each of the different sites of
                      the unit cell.
    :type site_types: tuple, optional.

    :parm site_coordinates: Pairs of real numbers specifying the
                            “fractional coordinates” of each site
                             in the unit cell.
    :type site_coordinates: tuple, optional.
    
    :parm neighboring_structure: Defines a neighboring structure block.
    :type neighboring_structure: tuple, optional.
    """

    def __init__(self, lattice_type: str = None,
                 cell_vectors: tuple = None,
                 repeat_cell: tuple = None,
                 n_cell_sites: int = None,
                 n_site_types: int = None,
                 site_type_names: tuple = None,
                 site_types: tuple = None,
                 site_coordinates: tuple = None,
                 neighboring_structure: tuple = None,
                 path_to_slab_yaml: str = None):
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

        if path_to_slab_yaml:
            print("Constructing KMC slab from YAML file:", path_to_slab_yaml)
            read_slab(path_to_slab_yaml)
        else:
            if not lattice_type:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "lattice_type argument is missed!\n"
                raise NameError(msg)
            if not cell_vectors:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "cell_vectors argument is missed!\n"
                raise NameError(msg)
            if not repeat_cell:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "repeat_cell argument is missed!\n"
                raise NameError(msg)
            if not n_cell_sites:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "n_cell_sites argument is missed!\n"
                raise NameError(msg)
            if not n_site_types:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "n_site_types argument is missed!\n"
                raise NameError(msg)
            if not site_type_names:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "site_type_names argument is missed!\n"
                raise NameError(msg)
            if not site_types:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "site_types argument is missed!\n"
                raise NameError(msg)
            if not site_coordinates:
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "site_coordinates argument is missed!\n"
                raise NameError(msg)
            if not neighboring_structure: 
                msg = "### ERROR ### Lattice.__init__.\n"
                msg += "neighboring_structure argument is missed!\n"
                raise NameError(msg)

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
