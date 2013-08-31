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

from ClusterInterface import Cluster
from NodeController import CloudNode,HardwareNode
import ConfigParser
import os


class DCSE(object):

    def __init__(self, cfgFile):
        self.cfg = cfgFile
        #first, read our configuration file
        self.readConfig()



    def readConfig(self):
        '''
        The DCSE  needs to get its configuration entirely from the configuration file we are passed here.
        The default configuration file in documented inline with detailed information about the options
        available. This module is only interested in general settings, within the "General" section of
        the config file.
        '''
        ##Open the config file for reading and find the relevant section. Some detailed validation needs
        # to be performed on the configuration variables we accept to avoid problems later.
        #
        try:
            #Make sure the config file exists and is readable
            if not os.path.isfile(self.cfg):
                raise Exception("Configuration file %s does not exist or cannot be read" % self.cfg)
            #Parse the config file into a RawConfigParser object
            config = ConfigParser.RawConfigParser()
            config.read(self.cfg)
            #The DCSE module is only interested in the "General" section of the configuration.
            config_section = "General"

            #First, get some basic information about our cluster
            self.clusterName = config.get(config_section, "cluster_name")

            ##Worker nodes may be hardware based, cloud based, or some mix of the two.
            # Accept boolean values for each type of node, and see which type we prefer,
            # 'Hardware' or 'Cloud'
            self.hasHardware = config.get(config_section, "has_hardware")
            self.hasCloud = config.get(config_section, "has_cloud")
            self.preferred = config.get(config_section, "node_preference")

            ##Obtain the chosen algorithm for cluster scaling:
            # longestqueued = Satisfy job which has been queued the longest
            # bestfit = Satisfy job which will use the most resources from our action
            self.algorithm = config.get(config_section, "algorithm")

            #

            ##
            #
            self.driverPath = config.get(config_section, "driver_path")
            self.driver = config.get(config_section, "cluster_driver")
        except ConfigParser.NoSectionError as section_err:
            print "The Configuration file does not contain a valid [General] section."
        except ConfigParser.NoOptionError as invalid_cfg_err:
            print "A required configuration item was not found in the configuration file:"
            print invalid_cfg_err
        except Exception as other_cfg_err:
            print other_cfg_err







##Invalid config file
dcse = DCSE("hpc-scaler.cfg")
