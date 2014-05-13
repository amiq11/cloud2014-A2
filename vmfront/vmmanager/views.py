from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.dom.minidom import parseString
from django.core.context_processors import csrf
from django import forms

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
    return render_to_response('vmmanager/status.html',
                              {
                                  'dom': dom,
                                  'info': dom.info,
                                  'graphics_port': parsed.getElementsByTagName('graphics')[0].getAttribute('port')
                              })

class VMForm(forms.Form):
        name = forms.CharField()
        memory = forms.ChoiceField(choices=[(256, "256"), (512, "512"), (1024, "1024")])
        vcpu = forms.ChoiceField(choices=[(1, "1"), (2, "2"), (3, "3")])
        disk = forms.ChoiceField(choices=[(2, "2"), (5, "5"), (10, "10"), (20, "20")])
        os = forms.ChoiceField(choices=[("", "")])

def create(request):
        if request.method == "POST":
                form = VMForm(request.POST)
                if form.is_valid():
                        # code of creating vm
                        # and redirecting to vnc
                        con = libvirt.open('qemu:///system')
			print("aaaaa")
                        domain = con.defineXML(D_XML % form.cleaned_data)
                        status = domain.create()
                        if status != -1:
                                # TODO
                                # return redirect to vnc
                                pass
        else:
                form = VMForm()
        c = {"form": form}
        return render_to_response('vmmanager/create.html', c,
                                                          context_instance=RequestContext(request))



D_XML = """\
<domain type="kvm"> <!-- Domain Type -->
        <name>(%name)s</name> <!-- name for vm -->
        <uuid></uuid> <!-- global identifier for virtual machines. if define/create a new machine, a random UUID is generated-->

        <os> <!-- Bootloader -->
                <type>hvm</type>  <!-- Full Virtualization -->
                <boot dev='cdrom'/> <!-- Boot Device -->
                <boot dev='hd' />
        </os>

        <vcpu>(%vcpu)d</vcpu> <!-- CPU allocation -->
        <memory unit='MiB'>(%memory)d</memory> <!-- Maximum Memory Allocation Size -->
        <currentMemory unit='MiB'>(%memory)d</currentMemory> <!-- Current Memory Allocation -->

        <devices> <!-- devices provided to the guest domain -->
                <emulator>/usr/bin/kvm</emulator> <!--  -->
                <disk type='file' device='disk'> <!-- type:underlying source for the disk, device:how the disk is exposed to the guest OS -->
                        <source file='/var/lib/libvirt/images/sparse.img' />
                        <target dev='hda' />
                </disk>
                <disk type='file' device='cdrom'>
                        <source file='/var/local/kvm/installer/debian-7.5.0-amd64-netinst.iso' />
                        <target dev='hda' />
                        <readonly/>
                        <address type='drive' controller='0' bus='1' target='0' unit='0'/>
                </disk>
                <interface type='network'>
                        <source network='default' />
                        <mac address='24:42:53:21:52:45' />
                </interface>
                <graphics type='vnc' port='-1' keymap='ja' />
        </devices>

</domain>
"""\
