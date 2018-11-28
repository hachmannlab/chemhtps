#!/usr/bin/env python



import sys
sys.path.insert(0, "/user/m27/pkg/openbabel/2.3.2/lib")
import pybel
import openbabel
#import subprocess
import time
import argparse
#import scipy
from collections import defaultdict
import operator


###################################################################################################

#import cStringIO
from mpi4py import MPI
import os
#import threading
from itertools import islice


'''
This is to remove the stereo chemistry information from smiles provided.
'''

        

mol_try= pybel.readfile("xyz",'1.xyz').next()
print mol_try.OBMol.GetTotalCharge()
print mol_try.OBMol.GetTotalSpinMultiplicity()



        
