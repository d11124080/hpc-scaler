'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''
try:
    from Build import Build
    from ClusterDriver import ClusterDriver
    from Node import Node
    from Job import Job
    import sys

except (NameError, ImportError) as e:
    print "Component(s) not found or not readable at default location:"
    print e


## Attempt to import our pbs_python library module, which used compiled c libraries
# (_pbs.so). If the module isn't present, attempt to build it on the fly and reload.
# This should only happen once per installation.
#
try:
    from pbs_python.fourthreefive import pbs
except (NameError, ImportError) as pbs_import_err:
    print "pbs_python module not built. Attempting to build..."
    try:
        #Build class compiles and installs the pbs_python package
        pbs_python_build = Build("../../../hpc-scaler.cfg") #FIXME: too static
    except Exception as build_err:
        print "An error occurred building the pbs_python module. Please attempt a manual build."
        sys.exit(0) ##Quit the program - we won't be able to speak to the Resource Manager.
    try:    ##We have built the binary - try import the module
        from pbs_python.fourthreefive import pbs
    except (NameError, ImportError) as pbs_import_err:  #still unable to import, give up.
        print "An irrecoverable error occurred importing the pbs_python module. Quitting."
        sys.exit(0) ##Quit the program - we won't be able to speak to the Resource Manager.



class TorqueDriver(ClusterDriver):
    '''
    This driver for the Torque/PBS Resource Manager is designed to function as part of the
    ClusterInterface.
    '''


    def __init__(self):
        '''
        Constructor must call Parent Constructor as per the rules specified by the ClusterDriver class.
        '''
        self.con = 0            #Variable which will hold the socket connection to a torque server.
        super(TorqueDriver, self).__init__()    #Return control to parent constructor.

    def connect(self, host=None):
        try:
            if host == None:
                pbs_server = pbs.pbs_default()
                #print "pbs_server is %s" % pbs_server
            else:
                pbs_server = host
            self.con = pbs.pbs_connect(pbs_server)
            if self.con > 0:    #Fail is -1, Success is 1
                self.connectionStatus = 'Connected'
                self.serverName = pbs_server
                print "Connected to %s" % self.serverName
            else:
                raise Exception("Unable to connect to Torque/PBS Server")
        except Exception, e:
            print e
            sys.exit(0) ##Quit the program - we won't be able to speak to the Resource Manager.

    def disconnect(self):
        #pbs_disconnect returns non-zero value if an error occurs
        retval = pbs.pbs_disconnect(self.con)
        if (retval == 0):
            self.connectionStatus = 'Not Connected'
            self.con = 0

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
        ##serverName should be already set by the connect function, but
        # if not, use pbs_default as a fallback option.
        if not self.serverName:
            self.serverName = pbs.pbs_default()
        ##Call our parent function's equivalent function as specified by the
        # ClusterDriver template for overridden methods.
        super(TorqueDriver, self).getServerName()


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
            thisnode.nodeType = 'hardware'      #Node type is "hardware" unless it proves itself a cloud node!
            ##Bit of a hack, but set num jobs to zero initially - jobs data will not be given
            # where there are no jobs running on a node, so overwrite this if that happens
            thisnode.setNumJobs(0)          ##Set number of running jobs to zero
            thisnode.setFreeCpus(thisnode.num_cpus) #Set free cpus to the total number of cpus on the node

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
                        if propertyName == 'cloud':         #Node has the "cloud" property
                            thisnode.nodeType = 'cloud'     #Convert nodetype to cloud
                        #print "added property",propertyName
                elif attrib.name == 'status':
                    #Torque 'status' contains a value which is in turn a string of attributes
                    #and corresponding values(e.g name1=value1,name2=value2 etc)
                    variables = attrib.value.split(',')
                    pairs = [variable.split('=',1) for variable in variables]
                    for data in pairs:

                        if data[0] == 'physmem':
                            thisnode.setMem(data[1])
                        elif data[0] == 'jobs':
                            if data[1]:     ##if our list is not empty, this node jobs running on it.
                                for jobid in data[1]:
                                    jobinstance = Job(jobid)
                                    thisnode.addJob(jobinstance)
                                thisnode.setNumJobs(thisnode.jobs.__len__())    ##Add the number of running jobs as a property of the node
                                if thisnode.num_jobs == thisnode.num_cpus:  ##If num_jobs = num_cpus, this node is completely full
                                    thisnode.setFreeCpus(0)
                                    self.fullnodes.append(thisnode)         ##Add to list of full nodes

                        #else: print "data is ",data[0]
                #else:
                    #print "attrib is",attrib.name,"and value is",attrib.value
            #thisnode.printDetails()
            self.nodes.append(thisnode)
            if thisnode.num_jobs == 0 and thisnode.state != 'down':
                thisnode.setState('idle')
            if thisnode.state == 'down':
                self.downnodes.append(thisnode)
            elif thisnode.state == 'idle':
                self.idlenodes.append(thisnode)
            if thisnode.nodeType == 'cloud':
                self.cloudnodes.append(thisnode)
                if thisnode.state == 'idle':
                    self.idlecloudnodes.append(thisnode)
            elif thisnode.nodeType == 'hardware':
                if thisnode.state == 'idle':
                    self.idlehardwarenodes.append(thisnode)
        self.total_nodes = len(self.nodes)
        self.idle_nodes = len(self.idlenodes)
        self.down_nodes = len(self.downnodes)
        self.numIdleCloudNodes = len(self.idlecloudnodes)
        self.numIdleHardwareNodes = len(self.idlehardwarenodes)
        #print "number of nodes is ", self.total_nodes
        #print "number of down nodes is",self.down_nodes
        #print "number of idle nodes is ", self.idle_nodes
        #print "number of free cpus is ", sum(sequence)


    def getJobs(self):
        self.numCpusInUse = 0
        #p = PBSQuery.PBSQuery()

        #jobslist = p.getjobs()

        jobslist = pbs.pbs_statjob(self.con, "", "NULL", "NULL")
        for jobInst in jobslist:
            job = Job(jobInst.name)
            #print "name is"+jobInst.name+"text is",jobInst.text,"next is",jobInst.next,"and this is",jobInst.this
            for attrib in jobInst.attribs:
                #print attrib.name+" is the name and the value is "+attrib.value
                if attrib.name == 'Resource_List':
                    if attrib.resource == "nodes":  #Value corresponding to nodes is in format (nodes=)X:ppn=Y[:property1[:propertyN]]
                            #value is an array of one item
                            if ":" in attrib.value:    #Node data may be colon separated with procs per node and node properties
                                #print "value for nodes is %s" % attrib.value
                                #nodes,ppnstring = attrib.value.split(":")

                                nodeDataList = attrib.value.split(":")
                                job.numNodes = int(nodeDataList[0])
                                iterNum = 0     ##Needed to iterate through our properies and skip the first one.
                                for item in nodeDataList:
                                    if "=" in item:         #An equals suggests a nodes= or ppn= assignment
                                        label,value = item.split("=")
                                        if label == 'ppn':
                                            job.ppn = int(value)
                                        ##No else, as it would match the walltime entry!
                                    else:       #No equals sign means this is a property
                                        if iterNum > 0: ##unless its the num_nodes int we stripped off earlier!
                                            job.properties.append(item)
                                            #If node has a "cloud" property, its cloud, else hardware

                                    iterNum += 1
                            else:   #ppn not specified so is taken to be one
                                job.numNodes = int(attrib.value)
                                job.ppn = 1
                                job.ncpus = job.numNodes
                    elif attrib.resource == "walltime":
                        job.walltime = attrib.value
                    elif attrib.resource == "nodect":
                        job.nodect = attrib.value
                    else:
                        print "attrib resource is %s" % attrib.resource
                elif attrib.name == 'qtime':
                    job.qtime = int(attrib.value)
                elif attrib.name == 'job_state':
                    if attrib.value == 'Q':
                        job.status = 'queued'
                        self.queuedJobs.append(job)
                    elif attrib.value == 'R':
                        job.status = 'running'
                        self.numCpusInUse += job.ncpus
                    else:
                        job.status = 'other'    #We are not interested in complete or errored jobs.
                else:
                    pass
                    #print "Attrib name is %s and value is %s" % (attrib.name, attrib.value)
            ##Now we have acquired all the information we need from each job. Store the job
            # data in our self.jobs array
            job.ncpus = job.numNodes * job.ppn
            self.jobs.append(job)
        self.numJobs = len(self.jobs)
        self.numQueuedJobs = len(self.queuedJobs)


##Un-comment for unit testing.
'''
print "***********************************"
print "UNIT TESTS FOR TORQUEDRIVER MODULE"
print "***********************************"
print "Creating new Torque Driver"
TD = TorqueDriver()
print "Created!"
print "Trying to connect..."
TD.connect()
print "Server name is %s" % TD.serverName
#print "Trying to disconnect..."
#TD.disconnect()

#TD.dumpDetails()
print TD.connectionStatus
TD.getNodes()
TD.listNodes()
TD.getJobs()
#TD.printJobs()
#TD.numDownNodes
TD.printJobs()
'''