#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright (C) 2006 José de Paula Eufrásio Junior (jose.junior@gmail.com)
#   AND#                      Yves Junqueira (yves.junqueira@gmail.com)
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

"""Provides miscelaneous information like enviroment variables and local
partitions.
"""

import os
import logging


logger = logging.getLogger("sysinfo.linux.misc")

class env:
    variables = {}
    
    def __init__(self):

        self.variables = os.environ

class disks:
    partitions = {}

    def __init__(self):

        self.partitions = self._get_partitions() 

    def _get_partitions(self, show_remote=0,show_dummy=0):
        """Get mounted partitions
        Get mounted partitions. If show_remote=0, show only local partitions.
        """
        
        #
        #From coreutils mountlist.c:
        #
        #    /* A file system is `remote' if its Fs_name contains a `:'
        #    or if (it is of type smbfs and its Fs_name starts with `//').  */
        #
        # 
        parts = []
        mtab = open('/etc/mtab', 'r')
        for part in mtab.readlines():
            [fsname, mountp, fstype, options, dump, ppass ] = part.split()
            # mtab brings octal escaped special strings
            mountp = mountp.decode('string_escape') 
            if show_remote == 0:
                if fsname.find(':') >= 0  : continue
                if fstype == 'smbfs' and \
                    fsname.startswith('//'): continue

            if show_dummy == 0:
                # another possibility is to check /proc/filesystems and exclude any
                # that has 'nodev'
                if fstype == 'tmpfs' or fstype == 'proc' \
                    or fstype == 'sysfs' or fstype == 'devpts' \
                    or fstype == 'none' \
                    or not fsname.startswith('/'): continue
       
            partstat = os.statvfs(mountp)
            part_dict = { 
                'fsname' : fsname,
                'mountpoint' : mountp,
                'fstype' : fstype,
                'fssize' : partstat[1] * partstat[2],
                # bytes available for non-root
                'fsfree' : partstat[1] * partstat[4], 
                }
           
            parts.append(part_dict)

        mtab.close()
        return parts

if __name__ == '__main__':
    e = env()
#    print e.variables
    d = disks()
    print d.partitions[0]['fssize'] /(1024 * 1024)
    print d.partitions[0]['fsfree'] / (1024 * 1024)
