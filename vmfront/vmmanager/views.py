from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from xml.dom.minidom import parseString
import libvirt
# Create your views here.

def index(request):
    #con = libvirt.open('qemu+tls://g4hv.exp.ci.i.u-tokyo.ac.jp/system')
    con = libvirt.open('qemu:///system')
    vmdoms = []
    for name in con.listDefinedDomains():
        dom = con.lookupByName(name)
        vmdoms.append(dom)

    for id in con.listDomainsID():
        dom = con.lookupByID(id)
        vmdoms.append(dom)
        
    return render_to_response('vmmanager/index.html',
                              {'vmdoms': vmdoms},
                              context_instance=RequestContext(request))

def status(request, vmname):
    #con = libvirt.open('qemu+tls://g4hv.exp.ci.i.u-tokyo.ac.jp/system')
    con = libvirt.open('qemu:///system')
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

    try:
        if request.POST["shutdown"] == "true":
            dom.destroy()
            return HttpResponseRedirect(reverse('vmmanager.views.index'))

#    except request.POST["PowerON"] == "true":
#        dom.start()
#        return HttpResponseRedirect(reverse('vmmanager.views.index'))
        
    except KeyError:
        
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
    
    else:
        if request.POST["PowerON"] == "true":
            dom.create()
            return HttpResponseRedirect(reverse('vmmanager.views.index'))
        

def create(request):
    return render_to_response('vmmanager/create.html')
