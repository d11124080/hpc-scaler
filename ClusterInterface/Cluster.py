'''
Created on 23 Jun 2013

@author: ronan
'''

class Cluster:
    '''
    classdocs
    '''


    def __init__(self, name, rmType, rmServer, rmPort):
        '''
        Constructor is initialised with the name of the cluster and some
        information about the resource manager - the type, server, and tcp port
        '''
        self.nodelist = []  #An empty list which will hold our Node objects
        self.name = name
        self.rm_type = rmType


