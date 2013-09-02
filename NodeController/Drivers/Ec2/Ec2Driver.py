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
    import time
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
        #Aws security groups needs to be an array, even a single element one.
        self.aws_security_groups = []
        self.aws_security_groups.append(config.get(config_section, "aws_security_group"))
        self.aws_api_delay = int(config.get(config_section, "aws_api_delay"))
        #Maximum number of cloud nodes we can activate at any given time
        self.maxCloudNodes = int(config.get(config_section, "max_cloud_nodes"))

        #Resolve IP of our hostname
        self.resolveIP()            #From parent class

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


        ##Once all is configured, connect to EC2, and obtain our running instances.
        self.connect()
        #Obtain an initial list of running instances, keypairs, and addresses
        self.getRunningInstances()
        self.getKeypairs()
        self.getAddresses()


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
                print i.id,"(",i.state,",",i.ip_address,")"

    def connect(self):
        #Initiate a connection to the amazon region specified in our config file.
        #No need to disconnect, as these API connections are over HTTPS
        try:
            self.conn = boto.ec2.connect_to_region(self.aws_region)
            #print "DEBUG: Connected: ",self.conn
        except Exception as e:
            print "Error occurred connecting to Amazon Web Services:"
            raise Exception(e)  ##Re-raise exception

    def disconnect(self):
        self.conn = None    #Not really required, but why not...

    def getRunningInstances(self):
        self.runningInstances = [] #new empty list of running instances
        # First obtain a list of all instances/reservations, including stopped, terminated, etc
        self.allInstances = self.conn.get_all_instances()
        # Now check the state of each instance, and only track the running ones.
        for reservation in self.allInstances:
            for instance in reservation.instances:
                #print dir(instance)
                #print instance.state
                if instance.state == 'terminated' or instance.state == 'shutting-down'\
                or instance.state == 'stopping' or instance.state == 'stopped':
                    pass    ##Do nothing - this is not an active instance
                elif instance.state == 'pending' or instance.state == 'running':
                    self.runningInstances.append(instance)
                self.numRunningInstances = len(self.runningInstances)

    def getKeypairs(self):
        self.keypairs = self.conn.get_all_key_pairs()


    def getAddresses(self):
        '''
        Fetch the available Elastic IP addresses from our EC2 Pool. Reject any IP
        addresses which are already bound to an instance.
        '''
        self.addresses = [] ##new empty array
        ##get_all_addresses returns a list of boto Address objects
        # we are interested in the "public_ip" and "instance_id" values
        # within these objects
        self.address_objects = self.conn.get_all_addresses()
        for address_obj in self.address_objects:
            if not address_obj.instance_id:     #Only accept IP addresses not already assigned
                self.addresses.append(address_obj.public_ip)
            else:
                #print "DEBUG: ip address %s already in use by instance %s" % (address_obj.public_ip,address_obj.instance_id)
                pass


    def getAllImages(self):
        '''Return a list of all available images'''
        self.images = self.conn.get_all_images()


    def powerOn(self):
        '''Start an Ec2 instance based on the machine type specified in the configuration file'''

        try:
            # Some checks before powering on the instance.
            self.getRunningInstances() #update the list of running instances
            if self.numRunningInstances >= self.maxCloudNodes:
                raise Exception("Error: You have reached the maximum number (%d) of cloud instances specified in the config file" % self.maxCloudNodes)
            ##First match the hostname we were given with a public IP address from our EC2 pool
            self.getAddresses()
            if self.ipAddr not in self.addresses:
                raise Exception("Error: The selected host IP address "+self.ipAddr+" is not available in the EC2 Pool")


            #self.getRunningInstances()
            #print dir(self.runningInstances)
            #for inst in self.runningInstances:
            #   #print "DEBUG:inst is %s and state is %s and ip is %s" % (inst.id, inst.state, inst.ip_address)
            #   pass


            reservation = self.conn.run_instances(image_id=self.aws_ami, key_name=self.aws_ssh_key, \
                                                  instance_type=self.aws_type, security_groups=self.aws_security_groups)
            time.sleep(self.aws_api_delay)  #give the aws backend time to deliver
            #Check the live instances for our current instance.
            for r in self.conn.get_all_instances():
                if r.id == reservation.id:          ##If there's a match, our reservation is live
                    break
            for inst in reservation.instances:
                self.instanceId = inst.id           #Obtain the EC2 instance ID

            ##Next we need to assign the unised IP address we selected earlier to this instance.
            #print "DEBUG: Requesting address %s for instance %s" % (self.ipAddr, reservation.id)
            assignment = self.conn.associate_address(public_ip=self.ipAddr,instance_id=self.instanceId)
            #print "DEBUG: ", dir(assignment)
            time.sleep(self.aws_api_delay)


        except TypeError as syntax_err:
            print "Error Powering On"
            raise Exception(syntax_err) ##Re-raise to calling class.
        #except Exception as e:
        #    print "An error occurred powering on the node %s:" % self.hostname
        #   print e


    def powerOff(self):
        try:
            self.getInstance()
            stoppedInstances = self.conn.terminate_instances(self.instanceId)
            if not stoppedInstances:
                raise Exception("Unable to stop instance %s - Manual Intervention is Required" % self.instanceId)
            else:
                print "Stopped instance %s (%s)" % (self.hostname, self.instanceId)
        except Exception as err:
            print err

    def powerCycle(self):
        pass    #reserved for future implementation

    def getInstance(self):
        '''Returns EC2 instance ID of the current instance based on self.hostname'''
        if not self.ipAddr:
            raise Exception("Current IP address of hostname %s has not been resolved." % self.hostname)
        else:   #we have an IP address, so obtain the instance ID
            address_objects = self.conn.get_all_addresses()
            for address_obj in address_objects:
                if address_obj.public_ip == self.ipAddr:
                    self.instanceId = address_obj.instance_id
            if not self.instanceId:
                raise Exception("Error obtaining instance IP - there may be no cloud instance for hostname %s" % self.hostname)


#Un-comment for unit testing
#'''
#ED = Ec2Driver("../../../hpc-scaler.cfg", "cloudnode1")

#ED.connect()
#ED.getRunningInstances()
#ED.printDetails()
#ED.getKeypairs()
#ED.powerOff()
#ED.getRunningInstances()
#ED.printDetails()
#'''
