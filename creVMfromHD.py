#!/usr/bin/env python
from __future__ import print_function
import sys
import libvirt
from xml.etree import ElementTree

xmlconfig='''
<domain type='kvm'>
<name>demo</name>
<uuid>c7a5fdbd-cdaf-9455-926a-d65c16db1809</uuid>
<memory unit='KiB'>4194304</memory>
<vcpu>1</vcpu>
<os>
    <type arch='x86_64' machine='rhel6.6.0'>hvm</type>
    <boot dev='hd'/>
</os>
<clock offset='utc'/>
<on_poweroff>destroy</on_poweroff>
<on_reboot>restart</on_reboot>
<on_crash>destroy</on_crash>
<devices>
<emulator>/usr/libexec/qemu-kvm</emulator>
<disk type='file' device='disk'>
<source file='/opt/vm-images/sz6vm4.img'/>
<driver name='qemu' type='raw'/>
<target dev='hda'/>
</disk>
<interface type='bridge'>
<mac address='52:54:00:d8:65:c9'/>
<source bridge='br1'/>
</interface>
<input type='mouse' bus='ps2'/>
<graphics type='vnc' port='-1' listen='127.0.0.1'/>
</devices>
</domain>
'''


domName = 'sz6vm4'
conn = libvirt.open('qemu:///system')
if conn == None:
	print('Failed to open connection to qemu:///system', file=sys.stderr)
	exit(1)
dom = conn.defineXML(xmlconfig)
if dom == None:
	print('Failed to define a domain from an XML definition.', file=sys.stderr)
	exit(1)
if dom.create() < 0:
	print('Can not boot guest domain.', file=sys.stderr)
	exit(1)
print('Guest '+dom.name()+' has booted', file=sys.stderr)
conn.close()
exit(0)
