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
    Some methods are required to be overridden. These methods will raise an exception
    if called directly from the parent, and are indicated as such.
    '''


    def __init__(self):
        '''
        The constructor defines and initialises the arrays and instance variables provided
        to the Cluster module by the Driver. Drivers should
        '''
        self.nodes = []         #An array of the worker nodes (of type Node) of the cluster
        self.idlenodes = []     #An array of nodes that are idle (i.e no jobs currently running)
        self.downnodes = []     #An array of nodes that are down (i.e powered off)
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

    def getJobs(self):
        '''
        Query the cluster to obtain information about its jobs. This function, when overridden by
        child, should populate the clusters job list in its entirety.
        '''
        try: #to be implemented by child
            raise Exception("Error - getJobs method MUST be implemented by Driver")
        except Exception as cept:
            print cept
            sys.exit(0)

    def listIdleNodes(self):
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

    def printJobs(self):
        print "printing ",self.numJobs," jobs"
        for job in self.jobs:
            job.printDetails()

    def getLongestWait(self):
        '''Find the Job which has been queued the longest - used for longestqueued strategy'''
        print "getting longest wait"
        longest_wait_time = 0
        if self.jobs:
            for job in self.jobs:
                job.getQueueTime()
                if job.tiq > longest_wait_time:
                    longest_wait_time = job.tiq
                    self.longest_wait_job = job.jobId
                    self.longest_wait_nodes = job.numNodes
                    self.longest_wait_ppn = job.ppn
                    self.longest_wait_ncpus = job.ncpus
                    self.longest_wait_time = longest_wait_time







