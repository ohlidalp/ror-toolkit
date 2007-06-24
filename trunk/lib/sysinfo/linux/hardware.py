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

from xml.sax import ContentHandler
from xml.sax import make_parser
from xml.sax import parseString

import StringIO
import xml.sax

import commands
import logging
import string 
import sys
import os

logger = logging.getLogger("sysinfo.linux.hardware")

# FIXME: teste feito em MDS500 mostrou que lshw às vezes gera um XML com
# caracteres estranhos, como ^E^D^D^C

class lshw_run_error(Exception):
    pass

class lshw_data_parser(ContentHandler):
    """Parse a XML file that was created using 'lshw -xml'. You need another
    function to parse it and copy the contents of "HardWare". The class
    "HardWare" below does that.
    """

    def __init__(self):
        logger.debug("Created new instance for the 'lshw_data_parser' class")
        # List of dicts containing Nodes data
        self.Nodes = []
        # Dict containing current tag data.
        self.CurrentTag = [{}]

        # String with the current tag represented unit, if available.
        self.CurrentTagUnits = ''
        # Dict containing relevant machine data.
        # Every item should support multiple values
        self.HardWare = {}

    def startElement(self, tag, attrs):

        self.CurrentTag.append({'name' : tag })
        # If it has a representation unit, set it.
        # FIXME: this is returning the WRONG unit
        # Disabled it temporarily until needed
        #try:
        #    unit = attrs.get('units')
        #except:
        #    self.CurrentTagUnits = ''
        #else:
        #    if unit:
        #        self.CurrentTagUnits = unit

        if tag == 'node':

            self.Nodes.append({'name' : 'node' })

            # Fill node attributes information
            try:
                nodeclass = attrs.get('class','')
            except:
                pass
            else:
                self.Nodes[-1]['class'] = nodeclass

            try:
                nodehandle = attrs.get('handle','')
            except:
                pass
            else:
                self.Nodes[-1]['handle'] = nodehandle


    def endElement(self, tag):
        
        # sanity test
        if self.CurrentTag[-1]['name'] != tag:
            sys.exit(1)

        else:
            self.CurrentTag.pop()
            if tag == 'node':
            # Node closing. We should get all that and store somewhere, then
	    # pop it
            # from the self.Nodes list.
                node = self.Nodes[-1]

                if node.has_key('physid') and node.has_key('description'):

                    self.setHardWare(node)

                else:
                    #print "Strange. Node lacks physid and/or description"
                    pass
                    
                if len(self.Nodes) > 1:
         #       print "closing", tag
                    self.Nodes.pop()
    
    def characters(self, ch):

        # This will populate self.Nodes[-1] with relevant data.
        # Not that it would only work for unique data (like physid)
        for x in ['description', 'physid', 'product', 'vendor', 'version', 
    'size', 'slot', 'width', 'serial']:

            if self.CurrentTag[-1]['name'] == x:
 
                if self.Nodes[-1].has_key(x):
                    self.Nodes[-1][x] += ch
                else:
                    self.Nodes[-1][x] = ch

    def setHardWare(self, node):
        """Argh. This is ugly.
        """
        # FIXME: hmm what's the string for CD reader?
        for element in ['CPU', 'BIOS', 'System Memory', 'System memory', 
    'Motherboard', 'VGA compatible controller', 
    'Multimedia audio controller', 'DVD-RAM writer', 'DVD reader', 
    'Modem' ,'Mouse', 'Ethernet interface']:

            if node['description'] == element:
                if not self.HardWare.has_key(element):
                    self.HardWare[element] = []
    
                self.HardWare[element].append({})
    
                for info in ['product', 'vendor', 'size','version', 'slot', 
		    'width', 'serial']:
                    if node.has_key(info):
                        set = node[info]
                        if info == 'size' and len(self.CurrentTagUnits) > 1:
                           unit = self.CurrentTagUnits
                           set += ' ' + unit
        
                        self.HardWare[element][-1][info] = set
                # In some cases (why?) 'System Memory' appears with
		# a minor 'm'.
                if element == 'System memory':
                    self.HardWare['System Memory'] = self.HardWare[element]    


class get_hardware:
 
    def __init__(self):
        parser = make_parser()
        handler = lshw_data_parser()
        parser.setContentHandler(handler)
        logger.info("Calling lshw.")

        id = str(os.getuid())

        if id != '0':
            logger.error("In the current version, sysinfo hardware collection \
requires root. Current uid: " + id)
	    print "Sysinfo must be run as root."
            sys.exit(1)

        lshwxml = commands.getstatusoutput(
	    "export LANGUAGE=C; /usr/bin/env lshw -xml 2>&1|grep -v WARNING")
        logger.info("lshw execution finished.")

        if lshwxml[0] != 0 or len(lshwxml[1]) < 1:
            # This would kill this module instance. 
	    # Should we handle it instead?
	    # 16/03/06: Die!!
            logger.error("Could not run lshw")
            raise lshw_run_error, "could not run lshw"
        else:
            xmldata = lshwxml[1]

        sane_data = ''
        for char in xmldata:
            if char in string.printable:
                sane_data += char

        input = StringIO.StringIO(sane_data)
        parser.parse(input)
        self.data = handler.HardWare

class keyboard:
    """Get keyboard info from /proc/bus/input/devices
    """
    
    def __init__(self):
        logger.debug("Getting keyboard data") 
    
        try:
            devices_file = open('/proc/bus/input/devices', 'r')
        except:
            pass
        else:

            input = devices_file.readlines()

            for line in input:
                if 'keyboard' in line:
                    k1 = line.replace('N: Name=','')
                    k2 = k1.replace('"','')
                    self.model = k2
            

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
            self.size = hw.data['System Memory'][0].get('size', '').replace(' bytes','')

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

class dvd_reader:
   
    product = ''
 
    def __init__(self, hw, index=0):
        if hw.data.has_key('DVD reader'):
            self.product = hw.data['DVD reader'][index].get('product', '')

class dvd_ram_writer:

    product = ''
    serial = ''
    vendor = ''


    def __init__(self, hw, index=0):
        if hw.data.has_key('DVD-RAM writer'):
            self.product = hw.data['DVD-RAM writer'][index].get('product', '')
            self.serial = hw.data['DVD-RAM writer'][index].get('serial', '')
            self.version = hw.data['DVD-RAM writer'][index].get('version', '')

class bios:

    product = ''
    size = ''
    vendor = ''
    
    def __init__(self, hw):
        if hw.data.has_key('BIOS'):
            self.product = hw.data['BIOS'][0].get('product', '')
            self.vendor = hw.data['BIOS'][0].get('vendor', '')
            self.version = hw.data['BIOS'][0].get('version', '')



class video_board:

    product = ''
    size = ''
    width = ''
    vendor = ''
    
    def __init__(self, hw, index=0):
        if hw.data.has_key('VGA compatible controller'):
            self.product = \
    hw.data['VGA compatible controller'][index].get('product')
            self.memory = \
    hw.data['VGA compatible controller'][index].get('size').replace(' bytes','')
            self.width = \
    hw.data['VGA compatible controller'][index].get('width')
            self.vendor = \
    hw.data['VGA compatible controller'][index].get('vendor')

class sound_board:

    product = ''
 
    def __init__(self, hw, index=0):
        if hw.data.has_key('Multimedia audio controller'):
            self.product = \
    hw.data['Multimedia audio controller'][index].get('product')

class ethernet_board:

    product = ''
    size = ''
    vendor = ''
    width = ''
    vendor = ''
    serial = ''

    def __init__(self, hw, index=0):

        if hw.data.has_key('Ethernet interface'):
            self.product = \
    hw.data['Ethernet interface'][index].get('product', '')
            self.width = \
    hw.data['Ethernet interface'][index].get('width', '')
            self.vendor = \
    hw.data['Ethernet interface'][index].get('vendor', '')
            self.version = \
    hw.data['Ethernet interface'][index].get('version', '')
            self.serial = \
    hw.data['Ethernet interface'][index].get('serial', '')
       
class cpu:

    product = ''
    size = ''
    vendor = ''
    
    def __init__(self, hw, index=0):
        if hw.data.has_key('CPU'):
            self.product = hw.data['CPU'][index].get('product', '')
            self.vendor = hw.data['CPU'][index].get('vendor', '')
            self.frequency = hw.data['CPU'][index].get('size', '')

class hardware:
    """This is the interfaced accessed by the user. It provides
    hardware data collected through get_hardware.
    """
    # FIXME: motherboard, cpu, etc need support to multiple values. Currently
    # uses index=0

    def __init__(self):
        logger.debug("Created new instance for the 'hardware' class")
        self.hw = get_hardware()
        self.motherboard = motherboard(self.hw, 0)
        self.cpu = cpu(self.hw, 0)
        self.ethernet_board = ethernet_board(self.hw, 0)
        self.video_board = video_board(self.hw, 0)
        self.sound_board = sound_board(self.hw, 0)
        self.bios = bios(self.hw) # BIOS is always index=0
        self.dvd_reader = dvd_reader(self.hw, 0)
        self.dvd_ram_writer = dvd_ram_writer(self.hw, 0)
        self.modem = modem(self.hw, 0)
        self.mouse = mouse(self.hw, 0)
        self.memory = memory(self.hw)
        self.keyboard = keyboard()

if __name__ == '__main__':
#    a = get_hardware()
#    print a.data
    x = hardware()
    y = x.motherboard
    print "h", x.motherboard.vendor, x.ethernet_board.product, \
	x.video_board.product, x.video_board.vendor,\
        x.dvd_reader.product, x.memory.size
