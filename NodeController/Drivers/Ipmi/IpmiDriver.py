'''
Created on 29 Aug 2013

@author: ronan
'''
try:
    from HardwareNode import HardwareNode
    import ConfigParser
    import sys
    import subprocess
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


    def __init__(self,cfgFile,address):
        '''
        Constructor just obtains the configuration
        '''
        self.iface = None       #The interface to use for IPMI connections, from the config file (lan/lanplus probably)
        self.username = None    #IMPI username, from the config file
        self.password = None    #IPMI password, from the config file
        self.exe = None         #Full path to the ipmitool binary, from the config file
        self.cfgFile = cfgFile  #Relative path to the configuration file
        self.host = address     #IP address of the host we are trying to control

        ##Now fetch the configuration
        self.getConfig()

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
        except Exception as configError:
            print "Error(s) occurred when parsing the Ipmi section of the config file:"
            print configError

    def printConfig(self):
        print "Interface: %s" % self.iface
        print "Username: %s" % self.username
        print "Password: %s" % self.password
        print "Ipmitool: %s" % self.exe
        print "Host: %s" % self.host
    
    #ipmitool -I lanplus -U <username> -P <password> -H <ipaddress> chassis power <command>
    def powerOn(self):
        onCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.host,"chassis","power","on"]
        try:
            power_on = subprocess.Popen(onCmd)
            power_on.wait()
            if power_on.returncode:    ##Non-zero return code implies an error with our power on command
                raise Exception("An error occurred powering on "+self.host)
        except Exception as err:
            print err

    def powerOff(self):
        offCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.host,"chassis","power","off"]
        try:
            power_off = subprocess.Popen(offCmd)
            power_off.wait()
            if power_off.returncode:    ##Non-zero return code implies an error with our power on command
                raise Exception("An error occurred powering off "+self.host)
        except Exception as err:
            print err

    def powerCycle(self):
        cycleCmd = [self.exe,"-U",self.username,"-P",self.password,"-H",self.host,"chassis","power","on"]
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
        except Exception as err:
            print err

#Un-comment for Unit Testing
'''
IN = IpmiDriver("../../../hpc-scaler.cfg", "127.0.0.1")
IN.getConfig()
IN.printConfig()
IN.getStatus()
'''
