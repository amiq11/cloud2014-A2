from django.shortcuts import render_to_response
from django.template import RequestContext
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
    return render_to_response('vmmanager/status.html',
                              {'dom': dom, 'info': dom.info()})

def create(request):
    return render_to_response('vmmanager/create.html')
