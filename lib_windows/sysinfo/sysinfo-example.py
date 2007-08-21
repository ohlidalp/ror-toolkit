#!/usr/bin/python

#Sample python-sysinfo usage

import sysinfo
import logging

format = "%(asctime)s %(levelname)s %(message)s"
sysinfo_log = logging.getLogger("sysinfo")
sysinfo_log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(format)
ch.setFormatter(formatter)
sysinfo_log.addHandler(ch)


net = sysinfo.network()
interf = net.interface('eth0')
last_user = net.last_user

hw =  sysinfo.hardware()

smb = sysinfo.services.smb()

pkgs = sysinfo.software.packages()

env = sysinfo.misc.env()

print hw.motherboard.product
print hw.motherboard.vendor
print hw.cpu.product
print hw.cpu.vendor
print hw.cpu.frequency
print hw.video_board.memory
print hw.memory.size
print hw.video_board.product
print hw.sound_board.product
print hw.keyboard.model
print hw.bios.vendor
print hw.bios.version
print hw.dvd_reader.product
print hw.modem.vendor
print hw.modem.product
print hw.mouse.product
print hw.mouse.vendor
print hw.ethernet_board.vendor
print hw.ethernet_board.product
 

print net.hostname
print net.default_gateway
print net.dnsresolvers
print net.dnsdomain


print interf.dhcp_server
print interf.mac_address
print interf.ip_network
print interf.ip_addresses[0]

print smb.smb_shares
print smb.wins_servers
print smb.workgroup
