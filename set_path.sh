#!/bin/bash

CWD=`pwd`

export PYTHONPATH=$CWD:$CWD/ClusterInterface:$CWD/ClusterInterface/Drivers:$CWD/ClusterInterface/Drivers/Torque:$CWD/NodeController:$CWD/NodeController/Drivers:$CWD/NodeController/Drivers/Ec2:$CWD/NodeController/Drivers/Ipmi
