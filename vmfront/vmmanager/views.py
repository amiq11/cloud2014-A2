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
    for name in con.listDefinedDomains():
        dom = con.lookupByName(name)
        vmdoms.append(dom)

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

    if dom.info()[0] == 1:
        vm_state = "running"
        maxVcpus = dom.maxVcpus()
    elif dom.info()[0] == 5:
        vm_state = "shut off"
        maxVcpus = None
    else:
        vm_state = dom.info()[0]
        maxVcpus = None


    if request.method == "POST":

        if 'PowerON' in request.POST:
            if vm_state == "shut off":
                dom.create()
            return HttpResponseRedirect(reverse('vmmanager.views.index_top'))
        elif 'shutdown' in request.POST:
            if vm_state == "running":
                dom.destroy()
            return HttpResponseRedirect(reverse('vmmanager.views.index_top'))
        
    
    #try:
    #    value = request.POST["PowerON"]

    #except KeyError:
        
    else:
        return render_to_response('vmmanager/status.html',
                                  context_instance=RequestContext(request, {
                                  'dom': dom,
                                  'info': dom.info(),
                                  'vm_state': vm_state,
                                  'state': dom.state(0),
                                  'memoryStats': dom.memoryStats(),
                                  'maxMemory': dom.maxMemory(),
				  'maxVcpus': maxVcpus,
                                  'vcpus': dom.vcpus(),
                                  'conGetMemoryStats': con.getMemoryStats(0,0),
                                  'conGetCPUStats': con.getCPUStats(0,0),
                                  'graphics_port': parsed.getElementsByTagName('graphics')[0].getAttribute('port')
                              }))
    

def create(request):
    return render_to_response('vmmanager/create.html')

def vnc(request, vmname):
    return display(request, vmname)
