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

# from http://www.voidspace.org.uk/python/pathutils.html (BSD License)

def formatbytes(sizeint, configdict=None, **configs):
    """
    Given a file size as an integer, return a nicely formatted string that
    represents the size. Has various options to control it's output.
    
    You can pass in a dictionary of arguments or keyword arguments. Keyword
    arguments override the dictionary and there are sensible defaults for options
    you don't set.
    
    Options and defaults are as follows :
    
    *    ``forcekb = False`` -         If set this forces the output to be in terms
    of kilobytes and bytes only.
    
    *    ``largestonly = True`` -    If set, instead of outputting 
        ``1 Mbytes, 307 Kbytes, 478 bytes`` it outputs using only the largest 
        denominator - e.g. ``1.3 Mbytes`` or ``17.2 Kbytes``
    
    *    ``kiloname = 'Kbytes'`` -    The string to use for kilobytes
    
    *    ``meganame = 'Mbytes'`` - The string to use for Megabytes
    
    *    ``bytename = 'bytes'`` -     The string to use for bytes
    
    *    ``nospace = True`` -        If set it outputs ``1Mbytes, 307Kbytes``, 
        notice there is no space.
    
    Example outputs : ::
    
        19Mbytes, 75Kbytes, 255bytes
        2Kbytes, 0bytes
        23.8Mbytes
    
    .. note::
    
        It currently uses the plural form even for singular.
    """
    defaultconfigs = {  'forcekb' : False,
                        'largestonly' : True,
                        'kiloname' : 'Kbytes',
                        'meganame' : 'Mbytes',
                        'bytename' : 'bytes',
                        'nospace' : True}
    if configdict is None:
        configdict = {}
    for entry in configs:
        # keyword parameters override the dictionary passed in
        configdict[entry] = configs[entry]
    #
    for keyword in defaultconfigs:
        if not configdict.has_key(keyword):
            configdict[keyword] = defaultconfigs[keyword]
    #
    if configdict['nospace']:
        space = ''
    else:
        space = ' '
    #
    mb, kb, rb = bytedivider(sizeint)
    if configdict['largestonly']:
        if mb and not configdict['forcekb']:
            return stringround(mb, kb)+ space + configdict['meganame']
        elif kb or configdict['forcekb']:
            if mb and configdict['forcekb']:
                kb += 1024*mb
            return stringround(kb, rb) + space+ configdict['kiloname']
        else:
            return str(rb) + space + configdict['bytename']
    else:
        outstr = ''
        if mb and not configdict['forcekb']:
            outstr = str(mb) + space + configdict['meganame'] +', '
        if kb or configdict['forcekb'] or mb:
            if configdict['forcekb']:
                kb += 1024*mb
            outstr += str(kb) + space + configdict['kiloname'] +', '
        return outstr + str(rb) + space + configdict['bytename']


