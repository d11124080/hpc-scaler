'''
Created on 6 Jul 2013

@author: ronan
'''

import requests     #python-requests is a wrapper for RESTful API ops - see dependencies.txt
import json         #json package from Python Standard Library to utilise json notation for data interchange

class Client:
    
    def __init__(self, URL, username, password, request):
        #do nothing
        self.URL = URL
        self.username = username
        self.password = password
        self.request = request
        

