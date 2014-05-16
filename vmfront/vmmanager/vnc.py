from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.dom.minidom import parseString
import libvirt
import threading
import time
import subprocess
import os
import socket
from novnc.websockify import WebSocketProxy
from vmmanager import get_virt_hostname, create_virConnect
from urlparse import urlparse

# Create your views here.
_wsproxy = None

def display(request, vmname):
    global _wsproxy
    con = create_virConnect()
    dom = con.lookupByName(vmname)
    parsed = parseString(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))
    # localhost:8000 -> localhost
    hostname = request.get_host()
    if hostname.count(':') > 0:
        hostname = hostname.rsplit(':', 1)[0]
        hostname = hostname.strip('[]')
    vncport = int(parsed.getElementsByTagName('graphics')[0].getAttribute('port'))
    wsport = vncport - 5900 + 26100
    myipaddr = socket.gethostbyname(socket.gethostname())
    virthost = urlparse(get_virt_hostname()).netloc
    if virthost == '':
        virthost = myipaddr
    #### Start a Proxy Server using subprocess
    if _wsproxy != None:
        _wsproxy.terminate()
        time.sleep(1)
    path = os.path.join(os.path.dirname(__file__), 'novnc/websockify.py')
    command = '%s %s:%s %s:%s' % ( path,
                                   myipaddr,
                                   wsport,
                                   virthost,
                                   vncport)
    print(command)
    _wsproxy = subprocess.Popen(command, shell=True)
    # time.sleep(3)

    #### Start a Proxy Server using threading
    # if _wsproxy != None:
    #     _wsproxy.stop()
    # _wsproxy = VNCWSProxy(listen_host = 'localhost',
    #                       listen_port = wsport,
    #                       target_host = hostname,
    #                       target_port = vncport)
    # _wsproxy.start()
    
    #time.sleep(10)
    print('wsport: %d, hostname: %s'%(wsport, hostname))
    return render_to_response('vmmanager/vnc.html',
                              {
                                  'dom': dom,
                                  'port': wsport,
                                  'hostname': hostname,
                                  'password': 'asdfghjkl'
                              })

class VNCWSProxy(object):
    class WSProxyThread(threading.Thread):
        def __init__(self, *args, **kwargs):
            print(kwargs)
            if 'target_host' not in kwargs:
                raise KeyError('target_host is missing')
            if 'target_port' not in kwargs:
                raise KeyError('target_port is missing')
            if 'listen_host' not in kwargs:
                raise KeyError('listen_host is missing')
            if 'listen_port' not in kwargs:
                raise KeyError('listen_port is missing')
            self.wsproxy = WebSocketProxy(*args, **kwargs)
            threading.Thread.__init__(self)
        def run(self):
            self.wsproxy.start_server()
        def join(self, timeout=None):
            #self._stopevent.set()
            threading.Thread.join(self, timeout)
    '''
    You need to set "target_host", "target_port", "listen_host" and "listen_port"
    '''
    def __init__(self, *args, **kwargs):
        self.th = self.WSProxyThread(*args, **kwargs)
    def start(self):
        self.th.start()
    def stop(self):
        self.th.join()
