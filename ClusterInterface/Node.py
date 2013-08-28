'''
Created on 3 Aug 2013

@author: ronan
'''

import string
from Job import Job

class Node(object):
    '''
   An object of type "node" is a HPC Cluster Worker Node. Instances of this class
   will be populated by the ClusterInterface polling the clusters resource manager
   using the Cluster module from this package (ClusterInterface) and a resource manager-
   specific 'driver'.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.num_cpus = 0   #Number of CPU cores on this worker node
        self.free_cpus = 0  #Number of available (free) CPU Cores
        self.mem = 0        #Amount of memory on this worker node (KiB)
        self.state = None  #State of the node - Should be set to Up or Down
        self.queues = []    #We'll store a list of queue objects representing the queue a node is in.
        self.properties = [] #Likewise a list of properties of this node.
        self.jobs = []      #Array of Jobs (of type Job) currently running on this node, if any.

    def setNumCpus (self,num):
        self.num_cpus = num

    def setMem(self,mem):
        self.mem = mem

    def setState(self,state):
        self.state = state

    def setHostname(self,hostname):
        self.hostname = hostname

    def setNumJobs(self, numJobs):
        self.num_jobs = numJobs

    def setFreeCpus(self, freeCpus):
        self.free_cpus = freeCpus

    def addQueue(self,queueName):
        pass

    def addProperty(self,prop):
        self.properties.append(prop)

    def getProperties(self):
        return string.join(self.properties)

    def addJob(self, job):
        self.jobs.append(job)


    def printDetails(self):
        print "Details for Worker Node \"",self.hostname,"\":"
        print "-----------------------------------------------"
        print "Number of CPU Cores:",self.num_cpus
        print "Total Available Memory:",self.mem
        print "Current Node State:",self.state
        print "Free CPU Cores:",self.free_cpus
        print "Properties:",self.getProperties()
        print "-----------------------------------------------"
