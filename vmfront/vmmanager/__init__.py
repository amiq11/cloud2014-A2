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

def create_virConnect():
    con = None
    try: 
        con = libvirt.open('qemu+tls://g4hv.exp.ci.i.u-tokyo.ac.jp/system')
    except:
        con = libvirt.open('qemu:///system')

    return con
