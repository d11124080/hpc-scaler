'''
Build object for pbs_python package source used as part of the TorqueDriver.
The pbs_python library needs to be compiled against the running version of Torque, so
binary distribution could not be used. Object should be used where an ImportError exception
is thrown by the ClusterInterface when trying to import from the pbs wrapper library.
Created on 26 Aug 2013

@author: ronan
'''

import ConfigParser
import os
import subprocess

class Build(object):
    '''
    The Build class is used to build the pbs_python wrapper from source
    '''


    def __init__(self,cfgFile):
        '''
        Constructor
        '''

        self.pbs_python_ver = '4.3.5'
        self.verstring = "fourthreefive"
        self.getConfig(cfgFile)
        try:
            self.buildBinary()
        except Exception as e:
            print "There were errors building the binary"
            deps_file = open("../../dependencies.txt", "r")
            deps_text = deps_file.read()
            print "**********************************************"
            print deps_text
            print "**********************************************"
            print "Error Message: ",e

    def getConfig(self, cfgFile):
        #Decipher build path from the ClusterInterface config
        config = ConfigParser.RawConfigParser()
        config.read(cfgFile)
        config_section = "General"      #FIXME: This is too static
        basedir = config.get(config_section, "basedir")
        config_section = "ClusterInterface"
        driverdir = config.get(config_section, "driver_path")
        drivername = config.get(config_section, "cluster_driver")

    def buildBinary(self):
        '''
        Calls the configure and make scripts provided by the pbs_python maintainers.
        (sources are included with this distribution, see licensing info provided.)
        '''

        ##Begin by determining the location of the pbs_python package we are compiling.
        cwd = os.getcwd()
        #print "current dir is ",cwd
        self.builddir = "pbs_python/"+self.verstring+'/'
        self.libdir = self.builddir
        #print "Using path %s" % self.builddir
        os.chdir(self.builddir)
        cwd = os.getcwd()
        print "current dir is ",cwd

        #Wrap our os commands in lists for passing to subprocess.Popen()
        make_clean = ["make", "clean"]
        configure = ["./configure", "--prefix="+cwd]
        make = ["make"]
        make_install = ["make", "install"]

        #Begin by cleaning up any potential failed builds
        print "Cleaning our build environment..."
        mc_cmd = subprocess.Popen(make_clean)
        mc_cmd.wait()
        #No need to check a return code here

        #Now run our configure command.
        print "Configuring pbs_python version"+self.pbs_python_ver
        cfg_cmd = subprocess.Popen(configure)
        cfg_cmd.wait()
        if cfg_cmd.returncode:    ##Non-zero return code implies an error with our configure
            raise Exception("An error occurred configuring pbs_python - check dependencies")

        #If configure has succesfully completed, we can try to compile
        make_cmd = subprocess.Popen(make)
        make_cmd.wait()
        if make_cmd.returncode:     ##Again, non-zero implies our make has gone wrong
            raise Exception("An error occurred building the pbs_python library - is gcc installed?")

        #All being well so far, we can try a make install at this point
        mi_cmd = subprocess.Popen(make_install)
        mi_cmd.wait()
        if mi_cmd.returncode:   ##non-zero is still an error!
            raise Exception("An error occurred installing the pbs_python binary - check permissions?")




#Uncomment for unit testing
bld = Build("../../../hpc-scaler.cfg")