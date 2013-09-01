'''
Cluster Module - Contains Cluster Class, an instance of which builds a model of,
and provides a level of interaction with, an abstract HPC cluster
Created on 23 Jun 2013

@author: ronan
'''

from importlib import import_module
import ConfigParser
import sys


class Cluster(object):
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

        ## Attempt to load our driver, which creates an interface to the driver within our
        # cluster object at Cluster.interface
        self.loadDriver()
        #print "DEBUG: Created a new cluster named %s which uses the %s Driver" % (self.name, self.driver)


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

    def buildCluster(self):
        '''
        Populates the Cluster instance with information about the clusters nodes using
        the interface created by loadDriver.
        '''
        pass
        #self.interface.getNodes()
        #self.interface.getJobs()

##Uncomment for unit testing
#'''
#c = Cluster("../hpc-scaler.cfg")
#try:
##name = c.interface.serverName
#print "name is",name
#c.interface.getNodes()
#c.interface.listNodes()
#c.interface.getJobs()
#c.interface.printJobs()
#print dir(c.interface)
#c.interface.getJobs()
#c.interface.printJobs()
# c.interface.getLongestWait()
#c.interface.dumpDetails()
#c.interface.disconnect()
#except Exception, ec:
#print ec
#d = Cluster("timmys cluster", "NonExistantDriver", "Drivers/")
#try:
#    d.interface.dumpDetails()
#except Exception, ed:
#    print ed
#f = Cluster("Some Name", "Torque", "invalidpath")
#try:
#    f.interface.dumpDetails()
#except Exception, ef:
#    print ef
#'''




