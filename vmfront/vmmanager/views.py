from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from xml.dom.minidom import parseString
import libvirt
# Create your views here.


def index(request):
    return render_to_response('vmmanager/index.html')

def status(request, vmname):
    #con = libvirt.open('qemu+tls://g4hv.exp.ci.i.u-tokyo.ac.jp/system')
    con = libvirt.open('qemu:///system')
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



def index_menu(request):
    #con = libvirt.open('qemu+tls://g4hv.exp.ci.i.u-tokyo.ac.jp/system')
    con = libvirt.open('qemu:///system')
    vmdoms = []
    for id in con.listDomainsID():
        dom = con.lookupByID(id)
        vmdoms.append(dom)
    return render_to_response('vmmanager/index_menu.html',
                              {'vmdoms': vmdoms},
                              context_instance=RequestContext(request))

def index_top(request):
    return render_to_response('vmmanager/index_top.html')


