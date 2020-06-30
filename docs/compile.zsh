#!/bin/zsh
make clean
sphinx-apidoc -o . ../pyzacros
# add mocules to the index.rst
make html 
open _build/html/index.html 

