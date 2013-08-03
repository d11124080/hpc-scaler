'''
Created on 3 Aug 2013

@author: ronan
'''

from Drivers.Torque.pbs_python.4.3.5 import pbs, PBSQuery, PBSAdvancedParser

class TorqueDriver(object):
    '''
    This driver for the Torque Resource Manager is designed to function as part of the
    ClusterInterface.
    '''


    def __init__(selfparams):
        '''
        Constructor
        '''
