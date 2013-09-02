'''
---------------------------------------------------------------
hpc-scaler - An Open-Source Dynamic HPC Cluster Scaling Engine
---------------------------------------------------------------
DCSE - Dynamic Cluster Scaling Engine:
This module builds on the included ClusterInterface and NodeController packages to interact with a HPC Cluster
in order to make decisions about powering on or off worker nodes, or expanding into a public cloud offering,
based on user configuration by documented configuration file.

Created on 3 Aug 2013

@author: ronan
'''

from ClusterInterface.Cluster import Cluster
from ClusterInterface.Job import Job
from WorkerNode import WorkerNode
import ConfigParser
import os
import sys
import datetime
import time


class DCSE(object):

    def __init__(self, cfgFile):
        ##Find the directory we are working in
        self.basedir = os.path.dirname(__file__)+'/'
        #print "DEBUG: Running DCSE from %s" % self.basedir
        self.cfg = cfgFile
        #first, read, validate, and process our configuration file
        self.readConfig()

        runcount = 0
        ## Daemonise process in an infinite loop
        while True:
            try:
                ##Now create our cluster object which invokes the ClusterInterface, giving
                # us access to the ClusterInterface's methods via self.Cluster.interface
                #
                self.createCluster()

                ##Our next step is dependent on the "strategy" choosen in the configuration file.
                # The startEngine function will check the cluster and carry out any actions necessary
                # to fulfill the targets set out in the configuration file.
                #
                self.startEngine()
                self.Cluster = None #kill existing cluster data for next iteration.
                #print "DEBUG: zzz...%s seconds" % self.checkInterval
                time.sleep(int(self.checkInterval))
                runcount += 1
            except KeyboardInterrupt as ctrlc:
                #Close any existing connection to our cluster interface
                self.Cluster.interface.disconnect()
            #except Exception as e:
               # print e

        #self.Cluster.interface.getJobs()
        #self.Cluster.interface.printJobs()




    def readConfig(self):
        '''
        The DCSE  needs to get its configuration entirely from the configuration file we are passed here.
        The default configuration file in documented inline with detailed information about the options
        available. This module is only interested in general settings, within the "General" section of
        the config file. As this is the only means for user input to the application, it should be
        strictly validated.
        '''
        ##Open the config file for reading and find the relevant section. Some detailed validation needs
        # to be performed on the configuration variables we accept to avoid problems later.
        #
        try:

            #Make sure the config file exists and is readable
            if not os.path.isfile(self.cfg):
                raise ConfigErrorException("Configuration file %s does not exist or cannot be read" % self.cfg)
                sys.exit(0)
            #If the config file includes a path, find it.
            self.cfgDir = os.path.dirname(self.cfg)
            if not self.cfgDir:
                #config file is in the current working directory.
                self.cfgDir = os.path.dirname(__file__)
            self.cfgPath = self.cfgDir+"/"+self.cfg
            #Parse the config file into a RawConfigParser object
            config = ConfigParser.RawConfigParser()
            config.read(self.cfg)
            #The DCSE module is only interested in the "General" section of the configuration.
            config_section = "General"

            #The first configuration value we look for is the logfile entry so we can begin
            #logging right away
            self.logFile = config.get(config_section, "logfile")
            msg = LogEntry(self.logFile, "Started hpc-scaler DCSE at %s" % datetime.datetime.now())

            #First, get some basic information about our cluster
            self.clusterName = config.get(config_section, "cluster_name")


            ##Worker nodes may be hardware based, cloud based, or some mix of the two.
            # Accept boolean values for each type of node, and see which type we prefer,
            # 'Hardware' or 'Cloud'
            #
            self.hasHardware = config.get(config_section, "has_hardware")
            if not self.hasHardware in ("True","False"):
                raise ConfigErrorException("'has_hardware' must be 'True' or 'False'. Currently '%s'" % self.hasHardware)

            self.hasCloud = config.get(config_section, "has_cloud")
            if not self.hasCloud in ("True","False"):
                raise ConfigErrorException("'has_cloud' must be 'True' or 'False'. Currently '%s'" % self.hasCloud)

            #Which type of node do we prefer? "Hardware" or "Cloud"?
            self.preferred = config.get(config_section, "node_preference")
            if not self.preferred in ("Hardware","Cloud"):
                raise ConfigErrorException("'node_preference' must be 'Hardware' or 'Cloud'. Currently '%s'" % self.preferred)

            ##Obtain the chosen strategy for cluster scaling:
            # longestqueued = Satisfy job which has been queued the longest
            # bestfit = Satisfy job which will use the most resources from our action
            #
            self.strategy = config.get(config_section, "strategy")
            if not self.strategy in ("longestqueued","bestfit"):
                raise ConfigErrorException("strategy must be 'longestqueued' or 'bestfit'. Currently '%s'" % self.strategy)

            #Get the number of spare physical and/or cloud nodes to keep booted
            if self.hasHardware == 'True':
                self.spareHardware = int(config.get(config_section, "spare_hardware"))
                if not isInt(self.spareHardware):
                    raise ConfigErrorException("'spare_hardware' should be an integer value. Currently '%s'" % self.spareHardware)

            if self.hasCloud == 'True':
                self.spareCloud = config.get(config_section, "spare_cloud")
                if not isInt(self.spareCloud):
                    raise ConfigErrorException("'spare_cloud' should be an integer value. Currently '%s'" % self.spareCloud)



            self.checkInterval = config.get(config_section, "check_interval")
            if not isInt(self.checkInterval):
                raise ConfigErrorException("'check_interval' should be an integer value. Currently '%s'" % self.checkInterval)
            elif int(self.checkInterval) < 5:
                raise ConfigErrorException("'check_interval' must be greater than five seconds. Currently '%s'" % self.checkInterval)

            #Inform the console (and the logs) of the validated configuration we are using
            msg = LogEntry(self.logFile, "Using validated DCSE configuration from %s" % self.cfgPath)  #FIXME: static
            msg.show()
        except ConfigParser.NoSectionError as section_err:
            error = LogEntry(self.logFile, "The Configuration file does not contain a valid [General] section.")
            error.show()
            sys.exit(0)
        except ConfigParser.NoOptionError as invalid_cfg_err:
            error = LogEntry(self.logFile, "A required configuration item was not found in the configuration file: %s" % invalid_cfg_err)
            error.write()
            error.show()
            sys.exit(0)
        except ConfigErrorException as cfg_err:
            error = LogEntry(self.logFile, "A configuration error was encountered in %s: %s" % (self.cfg,cfg_err))
            error.write()
            error.show()
            sys.exit(0)
        except Exception as err:
            error= LogEntry(self.logFile, "An unknown error occurred reading the configuration file at %s: %s" % (self.cfgPath,err))
            error.show()
            error.write()
            sys.exit(0)

    def createCluster(self):
        '''
        Initialised the Cluster object and creates an interface for communication with
        a HPC cluster via the ClusterInterface package. The DCSE does not need to know
        what third party driver to use to connect to the cluster - the ClusterInterface
        will handle that configuration section
        '''
        try:
            #Create cluster object using the full path to the configuration file
            self.Cluster = Cluster(self.cfgPath)  #Creates an interface at Cluster.interface

            #self.Cluster.interface.getNodes()
            #self.Cluster.interface.listNodes()

        except Exception as e:
            print e

    def getLongestJobSpec(self):
       self.Cluster.interface.getLongestWait()
       self.required_nodes = self.Cluster.interface.longest_wait_nodes
       self.required_ppn = self.Cluster.interface.longest_wait_ppn


    def startEngine(self):
            '''
            This function carries out the checks and power-ons/offs that are the core functionality
            of the Dynamic Cluster Scaling Engine
            '''
            #try:
            ## First, check the current state of utilisation of the cluster.
            # i.e are we currently over-provisioned or under-provisioned?
            # Then we can determine which method to invoke
            self.Cluster.interface.connect()    #Make a connection to the cluster
            self.Cluster.interface.getNodes()   #Populate our node lists via the cluster interface
            self.Cluster.interface.getJobs()    #Populate our job lists via the cluster interface


            #Now break down nodes into full, idle, and down.
            numFullNodes = len(self.Cluster.interface.fullnodes)
            numIdleNodes = len(self.Cluster.interface.idlenodes)
            numCloudNodes = len(self.Cluster.interface.cloudnodes)
            numIdleCloudNodes = len(self.Cluster.interface.idlecloudnodes)
            numIdleHardwareNodes = len(self.Cluster.interface.idlehardwarenodes)
            numDownNodes = len(self.Cluster.interface.downnodes)
            #Break down jobs into queued and running
            numJobs = len(self.Cluster.interface.jobs)
            numQueuedJobs = len(self.Cluster.interface.queuedJobs)
            #Get data about longest waiting job
            self.Cluster.interface.getLongestWait()  #Find the job which has been queued the longest
            longestWait = self.Cluster.interface.longest_wait_time      #Time waited, in seconds
            longWaitNodes = self.Cluster.interface.longest_wait_nodes   #Nodes requested
            longWaitPpn = self.Cluster.interface.longest_wait_ppn       #CPUs per node requested
            longWaitProps = self.Cluster.interface.longest_wait_props   #Node properties requested
            #Get data about total resource requests in the queue
            #self.Cluster.interface.getQueueData()


            #Print some summary information on each iteration
            nodesMsg = LogEntry(self.logFile, "Found %d idle nodes and %d down nodes" % (numIdleNodes, numDownNodes))
            nodesMsg.show()
            jobsMsg = LogEntry(self.logFile, "Found %d queued jobs out of %d jobs total" % (numQueuedJobs, numJobs))
            jobsMsg.show()




            #Decide if there is demand or there isn't. First indicator would be jobs in the queue!
            if numQueuedJobs > 0:   #There are jobs in the queue
                #We're in demand!
                if numIdleNodes > 0:
                    ##If there is at least one idle node, any demand must be for specific node properties
                    # or be due to a user or group exceeding their allocation. Cannot be considered to be
                    # in Demand
                    #
                    inDemand = False
                    #print "DEBUG: Cluster not in Demand."
                    #Still attempt to free the job which has been queued the longest
                    msg = LogEntry(self.logFile, "No demand for backfill strategy (idle nodes present) - falling back to longestqueued strategy")
                    msg.show()
                    msg.write()
                    self.longestQueuedStrategy(longWaitNodes, longWaitPpn, longWaitProps)
                else: # Queued jobs + No idle nodes = Demand!
                    print "DEBUG: Cluster in Demand."
                    inDemand = True
            else:   #No jobs in the queue can only mean we're not in demand
                inDemand = False
                print "DEBUG: Cluster Not in Demand."


            if inDemand == True:
                ## Now execute our chosen strategy for cluster expansion
                if self.strategy == 'longestqueued':
                    waitMsg = LogEntry(self.logFile, "Longest wait has been %d seconds for %d nodes of %d cpus each" \
                                       % (longestWait, longWaitNodes, longWaitPpn))
                    #waitMsg.show()
                    waitMsg.write()
                    self.longestQueuedStrategy(longWaitNodes, longWaitPpn, longWaitProps)
                elif self.strategy == 'bestfit':
                    self.bestFitStrategy()
                    pass
            elif inDemand == False:
                ## Cluster is not in demand, so initiate a shutdown of idle nodes
                if self.hasHardware == 'True':
                    if numIdleHardwareNodes > self.spareHardware:    #Our config file allows for a specified number of "spare" idle nodes

                        poweredoffcount = 0                                                     #Count nodes we power off.
                        idlehardwarenodes = self.Cluster.interface.idlehardwarenodes                  #Take a copy before iteration and modification
                        for node in idlehardwarenodes:                                             #Iterate through local copy
                            if len(self.Cluster.interface.idlehardwarenodes) > self.spareHardware:    #we have more idle cloud nodes than we'd like
                                try:
                                    Worker = WorkerNode(self.cfgPath,node.hostname,node.nodeType)   #Workernode is a generic type providing an interface to the driver
                                    Worker.interface.powerOff()                                     # This is where the magic happens...
                                    self.Cluster.interface.idlehardwarenodes.remove(node)              #Pop it off the list of idle nodes
                                    poweredoffcount += 1
                                    msg = LogEntry(self.logFile, "Powered off idle hardware node %s" % node.hostname)
                                    msg.show()
                                    msg.write()
                                except Exception as e:
                                    msg = LogEntry(self.logFile, e)
                                    msg.show()
                                    msg.write()
                                                                              #and increment our powered off counter.
                if self.hasCloud == 'True':
                    if numIdleCloudNodes > self.spareCloud:    #Our config file allows for a specified number of "spare" idle nodes
                        poweredoffcount = 0                                                     #Count nodes we power off.
                        idlecloudnodes = self.Cluster.interface.idlecloudnodes                  #Take a copy before iteration and modification
                        for node in idlecloudnodes:                                             #Iterate through local copy
                            if len(self.Cluster.interface.idlecloudnodes) > self.spareCloud:    #we have more idle cloud nodes than we'd like
                                try:
                                    Worker = WorkerNode(self.cfgPath,node.hostname,node.nodeType)   #Workernode is a generic type providing an interface to the driver
                                    Worker.interface.powerOff()                                     # This is where the magic happens...
                                    self.Cluster.interface.idlecloudnodes.remove(node)              #Pop it off the list of idle nodes
                                    poweredoffcount += 1                                            #and increment our powered off counter.
                                    msg = LogEntry(self.logFile, "Powered off idle cloud node %s" % node.hostname)
                                    msg.show()
                                    msg.write()
                                except Exception as e:
                                    msg = LogEntry(self.logFile, e)
                                    msg.show()
                                    msg.write()

            ## Terminate the connection to the pbs_server rather than waiting for a timeout -
            # otherwise the server eventually hits its resource limit.
            self.Cluster.interface.disconnect()
        #except Exception as e:
        #    print e


    def longestQueuedStrategy(self, nodes, ppn, properties):
        '''
        Function to power on the nodes needed to satisfy the longestqueued strategy
        '''
        stratMsg = LogEntry(self.logFile, "Using 'longestqueued' strategy to provision resources")
        stratMsg.show()
        stratMsg.write()

        ##Use the ClusterDriver getMinNodes method to populate the suitableNodes
        # and recommendedNodes lists, which contain a list of all eligible nodes
        # to run this job, and a subset of this list containing only enough
        # resources to run this specific job respectively.
        #
        self.Cluster.interface.getMinNodes(nodes, ppn, properties)
        ## Some debugging information
        #print "DEBUG: Nodes available that meet the criteria:"
        #print "Nodes: %d\t PPN: %d\nProperties:" % (nodes,ppn)
        #for p in properties:
        #   print p
        suitMsg = LogEntry(self.logFile, "Found %d suitable nodes" % len(self.Cluster.interface.suitableNodes))
        suitMsg.show()
        suitMsg.write()
        #for node in self.Cluster.interface.suitableNodes:
        #    print node.printDetails()

        ##Copy our recommendedNodes array. We can use this to add additional nodes to
        # the list we've already tried (in case substitutons are needed) to save modifying
        # an object which is being iterated through.
        #
        triednodes = self.Cluster.interface.recommendedNodes
        #print "DEBUG: Nodes selected to fulfill this request:"
        for node in self.Cluster.interface.recommendedNodes:
            #print node.hostname
            #print "DEBUG:\n",node.printDetails()
            ##New worker node object creates a WorkerNode interface
            # May need to recursively call this until we get success - some nodes may not be
            # contactable due to failure, maintenance, etc.
            #
            successFlag = False
            while successFlag == False:
                try:
                    Worker = WorkerNode(self.cfgPath,node.hostname,node.nodeType)
                    #print "DEBUG: Worker is", dir(Worker)
                    #print "DEBUG: interface is", dir(Worker.interface)
                    #print "--------------\nDEBUG\n-------------\n",Worker.interface.printDetails(),"\n----------------"
                    Worker.interface.powerOn()
                    #No exceptions thus far means we can flag this operation a success!
                    successFlag = True
                    ##Log and output the error if we weren't able to start a node, but
                    # also try to find an alternative node from the suitable nodes list
                    #
                    msg = LogEntry(self.logFile, "Powered on node %s" % node.hostname)
                    msg.show()
                    msg.write()
                except Exception as node_contact_error:
                    msg = LogEntry(self.logFile, "When powering on node %s, got %s" % (node.hostname,node_contact_error))
                    msg.show()
                    msg.write()
                    try:
                        #Fetch an alternative node that isn't already on the recommendedNodes list.
                        node = self.getAlternativeNode(self.Cluster.interface.suitableNodes, triednodes)
                        triednodes.append(node)
                    except NodesExhaustedException as nex:
                        msg = LogEntry(self.logFile, "No more nodes left to try - %s" % nex)
                        msg.show()
                        msg.write()
                        successFlag = True  # Misleading, as the operation failed, but we're done either way!
                        return  ##Break out of the loop

    def getAlternativeNode (self, suitables, trieds):
        '''
        Given a list of suitable nodes and a list of nodes already tried,
        return a suitable node to use as an alternative
        '''
        if not suitables:
            raise Exception("A list of suitable nodes must be provided")
        elif not trieds:
            raise Exception("A list of tried nodes must be provided")
        else:
            for node in suitables:
                if node not in trieds:
                    return node
            #If we get this far without returning a node, give up
            raise NodesExhaustedException("All possible nodes exhausted.")



    def bestFitStrategy(self):
        '''Function to power on enough nodes to satisfy the maximum possible of the queue'''
        ##Update queued request data via the cluster interface
        self.Cluster.interface.getNumQueuedNodes()
        self.Cluster.interface.getNumQueuedCpus()
        #Get the maximum amount of nodes we can be asked for
        maxNodes = self.Cluster.interface.numQueuedNodes
        #Get the total number of cpus we are being asked for.
        maxCpus = self.Cluster.interface.numQueuedCpus
        print "nodes is %d and cpus is %d" % (maxNodes, maxCpus)

        #Get the total number of cpus for queued jobs
        pass




class LogEntry(object):
    '''Class to add a message to the log file'''

    def __init__(self, logFile, msg):
        #Any exception must be caught here, so that only logging is affected
        self.msg = msg
        self.time = datetime.datetime.now()
        self.logFile = logFile

    def write(self):
        try:
            fh = open(self.logFile, 'a')
            fh.write("%s %s\n" % (self.time,self.msg))
        except IOError as ioe:
            print "An error occurred opening the logfile %s:" % self.logFile
        finally:
            fh.close()

    def show(self):
        '''Outputs LogEntry object message to standard output'''
        print self.msg



class ConfigErrorException(Exception):
    pass

class NodesExhaustedException(Exception):
    pass

##Global functions
def isInt(num):
    '''Check whether a string value is an integer ( isinstance(x, int) will not work for string-stored integers)'''
    try:
        float(num)
        return True
    except ValueError:
        return False


##where the magic happens...
dcse = DCSE("hpc-scaler.cfg")
