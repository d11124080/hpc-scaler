'''
Template Module for the power control of a HardwareNode. The actual functionality should be provided by
a vendor-specific Driver within the Drivers subdirectory.
Created on 23 Aug 2013

@author: ronan
'''


class HardwareNode(object):
    '''
    Template class for the control of Hardware Nodes. Functionality must be extended by a vendor specific
    Driver. Any methods of this class which provide functionality (i.e contain instructions other than
    "pass") MUST be processed after and overridding methods within the child driver.
    '''

    def __init__(self):
        '''
        HardwareNode instance is initialised with identifier and the type of power interface
        which are obtained from the configuration file we are passed on instance creation
        '''

    def powerOn(self):
        pass

    def powerOff(self):
        pass

    def powerCycle(self):
        pass
    
    def printDetails(self):
        pass    #useful for debugging



##Uncomment for unit testing
#HN = HardwareNode()
