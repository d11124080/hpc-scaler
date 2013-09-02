'''
Created on 29 Aug 2013

@author: ronan
'''
try:
    from HardwareNode import HardwareNode
    import ConfigParser
    import sys
    import subprocess
    import socket
except (NameError, ImportError) as e:
    print "Component(s) not found or not readable at default location:"
    print e
    sys.exit(0)


class IpmiDriver(HardwareNode):
    '''
    Ipmi Driver for the hpc-scaler NodeController. Extends the HardwareNode class to
    provide support for the management of Ipmi interfaces using the ipmitool application,
    which is required to be installed.
    '''


    def __init__(self,cfgFile,hostname):
        '''
        Constructor just obtains the configuration
        '''
        self.iface = None       #The interface to use for IPMI connections, from the config file (lan/lanplus probably)
        self.username = None    #IMPI username, from the config file
        self.password = None    #IPMI password, from the config file
        self.exe = None         #Full path to the ipmitool binary, from the config file
        self.cfgFile = cfgFile  #Full path to the configuration file
        self.host = hostname     #Hostname of the host we are trying to control

        ##Now fetch the configuration
        self.getConfig()
        ##Ipmi interfaces usually have different IP addresses to their
        #communications IP. Try to resolve this hostname with a .ipmi
        #suffix.
        #print "DEBUG:looking up address for %s" % self.host
        try:
            self.ipmiAddr = socket.gethostbyname(self.host+"."+self.suffix)
        except socket.error as error:
            #re-raise our exception to the calling class
            raise Exception("Error resolving %s.%s - %s" % (self.host,self.suffix,error))
        if not self.ipmiAddr:       # Should be caught by socket.error, but in case another error occurred
            raise Exception("Unexpected error in IPMI driver when assigning address.")

    def getConfig(self):
        try:
            config = ConfigParser.RawConfigParser()
            config.read(self.cfgFile)
            config_section = "Ipmi"
            # Obtain configuration data for the cluster we will connect to.
            self.iface = config.get(config_section, "ipmitool_iface")
            self.exe = config.get(config_section, "ipmitool_binary")
            self.username = config.get(config_section, "ipmi_username")
            self.password = config.get(config_section, "ipmi_password")
            self.suffix = config.get(config_section, "ipmi_dns_suffix")

        except Exception as configError:
            print "Error(s) occurred when parsing the Ipmi section of the config file:"
            print configError

    def printDetails(self):
        print "Interface: %s" % self.iface
        print "Username: %s" % self.username
        print "Password: %s" % self.password
        print "Ipmitool: %s" % self.exe
        print "Host: %s" % self.host
        print "IPMI address %s" % self.ipmiAddr

    #ipmitool -I lanplus -U <username> -P <password> -H <ipaddress> chassis power <command>
    def powerOn(self):
        #First check the status - if the node is already booting, leave it be!
        self.getStatus()
        if self.status == "on":
            print "Machine %s is already powered on" % self.host
        else:   #machine is off or indeterminate
            onCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.ipmiAddr,"chassis","power","on"]
            #try:
            power_on = subprocess.Popen(onCmd)
            power_on.wait()
            if power_on.returncode:    ##Non-zero return code implies an error with our power on command
                raise Exception("An error occurred powering on "+self.ipmiAddr)
            #except Exception as err:    ##Dont catch generic exceptions at the driver level.
            #print err

    def powerOff(self):
        offCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.ipmiAddr,"chassis","power","off"]
        try:
            power_off = subprocess.Popen(offCmd)
            power_off.wait()
            if power_off.returncode:    ##Non-zero return code implies an error with our power on command
                raise Exception("An error occurred powering off "+self.host)
        except Exception as err:
            raise Exception(err)

    def powerCycle(self):
        cycleCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.host,"chassis","power","reset"]
        try:
            power_cycle = subprocess.Popen(cycleCmd)
            power_cycle.wait()
            if power_cycle.returncode:    ##Non-zero return code implies an error with our power on command
                raise Exception("An error occurred powering cycling "+self.host)
        except Exception as err:
            print err

    def getStatus(self):
        statusCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.host,"chassis","power","status"]
        try:
            power_status = subprocess.Popen(statusCmd)
            power_status.wait()
            if power_status.returncode:    ##Non-zero return code implies an error with our power on command
                raise Exception("An error occurred checking power on "+self.host)
            #Read our status
            if "is on" in power_status.stdout:
                self.status = 'on'
            elif "is off" in power_status.stdout:
                self.status = 'off'
            else:
                self.status = 'unknown'

        except Exception as err:
            raise Exception(err)

#Un-comment for Unit Testing
#'''
#IN = IpmiDriver("../../../hpc-scaler.cfg", "alienware")
#IN.getConfig()
#IN.printDetails()
#IN.getStatus()
#'''
