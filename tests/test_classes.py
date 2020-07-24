#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.append("../pyzacros/classes")

from Species import *
from SpeciesList import *
from Cluster import *
from ElementaryReaction import *
from Mechanism import *

###
#  @brief
##
def main( argv ):
    Species.test()
    SpeciesList.test()
    Cluster.test()
    ElementaryReaction.test()
    Mechanism.test()

if  __name__ == "__main__":
        main( sys.argv[1:] )
