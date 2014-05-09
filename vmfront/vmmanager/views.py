from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from xml.dom.minidom import parseString
from vmmanager import create_virConnect
import libvirt
from vmmanager.vnc import display

# Create your views here.


def index(request):
    return render_to_response('vmmanager/index.html')
def index_menu(request):
    con = create_virConnect()
    vmdoms = []
    for id in con.listDomainsID():
        dom = con.lookupByID(id)
        vmdoms.append(dom)
    return render_to_response('vmmanager/index_menu.html',
                              {'vmdoms': vmdoms},
                              context_instance=RequestContext(request))
def index_top(request):
    return render_to_response('vmmanager/index_top.html')

def status(request, vmname):
    con = create_virConnect()
    dom = con.lookupByName(vmname)
    parsed = parseString(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))

    try:
        if request.POST["shutdown"] == "true":
            dom.destroy()
            return HttpResponseRedirect(reverse('vmmanager.views.index_top'))
        
    except KeyError:
        
        return render_to_response('vmmanager/status.html',
                                  context_instance=RequestContext(request, {
                                  'dom': dom,
                                  'info': dom.info,
                                  'mem': dom.memoryStats,
                                  'max_mem': dom.maxMemory,
				  'max_cpu': dom.maxVcpus,
                                  'getinfo': con.getInfo,
                                  'graphics_port': parsed.getElementsByTagName('graphics')[0].getAttribute('port')
                              }))

def create(request):
    return render_to_response('vmmanager/create.html')

def vnc(request, vmname):
    return display(request, vmname)
