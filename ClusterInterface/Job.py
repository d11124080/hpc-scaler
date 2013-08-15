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
        self.jobId = jobId   #A unique identifier for each job, provided by the resource manager.
        self.ncpus = None   #The number of cpu cores requested by a job
        self.properties = [] #An array of node properties this job is requesting.
        self.walltime = None #The walltime (expected runtime duration, provided by the user) requested for the job.
