#!/usr/bin/env python
#
# Author: Bas van der Vlies <basv@sara.nl>
# Date  : 17 Aug 2001 
# Desc. : Simple pbsnodes -a
#
# SVN info:
#   $Id: node_event_parse.py 287 2012-12-20 11:03:07Z bas $
#   $URL: https://oss.trac.surfsara.nl/pbs_python/svn/tags/4.3.5/examples/node_event_parse.py $ 
#
#
#


import pbs
import sys
from PBSQuery import PBSQuery

p = PBSQuery()
node = p.getnode('gb-r7n3')
print node['event']
