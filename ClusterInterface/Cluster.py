'''
Cluster Module - Contains Cluster Class, an instance of which builds a model of
and provide a level of interaction with a cluster
Created on 23 Jun 2013

@author: ronan
'''
'''try:
    from Drivers import *
except (NameError, ImportError) as e:
    print "Unable to load Cluster Drivers:"
    print e'''

from importlib import import_module
from pkgutil import iter_modules
import sys
from Drivers.Torque.TorqueDriver import TorqueDriver


class Cluster(object):
    '''
    classdocs
    '''


    def __init__(self, name, driver):
        '''
        Constructor is initialised with the name of the cluster and some
        information about the resource manager - the type, server, and tcp port
        '''
        self.nodelist = []  #An empty list which will hold our Node objects
        self.name = name
        self.driver = driver
        self.loadDriver()
        print "Created a new cluster named %s which uses the %s Driver" % (self.name, self.driver)
        self.buildCluster()

    def loadDriver(self):
        '''
        Creates an instance of the Driver interface within the cluster object
        '''
        try:
            module = import_module(self.driver +"Driver",package="ClusterInterface.Drivers.%s" % self.driver)
            class_ = getattr(module, self.driver +"Driver")
            self.clusterInstance = class_()
        except ImportError, e:
            print e
        except Exception, y:
            print y

    def buildCluster(self):
        '''
        Populates the Cluster instance with information about the clusters nodes.
        '''
        self.clusterInstance.dumpDetails()

##Uncomment for unit testing

c = Cluster("Ronans Cluster", "Torque")





