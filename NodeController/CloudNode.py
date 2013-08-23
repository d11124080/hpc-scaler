'''
Created on 23 Aug 2013

@author: ronan
'''

from importlib import import_module
import ConfigParser
import sys


class CloudNode(object):
    '''
    classdocs
    '''


    def __init__(self, configFile):
        '''
        Cluster instance is initialised with the name of the cluster and some
        information about the resource manager - the type, server, etc,
        which are obtained from the configuration file we are passed on
        instance creation
        '''
        # First, read the configuration file. We are only interested in the "ClusterInterface" section
        # (The ClusterInterface package can be a component of an application with a shared config file)
        config = ConfigParser.RawConfigParser()
        config.read(configFile)
        config_section = "ClusterInterface"
        # Obtain configuration data for the cluster we will connect to.
        self.name = config.get(config_section, "hostname")
        self.driverPath = config.get(config_section, "driver_path")
        self.driver = config.get(config_section, "cluster_driver")
        # Initialise cluster components
        self.nodelist = []  #An empty list which will hold our Node objects
        # Attempt to load our driver, which creates a driver interface within our
        # cluster object.
        self.loadDriver()
        #print "DEBUG: Created a new cluster named %s which uses the %s Driver" % (self.name, self.driver)
        #Call buildCluster to populate the cluster node data
        self.buildCluster()

    def loadDriver(self):
        '''
        Creates an instance of the Driver interface within the cluster object
        '''
        try:
            #Append the path to our driver to our python path
            sys.path.append(self.driverPath+'/' +self.driver)
            #dynamically load a driver we don't know the name of
            module = import_module(self.driver +"Driver")
            class_ = getattr(module, self.driver +"Driver")
            #self.interface will provide an interface between the cluster instance and
            #the driver we just loaded above
            self.interface = class_()
        except ImportError, e:
            print e
        except Exception, y:
            print y
