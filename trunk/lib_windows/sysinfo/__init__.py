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

"""Provides methods for collecting system information in
a portable way, for both Linux and Windows.
"""

# The current structure will be replaced by the following:
# 
# sysinfo.network().dnsdomains = list
# sysinfo.network().default_gateway = str
# sysinfo.network().interfaces = list
# sysinfo.network().interface() = method
# sysinfo.network().interface('eth0').ip_addresses = list
# sysinfo.network().interface('eth0').mac_address = str
# sysinfo.network().interface('eth0').product = str
# sysinfo.network().interface('eth0').vendor = str
# sysinfo.services.smb.workgroup = str
# sysinfo.services.smb.winsservers = list
# sysinfo.hardware.motherboard.product
# sysinfo.hardware.motherboard.vendor
# sysinfo.hardware.videoboard.product
# sysinfo.hardware.videoboard.vendor
# sysinfo.software.installed = list
#
# All data must be populated, even with empty values.
#
# Planned modules strucuture:
#
# sysinfo/
#           __init__.py
#           linux/
#                   __init__.py
#                   network.py      network class
#                   services.py     services class
#                   hardware.py     provides hardware class
#
#

import sys
import logging
import os

logger = logging.getLogger("sysinfo")

if sys.platform == 'linux2':
    logger.info("Loading sysinfo for Linux")
    from linux.network import network
    from linux.hardware import hardware
    from linux import services
    from linux import misc
    if os.path.isfile('/etc/debian_version'):
        from linux import apt as software
    elif os.path.isfile('/etc/redhat-release'):
        from linux import my_rpm as software

elif sys.platform == 'win32':
    logger.info("Loading sysinfo for win32")
    #from win32.network import network
    from win32.hardware import hardware
    from win32 import services
    from win32 import software
    from win32 import misc
