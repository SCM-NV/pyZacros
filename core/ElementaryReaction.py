from collections import Counter
from .SpeciesList import SpeciesList

__all__ = ['ElementaryReaction']

class ElementaryReaction:
    """
    Creates a new ElementaryReaction object

    *   ``initial`` -- List of species bound to the sites in the initial state, e.g. ``[ Species("H*"), Species("H*") ]``. Gas species have to be added at the end of the list.
    *   ``final`` -- Same as ``initial`` but for the final state.
    *   ``site_types`` -- Specifies the name of the sites in the graph pattern, e.g. ``['fcc','hcp']``. Notice that the order is essential and it should agree with the ``initial`` and ``final`` options.
    *   ``initial_entity_number`` -- List of the molecular entities ids bound to each site. For example, if a bidentate species is bound to sites 1 and 2 ( ``species=[ Species("H**",2), Species("H**",2) ]`` ), both of these sites will have the same entity numbers, i.e. ``entity_number=[0,0]``. By default, the list of entity numbers is created by assuming that species with the same symbol belong to the same entity.
    *   ``final_entity_number`` -- Same as ``initial_entity_number`` but for the final state.
    *   ``neighboring`` -- Specifies the neighboring between sites, if more than one sites appear in the graph pattern, e.g. [ (0,1) ]
    *   ``reversible`` -- Sets the reaction as a reversible step.
    *   ``pre_expon`` -- Specifies the pre-exponential in the Arrhenius formula giving the rate constant of that elementary step. Units: 1/s or Hz.
    *   ``pe_ratio`` -- Sets the ratio of forward over reverse pre-exponential terms if the reaction is reversible.
    *   ``activation_energy`` -- Sets the activation energy at the zero coverage limit. Units eV.
    *   ``prox_factor`` -- The proximity factor used in the BEP relationship to calculate the forward (and also reverse, if applicable) activation energy.
    *   ``label`` -- If None, a unique label is generated based on the label of its initial and final states.
    """

    def __init__(self,
                 initial,
                 final,
                 site_types = None,
                 initial_entity_number = None,
                 final_entity_number = None,
                 neighboring = None,
                 reversible = True,
                 pre_expon = 0.0,
                 pe_ratio = 0.0,
                 activation_energy = 0.0,
                 prox_factor = None,
                 label = None):

        if( ( type(initial) != SpeciesList and type(initial) != list )
            or ( type(final) != SpeciesList and type(final) != list ) ):
            msg  = "\n### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              Inconsistent type for initial or final\n"
            raise NameError(msg)

        sites_initial = len([ sp for sp in initial if sp.is_adsorbed() ])
        sites_final = len([ sp for sp in final if sp.is_adsorbed() ])
        if( sites_initial != sites_final ):
            msg  = "\n### ERROR ### ElementaryReaction.__init__.\n"
            msg += "Inconsistent number of surface sites between initial and final\n"
            msg += "sites_initial="+str([ sp.symbol for sp in initial if sp.is_adsorbed() ])+"\n"
            msg += "sites_final="+str([ sp.symbol for sp in final if sp.is_adsorbed() ])+"\n"
            raise NameError(msg)
        self.sites = sites_initial

        if( site_types is not None ):
            if( not ( all([ type(st)==int for st in site_types ]) or all([ type(st)==str for st in site_types ]) ) ):
                msg  = "\n### ERROR ### ElementaryReaction.__init__.\n"
                msg += "              Inconsistent type for site_types. It should be a list of int or str\n"
                raise NameError(msg)

            self.site_types = site_types   # e.g. [ "f", "f" ], [ 0, 0 ]
        else:
            self.site_types = self.sites*[ 0 ]

        self.neighboring = neighboring # e.g. [ (0,1) ]

        self.initial = initial
        if( type(initial) == list ): self.initial = SpeciesList(initial)
        self.__initial_gas = SpeciesList( [sp for sp in self.initial if sp.is_gas()] )
        self.__initial_adsorbed = SpeciesList( [sp for sp in self.initial if sp.is_adsorbed()] )

        self.initial_entity_number = initial_entity_number
        if( initial_entity_number is None ):
            self.initial_entity_number = SpeciesList.default_entity_numbers( self.sites, self.__initial_adsorbed )

        self.final = final
        if( type(final) == list ): self.final = SpeciesList(final)
        self.__final_gas = SpeciesList( [sp for sp in self.final if sp.is_gas()] )
        self.__final_adsorbed = SpeciesList( [sp for sp in self.final if sp.is_adsorbed()] )

        self.final_entity_number = final_entity_number
        if( final_entity_number is None ):
            self.final_entity_number = SpeciesList.default_entity_numbers( self.sites, self.__final_adsorbed )

        self.reversible = reversible
        self.pre_expon = pre_expon
        self.pe_ratio = pe_ratio
        self.activation_energy = activation_energy     # e.g. 0.200
        self.prox_factor = prox_factor

        #if( self.sites != sum([s.denticity for s in self.initial])
           #or self.sites != sum([s.denticity for s in self.final]) ):
            #msg  = "\n### ERROR ### ElementaryReaction.__init__.\n"
            #msg += "              Inconsistent dimensions for sites, initial or final\n"
            #raise NameError(msg)

        if( abs( self.initial.mass( self.initial_entity_number ) - self.final.mass( self.final_entity_number ) ) > 1e-6 ):
            msg  = "\n### ERROR ### ElementaryReaction.__init__.\n"
            msg += "              The mass is not conserved during the reaction\n"
            msg += "              initial:mass("+str([sp.symbol for sp in self.initial])+")="+str(self.initial.mass(self.initial_entity_number))
            msg += ", final:mass("+str([sp.symbol for sp in self.final])+")="+str(self.final.mass(self.final_entity_number))+"\n"
            msg += "              initial:entity_number="+str(self.initial_entity_number)
            msg += ", final:entity_number="+str(self.final_entity_number)+"\n"
            raise NameError(msg)

        self.__userLabel = label
        self.__label = None
        self.__updateLabel()


    def __eq__(self, other):
        """
        Returns True if both objects have the same label. Otherwise returns False

        *   ``other`` --
        """
        if( self.__label == other.__label ):
            return True
        else:
            return False


    def __hash__(self):
        """
        Returns a hash based on the label
        """
        return hash(self.__label)


    @staticmethod
    def __getSpeciesListFullName( species, entity_number, site_types ):
        label = ""

        for i in range(len(species)):
            label += species[i].symbol
            if( len(entity_number) > 1 ):
                label += str(entity_number[i]+1)
            label += str(site_types[i])

        return label


    def __updateLabel(self):
        """
        Updates the attribute 'label'
        """
        if( self.__userLabel is not None ):
            self.__label = self.__userLabel
            return

        initialLabel = ElementaryReaction.__getSpeciesListFullName( self.__initial_adsorbed, self.initial_entity_number, self.site_types )

        if( len(self.initial.gas_species()) > 0 ):
            initialLabel += ":" + SpeciesList(self.initial.gas_species()).label()

        finalLabel = ElementaryReaction.__getSpeciesListFullName( self.__final_adsorbed, self.final_entity_number, self.site_types )

        if( len(self.final.gas_species()) > 0 ):
            finalLabel += ":" + SpeciesList(self.final.gas_species()).label()

        self.__label = ""

        if( self.reversible ):
            # Reaction labels in lexicographical order
            if( initialLabel > finalLabel ):
                self.__label = initialLabel+"<->"+finalLabel
            else:
                self.__label = finalLabel+"<->"+initialLabel
        else:
            self.__label = initialLabel+"->"+finalLabel

        # For neighboring nodes are sorted
        if self.neighboring is not None:
            for i in range(len(self.neighboring)):
                if(i==0): self.__label += ";"
                lNeighboring = list(self.neighboring[i])
                lNeighboring.sort()
                self.__label += str(tuple(lNeighboring)).replace(" ", "")
                if( i != len(self.neighboring)-1):
                    self.__label += ","


    def label(self):
        """
        Returns the label of the cluster
        """
        if( self.__label is None ):
            self.__updateLabel()

        return self.__label


    def __str__(self):
        """
        Translates the object to a string
        """
        if( self.reversible ):
            output  = "reversible_step " + self.__label +"\n"
        else:
            output  = "step " + self.__label +"\n"

        initial_gas_species = SpeciesList( self.initial.gas_species() )
        final_gas_species = SpeciesList( self.final.gas_species() )

        if( len(initial_gas_species) != 0 or len(final_gas_species) != 0 ):
            output += "  gas_reacs_prods "

            gas_species_freqs = Counter( [ s.symbol for s in initial_gas_species ] )

            i=0
            for symbol,freq in gas_species_freqs.items():
                output += symbol+" "+str(-freq)
                if( i != len(gas_species_freqs)-1 ):
                    output += " "
                i += 1

            gas_species_freqs = Counter( [ s.symbol for s in final_gas_species ] )

            i=0
            for symbol,freq in gas_species_freqs.items():
                output += symbol+" "+str(freq)
                if( i != len(gas_species_freqs)-1 ):
                    output += " "
                i += 1

            output += "\n"

        if(self.sites != 0):
            output += "  sites " + str(self.sites)+"\n"
            if self.neighboring is not None and len(self.neighboring) > 0:
                output += "  neighboring "
                for i in range(len(self.neighboring)):
                    output += str(self.neighboring[i][0]+1) + "-" + str(self.neighboring[i][1]+1)
                    if(i != len(self.neighboring)-1):
                        output += " "
                output += "\n"

            output += "  initial"+"\n"
            site_identate = {}
            for i in range(self.sites):
                if( self.initial_entity_number[i] not in site_identate ):
                    site_identate[ self.initial_entity_number[i] ] = 0
                else:
                    site_identate[ self.initial_entity_number[i] ] = site_identate[ self.initial_entity_number[i] ] + 1

                if( site_identate[ self.initial_entity_number[i] ] >= self.initial[i].denticity ):
                    msg  = "\n### ERROR ### ElementaryReaction.__str__.\n"
                    msg += "Inconsistent of denticity value for "+self.initial[i].symbol+" (pos="+str(i)+")\n"
                    msg += "self.initial_entity_number = "+str(self.initial_entity_number)+"\n"
                    raise NameError(msg)

                output += "    "+str(self.initial_entity_number[i]+1)+" "+self.initial[i].symbol+" "+str(site_identate[self.initial_entity_number[i]]+1)+"\n"

            output += "  final"+"\n"
            site_identate = {}
            for i in range(self.sites):
                if( self.final_entity_number[i] not in site_identate ):
                    site_identate[ self.final_entity_number[i] ] = 0
                else:
                    site_identate[ self.final_entity_number[i] ] = site_identate[ self.final_entity_number[i] ] + 1

                if( site_identate[ self.final_entity_number[i] ] >= self.final[i].denticity ):
                    msg  = "\n### ERROR ### ElementaryReaction.__str__.\n"
                    msg += "Inconsistent of denticity value for "+self.final[i].symbol+" (pos="+str(i)+")\n"
                    msg += "self.final_entity_number = "+str(self.final_entity_number)+"\n"
                    raise NameError(msg)

                output += "    "+str(self.final_entity_number[i]+1)+" "+self.final[i].symbol+" "+str(site_identate[self.final_entity_number[i]]+1)+"\n"

            output += "  site_types "
            for i in range(len(self.site_types)):

                if( type(self.site_types[i]) == int ):
                    output += str(self.site_types[i]+1)
                elif( type(self.site_types[i]) == str ):
                    output += self.site_types[i]

                if(i != len(self.site_types)-1):
                    output += " "
            output += "\n"

        output += "  pre_expon "+("%12.5e"%self.pre_expon)+"\n"

        if self.reversible:
            output += "  pe_ratio "+("%12.5e"%self.pe_ratio)+"\n"

        output += "  activ_eng "+("%12.5e"%self.activation_energy)+"\n"

        if self.prox_factor is not None:
            output += "  prox_factor "+("%12.5e"%self.prox_factor)+"\n"

        if self.reversible:
            output += "end_reversible_step"
        else:
            output += "end_step"

        return output


    def site_types_set(self):
        """
        Returns the set of the sites types
        """
        return set(self.site_types)


    def replace_site_types( self, site_types_old, site_types_new ):
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

        self.__updateLabel()
