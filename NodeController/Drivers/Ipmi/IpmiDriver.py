'''
Created on 29 Aug 2013

@author: ronan
'''
try:
    from HardwareNode import HardwareNode
    import ConfigParser
    import sys
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
        Constructor
        '''
        self.iface = None       #
        self.username = None    #
        self.password = None    #
        self.exe = None         #
        self.cfgFile = cfgFile  #
        self.host = address     #

    def getConfig(self):
        config = ConfigParser.RawConfigParser()
        config.read(self.cfgFile)
        config_section = "Ipmi"
        # Obtain configuration data for the cluster we will connect to.
        self.iface = config.get(config_section, "ipmitool_interface")
        self.exe = config.get(config_section, "ipmitool_binary")
        self.username = config.get(config_section, "ipmi_username")
        self.password = config.get(config_section, "ipmi_password")




    def getStatus(self):
        pass


IN = IpmiDriver("../../hpc-scaler.cfg", "127.0.0.1")
IN.getConfig()
