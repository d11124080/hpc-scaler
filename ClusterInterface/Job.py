'''
Job module just specifies some basic information about a job. Could be more detailed,
but we are not acting as the job scheduler here!

Created on 15 Jul 2013

@author: ronan
'''

class Job(object):
    '''
    Job class contains very basic information about a job. Instances of this class may be jobs currently
    running on a node, or jobs which are queued for processing.
    '''


    def __init__(self, jobId):
        '''
        Constructor
        '''
        self.jobId = jobId      #A unique identifier for each job, provided by the resource manager.
        self.ncpus = 0          #The total number of cpu cores requested by a job
        self.numNodes = 0       #Number of nodes a job is requesting
        self.ppn = 0            #Processors per node requested by this job
        self.nodes = []         #Array of nodes this job is running on
        self.properties = []    #An array of node properties this job is requesting.
        self.walltime = 0       #The walltime (expected runtime duration, provided by the user) requested for the job.
        self.status = None      #Whether the job is 'queued', 'running', or 'other'

    def printDetails(self):
        print "*******************************************"
        print "Showing Details for Job %s" % self.jobId
        print "-------------------------------------------"
        print "Job Status: \t %s" % self.status
        print "Requested Nodes: \t %s" % self.numNodes
        print "CPUs Per Node: \t %s" % self.ppn
        print "Walltime Requested: \t %s" % self.walltime
        print "Nodes:"
        for node in self.nodes:
            print node+" "
        print "Total CPUs: \t %s" % self.ncpus
        print "*******************************************"
