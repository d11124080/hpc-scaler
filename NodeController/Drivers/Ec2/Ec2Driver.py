'''
hpc-scaler NodeController Driver Module for interacting with the Amazon EC2 API using boto.

Created on 29 Aug 2013

@author: ronan
'''
try:
    from CloudNode import CloudNode
    import sys
    import ConfigParser
    import boto.ec2
    import socket
except (NameError, ImportError) as e:
    print "Component(s) not found or not readable at default location:"
    print e
    sys.exit(0)



class Ec2Driver(CloudNode):
    '''
    Amazon Elastic Compute Cloud Driver for the hpc-scaler NodeController. Requires configuration in
    the hpc-scaler.cfg configuration file.
    '''

    def __init__(self, cfgFile, hostname):
        '''
        Constructor initialised some variables and reads configuration from the hpc-scaler.cfg configuration file.
        '''
        #take in hostname
        self.hostname = hostname
        self.ipAddr = socket.gethostbyname(hostname)
        # First, read the configuration file. We are only interested in the "Ec2" section
        # (The NodeController package can be a component of an application with a shared config file)
        config = ConfigParser.RawConfigParser()
        config.read(cfgFile)
        config_section = "Ec2"
        # Obtain configuration data for the cluster we will connect to.
        self.access_key_id = config.get(config_section, "aws_access_key_id")
        self.secret_access_key = config.get(config_section, "aws_secret_access_key")
        self.aws_region = config.get(config_section, "aws_region")
        self.aws_ssh_key = config.get(config_section, "aws_ssh_key")
        self.aws_ami = config.get(config_section, "aws_ami")
        self.aws_type = config.get(config_section, "aws_type")
        self.aws_suffix = config.get(config_section, "aws_suffix")

        # Get the Public IP associated with this hostname
        try:
            self.ec2Addr = socket.gethostbyname(self.hostname+"."+self.aws_suffix)
        except socket.error as error:
            #re-raise our exception to the calling class
            raise Exception("Error resolving %s.%s - %s" % (self.hostname,self.aws_suffix,error))
        if not self.ec2Addr:       # Should be caught by socket.error, but in case another error occurred
            raise Exception("Unexpected error in EC2 driver when assigning address.")


        ##Now need to build our boto config on the fly - this saves the user having to generate a
        #boto configuration file. See https://code.google.com/p/boto/wiki/BotoConfig for further info.
        #
        if not boto.config.has_section('Boto'):
            boto.config.add_section('Boto')
            boto.config.set('Boto', 'num_retries', '0')
        if not boto.config.has_section('Credentials'):
            boto.config.add_section('Credentials')
            boto.config.set('Credentials', 'aws_access_key_id', self.access_key_id)
            boto.config.set('Credentials', 'aws_secret_access_key', self.secret_access_key)

    def printDetails(self):
        '''Print Driver object data for debugging'''
        print "access key id is %s" % self.access_key_id
        print "secret access key is %s" % self.secret_access_key
        print "using ssh key %s" % self.aws_ssh_key
        print "aws region is %s" % self.aws_region
        print "ami is %s" % self.aws_ami
        print "instance type is %s" % self.aws_type
        print "Number of running instances: %d" % self.numRunningInstances
        if self.runningInstances:
            print "Instances:"
            for i in self.runningInstances:
                print i

    def connect(self):
        #Initiate a connection to the amazon region specified in our config file.
        #No need to disconnect, as these API connections are over HTTPS
        try:
            self.conn = boto.ec2.connect_to_region(self.aws_region)
            print "Connected: ",self.conn
        except Exception as e:
            print "Error occurred connecting to Amazon Web Services:"
            raise Exception(e)  ##Re-raise exception

    def disconnect(self):
        self.conn = None    #Not really required, but why not...

    def getRunningInstances(self):
        self.runningInstances = self.conn.get_all_instances()
        self.numRunningInstances = len(self.runningInstances)

    def getKeypairs(self):
        keypairs = self.conn.get_all_key_pairs()
        for i in keypairs:
            print i

    def getAddresses(self):
        self.addresses = self.conn.get_all_addresses()
        #for i in self.addresses:
        #   print i

    def getAllImages(self):
        '''Return a list of all available images'''
        self.images = self.conn.get_all_images()


    def powerOn(self):
        '''Start an Ec2 instance based on the machine type specified in the configuration file'''
        ##First find an unused public IP address from our pool
        self.getAddresses()
        self.getRunningInstances()
        for inst in self.runningInstances:
            print inst
            pass

        reservation = self.conn.run_instances(image_id=self.aws_ami, key_name=self.aws_ssh_key, instance_type=self.aws_type)
        for r in self.conn.get_all_instances():
            if r.id == reservation.id:
                break
            print r.instances[0].public_dns_name
            self.instanceId = reservation.id
        pass

    def stopInstance(self):
        try:
            stoppedInstances = self.conn.stop_instances(self.instanceId)
            if not stoppedInstances:
                raise Exception("Unable to stop instance %s - Manual Intervention is Required" % self.instanceId)
        except Exception as err:
            print err





#Un-comment for unit testing
#'''
ED = Ec2Driver("../../../hpc-scaler.cfg", None)

ED.connect()
ED.getRunningInstances()
ED.printDetails()
ED.getKeypairs()
#ED.startInstance()
#'''
