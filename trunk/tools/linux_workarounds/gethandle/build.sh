#!/bin/sh
g++ -shared `/usr/lib/wx/config/gtk2-unicode-release-2.8 --cflags` `pkg-config gtk+-2.0 --cflags` `/usr/lib/wx/config/gtk2-unicode-release-2.8 --libs` `pkg-config gtk+-2.0 --libs` -lGL wxogre_util.cpp -o libwxogre_util.so
