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

"""Provides package management system information using APT
"""

# thanks to http://users.sarai.net/shehjar/download/py-apt-tut.txt

import apt_pkg
import os
import sys
import commands
import re
import logging

logger = logging.getLogger("sysinfo.linux.apt")

class packages:

    installed = []
    installed_ver = {}
    update_candidates = {}
    
    def __init__(self):
        # FIXME: These works, but isn't it ugly?
        #os.close(1)
        #os.close(2)
        c = cache()
        self.installed = c.installed_packages.keys()
        self.installed.sort()
        self.update_candidates = c.update_candidates
        
        for software in self.installed:
            self.installed_ver[software] = c.installed_packages[software].VerStr
        

class cache:

    installed_packages = {}
    update_candidates = {}
    cache = ''
    
    def __init__(self):

        apt_pkg.init()
        self.cache = apt_pkg.GetCache()
        self.installed_packages = self._get_installed_packages()
        self.update_candidates = self._get_update_candidates()
        

    def _get_update_candidates(self):

        update_pkgs = {} 

        try:
            depcache = apt_pkg.GetDepCache(self.cache)

        except AttributeError:
            # We are using an old version of libapt (like sarge's)
            aptget = commands.getstatusoutput("export LANGUAGE=C; /usr/bin/env  aptitude search '~U' -F '%p## %V##' 2> /dev/null")
            if aptget[0] != 0:
                logger.error("Error while trying to run apt-get upgrade")
                logger.error("ERROR:" + str(aptget[1]))
                return False

            get = aptget[1].split('\n')
            for line in get:
                h = re.compile('^(?P<pk_name>[\S]+)\s+(?P<pk_ver>[\S]+)')
                p = h.search(line)
                try:
                    if not (p.group('pk_name') and p.group('pk_ver')):
                        continue     
		except AttributeError:
		    continue 
		else:
                    update_pkgs[p.group('pk_name')] = p.group('pk_ver')

        else:
            # Ok, new version of apt. This is the pretty way to do it :-)
            depcache.ReadPinFile()
            depcache.Init()
            depcache.Upgrade()

            for pkg in self.cache.Packages:
               if depcache.MarkedInstall(pkg) or depcache.MarkedUpgrade(pkg):
                   if depcache.GetCandidateVer(pkg) != pkg.CurrentVer:
                       update_pkgs[pkg.Name] = \
                       depcache.GetCandidateVer(pkg).VerStr
        return update_pkgs
               
 
    def _get_installed_packages(self):
        inst_pkgs = {}
        
        for pkg in self.cache.Packages:
            if pkg.CurrentVer:
                inst_pkgs[pkg.Name] = pkg.CurrentVer
        return inst_pkgs        

if __name__ == '__main__':
    s = packages()
    #print "instalados", s.installed
    #print "instalados_versao", s.installed_ver
    print "update", s.update_candidates
    
