'''
WorkerNode module loads the type-specific (i.e hardware or cloud) module
required for NodeController interaction with hardware or cloud interfaces.
Created on 13 Jul 2013

@author: ronan
'''

from importlib import import_module
import ConfigParser
import sys


class WorkerNode(object):
    '''
    WorkerNode class creates an interface between the NodeController and hardware or cloud interfaces.
    The interface is created at WorkerNode.interface and provides access to the functionality provided
    by the HardwareNode and CloudNode classes, and the vendor-specific drivers they
    '''


    def __init__(self, configFile, nodeName, nodeType):
        '''
        WorkerNode is initialised by passing the configuration file, hostname of the node we want to
        interact with, and the node type ("cloud" or "hardware"). Constructor then loads the required
        driver and creates the interface object.
        '''
        self.cfgFile = configFile
        self.nodeName = nodeName
        self.nodeType = nodeType
        print "nodename is %s and type is %s and config is %s" % (nodeName,nodeType,configFile)
        # First, read the configuration file. We are only interested in the "NodeController" section
        # (The NodeController package can be a component of an application with a shared config file)
        config = ConfigParser.RawConfigParser()
        config.read(configFile)
        config_section = "NodeController"
        # Obtain configuration data for the node types we will connect to.
        self.driverPath = config.get(config_section, "driver_path")
        if nodeType == 'hardware':
            self.driver = config.get(config_section, "hardware_driver")
        elif nodeType == 'cloud':
            self.driver = config.get(config_section, "cloud_driver")
        else:
            print "Error: no driver for node type %s" % nodeType

        ## Attempt to load our drivers, which creates an interface to the driver within our
        # cluster object.
        print "loading driver"
        self.loadDriver()

    def loadDriver(self):
        '''
        Creates an instance of the Driver interface within the WorkerNode object
        '''
        try:
            #Append the path to our driver to our python path
            sys.path.append(self.driverPath+'/' +self.driver)
            #dynamically load a driver we don't know the name of
            module = import_module(self.driver +"Driver")
            class_ = getattr(module, self.driver +"Driver")
            #self.interface will provide an interface between the cluster instance and
            #the driver we just loaded above
            #print "DEBUG: new module is %s and class is %s" % (module,class_)
            self.interface = class_(self.cfgFile, self.nodeName)
        except ImportError, e:
            print e
        #except Exception, y:
        #    print "unknown y exception"
        #    print y
