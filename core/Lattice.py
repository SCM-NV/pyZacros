"""Module containing the Lattice class."""

from os import path
import math
import yaml

__all__ = ['Lattice']

class Lattice:
    """
    Lattice class that defines the lattice structure on which species can bind, diffuse and react.
    As in Zacros' original input files, there are three different ways of specifying a lattice structure.
    Below we describe these three ways with the corresponding parameters as well with examples of use.

    **Default Lattices:**

    * ``lattice_type`` -- Define the lattice to use. Possible options are:

      - ``Lattice.TRIANGULAR``: Specifies a lattice with coordination number 3. The unit cell contains 4 sites.
      - ``Lattice.RECTANGULAR``: Specifies a lattice with coordination number 4. The unit cell contains 1 site.
      - ``Lattice.HEXAGONAL``: Specifies a lattice with coordination number 6. The unit cell contains 2 sites.

    * ``lattice_constant`` -- Defines the lattice constant (in angstrom).
    * ``repeat_cell`` -- The number of repetitions of the unit cell in the directions of unit vectors.

    Example:

    .. code:: python

        lattice = pz.Lattice( lattice_type=pz.Lattice.HEXAGONAL, lattice_constant=1.0,
                              repeat_cell=[4,5] )

    .. image:: ../../images/lattice_default.png
       :align: center

    **Unit-Cell-Defined Periodic Lattices:**

    * ``cell_vectors`` -- Define the unit vectors. *e.g.* ``[[0.123, 0.000],[1.234,1.234]]``
    * ``repeat_cell`` -- The number of repetitions of the unit cell in the directions of unit vectors. *e.g.* ``(10,10)``
    * ``site_types`` -- The names of the different site types. *e.g.* ``[ "cn2", "br42", "cn2" ]``
    * ``site_coordinates`` -- Pairs of real numbers specifying the “fractional coordinates” of each site
      in the unit cell. *e.g.* ``[ (0.123,0.894), (0.456,0.123) ]``
    * ``neighboring_structure`` -- Defines a neighboring structure block. *e.g.*
      ``[ ((0,0),Lattice.NORTH), ((0,1),Lattice.NORTHEAST) ]``

    Example:

    .. code:: python

        lattice = pz.Lattice( cell_vectors=[[2.77185866, 0.00000000],[1.38592933, 2.40050002]],
                              repeat_cell=[2, 2],
                              site_types=["b", "h", "b", "b", "f", "t"],
                              site_coordinates=[[0.00001, 0.49999],
                                                [0.33333, 0.33333],
                                                [0.49999, 0.00001],
                                                [0.49999, 0.49999],
                                                [0.66667, 0.66667],
                                                [0.99999, 0.00001]],
                              neighboring_structure=[ [(0,1), pz.Lattice.SELF],
                                                      [(1,2), pz.Lattice.SELF],
                                                      [(1,3), pz.Lattice.SELF],
                                                      [(3,4), pz.Lattice.SELF],
                                                      [(4,2), pz.Lattice.NORTH],
                                                      [(4,0), pz.Lattice.EAST],
                                                      [(5,5), pz.Lattice.NORTH],
                                                      [(5,5), pz.Lattice.EAST],
                                                      [(5,4), pz.Lattice.SELF],
                                                      [(5,1), pz.Lattice.SELF],
                                                      [(5,1), pz.Lattice.EAST],
                                                      [(5,4), pz.Lattice.SOUTHEAST],
                                                      [(5,1), pz.Lattice.SOUTHEAST],
                                                      [(4,5), pz.Lattice.NORTH],
                                                      [(5,5), pz.Lattice.SOUTHEAST] ] )

    .. image:: ../../images/lattice_unit_cell.png
       :align: center

    **Explicitly Defined Custom Lattices:**

    * ``site_types`` -- The names of the different site types. *e.g.* ``[ "cn2", "br42" ]``
    * ``site_coordinates`` -- Pairs of real numbers specifying the “fractional coordinates” of each site
      in the unit cell. *e.g.* ``[ (0.123,0.894), (0.456,0.123) ]``
    * ``nearest_neighbors`` -- Defines the neighboring structure. *e.g.* ``[ (2,6), (2,4,7,8) ]``
    * ``cell_vectors`` -- Define the unit vectors. Optional

    Example:

    .. code:: python

        lattice = pz.Lattice( site_types=["cn2", "br42", "cn4", "br42", "cn2", "br42",
                                          "br44", "br44", "br42", "cn4", "br44", "cn4",
                                          "br42", "br42", "cn2"],
                              site_coordinates=[[0.0000e+0, 0.0000e+0],
                                                [1.4425e+0, 0.0000e+0],
                                                [2.8850e+0, 0.0000e+0],
                                                [4.3275e+0, 0.0000e+0],
                                                [5.7700e+0, 0.0000e+0],
                                                [7.2125e-1, 1.2492e+0],
                                                [2.1637e+0, 1.2492e+0],
                                                [3.6062e+0, 1.2492e+0],
                                                [5.0487e+0, 1.2492e+0],
                                                [1.4425e+0, 2.4985e+0],
                                                [2.8850e+0, 2.4985e+0],
                                                [4.3275e+0, 2.4985e+0],
                                                [2.1637e+0, 3.7477e+0],
                                                [3.6062e+0, 3.7477e+0],
                                                [2.8850e+0, 4.9970e+0]],
                              nearest_neighbors=[[ 1,  5],
                                                 [ 0,  2],
                                                 [ 1,  3,  6, 7],
                                                 [ 2,  4],
                                                 [ 3,  8],
                                                 [ 0,  9],
                                                 [ 2,  9],
                                                 [ 2, 11],
                                                 [ 4, 11],
                                                 [ 5,  6, 10, 12],
                                                 [ 9, 11],
                                                 [ 7,  8, 10, 13],
                                                 [ 9, 14],
                                                 [11, 14],
                                                 [12, 13]] )

    .. image:: ../../images/lattice_custom.png
       :align: center

    """

    # Origin
    __FROM_DEFAULT = 0
    __FROM_UNIT_CELL = 1
    __FROM_EXPLICIT = 2

    # Default lattices
    TRIANGULAR = 3
    RECTANGULAR = 4
    HEXAGONAL = 6

    # Neighboring_structure
    SELF = (0,0)
    NORTH = (0,1)
    NORTHEAST = (1,1)
    EAST = (1,0)
    SOUTHEAST = (1,-1)

    __NeighboringToStr = { SELF:"self", NORTH:"north", NORTHEAST:"northeast", EAST:"east", SOUTHEAST:"southeast" }

    def __init__(self, **kwargs):
        self.cell_vectors = None
        self.site_types = None
        self.site_coordinates = None
        self.nearest_neighbors = None

        self.__origin = None

        # Default Lattices
        if( "lattice_type" in kwargs and
            "lattice_constant" in kwargs and
            "repeat_cell" in kwargs ):
            self.__origin = Lattice.__FROM_DEFAULT
            self.__lattice_type_default = None
            self.__lattice_constant_default = None
            self.__repeat_cell_default = None

            self.__fromDefaultLattices( kwargs["lattice_type"], kwargs["lattice_constant"], kwargs["repeat_cell"] )

        # Unit-Cell-Defined Periodic Lattices
        elif( "cell_vectors" in kwargs and
              "repeat_cell" in kwargs and
              "site_types" in kwargs and
              "site_coordinates" in kwargs and
              "neighboring_structure" in kwargs ):
            self.__origin = Lattice.__FROM_UNIT_CELL
            self.__cell_vectors_unit_cell = None
            self.__repeat_cell_unit_cell = None
            self.__site_types_unit_cell = None
            self.__site_coordinates_unit_cell = None
            self.__neighboring_structure_unit_cell = None

            self.__fromUnitCellDefined( kwargs["cell_vectors"], kwargs["repeat_cell"], kwargs["site_types"],
                                                kwargs["site_coordinates"], kwargs["neighboring_structure"] )

        # Explicitly Defined Custom Lattices
        elif( "site_types" in kwargs and
              "site_coordinates" in kwargs and
              "nearest_neighbors" in kwargs ):
            self.__origin = Lattice.__FROM_EXPLICIT

            self.__fromExplicitlyDefined( kwargs["site_types"], kwargs["site_coordinates"],
                                                  kwargs["nearest_neighbors"], cell_vectors=kwargs.get("cell_vectors") )

        ## From YAML file
        #elif( "path" in kwargs ):
            #self.__fromYAMLfile( kwargs["path"] )

        else:
            msg  = "\nError: The constructor for Lattice with the parameters:"+str(kwargs)+" is not implemented!\n"
            msg += "       Available options:\n"
            msg += "       - Lattice( lattice_type, lattice_constant, repeat_cell )\n"
            msg += "       - Lattice( cell_vectors, repeat_cell, site_types, site_coordinates, neighboring_structure )\n"
            msg += "       - Lattice( site_types, site_coordinates, nearest_neighbors, cell_vectors=None )\n"
            msg += "       - Lattice( path )\n"
            raise Exception(msg)


    def __fromDefaultLattices(self, lattice_type, lattice_constant, repeat_cell):
        """
        Creates a default Lattice
        """
        self.__lattice_type_default = lattice_type
        self.__lattice_constant_default = lattice_constant
        self.__repeat_cell_default = repeat_cell

        if( self.__lattice_type_default == Lattice.TRIANGULAR ):

            cell_vectors = [[lattice_constant*math.sqrt(3.0), 0.0],[0.0,3.0*lattice_constant]]
            site_types = ["StTp1", "StTp1", "StTp1", "StTp1"]
            site_coordinates = [[0.0, 0.0],[1.0/2.0, 1.0/6.0],[1.0/2.0, 1.0/2.0],[0.0, 2.0/3.0]]
            neighboring_structure=[ [(0,1), Lattice.SELF],
                                    [(1,2), Lattice.SELF],
                                    [(2,3), Lattice.SELF],
                                    [(1,0), Lattice.EAST],
                                    [(2,3), Lattice.EAST],
                                    [(3,0), Lattice.NORTH] ]

            self.__fromUnitCellDefined(cell_vectors, repeat_cell, site_types, site_coordinates, neighboring_structure)

        elif( self.__lattice_type_default == Lattice.RECTANGULAR ):

            cell_vectors = [[lattice_constant, 0.0],[0.0,lattice_constant]]
            site_types = ["StTp1"]
            site_coordinates = [[0.0, 0.0]]
            neighboring_structure=[ [(0,0), Lattice.NORTH],
                                    [(0,0), Lattice.EAST] ]

            self.__fromUnitCellDefined(cell_vectors, repeat_cell, site_types, site_coordinates, neighboring_structure)

        elif( self.__lattice_type_default == Lattice.HEXAGONAL ):

            cell_vectors = [[lattice_constant*math.sqrt(3.0), 0.0],[0.0,lattice_constant]]
            site_types = ["StTp1", "StTp1"]
            site_coordinates = [[0.0, 0.0],[0.5, 0.5]]
            neighboring_structure=[ [(0,0), Lattice.NORTH],
                                    [(0,1), Lattice.SELF],
                                    [(1,0), Lattice.NORTH],
                                    [(1,1), Lattice.NORTH],
                                    [(1,0), Lattice.NORTHEAST],
                                    [(1,0), Lattice.EAST] ]

            self.__fromUnitCellDefined(cell_vectors, repeat_cell, site_types, site_coordinates, neighboring_structure)


    def __fromUnitCellDefined(self, cell_vectors, repeat_cell, site_types, site_coordinates, neighboring_structure):
        """
        Creates a Unit-Cell-Defined periodic Lattice
        """
        assert( len(site_types) == len(site_coordinates) )

        self.__cell_vectors_unit_cell = cell_vectors
        self.__repeat_cell_unit_cell = repeat_cell
        self.__site_types_unit_cell = site_types
        self.__site_coordinates_unit_cell = site_coordinates
        self.__neighboring_structure_unit_cell = neighboring_structure

        ncellsites = len(site_types)
        ncells = repeat_cell[0]*repeat_cell[1]
        nsites = ncells*ncellsites

        self.cell_vectors = [ [repeat_cell[0]*a,repeat_cell[1]*b] for a,b in cell_vectors ]
        self.site_coordinates = nsites*[None]
        self.site_types = nsites*[None]
        self.nearest_neighbors = nsites*[None]

        def getcellnumber(i, j):
            if( i < 0 or j < 0 or i >= repeat_cell[0] or j >= repeat_cell[1] ):
                return None
            return i*repeat_cell[1] + j

        v1 = cell_vectors[0]
        v2 = cell_vectors[1]

        for i in range(repeat_cell[0]):
            for j in range(repeat_cell[1]):

                id_cell = i*repeat_cell[1] + j # cell counter

                xcellpos = i*v1[0] + j*v2[0] # cell position x
                ycellpos = i*v1[1] + j*v2[1] # cell position y

                for k in range(ncellsites):

                    id_site = ncellsites*id_cell + k

                    # x-y coordinates of the site
                    xsite = site_coordinates[k][0]*v1[0] + site_coordinates[k][1]*v2[0] + xcellpos
                    ysite = site_coordinates[k][0]*v1[1] + site_coordinates[k][1]*v2[1] + ycellpos

                    self.site_coordinates[id_site] = [xsite,ysite]
                    self.site_types[id_site] = site_types[k]

                    # neighboring structure
                    for (id_1,id_2),lDisp in neighboring_structure:  # ldisp=latteral displacements

                        if( id_1 == k ):
                            id_cell_2 = getcellnumber(i+lDisp[0],j+lDisp[1])
                            if( id_cell_2 is not None ):
                                id_2_shifted = ncellsites*id_cell_2 + id_2

                                if( self.nearest_neighbors[id_site] is None ):
                                    self.nearest_neighbors[id_site] = set()

                                self.nearest_neighbors[id_site].add( id_2_shifted )
                        if( id_2 == k ):
                            id_cell_1 = getcellnumber(i-lDisp[0],j-lDisp[1])
                            if( id_cell_1 is not None ):
                                id_1_shifted = ncellsites*id_cell_1 + id_1

                                if ( self.nearest_neighbors[id_site] is None ):
                                    self.nearest_neighbors[id_site] = set()

                                self.nearest_neighbors[id_site].add( id_1_shifted )



    def __fromExplicitlyDefined(self, site_types, site_coordinates, nearest_neighbors, cell_vectors=None):
        """
        Creates a explicitly defined custom Lattice
        """
        self.site_types = site_types
        self.site_coordinates = site_coordinates
        self.nearest_neighbors = nearest_neighbors
        self.cell_vectors = cell_vectors


    #def __fromYAMLfile(self, path):
        """
        :parm path_to_slab_yaml: Path to .yml or .yaml kmc slab file.
        """
        #argument_dict = locals()
        #i = None

        #if path_to_slab_yaml is not None:
            ## Read arguments from .yaml file:
            #if not path.exists(path_to_slab_yaml):
                #msg = "### ERROR ### Lattice class.\n"
                #msg += "KMC slab file not found.\n"
                #raise FileNotFoundError(msg)

            #else:
                #print("Constructing KMC slab from YAML file:\n",
                      #path_to_slab_yaml)
                ## Read .yaml dicctionary:
                #yaml_dict = path_to_slab_yaml
                #with open(yaml_dict, 'r') as f:
                    #KMC_list = yaml.load(f, Loader=yaml.FullLoader)

                ## Loop on the None defined arguments:
                #for i in argument_dict.keys():
                    #if i != 'default_lattice' and argument_dict[i] is None:
                        #argument_dict[i] = KMC_list[i]
                        #setattr(self, i, argument_dict[i])
        #else:
            ## Reading arguments from user defined object:
            #del argument_dict['path_to_slab_yaml'] # we don't need it.
            ## Rise errors when the object is defined by the user:
            #if self.lattice_type == 'default_choice':
                #if not self.default_lattice:
                    #msg = "### ERROR ### Lattice.__init__.\n"
                    #msg += "default_choice requires a default_lattice argument.\n"
                    #raise NameError(msg)
            #else:
                #for i in argument_dict.keys():
                    #if i != 'default_lattice' and argument_dict[i] is None:
                        #msg = "### ERROR ### Lattice.__init__.\n"
                        #msg += str(i) + " argument is missed.\n"
                        #raise NameError(msg)

        #raise Exception("Error: The constructor Lattice.__fromYAMLfile has not been implemented yet!")


    def plot(self, pause=-1, show=True, color=None, ax=None, close=False, show_sites_ids=False):
        """
        Uses Matplotlib to visualize the lattice. Be sure that Matplotlib is installed in your system; otherwise, the function does nothing.

        *   ``pause`` -- After showing the figure, it will wait ``pause``-seconds before refreshing. This can be used for crude animation.
        *   ``show`` -- Enables showing the figure on the screen.
        *   ``color`` -- Uses the same color for both binding sites and connections; e.g. 'k'. See `matplotlib.colors <https://matplotlib.org/stable/api/colors_api.html>`_.
        *   ``ax`` -- The axes of the plot. It contains most of the figure elements: Axis, Tick, Line2D, Text, Polygon, etc., and sets the coordinate system. See `matplotlib.axes <https://matplotlib.org/stable/api/axes_api.html#id2>`_.
        *   ``close`` -- Closes the figure window after pause time.
        *   ``show_sites_ids`` -- Shows the binding sites id on the figure.
        """
        try:
            import math
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError as e:
            return  # module doesn't exist, deal with it.

        if( ax is None ):
            fig,ax = plt.subplots()

        if( self.cell_vectors is not None ):
            v1 = self.cell_vectors[0]
            v2 = self.cell_vectors[1]
            xvalues = [0.0,v1[0],  v1[0]+v2[0],   v2[0],  0.0]
            yvalues = [0.0,v1[1],  v1[1]+v2[1],   v2[1],  0.0]

            lcolor = color if color is not None else 'k'
            ax.plot(xvalues, yvalues, color=lcolor, linestyle='dashed', linewidth=1, zorder=3)

            x_len = abs(v2[0]-v1[0])
            ax.set_xlim( [ 0.0-0.1*x_len, v1[0]+v2[0]+0.1*x_len ] )
            y_len = abs(v2[1]-v1[1])
            ax.set_ylim( [ 0.0-0.1*y_len, v1[1]+v2[1]+0.1*y_len ] )

            if( x_len > y_len ):
                ax.set_aspect(1.8*y_len/x_len)
            elif( y_len > x_len ):
                ax.set_aspect(1.8*x_len/y_len)
            elif( x_len == y_len ):
                ax.set_aspect(1.0)

            v1 = self.__cell_vectors_unit_cell[0]
            v2 = self.__cell_vectors_unit_cell[1]
            xvalues = [0.0,v1[0],  v1[0]+v2[0],   v2[0],  0.0]
            yvalues = [0.0,v1[1],  v1[1]+v2[1],   v2[1],  0.0]

            lcolor = color if color is not None else 'k'
            ax.plot(xvalues, yvalues, color=lcolor, linestyle='solid', linewidth=3, zorder=3)

        #ax.set_xlabel('x ($\AA$)')
        #ax.set_ylabel('y ($\AA$)')

        ax.set_xlabel('x (ang.)')
        ax.set_ylabel('y (ang.)')

        #markers = ['o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'd']
        markers = ['o', 's', 'v', '^']
        colors = ['r', 'g', 'b', 'm']

        for i,st_i in enumerate(list(set(self.site_types))):
            xvalues = [ x for (x,y),st in zip(self.site_coordinates,self.site_types) if st==st_i ]
            yvalues = [ y for (x,y),st in zip(self.site_coordinates,self.site_types) if st==st_i ]

            lcolor = color if color is not None else colors[i]
            ax.scatter(xvalues, yvalues, color=lcolor, marker=markers[i],
                       s=440/math.sqrt(len(self.site_coordinates)), zorder=2, label=st_i)

            if( show_sites_ids ):
                for i,(x,y) in enumerate(self.site_coordinates):
                    plt.annotate(str(i), (x,y), ha='center', va='center', zorder=100)


        for i,ineigh in enumerate(self.nearest_neighbors):
            if( ineigh is None ): continue

            for k in ineigh:
                xvalues = np.array([ self.site_coordinates[i][0], self.site_coordinates[k][0] ])
                yvalues = np.array([ self.site_coordinates[i][1], self.site_coordinates[k][1] ])

                norm = math.sqrt( (xvalues[0]-xvalues[1])**2 + (yvalues[0]-yvalues[1])**2 )

                if( self.cell_vectors is not None ):
                    if( norm > np.linalg.norm(1.5*np.array(v1)) ): continue
                    if( norm > np.linalg.norm(1.5*np.array(v2)) ): continue

                lcolor = color if color is not None else 'k'
                ax.plot(xvalues, yvalues, color=lcolor, linestyle='solid',
                        linewidth=1.5/math.sqrt(len(self.site_coordinates)), zorder=1)

        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()

        if( show ):
            if( pause == -1 ):
                plt.show()
            else:
                plt.pause( pause )

                if( close ):
                    plt.close("all")


    def __str__(self):
        """
        Translate the object to a string following the Zacros input files format
        """
        output = ""

        if( self.__origin == Lattice.__FROM_DEFAULT ):
            output += "lattice default_choice\n"

            if( self.__lattice_type_default == Lattice.TRIANGULAR ):
                output += "  triangular_periodic"
            elif( self.__lattice_type_default == Lattice.RECTANGULAR ):
                output += "  rectangular_periodic"
            elif( self.__lattice_type_default == Lattice.HEXAGONAL ):
                output += "  hexagonal_periodic"
            else:
                raise Exception("Error: Default lattice not implemented yet! ("+self.__lattice_type_default+")")

            output += " "+str(self.__lattice_constant_default)
            output += " "+str(self.__repeat_cell_default[0])
            output += " "+str(self.__repeat_cell_default[1])+"\n"

            output += "end_lattice"

        elif( self.__origin == Lattice.__FROM_UNIT_CELL ):
            output += "lattice periodic_cell\n"

            output += "  cell_vectors\n"
            for i in range(2):
                for j in range(2):
                    output += "    "+("%.8f"%self.__cell_vectors_unit_cell[i][j])
                output += "\n"

            output += "  repeat_cell "+str(str(self.__repeat_cell_unit_cell)[1:-1]).replace(',', '')+"\n"

            n_cell_sites = len(self.__site_coordinates_unit_cell)

            site_types_names = list(set(self.__site_types_unit_cell))
            site_types_names.sort()

            output += "  n_site_types "+str(len(site_types_names))+"\n"
            output += "  site_type_names "+str(' '.join(str(x) for x in site_types_names))+"\n"
            output += "  n_cell_sites "+str(n_cell_sites)+"\n"
            output += "  site_types "+str(' '.join(str(x) for x in self.__site_types_unit_cell))+"\n"

            output += "  site_coordinates\n"
            for i in range(n_cell_sites):
                for j in range(2):
                    output += "    "+("%.8f"%self.__site_coordinates_unit_cell[i][j])
                output += "\n"

            output += "  neighboring_structure\n"
            for i in range(len(self.__neighboring_structure_unit_cell)):
                output += "    "+str('-'.join(str(self.__neighboring_structure_unit_cell[i][0][j]+1) for j in range(2)))
                output += "  "+Lattice.__NeighboringToStr[self.__neighboring_structure_unit_cell[i][1]]+"\n"
            output += "  end_neighboring_structure\n"

            output += "end_lattice"

        elif( self.__origin == Lattice.__FROM_EXPLICIT ):
            output += "lattice explicit\n"

            if( self.cell_vectors is not None ):
                output += "  cell_vectors\n"
                for i in range(2):
                    for j in range(2):
                        output += "  "+("%.8f"%self.cell_vectors[i][j])
                    output += "\n"

            output += "  n_sites "+str(len(self.site_types))+"\n"
            output += "  max_coord "+str(max([ len(neighbors) for neighbors in self.nearest_neighbors ]))+"\n"

            site_types_names = list(set(self.site_types))
            site_types_names.sort()

            output += "  n_site_types "+str(len(site_types_names))+"\n"
            output += "  site_type_names "+str(' '.join(str(x) for x in site_types_names))+"\n"

            output += "  lattice_structure\n"

            for i in range(len(self.site_types)):
                output += "    "+"%4d"%(i+1)
                output += "  "+"%.8f"%self.site_coordinates[i][0]+"  "+"%.8f"%self.site_coordinates[i][1]
                output += "  "+"%10s"%self.site_types[i]
                output += "  "+"%4d"%len(self.nearest_neighbors[i])

                for j in range(len(self.nearest_neighbors[i])):
                    output += "%6d"%(self.nearest_neighbors[i][j]+1)

                output += "\n"

            output += "  end_lattice_structure\n"

            output += "end_lattice"

        return output


    def number_of_sites( self ):
        """
        Returns the total number of sites
        """
        return len(self.site_types)


    def site_types_set( self ):
        """
        Returns the set of the sites types
        """
        if( self.__origin == Lattice.__FROM_DEFAULT ):
            return set([0])
        else:
            return set(self.site_types)


    def set_repeat_cell( self, repeat_cell ):
        """
        Set the parameter repeat_cell and update all internal information

        *   ``repeat_cell`` -- The number of repetitions of the unit cell in the directions of unit vectors. *e.g.* ``(10,10)``
        """
        if( self.__origin == Lattice.__FROM_DEFAULT ):
            self.__fromDefaultLattices( self.__lattice_type_default, self.__lattice_constant_default, repeat_cell )

        elif( self.__origin == Lattice.__FROM_UNIT_CELL ):
            self.__fromUnitCellDefined( self.__cell_vectors_unit_cell, repeat_cell, self.__site_types_unit_cell,
                                                self.__site_coordinates_unit_cell, self.__neighboring_structure_unit_cell )

        elif( self.__origin == Lattice.__FROM_EXPLICIT ):
            pass


    def replace_site_types_names( self, site_types_old, site_types_new ):
        """
        Replaces the site types names

        *   ``site_types_old`` -- List of strings containing the old site_types to be replaced
        *   ``site_types_new`` -- List of strings containing the new site_types which would replace old site_types_old.
        """
        assert( len(site_types_old) == len(site_types_new) )

        for i in range(len(site_types_old)):
            for j in range(len(self.site_types)):
                if( self.site_types[j] == site_types_old[i] ):
                    self.site_types[j] = site_types_new[i]

            for j in range(len(self.__site_types_unit_cell)):
                if( self.__site_types_unit_cell[j] == site_types_old[i] ):
                    self.__site_types_unit_cell[j] = site_types_new[i]
