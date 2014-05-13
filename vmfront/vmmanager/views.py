from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from xml.dom.minidom import parseString
import libvirt
# Create your views here.

def index(request):
    con = libvirt.open('qemu:///system')
    vmdoms = []
    for id in con.listDomainsID():
        dom = con.lookupByID(id)
        vmdoms.append(dom)
    return render_to_response('vmmanager/index.html',
                              {'vmdoms': vmdoms},
                              context_instance=RequestContext(request))

def status(request, vmname):
    con = libvirt.open('qemu:///system')
    dom = con.lookupByName(vmname)
    parsed = parseString(dom.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE))

    #if request.method == 'POST':
    if request.POST["shutdown"] == "true":
        dom.destroy()
        return HttpResponseRedirect("http://127.0.0.1:8000/vmmanager/")
     
    else:
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
