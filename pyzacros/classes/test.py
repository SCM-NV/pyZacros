#!/usr/bin/env python3

import sys

from Specie import *
from Cluster import *
from ElementaryReaction import *

###
#  @brief
##
def main( argv ):
    Specie.test()
    Cluster.test()
    ElementaryReaction.test()

if  __name__ == "__main__":
        main( sys.argv[1:] )
