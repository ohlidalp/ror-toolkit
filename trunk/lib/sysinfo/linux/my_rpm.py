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

"""Provides package management system information using RPM
"""

# thanks to http://users.sarai.net/shehjar/download/py-apt-tut.txt

import rpm
import logging

logger = logging.getLogger("sysinfo.linux.rpm")

class packages:

    installed = []
    installed_ver = {}
    update_candidates = {}
    
    def __init__(self):
        self.installed = self._get_installed()
        self.installed.sort()
       
    def _get_installed(self):
        """Gets installed packages information using RPM.
        """
        ins_pkgs = []
        ts = rpm.TransactionSet()
        mi = ts.dbMatch() # all installed packages
        for h in mi:
            ins_pkgs.append(h['name'])
        return ins_pkgs
 
if __name__ == '__main__':
    s = packages()
    print "instalados", s.installed
    #print "instalados_versao", s.installed_ver
    print "update", s.update_candidates
    
