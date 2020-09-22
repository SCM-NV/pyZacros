# -*- PLT@NLeSC(2020) -*-
"""Module containing the Lattice class."""

from os import path
import yaml


class Lattice():
    """
    **summary line** Lattice class defining the KMC surface slab.

    :parm lattice_type: Allows the user to construct a lattice by giving
                        information about the unit cell.
    :type lattice_type: str, optional.

    :parm default_lattice: If lattice_type == 'default_choice', then
                          default_lattice must be declared as:
                          - triangular_periodic
                          - rectangular_periodic
                          - hexagonal_periodic
                         followed by one float and two integer numbers.
    :type default_lattice: list, optional.

    :parm cell_vectors: Define the unit vectors.
    :type cell_vectors: list, optional.

    :parm repeat_cell: The number of repetitions of the unit cell in the
                       directions of unit vectors.
    :type repeat_cell: list, optional.

    :parm n_cell_sites: The total number of sites (of any site type) in the
                        unit cell.
    :type n_cell_sites: int, optional.

    :parm n_site_types: The number of different site types.
    :type n_site_types: int, optional.

    :parm site_type_names: The names of the different site types.
    :type site_type_names: list, optional.

    :parm site_types: The site types for each of the different sites of
                      the unit cell.
    :type site_types: list, optional.

    :parm site_coordinates: Pairs of real numbers specifying the
                            “fractional coordinates” of each site
                             in the unit cell.
    :type site_coordinates: list, optional.

    :parm neighboring_structure: Defines a neighboring structure block.
    :type neighboring_structure: list, optional.

    :parm path_to_slab_yaml: Path to .yml or .yaml kmc slab file.
    :type site_coordinates: str, optional.
    """

    def __init__(self, lattice_type: str = None,
                 default_lattice: list = None,
                 cell_vectors: list = None,
                 repeat_cell: list = None,
                 n_cell_sites: int = None,
                 n_site_types: int = None,
                 site_type_names: list = None,
                 site_types: list = None,
                 site_coordinates: list = None,
                 neighboring_structure: list = None,
                 path_to_slab_yaml: str = None):
        """Initialize the Lattice class."""
        self.lattice_type = lattice_type
        self.default_lattice = default_lattice
        self.cell_vectors = cell_vectors
        self.repeat_cell = repeat_cell
        self.n_cell_sites = n_cell_sites
        self.n_site_types = n_site_types
        self.site_type_names = site_type_names
        self.site_types = site_types
        self.site_coordinates = site_coordinates
        self.neighboring_structure = neighboring_structure

        argument_dict = locals()
        i = None

        if path_to_slab_yaml is not None:
            # Read arguments from .yaml file:
            if not path.exists(path_to_slab_yaml):
                msg = "### ERROR ### Lattice class.\n"
                msg += "KMC slab file not found.\n"
                raise FileNotFoundError(msg)

            else:
                print("Constructing KMC slab from YAML file:\n",
                      path_to_slab_yaml)
                # Read .yaml dicctionary:
                yaml_dict = path_to_slab_yaml
                with open(yaml_dict, 'r') as f:
                    KMC_list = yaml.load(f, Loader=yaml.FullLoader)

                # Loop on the None defined arguments:
                for i in argument_dict.keys():
                    if i != 'default_lattice' and argument_dict[i] is None:
                        argument_dict[i] = KMC_list[i]
                        setattr(self, i, argument_dict[i])
        else:
            # Reading arguments from user defined object:
            del argument_dict['path_to_slab_yaml']
            # Rise errors when the object is defined by the user:
            if self.lattice_type == 'default_choice':
                if not self.default_lattice:
                    msg = "### ERROR ### Lattice.__init__.\n"
                    msg += "default_choice requires a default_lattice\
 argument.\n"
                    raise NameError(msg)
            else:
                for i in argument_dict.keys():
                    if i != 'default_lattice' and argument_dict[i] is None:
                        msg = "### ERROR ### Lattice.__init__.\n"
                        msg += str(i) + " argument is missed.\n"
                        raise NameError(msg)


    def __str__(self) -> str:
        """Translate the object to a string."""
        output = "lattice"+" "+self.lattice_type+"\n"
        if self.default_lattice is not None:
            for i in range(4):
                output += str(self.default_lattice[i]) + " "
        else:
            output += "cell_vectors"
            for i in range(2):
                output += "\n"
                for j in range(2):
                    output += "  "+("%.5f"%self.cell_vectors[i][j])

            output += "\nrepeat_cell "
            output += str(str(self.repeat_cell)[1:-1]).replace(',', '')

            output += "\nn_cell_sites "+str(self.n_cell_sites)

            output += "\nn_site_types "+str(self.n_site_types)

            output += "\nsite_type_names " \
                      + str(' '.join(str(x) for x in self.site_type_names))

            output += "\nsite_types " \
                      + str(' '.join(str(x) for x in self.site_types))

            output += "\nsite_coordinates"
            for i in range(self.n_cell_sites):
                output += "\n"
                for j in range(2):
                    output += "  "+("%.5f"%self.site_coordinates[i][j])

            output += "\nneighboring_structure"
            for i in range(len(self.neighboring_structure)):
                output += "\n"
                output += "  "+str(' '.join(str(self.neighboring_structure[i][j])
                                   for j in range(2)))
            output += "\nend_neighboring_structure"
            output += "\nend_lattice"

        return output
