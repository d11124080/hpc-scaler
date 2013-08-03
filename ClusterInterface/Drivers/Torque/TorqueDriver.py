'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''

from ClusterInterface.Drivers.Torque.pbs_python.fourthreefive import pbs, PBSQuery, PBSAdvancedParser

class TorqueDriver(object):
    '''
    This driver for the Torque Resource Manager is designed to function as part of the
    ClusterInterface.
    '''


    def __init__(selfparams):
        '''
        Constructor
        '''
