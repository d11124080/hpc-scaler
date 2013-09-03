'''
Template Module for the power control of a HardwareNode. The actual functionality should be provided by
a vendor-specific Driver within the Drivers subdirectory.
Created on 23 Aug 2013

@author: ronan
'''

import socket

class CloudNode(object):
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
        '''
        Function to power on a cloud instance. Must be implemented by
        driver

        '''
        pass

    def powerOff(self):
        '''
        Function to terminate a currently running cloud instance. Must be implemented by
        driver

        '''
        pass

    def powerCycle(self):
        '''
        Function to reset a currently running instance. Must be implemented by
        driver

        '''
        pass

    def getRunningInstances(self):
        '''
        Function to obtain details about currently running instances. Must be implemented by
        driver. Should populate a variable named numRunningInstances with the count of currently
        active cloud nodes.
        '''
        pass

    def resolveIp(self):
        # Get the Public IP associated with this hostname
        try:
            self.ipAddr = socket.gethostbyname(self.hostname)
            if not self.ipAddr:       # Should be caught by socket.error, but in case another error occurred
                raise Exception("Unexpected error in EC2 driver when resolving address.")
        except socket.error as error:
            #re-raise our exception to the calling class
            raise Exception("Error resolving %s - %s" % (self.hostname, error))
