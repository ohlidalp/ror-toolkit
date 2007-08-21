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

"""Provides network information for linux systems
"""

import commands
import logging
import re
import socket
import struct
import sys

logger = logging.getLogger("sysinfo.linux.network")

# auxiliary functions
def hex2dec(s):
    """Returns the integer value of a hexadecimal string s
    """
    return int(s, 16)
# Functions based on:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66517
# which is licensed under the BSD license.

def dottedQuadToNum(ip):
    """convert decimal dotted quad string to long integer"""
    return struct.unpack('L',socket.inet_aton(ip))[0]

def numToDottedQuad(n):
    """Convert long int to dotted quad string
    """
    return socket.inet_ntoa(struct.pack('L',n))

def convert_ip_to_net_and_host(ip, maskstring):
    """Returns tuple (network, host) dotted-quad addresses given IP and mask"""
    # (by Greg Jorgensen)

    n = dottedQuadToNum(ip)
    m = dottedQuadToNum(maskstring)

    host = n & m
    net = n - host

    return numToDottedQuad(net), numToDottedQuad(host)


class ifconfig:
    """Gets information from /sbin/ifconfig
    and populates interf_dict
    """

    interf_dict = {}

    def __init__(self):
        logger.info("Reading ifconfig data")
        # Sets 'ifconfig' 
        ifconfig = commands.getstatusoutput("export LANGUAGE=C; ifconfig")
        if ifconfig[0] != 0:
            # This would kill this module instance.
            logger.error("Could not run ifconfig")
            raise IfconfigError, "could not run ifconfig"
        else:
            i = ifconfig[1]
            sp = re.compile('([ae]th[\d]+|lo) ')
            interf_list = sp.split(i)
            interf_list.pop(0)
            i = 1
            # Assemble a dict using 1 as key, 2 as value; 3 as key, 4 as value...
            for x in interf_list:
                if i % 2 == 0: # Even
                    self.interf_dict[ interf_list[i - 2] ] = x
                i += 1



class resolv:
    """Gets resolver information from /etc/resolv.conf
    and populates resolvconf, dns_domain and dns_resolvers
    """

    resolvconf = ''
    dns_domain = ''
    dns_resolvers = ''

    def __init__(self):
        # Return empty resolvconf. Do not raise error.

        self.resolvconf = self._get_resolvconf()
        self.dns_domain = self._get_dns_domain()
        self.dns_resolvers = self._get_dnsresolvers()

    def _get_resolvconf(self):
        logger.debug("Getting DNS resolvers data")
        try:
            r = open('/etc/resolv.conf','r')
        except:
            logger.error("Error while reading /etc/resolv.conf")
            return ''
        else:
            return r.read()
            r.close()

    def _get_dns_domain(self):

        h = re.compile( r'(domain|search)\s+(?P<domain>.*)\s*',
                        re.I)
        w = h.search(self.resolvconf)
        if w:
            domain = w.group('domain')
            if domain:
                return domain

        return ''

    def _get_dnsresolvers(self):

        r = re.compile( r'([\W]nameserver)\s+(?P<resolver>\S+)\s*'
                        r'((nameserver)\s+(?P<resolver2>\S+)\s*)?',
                        re.I)

        x = r.search(self.resolvconf)
        #Resolvers must return at least two empty values
        resolvers = ['','']
        if x:
            resolver = x.group('resolver')
            if resolver:
                resolvers[0]= resolver

            resolver2 = x.group('resolver2')

            if resolver2:
                resolvers[1] = resolver2

        if resolvers is not None:
            return resolvers
        else:
            return []

class misc:
    """Gets miscelaneous information from the system.
    """

    hostname = ''
    default_gateway = ''
    interfaces = []
   
    def __init__(self, ifc):
        self.hostname = socket.gethostname()
        self.default_gateway = self._get_default_gateway()
        self.interfaces = ifc.interf_dict.keys()

    def _get_default_gateway(self):
        t1 = self._get_default_gateway_from_proc()
        if not t1:
            t1 = self._get_default_gateway_from_bin_route()
            if not t1:
               return None
        return t1

    def _get_default_gateway_from_proc(self):
        """"Returns the current default gateway, reading that from /proc'
        """
        logger.debug("Reading default gateway information from /proc")
        try:
            f = open('/proc/net/route','r')
            route = f.read()
        except:
            logger.error("Failed to read def gateway from /proc")
            return None
        else:
            h = re.compile('\n(?P<interface>\w+)\s+00000000\s+(?P<def_gateway>[\w]+)\s+')
            w = h.search(route)
            if w:
                if w.group('def_gateway'):
                    return numToDottedQuad(hex2dec(w.group('def_gateway')))
                else:
                    logger.error("Could not find def gateway info in /proc") 
                    return None
            else:
                logger.error("Could not find def gateway info in /proc") 
                return None


    def _get_default_gateway_from_bin_route(self):
        """Get Default Gateway from '/sbin/route -n
        Called by get_default_gateway and is only used if could not get that from /proc
        """
        logger.debug("Reading default gateway information from route binary")
        routebin = commands.getstatusoutput("export LANGUAGE=C; /usr/bin/env route -n")

        if routebin[0] != 0:
            logger.error("Error while trying to run route")
            return false
        h = re.compile('\n0.0.0.0\s+(?P<def_gateway>[\w.]+)\s+')
        w = h.search(routebin[1])
        if w:
            def_gateway = w.group('def_gateway')

        if def_gateway:
            return def_gateway
        
        logger.error("Could not find default gateway by running route")
        return ''

class interface:
    """Retrieves interface specific information
    """

    ip_addresses = []
    mac_address = ''
    netmask = ''
    ip_network = ''

    def __init__(self, ifc, interf=None):
        self.interf_dict = ifc.interf_dict

        if interf:
            self.ip_addresses = self._get_ip_addresses(interf)
            self.mac_address = self._get_mac_address(interf)
            self.netmask = self._get_netmask(interf)
            self.ip_network = self._get_network(self.ip_addresses[0],
                self.netmask)
            self.status = self._get_status(interf)
            self.dhcp_server = self._get_dhcp_server(interf)

    def _get_ip_addresses(self, interf=None):
        """Shows the interface's respective IP addresses
        """
        # FIXME: get_address currently returns a singleton list.

        h = re.compile(r'inet add?r:(?P<ip_addr>[\w.]+)', re.I)
        try:
            w = h.search(self.interf_dict[interf])
        except KeyError:
            logger.error("Could not find " + str(interf) + " in the list of \
active network interfaces. Please review your configuration.")
            sys.exit(1)

        ip_addrs = []
        if w:
            ip_addrs.append(w.group('ip_addr'))
        return ip_addrs

    
    def _get_mac_address(self,interf=None):
        """Gives network interfaces hardware address
        """
        mac = ''
        if interf:
            h = re.compile(r'HW(addr)? (?P<mac>[\w:]+) ', re.I)
            w = h.search(self.interf_dict[interf])
            if w:
                mac = w.group('mac')
        return mac

    def _get_network(self,ip=None,netmask=None):

        network = ''

        if ip and netmask:
            (host, network) = convert_ip_to_net_and_host(ip, netmask)
        return network

    def _get_netmask(self,interf=None):
        """Shows the interface's respective IP netmask
        """
        netmask = '' 
 
        if interf:
            h = re.compile(r'Mask:(?P<netmask>[\w.]+)', re.I)
            w = h.search(self.interf_dict[interf])
            if w:
                netmask = w.group('netmask')
        return netmask

    def _get_status(self,interf=None):
        """Shows interface status
        """
        
        if interf:
            h = re.compile('UP',re.I)
            w = h.search(self.interf_dict[interf])
            if w:
                 return 'UP'
            else:
                 return 'DOWN'
        else:
            return ''

    def _get_dhcp_server(self,interf=None):
        """Return the current DHCP Server for the 'interf' interface, by parsing the dhclient.leases file.
        It will try to define if the IP was indeed setup using DHCP by trying to find dhclient in the
        current running process list.
        In case there are many leases stored, it should consider the last one for the given interface.
        """
 
        if interf == None:
            return ''

        # FIXME if there is a better way to define if a machine is using DHCP
        # besides checking dhclient?

        dh = commands.getstatusoutput('ps aux|grep dhclient')

        if dh[0] != 0:
            logger.error("Error finding a running dhclient")
            return ''
        else:
            i = dh[1]
            sp = re.compile('-lf\s+(?P<leases_file>\S+)\s+.*(?P<interface>[ae]th[\d]+|lo)')
            m = sp.search(dh[1])
            if m:
                leases_file = m.group('leases_file')
            else:
                #FIXME: this should work for other distros and dhclient versions
                leases_file = '/var/lib/dhcp3/dhclient.leases'
            try:
                f = open(leases_file)
            except:
                logger.error("Could not open leases_file (tried from " + \
                            leases_file + " )")
                return ''
        dhcp = f.read()
        f.close()

        sp = re.compile('(lease)\s*{')
        leases_list = sp.split(dhcp)

        test_int = re.compile('interface\s*"'+ interf)

        # Removing leases unrelated to 'interf'
        for x in leases_list:
            m = test_int.search(x)
            if not m:
               leases_list.remove(x)
        if len(leases_list) == 0:
            return ''
        lease = leases_list.pop()

        o = re.compile('option\s+dhcp-server-identifier\s+(?P<dhcp_server>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*;')
        k = o.search(lease)

        if k: 
            server = k.group('dhcp_server')
        else:
            server = ''

        # Shows the last lease
        return server

class last_logon:

    last_user = ''

    def __init__(self):
        self.last_user = self._get_last_user()

    def _get_last_user(self):
        logger.debug("Getting last logon")
        l = commands.getstatusoutput('export LANGUAGE=C; last')
        if l[0] != 0:
            logger.error("Error while running 'last'")
            return ''
        else:
            last_f = l[1].split()[0]
            return last_f
                                        
class network(resolv, ifconfig, misc, last_logon):
    """This is the stuff users will access. It inherits data from other 'os' 
    classes so users can access information like network.dns_domain.
    """

    def __init__(self):
        self._ifc = ifconfig()
        resolv.__init__(self)
        misc.__init__(self, self._ifc)
        last_logon.__init__(self)
        self.interface = self.interface_wrapper

    def interface_wrapper(self, interf):
        i = interface(self._ifc, interf)
        return i

if __name__ == '__main__':
# Log para stdout
    format = "%(asctime)s %(levelname)s %(message)s"
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(format)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    g = network()

    #print i.interf_dict
    #print d.dns_domain, d.dns_resolvers
    b = g.interface(g.interfaces[1])
    print "teste", g.interfaces, b.ip_addresses, g.last_user, b.dhcp_server
