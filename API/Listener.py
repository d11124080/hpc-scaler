'''
Listener class is a thread which listens for incoming
API requests and forks a Client Handler thread for each
connection. It shouldn't need to be extended.

@author: ronan
'''

class Listener(object):
    

    def __init__(self):
        '''
        Constructor
        '''
        