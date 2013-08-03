'''
Listener class is a thread which listens for incoming
API requests and forks a Client Handler thread for each
connection. It shouldn't need to be extended.

@author: ronan
'''

from bottle import route, run


@route('/<controller>/<method>/<data>')
def InvokeAction(controller,method,data):
    print "Controller is", controller
    print "Method is ", method
    print "Data is ", data

run(host='localhost', port=8080, server='paste') #eventlet is an asyncrhonous framework with WSGI support.
