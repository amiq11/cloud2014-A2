#!/usr/bin/env python
import libvirt

con = libvirt.open('qemu:///system')

for id in con.listDomainsID():
  dom = con.lookupByID(id)
  info = dom.info()
  print( "=========================================================" )
  print( "DOM[%3d] Name:   %8s      |  State:   %8s" % ( id, dom.name(), info[0] ) )
  print( "         MaxMem: %8d [MB] |  Mem:     %8d [MB]" % (info[1]/1E3, info[2]/1E3) )
  print( "         CPUs:   %8d      |  CPUTime: %8.2f [s]" % (info[3], info[4]/1.0E9) )
  print( "         OSType: %8s " % dom.OSType() )
#  print( "         Memory Params: %s" % dom.memoryParameters(0) )

print( "=========================================================" )
print( "Host Stats" )

hostMemStats = con.getMemoryStats(0,0)
print( "Memory: %d MB Free: %d MB" % (hostMemStats['total']/1E3, hostMemStats['free']/1E3) )
print( "Memory Free: %d MB" % (con.getFreeMemory()/1E6) )
print( con.listStoragePools() )
#sysInfo = con.getSysinfo(0)
#print( "SysInfo: %s" % sysInfo )
#print( con.getCPUStats(0,0) )


