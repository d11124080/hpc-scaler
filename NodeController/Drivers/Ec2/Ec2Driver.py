'''
hpc-scaler NodeController Driver Module for interacting with the Amazon EC2 API using boto.

Created on 29 Aug 2013

@author: ronan
'''
try:
    import sys
    import ConfigParser
    import boto
except (NameError, ImportError) as e:
    print "Component(s) not found or not readable at default location:"
    print e
    sys.exit(0)


class Ec2Driver(object):
    '''
    Amazon Elastic Compute Cloud Driver for the hpc-scaler NodeController. Requires configuration in
    the hpc-scaler.cfg configuration file.
    '''


    def __init__(self, cfgFile):
        '''
        Constructor initialised some variables and reads configuration from the config file
        '''
        # First, read the configuration file. We are only interested in the "Ec2" section
        # (The NodeController package can be a component of an application with a shared config file)
        config = ConfigParser.RawConfigParser()
        config.read(cfgFile)
        config_section = "Ec2"
        # Obtain configuration data for the cluster we will connect to.
        self.access_key_id = config.get(config_section, "aws_access_key_id")
        self.secret_access_key = config.get(config_section, "aws_secret_access_key")

    def printDetails(self):
        print "access key id is %s" % self.access_key_id
        print "secret access key is %s" % self.secret_access_key



#Un-comment for unit testing
ED = Ec2Driver("../../../hpc-scaler.cfg")
ED.printDetails()
