'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''
try:
    from Drivers.Torque.Build import Build
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
    from pbs_python.fourthreefive import pbs, PBSQuery, PBSAdvancedParser
except (NameError, ImportError) as pbs_import_err:
    print "pbs_python module not built. Attempting to build..."
    try:
        #Build class compiles and installs the pbs_python package
        pbs_python_build = Build("../../../hpc-scaler.cfg") #FIXME: too static
    except Exception as build_err:
        print "An error occurred building the pbs_python module. Please attempt a manual build."
        sys.exit(0) ##Quit the program - we won't be able to speak to the Resource Manager.
    try:    ##We have built the binary - try import the module
        from pbs_python.fourthreefive import pbs, PBSQuery, PBSAdvancedParser
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
            if self.con:
                self.connectionStatus = 'Connected'
                self.serverName = pbs_server
                print "Connected to %s" % self.serverName
            else:
                raise Exception("Unable to connect to Torque/PBS Server")
                sys.exit(0) ##Quit the program - we won't be able to speak to the Resource Manager.
        except Exception, e:
            print e

    def disconnect(self):
        #pbs_disconnect returns non-zero value if an error occurs
        retval = pbs.pbs_disconnect(self.con)
        if (retval == 0):
            self.connectionStatus = 'Not Connected'
            self.con = 0
        else:
            #print pbs.pbs_statserver(self.con)
            print "retval is ",retval

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
            self.idle_nodes = len(self.idlenodes)
        #print "number of nodes is ", self.total_nodes
        #print "number of idle nodes is ", self.idle_nodes
        #print "number of free cpus is ", sum(sequence)

    def getJobs(self):
        p = PBSQuery.PBSQuery()
        jobslist = p.getjobs()
        self.numJobs = len(jobslist)
        for job_id, attributes in jobslist.iteritems():
            job = Job(job_id)
            for k,v in attributes.iteritems():
                #Resource_List contains a tuple we need to process further
                if k == 'Resource_List':
                    for resource,value in v.iteritems():
                        #print "resource is %s and value is %s" % (resource, value)
                        if resource == "nodes":  #Value corresponding to nodes is in format X:ppn=Y
                            #value is an array of one item
                            for elem in value:
                                if ":" in elem:    #Nodes may be colon separated with procs per node
                                    nodes,ppnstring = elem.split(":")
                                    job.numNodes = int(nodes)   #Cast as integer
                                    label,ppn = ppnstring.split("=")
                                    job.ppn = int(ppn)          #Cast as integer
                                    job.ncpus = job.numNodes * job.ppn  #Total CPUs requested for this job.
                                else:   #ppn not specified so is taken to be one
                                    job.numNodes = int(elem)
                                    job.ppn = 1
                                    job.ncpus = job.numNodes
                        elif resource == "walltime":
                            for elem in value: #resources are an array - walltime is a single item array
                                job.walltime = elem
                #Check job state last, so we can add the job object to the appropriate group
                elif k == 'job_state':
                    for item in v:
                        if item == 'Q':
                            job.status = 'queued'
                            self.queuedJobs.append(job)
                        elif item == 'R':
                            job.status = 'running'
                        else:
                            job.status = 'other'    #We are not interested in complete or errored jobs.
                elif k == 'qtime':
                    for elem in v:
                        job.qtime = int(elem)
            ##Now we have acquired all the information we need from each job. Store the job
            # data in our self.jobs array
            self.jobs.append(job)
            if job.status == 'queued':
                self.queuedJobs.append(job)

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
TD.getIdleNodes()
TD.getJobs()
'''