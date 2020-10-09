#!/bin/bash
#SBATCH -J O+Pt111
#SBATCH -n 1
#SBATCH -t 01:00:00
#SBATCH --output=O+Pt111.out
#SBATCH --error=O+Pt111.err

export PYTHONPATH=/projects/0/reaxpro/Sources/pyZacros:$AMSHOME/scripting:$PYTHONPATH
export PATH=/projects/0/reaxpro/Sources/Zacros.nestor:$PATH

python3 O+Pt111.py
