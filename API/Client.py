'''
Created on 6 Jul 2013

@author: ronan

Client class for a simple generic JSON-based API model. Class should be extended
in order to be made useful, as it does not do anything with the json data it collects
'''

try:
    import requests     #python-requests is a wrapper for RESTful API ops - see dependencies.txt
except ImportError:
    print "Dependency python-requests not found"

#import json         #json package from Python Standard Library to utilise json notation for data interchange

class APIClient:

    def __init__(self, URL, username, password, request, timeout):
        #Initialise the client with basic data about the request we
        #are making. If this parent class is used directly, the makeRequest
        #method is called on initialisation so these values cannot be overwritten.
        #To overwrite class variables, extend the class and call makeRequest
        #directly (or override it).
        self.url = URL              #URL of the resource to contact
        self.username = username    #If authentication is required
        self.password = password    # - obtain username and password
        self.request = request      # Request object in parameters format
        self.timeout = timeout      ##

        ##Once the client is initialised, make the request (catch exceptions)
        try:
            self.makeRequest()
        except Exception as e:
            print "The following exception occurred: " , e

    def makeRequest(self):
        r = requests.get(self.url, params=self.request, timeout=self.timeout)
        self.status_code = r.status_code
        if r.status_code != requests.codes.ok:
            raise Exception("An error occurred making the request: ".r.status_code)
        #If our status is ok, obtain the results of the query. These results will be
        #handled by modules which extend this class.
        else:
            self.results = r.json()    ##default results are in JSON format
            self.results_raw = r.raw ##Also provide for raw data format results

#Uncomment for unit testing
#Client = APIClient('https://github.com/timeline.json', None, None, None, 1)
Client = APIClient('http://localhost:8080/ctrl/meth/stuff', None, None, None, 1)
print Client.status_code
print Client.results



