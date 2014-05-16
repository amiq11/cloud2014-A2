from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from xml.dom.minidom import parseString
from django.core.context_processors import csrf
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
        maxVcpus = "(N/A)"
    else:
        vm_state = dom.info()[0]
        maxVcpus = "(N/A)"

    graphics_port = parsed.getElementsByTagName('graphics')[0].getAttribute('port')
    if graphics_port == "-1":
        graphics_port = "(N/A)"

    if request.method == "POST":

        if 'PowerON' in request.POST:
            if vm_state == "shut off":
                dom.create()
            return HttpResponseRedirect(reverse('vmmanager.views.status', args=(vmname,)))
        elif 'shutdown' in request.POST:
            if vm_state == "running":
                dom.destroy()
            return HttpResponseRedirect(reverse('vmmanager.views.status', args=(vmname,)))
        
    
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
                                  'graphics_port': graphics_port,
                                  'OSType': dom.OSType(),
                              }))
    

class VMForm(forms.Form):
        name = forms.CharField()
        memory = forms.ChoiceField(choices=[(256 * 1024, "256"), (512 * 1024, "512"), (1024 * 1024, "1024")])
        vcpu = forms.ChoiceField(choices=[(1, "1"), (2, "2"), (3, "3")])
        disk = forms.ChoiceField(choices=[(2, "2"), (5, "5"), (10, "10"), (20, "20")])
        os = forms.ChoiceField(choices=[("freebsd", "FreeBSD"), ("ubuntu", "Ubuntu"), ("centos", "CentOS"), ("debian", "Debian")])
		
	def clean_name(self):
		# Custom validation
		# Check overlapping of domain name
		con = create_virConnect()
		#con = libvirt.open('qemu:///system')
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
                        con = create_virConnect()
			
               	        # con = libvirt.open('qemu:///system')
			# Create Volume
			for name in  con.listStoragePools() :
					pool = con.storagePoolLookupByName(name)

			pool.createXML(V_XML % form.cleaned_data, 0)

			# Create Domain
                        domain = con.defineXML(D_XML % form.cleaned_data)
                        status = domain.create()
                        if status != -1:
                                # TODO
                                # return redirect to vnc
                                return HttpResponseRedirect(reverse('vmmanager.views.status', args=(form.cleaned_data["name"],)))
			   
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
                        <source file='/var/shared/%(os)s.iso' />
                        <target dev='hda' />
                        <readonly/>
                        <address type='drive' controller='0' bus='1' target='0' unit='0'/>
                </disk>
                <interface type='network'>
                        <source network='default' />
                        <mac address='24:42:53:21:52:45' />
                </interface>
                <graphics type='vnc' port='-1' keymap='ja' passwd="asdfghjkl">
			<listen type='address' address='157.82.3.140'/>
		</graphics>
        </devices>

</domain>
"""\

def vnc(request, vmname):
    return display(request, vmname)
