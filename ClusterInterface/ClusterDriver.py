'''
A Template for hpc-scaler ClusterInterface Drivers.
This class should be extended by individual vendor-specific drivers.
This class is essentially a template which must be extended to provide
functionality to the ClusterInterface.
Created on 4 Aug 2013

@author: ronan
'''

class ClusterDriver(object):
    '''
    Template Class which defines how a vendor-specific Driver should be implemented.
    Subclass Methods which override the methods of this class MUST call the parent method
    on completion
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass

    def connect(self):
        #Create a connection to the cluster
        pass    #to be overwritten by child

    def disconnect(self):
        #Destroy a connection to the cluster
        pass    #to be overwritten by child

    def query(self):
        #Create a connection to the cluster
        pass    #to be overwritten by child

    def getServerName(self):
        print "now in superclass"
        print "sn is %s" % self.serverName
        for k, v in vars(self).items():
            print k, v
        return self.serverName

    



