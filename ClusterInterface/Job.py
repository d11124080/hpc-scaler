'''
Job module just specifies some basic information about a job. Could be more detailed,
but we are not acting as the job scheduler here!

Created on 15 Jul 2013

@author: ronan
'''

import time

class Job(object):
    '''
    Job class contains very basic information about a job. Instances of this class may be jobs currently
    running on a node, or jobs which are queued for processing.
    '''


    def __init__(self, jobId):
        '''
        Constructor just defines the properties of our job
        '''
        self.jobId = jobId      #A unique identifier for each job, provided by the resource manager.
        self.ncpus = 0          #The total number of cpu cores requested by a job
        self.numNodes = 0       #Number of nodes a job is requesting
        self.ppn = 0            #Processors per node requested by this job
        self.nodes = []         #Array of nodes this job is running on
        self.properties = []    #An array of node properties this job is requesting.
        self.walltime = 0       #The walltime (expected runtime duration, provided by the user) requested for the job.
        self.status = None      #Whether the job is 'queued', 'running', or 'other'
        self.qtime = 0          #Timestamp of job submission to queue
        self.tiq = 0            #Number of seconds job has been queued

    def getQueueTime(self):
        '''Determine the time (in seconds) job has been in the queue'''
        self.tiq = time.time() - self.qtime

    def printDetails(self):
        self.getQueueTime() ##First update the time-in-queue

        print "*******************************************"
        print "Showing Details for Job %s" % self.jobId
        print "-------------------------------------------"
        print "Job Status: \t %s" % self.status
        print "Req'd Nodes: \t %s" % self.numNodes
        print "CPUs Per Node: \t %s" % self.ppn
        print "Walltime : \t %s" % self.walltime
        if self.nodes:
            print "Nodes:"
            for node in self.nodes:
                print node+" "
        print "Total CPUs: \t %s" % self.ncpus
        print "Queued since: \t %d" % self.qtime
        print "Time in Q: \t %d seconds." % self.tiq
        print "*******************************************"
