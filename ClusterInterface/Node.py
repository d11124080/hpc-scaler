'''
Created on 3 Aug 2013

@author: ronan
'''

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
        self.mem = 0        #Amount of memory on this worker node (KiB)
        self.status = None  #Status of node as per resource manager
        self.queues = []    #We'll store a list of queue objects representing the queue a node is in.

    def setNumCpus (self,num):
        self.num_cpus = num

    def setMem(self,mem):
        self.mem = mem

    def setStatus(self,status):
        self.status = status

    def addQueue(self,queueName):
        self.
