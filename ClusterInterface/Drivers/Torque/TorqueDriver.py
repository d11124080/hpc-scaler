'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''


try:
    from pbs_python.fourthreefive import pbs, PBSQuery, PBSAdvancedParser
except (NameError, ImportError) as pbs_import_err:
    try:
        from Build import Build
    except (NameError, ImportError) as bld_imp_err:
        print "Fatal Error Building pbs_python:",bld_imp_err
    pbs_python_build = Build("../../../../../hpc-scaler.cfg")

try:
    from ClusterInterface.ClusterDriver import ClusterDriver
    from ClusterInterface.Node import Node
    from ClusterInterface.Job import Job
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
        self.nodes = []         #An array of the worker nodes (of type Node) of the cluster
        self.idlenodes = []     #An array of nodes that are idle (i.e no jobs currently running)
        self.fullnodes = []     #An array of nodes that are at maximum cpu core usage

    def connect(self, host=None):
        try:
            if host == None:
                pbs_server = pbs.pbs_default()
            else:
                pbs_server = host
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
            # Call our parent function's equivalent function as specified by the
            # ClusterDriver template for overwritten methods.
            super(TorqueDriver, self).getServerName()
        else:
            errno, text = pbs.error()
            print errno, text


    def dumpDetails(self):
        pbs_server = pbs.pbs_default()
        if not pbs_server:
            print "No default pbs server"
            sys.exit(1)

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
                        #print "added property",propertyName
                elif attrib.name == 'status':
                    #Torque 'status' contains a value which is in turn a string of attributes
                    #and corresponding values(e.g name1=value1,name2=value2 etc)
                    variables = attrib.value.split(',')
                    pairs = [variable.split('=',1) for variable in variables]
                    for data in pairs:
                        if data[0] == 'jobs':
                            if not data[1]:     ##if our list is empty, this node has no jobs running on it.
                                self.idlenodes.append(thisnode) ##Add to idle nodes list
                                thisnode.setNumJobs(0)          ##Set number of running jobs to zero
                                thisnode.setFreeCpus(thisnode.num_cpus) #Set free cpus to the total number of cpus on the node
                            else:               ##Node is running jobs
                                for jobid in data[1]:
                                    jobinstance = Job(jobid)
                                    thisnode.addJob(jobinstance)
                                thisnode.setNumJobs(thisnode.jobs.__len__())    ##Add the number of running jobs as a property of the node
                                if thisnode.num_jobs == thisnode.num_cpus:  ##If num_jobs = num_cpus, this node is completely full
                                    thisnode.setFreeCpus(0)
                                    self.fullnodes.append(thisnode)         ##Add to list of full nodes
                        elif data[0] == 'physmem':
                            thisnode.setMem(data[1])
                            #print "mem is ",thisnode.mem
                        #else: print "data is ",data
                #else:
                    #print "attrib is",attrib.name,"and value is",attrib.value
            #thisnode.printDetails()
            self.nodes.append(thisnode)
            self.total_nodes = len(self.nodes)
        print "number of nodes is ",self.total_nodes
        print "number of idle nodes is ",len(self.idlenodes)
        #print "number of free cpus is ", sum(sequence)





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

#TD.dumpDetails()
print TD.connectionStatus
TD.getNodes()
TD.getIdleNodes()
