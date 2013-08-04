'''
Cluster Module - Contains Cluster Class, an instance of which builds a model of
and provide a level of interaction with a cluster
Created on 23 Jun 2013

@author: ronan
'''

class Cluster(object):
    '''
    classdocs
    '''


    def __init__(self, name, driver):
        '''
        Constructor is initialised with the name of the cluster and some
        information about the resource manager - the type, server, and tcp port
        '''
        self.nodelist = []  #An empty list which will hold our Node objects
        self.name = name
        self.driver = driver
        print "Created a new cluster named %s which uses the %s Driver" % (self.name, self.driver)

    def buildCluster(self):
        '''
        Populates the Cluster instance with information about the clusters nodes.
        '''



c = Cluster("Ronans Cluster", "Torque")





