'''
TorqueDriver module for the ClusterInterface component. Enables the ClusterInterface to interact with
the Torque Resource Manager. Should be compliant with other PBS-based Resource Managers such as PBSPro, OpenPBS, etc.
This version of the driver uses pre-compiled binaries and modules from the pbs_python library.

Created on 13 June 2013

@author: ronan
'''


try:
    from pbs_python.fourthreefive import pbs, PBSQuery, PBSAdvancedParser
    from ClusterInterface.ClusterDriver import ClusterDriver
    import sys
except (NameError, ImportError) as e:
    print "Component(s) not found or not readable at default location:"
    print e



class TorqueDriver(ClusterDriver):
    '''
    This driver for the Torque Resource Manager is designed to function as part of the
    ClusterInterface.
    '''


    def __init__(self):
        '''
        Constructor
        '''

    #Return the FQDN of the job submission host
    def getServerName(self):
        pbs_server = pbs.pbs_default()
        if pbs_server:
            self.serverName = pbs_server
            print "about to return name %s" % self.serverName
            super(TorqueDriver, self).getServerName()
        else:
            errno, text = pbs.error()
            print errno, text

    def dumpDetails(self):
        pbs_server = pbs.pbs_default()
        if not pbs_server:
            print "No default pbs server"
            sys.exit(1)

        con = pbs.pbs_connect(pbs_server)
        nodes = pbs.pbs_statnode(con, "", "NULL", "NULL")

        for node in nodes:
            print node.name
            for attrib in node.attribs:
                print '\t', attrib.name, '=', attrib.value




print "Creating new Torque Driver"
TD = TorqueDriver()
print "Created!"
sn = TD.getServerName()
print "Server name is %s" % sn
TD.dumpDetails()
