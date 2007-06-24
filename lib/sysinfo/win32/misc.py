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
partitions for win32systems
"""

import logging
import os
import win32com.client

logger = logging.getLogger("sysinfo.win32.misc")

class env:
    variables = {}
    
    def __init__(self):
        for k in os.environ.keys():
            self.variables[k] = os.environ[k]
        

class disks:
    partitions = {}

    def __init__(self):

        self.partitions = self._get_partitions() 

    def _get_partitions(self, show_remote=0,show_dummy=0):
        """Get mounted partitions
        Get mounted partitions. Currently ignoring show_remote and show_dummy
        """
        
        parts = []
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_LogicalDisk \
            WHERE DriveType = 3")
        for objItem in colItems:
            part_dict = {
                'fsname' : objItem.DeviceID,
                'mountpoint' : objItem.Name,
                'fstype' : objItem.FileSystem,
                'fssize' : int(objItem.Size),
                'fsfree' : int(objItem.FreeSpace),
                'fsserial' : objItem.VolumeSerialNumber 
                }
           
            parts.append(part_dict)

        return parts

if __name__ == '__main__':
    e = env()
    #print repr(e.variables)
    d = disks()
    print repr(d.partitions)
   
