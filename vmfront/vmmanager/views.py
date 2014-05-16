from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.dom.minidom import parseString
from django.core.context_processors import csrf
from django import forms
from django.http import HttpResponse

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
        memory = forms.ChoiceField(choices=[(256 * 1024, "256"), (512 * 1024, "512"), (1024 * 1024, "1024")])
        vcpu = forms.ChoiceField(choices=[(1, "1"), (2, "2"), (3, "3")])
        disk = forms.ChoiceField(choices=[(2, "2"), (5, "5"), (10, "10"), (20, "20")])
        os = forms.ChoiceField(choices=[("freebsd", "FreeBSD"), ("ubuntu", "Ubuntu"), ("centos", "CentOS"), ("debian", "Debian")])
		
	def clean_name(self):
		# Custom validation
		# Check overlapping of domain name
		con = libvirt.open('qemu:///system')
		vm_names = []
		for id in con.listDomainsID():
			dom = con.lookupByID(id)
			vm_names.append(dom.name())
		vm_names.append(con.listDefinedDomains())
		if self.cleaned_data['name'] in vm_names:
				raise forms.ValidationError(u'Overlapping domain name')
		else:
				return self.cleaned_data['name']

def create(request):
        if request.method == "POST":
                form = VMForm(request.POST)
                if form.is_valid():
                        con = libvirt.open('qemu:///system')

			# Create Volume
			for name in  con.listStoragePools() :
					pool = con.storagePoolLookupByName(name)

			pool.createXML(V_XML % form.cleaned_data, 0)

			# Create Domain
			with open('/home/guest/hoge/hoge.xml', 'w') as fw:
			    fw.write(D_XML % form.cleaned_data)

                        domain = con.defineXML(D_XML % form.cleaned_data)
                        status = domain.create()
                        if status != -1:
                                # TODO
                                # return redirect to vnc
                                pass
        else:
                form = VMForm()
	c = {}
        return render_to_response('vmmanager/create.html', c,
                                                          context_instance=RequestContext(request))

V_XML = """\
    <volume>
        <name>%(name)s.img</name>
        <allocation>0</allocation>
        <capacity unit="G">%(disk)s</capacity>
      <!--  <target>
          <path>/var/lib/virt/images/%(name)s.img</path>
          <permissions>
            <owner>107</owner>
            <group>107</group>
            <mode>0744</mode>
            <label>virt_image_t</label>
          </permissions>
        </target> -->
      </volume>
"""\

D_XML = """\
<domain type="kvm"> <!-- Domain Type -->
        <name>%(name)s</name> <!-- name for vm -->
        <uuid></uuid> <!-- global identifier for virtual machines. if define/create a new machine, a random UUID is generated-->

        <os> <!-- Bootloader -->
                <type>hvm</type>  <!-- Full Virtualization -->
                <boot dev='cdrom'/> <!-- Boot Device -->
                <boot dev='hd' />
        </os>

        <vcpu>%(vcpu)s</vcpu> <!-- CPU allocation -->
        <memory unit='KiB'>%(memory)s</memory> <!-- Maximum Memory Allocation Size -->
        <currentMemory unit='KiB'>%(memory)s</currentMemory> <!-- Current Memory Allocation -->
        <devices> <!-- devices provided to the guest domain -->
                <emulator>/usr/bin/kvm</emulator> <!--  -->
                <disk type='file' device='disk'> <!-- type:underlying source for the disk, device:how the disk is exposed to the guest OS -->
                        <source file='/var/lib/libvirt/images/%(name)s.img' />
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
                <graphics type='vnc' port='-1' keymap='ja' passwd="asdfghjkl">
		  <!-- <listen type='address' address='157.82.3.140'/> -->
		</graphics>
        </devices>

</domain>
"""\

