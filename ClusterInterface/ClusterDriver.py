'''
A Template for hpc-scaler ClusterInterface Drivers.
This class should be extended by individual vendor-specific drivers.
This class is essentially a template which must be extended to provide
functionality to the ClusterInterface.
Created on 4 Aug 2013

@author: ronan
'''

import sys


class ClusterDriver(object):
    '''
    Template Class which defines how a vendor-specific Driver should be implemented.
    Subclass Methods which override the implemented (i.e non-"pass")methods of this class,
    including Constructor methods, MUST call the parent method on completion.
    '''


    def __init__(self):
        '''
        The constructor defines and initialises the arrays and instance variables provided
        to the Cluster module by the Driver. Drivers should
        '''
        self.nodes = []         #An array of the worker nodes (of type Node) of the cluster
        self.idlenodes = []     #An array of nodes that are idle (i.e no jobs currently running)
        self.fullnodes = []     #An array of nodes that are at maximum cpu core usage
        self.jobs = []          #An array of jobs of all status
        self.queuedJobs = []    #An array of all jobs currently in the queue
        self.connectionStatus = 'Not Connected' #Initialise connection status (Connected | Not Connected)
        self.numNodes = 0       #Number of worker nodes we know about
        self.numIdleNodes = 0   #Number of idle nodes we are aware of
        self.numFreeCpus = 0    #Number of cpu cores currently free on the cluster
        self.numCpus = 0        #Total number of cpu cores on the cluster
        self.numJobs = 0        #Total number of jobs of all status
        self.numQueuedJobs = 0  #Total number of queued jobs

    def connect(self,host='localhost'):
        ##Create a connection to the cluster. Must assign a value of "Connected"
        # to the connectionStatus instance variable on successful completion, or
        # leave the value unchanged if connection does not succeed.
        pass    #to be overwritten by child

    def disconnect(self):
        ##Destroy a connection to the cluster. Must assign a value of "Not Connected"
        # to the connectionStatus instance variable on successful completion, or leave
        # the value unchanged if disconnection is not succesful.
        pass    #to be overwritten by child

    def query(self):
        #Create a connection to the cluster
        pass    #to be overwritten by child

    def getServerName(self):
        ##Function to return the server name associated with this cluster.
        #print "about to return %s" % self.serverName
        return self.serverName

    def getNodes(self):
        '''
        Query the cluster to obtain information about its worker nodes. This function, when overridden by
        child, should populate the clusters nodelist in its entirety.

        '''
        try: #to be implemented by child
            raise Exception("Error - getNodes method MUST be implemented by Driver")
        except Exception as cept:
            print cept
            sys.exit(0)

    def getIdleNodes(self):
        '''
        Retrieve a list of idle nodes (i.e nodes which are not running jobs)
        '''
        if self.idlenodes:
            for node in self.idlenodes:
                print "Idle Node: %s, State: %s" % (node.hostname, node.state)
    def listNodes(self):
        '''
        Prints a list of nodes and their state
        '''
        if self.nodes:
            for node in self.nodes:
                print "Node: %s, State: %s" % (node.hostname, node.state)
        else:
            print "There are currently no known nodes in this cluster"




