'''
Created on 3 Aug 2013

@author: ronan
'''
from bottle import route, run, template

@route('/hello/<name>')
def banana(name='World'):
    return template('<b>Hello {{name}}</b>!', name=name)

run(host='localhost', port=8080)