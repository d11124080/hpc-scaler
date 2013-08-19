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
    Subclass Methods which override the implemented (i.e non-"pass")methods of this class
    MUST call the parent method on completion.
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
        #print "now in superclass"
        #print "sn is %s" % self.serverName
        #for k, v in vars(self).items():
        #    print k, v
        return self.serverName

    def getNodes(self):
        '''
        query the cluster to obtain information about its worker nodes
        '''
        pass #to be implemented by child

    def getIdleNodes(self):
        '''
        Retrieve a list of idle nodes (i.e nodes which are not running jobs)
        '''
    def listNodes(self):
        '''
        Prints a list of nodes and their state
        '''
        if self.nodes:
            for node in self.nodes:
                print "Node: %s, State: %s" % (node.hostname, node.state)
        else:
            print "There are currently no known nodes in this cluster"




