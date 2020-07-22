#!/usr/bin/env python3

import sys

from Specie import *
from SpecieList import *
from Cluster import *
from ElementaryReaction import *
from Mechanism import *

###
#  @brief
##
def main( argv ):
    Specie.test()
    SpecieList.test()
    Cluster.test()
    ElementaryReaction.test()
    Mechanism.test()

if  __name__ == "__main__":
        main( sys.argv[1:] )
