#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
#
# Author:   Makoto Shimazu <makoto.shimaz@gmail.com>
# URL:      https://amiq11.tumblr.com
# License:  MIT License
# Created:  2014-05-16
#
import libvirt

_hostname = None

def get_virt_hostname():
    return _hostname

def create_virConnect():
    global _hostname
    con = None
    try: 
        path = 'qemu+tls://g4hv.exp.ci.i.u-tokyo.ac.jp/system'
        con = libvirt.open(path)
        _hostname = path
	print("Release VM")
    except:
        path = 'qemu:///system'
        con = libvirt.open(path)
        _hostname = path
	print("Local VM")

    return con
