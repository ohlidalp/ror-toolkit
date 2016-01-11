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

import win32com.client
import logging

class get_hardware:
    """Uses win32com to get hardware information. Script sampled from Microsoft.
    """
    
    data = {}

    def __init__(self):
        target_list = [
                       'Win32_ComputerSystem', 
                       'Win32_BIOS', 
                       #'Win32_NetworkAdapter', 
                       #'Win32_NetworkAdapterConfiguration',
                       'Win32_OperatingSystem',
                       'Win32_CDROMDrive'
                       ]

        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

        for target in target_list:
            #print "verificando " + target
            self.data['CD reader'] = []
            colItems = objSWbemServices.ExecQuery("Select * from %s" % target)
            
            for item in colItems:
             
                if target == 'Win32_NetworkAdapter':

                    mac_address = str(item.MACAddress).replace(':','-')
                    self.data['mac_address'] = mac_address

                if target == 'Win32_NetworkAdapterConfiguration':
                               
                    pass

                    #self.data['ip_network'] = item.IPAddress

                if target == 'Win32_OperatingSystem':
                    logging.debug("Memory: " + item.TotalVisibleMemorySize)
                    self.data['System Memory'] = []
                    self.data['System Memory'].append({})
                    self.data['System Memory'][0]['size'] = item.TotalVisibleMemorySize

                if target == 'Win32_CDROMDrive':
                    self.data['CD reader'].append({})
                    self.data['CD reader'][-1]['product'] = item.Name
                        
class motherboard:
    product = ''
    vendor = ''

    def __init__(self, hw, index=0):
        if hw.data.has_key('Motherboard'):
            self.product = hw.data['Motherboard'][index].get('product', '')
            self.vendor = hw.data['Motherboard'][index].get('vendor', '')


class memory:
    size = ''

    def __init__(self, hw):
        if hw.data.has_key('System Memory'):
            self.size = hw.data['System Memory'][0].get('size', '')
        
class mouse:
    product = ''
    vendor = ''

    def __init__(self, hw, index=0):
        if hw.data.has_key('Mouse'):
            self.product = hw.data['Mouse'][index].get('product', '')
            self.vendor = hw.data['Mouse'][index].get('vendor', '')


class modem:
    product = ''
    vendor = ''

    def __init__(self, hw, index=0):
        if hw.data.has_key('Modem'):
            self.product = hw.data['Modem'][index].get('product', '')
            self.vendor = hw.data['Modem'][index].get('vendor', '')

class cd_reader:
    product = ''
    
    def __init__(self, hw, index=0):
        if hw.data.has_key('DVD reader'):
            self.product = hw.data['DVD reader'][index].get('product', '')
            
class dvd_reader:
    product = ''
    
    def __init__(self, hw, index=0):
        if hw.data.has_key('CD reader'):
            self.product = hw.data['CD reader'][index].get('product', '')

class bios:
    product = ''
    vendor = ''
    version = ''
    
    def __init__(self, hw):
        if hw.data.has_key('BIOS'):
            self.product = hw.data['BIOS'][0].get('product', '')
            self.vendor = hw.data['BIOS'][0].get('vendor', '')
            self.version = hw.data['BIOS'][0].get('version', '')

class video_board:
    product = ''
    vendor = ''
    memory = ''
    resolution = ''
    width = ''
    
    def __init__(self, hw, index=0):
        self._set_video_info()
        
    def _set_video_info(self):
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_VideoController")
        for objItem in colItems:
            self.memory = objItem.AdapterRAM
            self.product = objItem.Description
            self.resolution = str(objItem.CurrentHorizontalResolution) + \
                'x' + str(objItem.CurrentVerticalResolution)
            self.width = objItem.CurrentBitsPerPixel
            break
        
class sound_board:
    product = ''
    
    def __init__(self, hw, index=0):
        if hw.data.has_key('Multimedia audio controller'):
            self.product = hw.data['Multimedia audio controller'][index].get('product')

class ethernet_board:
    product = ''
    width = ''
    version = ''
    vendor = ''
    serial = ''

    def __init__(self, hw, index=0):
        if hw.data.has_key('Ethernet interface'):
            self.product = hw.data['Ethernet interface'][index].get('product', '')
            self.width = hw.data['Ethernet interface'][index].get('width', '')
            self.vendor = hw.data['Ethernet interface'][index].get('vendor', '')
            self.version = hw.data['Ethernet interface'][index].get('version', '')
            self.serial = hw.data['Ethernet interface'][index].get('serial', '')
       
class cpu:
    product = ''
    vendor = ''
    frequency = ''
    serial = ''
    
    def __init__(self, hw, index=0):
        self._set_cpu_info()
        
    def _set_cpu_info(self):
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_Processor")
        for objItem in colItems:
            self.vendor = objItem.Manufacturer
            self.frequency = objItem.MaxClockSpeed
            self.product = objItem.Name
            break
        
class hardware:
    """This is the interfaced accessed by the user. It provides
    hardware data collected through get_hardware.
    """
    # FIXME: motherboard, cpu, etc need support to multiple values. Currently
    # uses index=0

    # Tá certo iniciar o objeto assim, com string em branco? Ele nao vai ser string
    hw = ''
    motherboard = ''
    cpu = ''
    ethernet_board = ''
    video_board = ''
    sound_board = ''
    bios = ''
    dvd_reader = ''
    cd_reader = ''
    modem = ''
    mouse = ''
    memory = ''
    
    def __init__(self):
        self.hw = get_hardware()
        self.motherboard = motherboard(self.hw, 0)
        self.cpu = cpu(self.hw, 0)
        self.ethernet_board = ethernet_board(self.hw, 0)
        self.video_board = video_board(self.hw, 0)
        self.sound_board = sound_board(self.hw, 0)
        self.bios = bios(self.hw) # BIOS is always index=0
        self.dvd_reader = dvd_reader(self.hw, 0)
        self.cd_reader = cd_reader(self.hw, 0)
        self.modem = modem(self.hw, 0)
        self.mouse = mouse(self.hw, 0)
        self.memory = memory(self.hw)

if __name__ == '__main__':

    teste = get_hardware()
    x = hardware()
        
#    a = get_hardware()
#    print a.data
#    x = hardware()
#    y = x.motherboard
#    print "h", x.motherboard.vendor, x.ethernet_board.product, x.video_board.product, x.video_board.vendor,\
#        x.dvd_reader.product, x.memory.size
