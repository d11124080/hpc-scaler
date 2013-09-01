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
        self.cloudnodes = []    #An array of nodes with the "cloud" property
        self.idlecloudnodes = [] #An array of idle nodes with the cloud property
        self.hardwarenodes = [] #An array of nodes without the 'cloud' property
        self.suitableNodes = [] #Array of nodes which would be suitable for a given job
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
        #print "DEBUG: getting longest wait"
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
                    self.longest_wait_props = job.properties
                    self.longest_wait_time = longest_wait_time
                    if not isinstance(self.longest_wait_time, int):
                        raise Exception("longest wait time not an int: %s" % self.longest_wait_time)
                    if not isinstance(self.longest_wait_nodes, int):
                        raise Exception("longest wait nodes not an int: %s" % self.longest_wait_nodes)
                    if not isinstance(self.longest_wait_ppn, int):
                        raise Exception("longest wait ppn not an int: %s" % self.longest_wait_ppn)

    def getMinNodes(self, num_nodes, ppn, props=[]):
        '''
        Function to obtain the minimal resources required to satisfy a given number
        of nodes, cpus per node, and a specific set of properties. Should return a list
        of hostnames
        '''
        self.suitableNodes = []                  #Array to hold suitable nodes
        self.recommendedNodes = []              #Array to hold the nodes we will recommend
        for node in self.nodes:
            #Set an initial flag to determine if the node being examined right now is suitable
            thisnode = True;                 #Useful until it proves otherwise!
            if node.state == 'down':         #Only nodes which are currently down are suitable, obviously!
                if node.num_cpus >= ppn:     #Node will need to equal or exceed the requested ppn
                    ##Now make sure node satisfies all the properties requested by the job. Check
                    # each requested property in sequence
                    for prop in props:
                        #print "DEBUG: checking prop %s" % prop
                        if prop not in node.properties:
                            thisnode = False    #This node doesn't have at least one of the properties we wanted.
                        else:
                            print "node %s has property %s" % (node.hostname,prop)
                    #All properties have been checked, check our flag
                    if thisnode is True:
                        self.suitableNodes.append(node)

        ##Now establish the set of resources to recommend provisioning
        #nodecount = 0
        for node in self.suitableNodes:
            while len(self.recommendedNodes) < num_nodes:   #No need to return more nodes than the job is requesting!
                self.recommendedNodes.append(node)
                #print "DEBUG: selected ",node.hostname








