'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''


try:
    from pbs_python.fourthreefive import pbs, PBSQuery, PBSAdvancedParser
    from ClusterInterface.ClusterDriver import ClusterDriver
    from ClusterInterface.Node import Node
    import sys

except (NameError, ImportError) as e:
    print "Component(s) not found or not readable at default location:"
    print e



class TorqueDriver(ClusterDriver):
    '''
    This driver for the Torque Resource Manager is designed to function as part of the
    ClusterInterface.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.nodes = []

    def connect(self):
        try:
            pbs_server = pbs.pbs_default()
            self.con = pbs.pbs_connect(pbs_server)
            if self.con:
                self.connectionStatus = 'Connected'
        except Exception, e:
            print e

    def disconnect(self):
        #pbs_disconnect returns non-zero value if an error occurs
        retval = pbs.pbs_disconnect(self.con)
        if (retval == 0):
            self.connectionStatus = 'Not Connected'
            self.con = 0
        else:
            print pbs.pbs_statserver(self.con)

    def getConStatus(self):
        '''
        Determines whether an active connection with the Resource Manager exists -
        Can be handled by parent class, so just call the equivilent function in the parent.
        '''
        super(TorqueDriver, self).getConStatus()


    def getServerName(self):
        '''
        Returns the FQDN of the job submission host
        '''
        pbs_server = pbs.pbs_default()
        if pbs_server:
            self.serverName = pbs_server
            #print "DEBUG: about to return name %s" % self.serverName
            #Call our parent function's equivilent function
            super(TorqueDriver, self).getServerName()
        else:
            errno, text = pbs.error()
            print errno, text


    def dumpDetails(self):
        pbs_server = pbs.pbs_default()
        if not pbs_server:
            print "No default pbs server"
            sys.exit(1)

        #con = pbs.pbs_connect(pbs_server)
        nodes = pbs.pbs_statnode(self.con, "", "NULL", "NULL")

        for node in nodes:
            print node.name
            for attrib in node.attribs:
                print '\t', attrib.name, '=', attrib.value

    def getNodes(self):
        '''
        Build an array of Node objects comprising the worker nodes of the cluster.
        '''
        #pbs_statnode queries the pbs server over an existing connection and
        #returns a list of nodes and some of their properties
        nodelist = pbs.pbs_statnode(self.con, "", "NULL", "NULL")

        #Iterate through the nodelist, creating
        for node in nodelist:
            thisnode = Node()
            thisnode.setHostname(node.name)
            for attrib in node.attribs:
                if attrib.name == 'state':
                    thisnode.setState(attrib.value)
                elif attrib.name == 'np':
                    #np attribute contains the number of cpu cores
                    #as defined in Torques nodes file
                    thisnode.setNumCpus(attrib.value)
                elif attrib.name == 'properties':
                    #"properties" is a resource-manager 'label' indicating
                    #any specific features provided by this node, such as
                    #applications or physical components
                    propertyList = attrib.value.split(',')
                    for propertyName in propertyList:
                        thisnode.addProperty(propertyName)
                        print "added property",propertyName
                elif attrib.name == 'status':
                    #Torque 'status' contains a value which is in turn a string of attributes
                    #and corresponding values(e.g name1=value1,name2=value2 etc)
                    variables = attrib.value.split(',')
                    pairs = [variable.split('=',1) for variable in variables]
                    for data in pairs:
                        if data[0] == 'jobs':
                            for job in data[1]:
                                print "job is ",job
                        elif data[0] == 'physmem':
                            thisnode.setMem(data[1])
                            print "mem is ",thisnode.mem
                        else: print "data is ",data
                else:
                    print "attrib is",attrib.name,"and value is",attrib.value
            thisnode.printDetails()



##Un-comment for unit testing.
print "Creating new Torque Driver"
TD = TorqueDriver()
print "Created!"
TD.getServerName()
print "Server name is %s" % TD.serverName
print "Trying to connect..."
TD.connect()
#print "Trying to disconnect..."
#TD.disconnect()

TD.dumpDetails()
print TD.connectionStatus
TD.getNodes()
