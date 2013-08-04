'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''

from pbs_python.fourthreefive.pbs import pbs
from pbs_python.fourthreefive.PBSQuery import PBSQuery
from pbs_python.fourthreefive.PBSAdvancedParser import PBSAdvancedParser

class TorqueDriver(object):
    '''
    This driver for the Torque Resource Manager is designed to function as part of the
    ClusterInterface.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pbs_server = pbs.pbs_default()
        print pbs_server


TD = TorqueDriver()

