#!/bin/env python
# Lepes: constants used on ror
import ogre.renderer.OGRE as ogre
import wx
from ror.settingsManager import rorSettings

RORCAMERA = "RoRcamera"
RORCHARACTER = "RoRcharacter"
RORTRUCK = "RoRstartTruck"
FIXEDENTRIES = [RORCAMERA, RORCHARACTER, RORTRUCK]

VALIDSTRUCKS = ['.truck', '.load', '.boat', '.trailer', '.airplane', '.car', '.fixed', '.machine']


CLCREAM = "TruckEditor/NodeExhaustReference"
CLBLUE = "mysimple/blue"
CLRED = "mysimple/red"
CLGREEN = "mysimple/green"
CLYELLOW = "mysimple/yellow"

CLTRANSRED = "mysimple/transred"
CLTRANSGREEN = "mysimple/transgreen"
CLTRANSBLUE = "mysimple/transblue"
CLTRANSYELLOW = "mysimple/transyellow"

""" they are not constants, are the actual value used on truck editor"""
BEAM_DIAMETER = 0.006
DOT_SCALE = 0.018 #0.010696
NODE_NUMBERS = 0.18
BEAMS = ['beams', 'commands', 'commands2', 'shocks', 'shocks2', 'hydros']
NOTEPAD_HIGHLIGHTCOLOR = wx.Color(248, 184, 184)

RWHEELS = 'rorToolkit-wheels' # wheels created dynamically
colors = {'BACKGROUND':[0.5, 0.5, 0.57]

		}

def color(key):
	return ogre.ColourValue(colors[key][0], colors[key][1], colors[key][2])
