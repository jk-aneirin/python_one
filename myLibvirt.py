#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: mylibvirt.py
from __future__ import print_function
import sys
import libvirt
from xml.etree import ElementTree
from xml.dom import minidom

class Opevm():
	conn=None
	def __init__(self,ct=0,remote_ip=None):
		if ct==0:
			self.connect_local()
		else:
			if remote_ip==None:
				print("Input remote host's IP you want to connect")
			else:
				self.connect_remote(remote_ip)
	def connect_local(self):
		self.conn=libvirt.open("qemu:///system")
		if self.conn==None:
			print("Failed to open local connection",file=sys.stderr)
			exit(1)
	def connect_remote(self,ip):
		uri='qemu+ssh://root@'+ip+'/system'
		self.conn=libvirt.open(uri)
		if self.conn==None:
			print("Failed to open remote connection",file=sys.stderr)
                        exit(1)
	def nodeCapabilities(self):
		print("Capabilites:\n"+self.conn.getCapabilities())
	def getNodeName(self):
		print("Node's name is:"+self.conn.getHostname())
	def getMaxVcpusperGuest(self):
		print('Maximum support virtual CPUS:'+str(self.conn.getMaxVcpus(None)))
	def getINFO(self):
		print('Model:'+str(self.conn.getInfo()[0]))
		print('Memory size:'+str(self.conn.getInfo()[1])+'MB')
		print('Number of CPUs:'+str(self.conn.getInfo()[2]))
		print('MHz of CPUs:'+str(self.conn.getInfo()[3]))
		print('Number of NUMA nodes:'+str(self.conn.getInfo()[4]))
		print('Number of CPU sockets:'+str(self.conn.getInfo()[5]))
		print('Number of CPU cores per socket:'+str(self.conn.getInfo()[6]))
		print('Number of CPU threads per core:'+str(self.conn.getInfo()[7]))
	def disAllDomNames(self):
		'''function listAllDomains() is ok too'''
		domainNames = self.conn.listDefinedDomains()
		if domainNames == None:
			print('Failed to get a list of domain names', file=sys.stderr)
		domainIDs = self.conn.listDomainsID()
		if domainIDs == None:
			print('Failed to get a list of domain IDs', file=sys.stderr)
		if len(domainIDs) != 0:
			for domainID in domainIDs:
				domain = self.conn.lookupByID(domainID)
				domainNames.append(domain.name())
		print("All (active and inactive domain names):")
		for domainName in domainNames:
			print(' '+domainName)
	def disAcDomNameIds(self):
        	domName=[]
        	domId=[]
        	domIDs=self.conn.listDomainsID()
        	if domIDs==None:
                	print('Failed to get a list of domain IDs', file=sys.stderr)
        	if len(domIDs)==0:
                	print('None')
        	else:
                	for domid in domIDs:
                        	domName.append(domid)
		                domId.append(self.conn.lookupByID(domid).name())

        	print(dict(zip(domName,domId)))
	def provisionGuest(self,flag):
		pass
	def setvCPUs(self,name,num):
		dom=self.conn.lookupByName(name)
		dom.setVcpus(num)
	def setMemory(self,name,size):
		dom=self.conn.lookupByName(name)
		dom.setMemory(size)
	def setAutoStart(self,name):
		dom=self.conn.lookupByName(name)
		if dom==None:
			print("Failed to find the domain:"+name,file=sys.stderr)
			exit(1)
		dom.setAutostart(1)		
	def getCpuStats(self,name):
		dom=self.conn.lookupByName(name)
		if dom==None:
			print('Failed to find domain'+name,file=sys.stderr)
			exit(1)

	#	cpu_stats=dom.getCPUStats(False,0)//API BUG
	#	for (i,cpu) in enumerate(cpu_stats):
	#		print('CPU '+str(i)+' Time: '+str(cpu['cpu_time'] / 1000000000.))
	#---------------------------------------------------------------------------------
	#	stats = dom.getCPUStats(True,0)
	#	print('cpu_time: '+str(stats[0]['cpu_time']))
	#	print('system_time: '+str(stats[0]['system_time']))
	#	print('user_time: '+str(stats[0]['user_time']))
	def getMemStats(self,name):
		dom=self.conn.lookupByName(name)
		stats=dom.memoryStats()
		print("memory used:")
		for name in stats:
			print(' '+str(stats[name])+' ('+name+')')
	def getIfStats(self,name):
		dom=self.conn.lookupByName(name)
		tree = ElementTree.fromstring(dom.XMLDesc(0))
		iface = tree.find('devices/interface/target').get('dev')
		stats = dom.interfaceStats(iface)
		print('read bytes: '+str(stats[0]))
		print('read packets: '+str(stats[1]))
		print('read errors: '+str(stats[2]))
		print('read drops: '+str(stats[3]))
		print('write bytes: '+str(stats[4]))
		print('write packets: '+str(stats[5]))
		print('write errors: '+str(stats[6]))
		print('write drops: '+str(stats[7]))
	def disDisks(self,name):
		dom=self.conn.lookupByName(name)
		raw_xml = dom.XMLDesc(0)
		xml = minidom.parseString(raw_xml)
		diskTypes = xml.getElementsByTagName('disk')
		for diskType in diskTypes:
			print('disk: type='+diskType.getAttribute('type')+' '+'device='+diskType.getAttribute('device'))
			diskNodes = diskType.childNodes
			for diskNode in diskNodes:
				if diskNode.nodeName[0:1] != '#':
					print(' '+diskNode.nodeName)
					for attr in diskNode.attributes.keys():
						print(' '+diskNode.attributes[attr].name+' = '+diskNode.attributes[attr].value)
	def disDomainIf(self,name):
		dom = self.conn.lookupByName(name)

		raw_xml = dom.XMLDesc(0)
		xml = minidom.parseString(raw_xml)
		interfaceTypes = xml.getElementsByTagName('interface')
		for interfaceType in interfaceTypes:
			print('interface: type='+interfaceType.getAttribute('type'))
			interfaceNodes = interfaceType.childNodes
			for interfaceNode in interfaceNodes:
				if interfaceNode.nodeName[0:1] != '#':
					print(' '+interfaceNode.nodeName)
					for attr in interfaceNode.attributes.keys():
						print(' '+interfaceNode.attributes[attr].name+' = '+interfaceNode.attributes[attr].value)
	def disNodeUpIf(self):
		ifaces=self.conn.listInterfaces()
		print("Active host interfaces:")
		for iface in ifaces:
			print('  '+iface)
	def disNodeDownIf(self):
		ifaces=self.conn.listDefinedInterfaces()
		print("Inactive host interfaces:")
		for iface in ifaces:
			print(' '+iface)		
        '''backup guest memory status to id.img'''
	def saveVM(self,name):
		filename='/var/lib/libvirt/save/'+name+'.img'
		dom=self.conn.lookupByName(name)
		if dom==None:
			print("Cannot find guest to be saved.",file=sys.stderr)
			exit(1)
		info=dom.info()
		if info==None:
			print('Cannot check guest state',file=sys.stderr)
			exit(1)
		#if dom.state==VIR_DOMAIN_SHUTOFF:
		#	print('Not saving guest that is not running',file=sys.stderr)
		#	exit(1)
		if dom.save(filename)<0:
			print('Unable to save guest to'+filename,file=sys.stderr)
		print('Guest state saved to'+filename,file=sys.stderr)	
	def restoreVM(self,name):
		filename='/var/lib/libvirt/save/'+name+'.img'
		if self.conn.restore(filename)<0:
			print('Unable to restore guest from'+filename,file=sys.stderr)			
			exit(1)
	def conn_close(self):
		self.conn.close()
if __name__=="__main__":
	vm=Opevm(1,'192.168.0.42')
	vm.disAcDomNameIds()
	vm.conn_close()
	
