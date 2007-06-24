#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright (C) 2006 José de Paula Eufrásio Junior (jose.junior@gmail.com) AND
#                      Yves Junqueira (yves.junqueira@gmail.com)
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA



"""Provides specific services information
"""

import logging
import win32net
import win32com.client

class smb:
    """Provides information from the SMB service using information from the smb.conf file.
    That may not be an exact science, but it's the best method available.
    """
   
    def __init__(self):
        self.wins_servers = []
        self._set_wins_info()
        (self.workgroup, self.domain ) = self._get_workgroup_domain()
        self.smb_shares = self._get_shares()
        
    def _get_shares(self):
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_Share")
        
        shares = []
        for objItem in colItems:
            share = { }
            share['name'] = objItem.Name
            share['type'] = objItem.Type
            share['comment'] = objItem.Caption
            shares.append(share)

        return shares

    def _get_workgroup_domain(self):
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_ComputerSystem")
        workgroup = ''
        domain  = ''
        for item in colItems:
            if item.Workgroup:
                workgroup = item.Workgroup
                
            if item.Domain:
                domain = item.Domain
                
        return [workgroup,domain]                
        
    def _set_wins_info(self):
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_NetworkAdapterConfiguration")
        for objItem in colItems:
##            print "Arp Always Source Route: ", objItem.ArpAlwaysSourceRoute
##            print "Arp Use EtherSNAP: ", objItem.ArpUseEtherSNAP
##            print "Caption: ", objItem.Caption
##            print "Database Path: ", objItem.DatabasePath
##            print "Dead GW Detect Enabled: ", objItem.DeadGWDetectEnabled
##            z = objItem.DefaultIPGateway
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "Default IP Gateway: ", x
##            print "Default TOS: ", objItem.DefaultTOS
##            print "Default TTL: ", objItem.DefaultTTL
##            print "Description: ", objItem.Description
##            print "DHCP Enabled: ", objItem.DHCPEnabled
##            print "DHCP Lease Expires: ", objItem.DHCPLeaseExpires
##            print "DHCP Lease Obtained: ", objItem.DHCPLeaseObtained
##            print "DHCP Server: ", objItem.DHCPServer
##            print "DNS Domain: ", objItem.DNSDomain
##            z = objItem.DNSDomainSuffixSearchOrder
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "DNS Domain Suffix Search Order: ", x
##            print "DNS Enabled For WINS Resolution: ", objItem.DNSEnabledForWINSResolution
##            print "DNS Host Name: ", objItem.DNSHostName
##            z = objItem.DNSServerSearchOrder
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "DNS Server Search Order: ", x
##            print "Domain DNS Registration Enabled: ", objItem.DomainDNSRegistrationEnabled
##            print "Forward Buffer Memory: ", objItem.ForwardBufferMemory
##            print "Full DNS Registration Enabled: ", objItem.FullDNSRegistrationEnabled
##            z = objItem.GatewayCostMetric
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "Gateway Cost Metric: ", x
##            print "IGMP Level: ", objItem.IGMPLevel
##            print "Index: ", objItem.Index
##            z = objItem.IPAddress
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IP Address: ", x
##            print "IP Connection Metric: ", objItem.IPConnectionMetric
##            print "IP Enabled: ", objItem.IPEnabled
##            print "IP Filter Security Enabled: ", objItem.IPFilterSecurityEnabled
##            print "IP Port Security Enabled: ", objItem.IPPortSecurityEnabled
##            z = objItem.IPSecPermitIPProtocols
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IP Sec Permit IP Protocols: ", x
##            z = objItem.IPSecPermitTCPPorts
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IP Sec Permit TCP Ports: ", x
##            z = objItem.IPSecPermitUDPPorts
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IPSec Permit UDP Ports: ", x
##            z = objItem.IPSubnet
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IP Subnet: ", x
##            print "IP Use Zero Broadcast: ", objItem.IPUseZeroBroadcast
##            print "IPX Address: ", objItem.IPXAddress
##            print "IPX Enabled: ", objItem.IPXEnabled
##            z = objItem.IPXFrameType
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IPX Frame Type: ", x
##            print "IPX Media Type: ", objItem.IPXMediaType
##            z = objItem.IPXNetworkNumber
##            if z is None:
##                a = 1
##            else:
##                for x in z:
##                    print "IPX Network Number: ", x
##            print "IPX Virtual Net Number: ", objItem.IPXVirtualNetNumber
##            print "Keep Alive Interval: ", objItem.KeepAliveInterval
##            print "Keep Alive Time: ", objItem.KeepAliveTime
##            print "MAC Address: ", objItem.MACAddress
##            print "MTU: ", objItem.MTU
##            print "Num Forward Packets: ", objItem.NumForwardPackets
##            print "PMTUBH Detect Enabled: ", objItem.PMTUBHDetectEnabled
##            print "PMTU Discovery Enabled: ", objItem.PMTUDiscoveryEnabled
##            print "Service Name: ", objItem.ServiceName
##            print "Setting ID: ", objItem.SettingID
##            print "Tcpip Netbios Options: ", objItem.TcpipNetbiosOptions
##            print "Tcp Max Connect Retransmissions: ", objItem.TcpMaxConnectRetransmissions
##            print "Tcp Max Data Retransmissions: ", objItem.TcpMaxDataRetransmissions
##            print "Tcp Num Connections: ", objItem.TcpNumConnections
##            print "Tcp Use RFC1122 Urgent Pointer: ", objItem.TcpUseRFC1122UrgentPointer
##            print "Tcp Window Size: ", objItem.TcpWindowSize
##            print "WINS Enable LMHosts Lookup: ", objItem.WINSEnableLMHostsLookup
##            print "WINS Host Lookup File: ", objItem.WINSHostLookupFile
##            print "WINS Primary Server: ", objItem.WINSPrimaryServer
            self.wins_servers.append(objItem.WINSPrimaryServer)
            self.wins_servers.append(objItem.WINSSecondaryServer)
            break # consider only the first network adapter

if __name__ == '__main__':

    s = smb()

    #print i.interf_dict
    #print d.dnsdomain, d.dnsresolvers
    print "teste", s.workgroup,s.wins_servers
    print repr(s.smb_shares)

