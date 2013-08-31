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
from NodeController import CloudNode,HardwareNode
import ConfigParser
import os
import sys
import datetime
import time


class DCSE(object):

    def __init__(self, cfgFile):
        ##Find the directory we are working in
        self.basedir = os.path.dirname(__file__)+'/'
        print "Running DCSE from %s" % self.basedir
        self.cfg = cfgFile
        #first, read, validate, and process our configuration file
        self.readConfig()

        count = 0
        ## Daemonise process in an infinite loop
        while True:
            #try:
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
                print "zzz...%s" % self.checkInterval
                time.sleep(int(self.checkInterval))
                count += 1
                print "ran %d times" % count

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
            self.strategy = config.get(config_section, "strategy")
            if not self.strategy in ("longestqueued","bestfit"):
                raise ConfigErrorException("strategy must be 'longestqueued' or 'bestfit'. Currently '%s'" % self.strategy)

            #Get the number of spare physical and/or cloud nodes to keep booted
            self.spareHardware = config.get(config_section, "spare_hardware")
            if not isInt(self.spareHardware):
                raise ConfigErrorException("'spare_hardware' should be an integer value. Currently '%s'" % self.spareHardware)

            self.spareCloud = config.get(config_section, "spare_cloud")
            if not isInt(self.spareCloud):
                raise ConfigErrorException("'spare_cloud' should be an integer value. Currently '%s'" % self.spareCloud)

            #Maximum number of cloud nodes we can activate at any given time
            self.maxCloudNodes = config.get(config_section, "max_cloud_nodes")
            if not isInt(self.maxCloudNodes):
                raise ConfigErrorException("'max_cloud_nodes' should be an integer value. Currently '%s'" % self.maxCloudNodes)

            self.checkInterval = config.get(config_section, "check_interval")
            if not isInt(self.checkInterval):
                raise ConfigErrorException("'check_interval' should be an integer value. Currently '%s'" % self.checkInterval)
            elif int(self.checkInterval) < 5:
                raise ConfigErrorException("'check_interval' must be greater than five seconds. Currently '%s'" % self.checkInterval)

            #Inform the console (and the logs) of the validated confiduration we are using
            msg = LogEntry(self.logFile, "Using validated DCSE configuration from %s" % self.cfgPath)  #FIXME: static
            msg.show()
        except ConfigParser.NoSectionError as section_err:
            print "The Configuration file does not contain a valid [General] section."
        except ConfigParser.NoOptionError as invalid_cfg_err:
            print "A required configuration item was not found in the configuration file:"
            print invalid_cfg_err
        except ConfigErrorException as cfg_err:
            print "A configuration error was encountered in %s:" % self.cfg
            print cfg_err
        except Exception as err:
            print "An unknown error occurred reading the configuration file at %s:" % self.cfgPath
            print err

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
        try:
            ## First, check the current state of utilisation of the cluster.
            # i.e are we currently over-provisioned or under-provisioned?
            # Then we can determine which method to invoke
            self.Cluster.interface.connect()    #Make a connection to the cluster
            self.Cluster.interface.getNodes()   #Populate our node lists via the cluster interface
            self.Cluster.interface.getJobs()    #Populate our job lists via the cluster interface
            self.Cluster.interface.getLongestWait() #Find the job which has been queued the longest

            #Now break down nodes into full, idle, and down.
            numFullNodes = len(self.Cluster.interface.fullnodes)
            numIdleNodes = len(self.Cluster.interface.idlenodes)
            numDownNodes = len(self.Cluster.interface.downnodes)
            #Break down jobs into queued and running
            numJobs = len(self.Cluster.interface.jobs)
            numQueuedJobs = len(self.Cluster.interface.queuedJobs)
            #Get data about longest waiting job
            self.Cluster.interface.printJobs()
            longestWait = self.Cluster.interface.longest_wait_time
            longWaitNodes = self.Cluster.interface.longest_wait_nodes
            longWaitPpn = self.Cluster.interface.longest_wait_ppn

            nodesMsg = LogEntry(self.logFile, "Found %d idle nodes and %d down nodes" % (numIdleNodes, numDownNodes))
            nodesMsg.show()
            jobsMsg = LogEntry(self.logFile, "Found %d queued jobs out of %d jobs total" % (numQueuedJobs, numJobs))
            jobsMsg.show()
            waitMsg = LogEntry(self.logFile, "Longest wait has been %d seconds for %d nodes of %d cpus each" \
                               % (longestWait, longWaitNodes, longWaitPpn))
            waitMsg.show()
            print "Longest job is waiting ",longestWait,"for",longWaitNodes,"nodes, with ",longWaitPpn,"CPU per node"

        except Exception as e:
            print e
        finally:
            self.Cluster.interface.disconnect()






class LogEntry(object):
    '''Class to add a message to the log file'''

    def __init__(self, logFile, msg):
        #Any exception must be caught here, so that only logging is affected
        self.msg = msg
        try:
            fh = open(logFile, 'a')
            fh.write(msg+"\n")
        except IOError as ioe:
            print "An error occurred opening the logfile %s:" % logFile
        finally:
            fh.close()

    def show(self):
        '''Outputs LogEntry object message to standard output'''
        print self.msg



class ConfigErrorException(Exception):
    pass

##Global functions
def isInt(num):
    '''Check whether a string value is an integer (isinstance(x, int) will not work for string-stored integers)'''
    try:
        float(num)
        return True
    except ValueError:
        return False





##where the magic happens...
dcse = DCSE("hpc-scaler.cfg")
