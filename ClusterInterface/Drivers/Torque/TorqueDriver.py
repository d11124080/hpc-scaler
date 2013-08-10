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

    def connect(self):
        try:
            pbs_server = pbs.pbs_default()
            self.con = pbs.pbs_connect(pbs_server)
            if self.con:
                self.connectionStatus = 'Connected'
        except Exception, e:
            print e

    def disconnect(self):
        #pbs_disconnect returns non-zero value if an error occurs
        retval = pbs.pbs_disconnect(self.con)
        if (retval is 0):
            self.connectionStatus = 'Not Connected'
            self.con = 0
        else:
            print pbs.pbs_statserver(self.con)

    def getConStatus(self):
        '''
        Determines whether an active connection with the Resource Manager exists -
        Can be handled by parent class, so just call the equivilent function in the parent.
        '''
        super(TorqueDriver, self).getConStatus()


    #Return the FQDN of the job submission host
    def getServerName(self):
        pbs_server = pbs.pbs_default()
        if pbs_server:
            self.serverName = pbs_server
            #print "DEBUG: about to return name %s" % self.serverName
            #Call our parent function's equivilent function
            super(TorqueDriver, self).getServerName()
        else:
            errno, text = pbs.error()
            print errno, text


    def dumpDetails(self):
        pbs_server = pbs.pbs_default()
        if not pbs_server:
            print "No default pbs server"
            sys.exit(1)

        #con = pbs.pbs_connect(pbs_server)
        nodes = pbs.pbs_statnode(self.con, "", "NULL", "NULL")

        for node in nodes:
            print node.name
            for attrib in node.attribs:
                print '\t', attrib.name, '=', attrib.value

    def getNodes(self):
        '''

        '''



##Un-comment for unit testing.
print "Creating new Torque Driver"
TD = TorqueDriver()
print "Created!"
TD.getServerName()
print "Server name is %s" % TD.serverName
print "Trying to connect..."
TD.connect()
print "Trying to disconnect..."
TD.disconnect()

TD.dumpDetails()
print TD.connectionStatus
