import libvirt

def listAllVMUUIDs(uri):
  hv = libvirt.open(uri)
  if hv is None:
    return False
  vms_uuid = []
  ## Obtain running virtual machines
  running_vms = hv.listDomainsID()
  for vmid in running_vms:
    uuid = hv.lookupByID(vmid).UUID()
    vms_uuid.append(uuid)
  ## Obtain defined but not running virtual machines
  defined_vms = hv.listDefinedDomains()
  for vmname in defined_vms:
    uuid = hv.lookupByName(vmname).UUID()
    vms_uuid.append(uuid)
  return vms_uuid

if __name__ == "__main__":
  ## List all virtual machines' UUID defined at the hypervisor of the specified URI
  print( listAllVMUUIDs("qemu:///system") )

