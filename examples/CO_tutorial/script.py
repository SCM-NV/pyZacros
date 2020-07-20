from pyzacros.classes.kmc import sayhi, KmcSimulation
import pathlib
#from pathlib import Path
import os
p=pathlib.Path()
task1=KmcSimulation(engine="Zacros", electronic_package="AMS", path="/Users/plopez/Programs/pyZacros/examples/CO_tutorial")
#print(os.getcwd())
#print(pathlib.Path.cwd())

#task1.run()
#sayhi()







#pyzacros.run_command( ['/bin/sh', '-c'], workdir='/Users/plopez/Programs/pyZacros/example')