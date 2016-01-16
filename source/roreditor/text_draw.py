#
#from: http://www.ogre3d.org/wiki/index.php/ObjectTextDisplay
#
# The Code for Python-Ogre
#
#I use Python-Ogre, so I translated this to Python, and thought I'd save others the work. In my application, I use a function tempName() to generate object names. You may want to replace it with your own naming system. I include the code for tempName here so you can run my code without modification:

NEXTID = 1

def tempName():
	global NEXTID
	id = NEXTID
	NEXTID += 1
	return 'text%d'%id

#Here is the Python class:

# Copyright (c) 2007, David Mandelin
# All rights reserved.
# Use and redistribute freely.
#
# Translated from a C++ version authored by and copyright "Xavier".
# (He did all the hard work.)
#
# This code is provided as is, without warranty, use at your own risk.

import ogre.renderer.OGRE as ogre
from wxogre.OgreManager import *

#   ERROR
#21:15:42: OverlayElementFactory for type Panel registered.
#21:15:42: OverlayElementFactory for type BorderPanel registered.
#21:15:42: OverlayElementFactory for type TextArea registered.
#
#21:15:52: OGRE EXCEPTION(5:ItemIdentityException): Cannot locate factory for element type Panel in OverlayManager::createOverlayElement at ..\src\OgreOverlayManager.cpp (line 568)
#Traceback (most recent call last):
#  File "I:\Archivos de programa\Rigs of Rods 0.35\TOOLKIT\Rigs of Rods 0.34 Toolkit\lib_common\roreditor\RoRTerrainOgreWindow.py", line 1751, in onMouseEvent
#	self.selectnew(event)
#  File "I:\Archivos de programa\Rigs of Rods 0.35\TOOLKIT\Rigs of Rods 0.34 Toolkit\lib_common\roreditor\RoRTerrainOgreWindow.py", line 1223, in selectnew
#	self.changeSelection(r.movable)
#  File "I:\Archivos de programa\Rigs of Rods 0.35\TOOLKIT\Rigs of Rods 0.34 Toolkit\lib_common\roreditor\RoRTerrainOgreWindow.py", line 629, in changeSelection
#	OgreText(self.selected.entry.entity, self.camera, "myText")
#  File "I:\Archivos de programa\Rigs of Rods 0.35\TOOLKIT\Rigs of Rods 0.34 Toolkit\lib_common\roreditor\text_draw.py", line 41, in __init__
#	self.container = c = ovm.createOverlayElement("Panel", tempName())

class OgreText(object):
	"""Class for displaying text in Ogre above a Movable."""
	def __init__(self, movable, camera, text=''):
		self.movable = movable
		self.camera = camera
		self.text = ''
		self.container = None
		self.enabled = True

		ovm = ogre.OverlayManager.getSingleton()
		self.overlay = ov = ovm.create(tempName())
		self.container = c = ovm.createOverlayElement("Panel", tempName())
		ov.add2D(c)
		self.textArea = t = ovm.createOverlayElement('TextArea', tempName())
#		t.setDimensions(1.0, 1.0)
		t.setDimensions(0.3, 0.3)
		t.setMetricsMode(ogre.GMM_PIXELS)
		t.setPosition(0, 0)
		t.setParameter('font_name', 'BlueHighway')
		t.setParameter('char_height', '16')
		t.setParameter('horz_align', 'center')
		t.setColour(ogre.ColourValue(1.0, 1.0, 1.0))
		c.addChild(t)

		self.update()
		ov.show()

		self.setText(text)

	def __del__(self):
		self.destroy()

	def destroy(self):
		if hasattr(self, 'dead'): return
		self.dead = True
		self.overlay.hide()
		ovm = ogre.OverlayManager.getSingleton()
		self.container.removeChild(self.textArea.name)
		self.overlay.remove2D(self.container)
		ovm.destroyOverlayElement(self.textArea.name)
		ovm.destroyOverlayElement(self.container.name)
		ovm.destroy(self.overlay.name)

	def enable(self, f):
		self.enabled = f
		if f:
			self.overlay.show()
		else:
			self.overlay.hide()

	def setText(self, text):
		self.text = text
		self.textArea.setCaption(ogre.UTFString(text))

	def update(self):
		if not self.enabled : return

		# get the projection of the object's AABB into screen space
		bbox = self.movable.getWorldBoundingBox(True);
		mat = self.camera.getViewMatrix();
		corners = bbox.getAllCorners();

		min_x, max_x, min_y, max_y = 1.0, 0.0, 1.0, 0.0
		# expand the screen-space bounding-box so that it completely encloses
		# the object's AABB
		for corner in corners:
			# multiply the AABB corner vertex by the view matrix to
			# get a camera-space vertex
			corner = mat * corner;
			# make 2D relative/normalized coords from the view-space vertex
			# by dividing out the Z (depth) factor -- this is an approximation
			x = corner.x / corner.z + 0.5
			y = corner.y / corner.z + 0.5

			if x < min_x: min_x = x
			if x > max_x: max_x = x
			if y < min_y: min_y = y
			if y > max_y: max_y = y

		# we now have relative screen-space coords for the
		# object's bounding box; here we need to center the
		# text above the BB on the top edge. The line that defines
		# this top edge is (min_x, min_y) to (max_x, min_y)

	# self.container.setPosition(min_x, min_y);
		# Edited by alberts: This code works for me
		self.container.setPosition(1-max_x, min_y);
		# 0.1, just "because"
		self.container.setDimensions(max_x - min_x, 0.1);
