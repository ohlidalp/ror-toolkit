# by Lepes
# parser for extension file .toolkit that hold:
# attatch points

import copy, os, os.path
import errno
import ogre.renderer.OGRE as ogre
from ror.logger import log
from ror.rorcommon import *
from ror.settingsManager import *
from ror.lputils import *
from types import *



dicty={
		'attatch':[],
		'splines':{}
		}

#BUG: attatched points of other classes are added to the terrain
#BUG: saving and start RoR will loose splines not saved before... memory leaks? OGRE.loadResource ?
class toolkitClass(object):
	""" Lepes: class for .toolkit files """
	

	def __init__(self, filename = None):
		self.properties = []
		self.filename = ""
		self.loaded = False
		self.splineNames = {}
		for k in dicty.keys():
			self.resolveProperty(k)
		if not filename is None:
			self.loadFromFile(filename)

	def __del__(self):
		del self.splineNames
		for p in self.properties:
			prop = getattr(self, p) 
			if isinstance(prop, ListType):
				del prop[0:len(prop)]
				del prop
			elif isinstance(prop, DictType):
				prop.clear()
				del prop
			
	
	def __str__(self):
		return 'File: "%s", %d attatch, %d splines' %(self.filename, len(self.attatch), self.splines.keys().count())
	
	def resolveProperty(self, name):
		""" create a new property 
			RTTI rules !! ;-)
		"""
		if not hasattr(self, name):
			if name in dicty.keys():
				setattr(self, name, dicty[name]) 
			else :
				log().error('the word %s is not a valid toolkitClass token' % name)	
				
			self.properties.append(name) # record the property name to free memory
		return getattr(self, name)

	def addPointToSpline(self, UID = '', vector3Pos = None, tuplePos = None):
		x = positionClass()
		if vector3Pos is not None:
			x.asVector3 = vector3
		elif tuplePos is not None:
			x.asTuple = tuplePos
		else:
			raise Exception("toolkitClass.addPointToSpline: no position has been supplied")
		if not self.splines.has_key(UID):
			self.splines[UID] = []
		self.splines[UID].append(x)
		
	def loadFromFile(self, toolkitFilename):
		if toolkitFilename[ - 8:] != ".toolkit":
			toolkitFilename += ".toolkit"
		self.filename = toolkitFilename
		content = loadResourceFile(toolkitFilename)
		values = []
		uid = ''
		for line in content:
			try:
				if len(line.strip()) == 0:
					continue
				values = line.strip().split(',')
				if len(values) == 0 or values[:1]==';' or values[:2] == '//' :
					continue

				str = [z.strip() for z in values[0].split(' ') if z.strip() !='']
				propname = str[0]
				if len(str) > 1:
					values[0]= str[1]
				if propname == 'splines':
					uid = values[0]
					continue
				elif propname == 'end_splines':
					uid = ''
					continue
				elif propname == 'splineName':
					self.splineNames[uid] = line[11:]
					continue
					
					
				x = positionClass()
				x.asStrList= values
			except Exception, err:
				log().info('error procesing file %s. Ignoring line "%s"' % (toolkitFilename, line))
				log().info(err)
				continue

			if len(uid) > 0 and propname == 'point':
				if not self.splines.has_key(uid):
					self.splines[uid] = []
				self.splines[uid].append(x)
				continue
				
			prop = self.resolveProperty(propname)
			prop.append(x)
		self.loaded = True
		l = len(content) > 0 
		content = []
		return l

	def saveToFile(self, fn = None):
		#BUG: after launching ror, I only get the latest spline in combobox
		if fn is not None:
			if fn[ - 8:] != ".toolkit":
				fn += ".toolkit"
			
			content = []
			try:
				for k in dicty.keys(): # property name
					prop = getattr(self, k)
					if type(prop) is DictType:
						for s in prop.keys(): # each Spline points
							content.append("%s %s\n" % (k, s) )
							if self.splineNames.has_key(s):
								content.append('splineName %s\n' % self.splineNames[s])
							for i in range(len(prop[s])): # each point
								content.append(prop[s][i].leftAlign("point") + '\n')
							content.append("end_%s\n" % k)
					elif type(prop) is ListType:
						for i in range(len(prop)):
							content.append(prop[i].leftAlign(k) + "\n")
			except Exception, err:
				log().error('error in file "%s". The file has been truncated to previous line of the error' % fn)
				log().error(str(err))
			f = open(fn,'w')
			f.writelines(content)
			f.close()
			log().debug('saved SplineLines in %s' % fn)
				
	def purgueSpline(self, strUID):
		if self.spline.has_key(strUID):
			self.spline.pop(strUID)
		if self.splineNames.has_key(strUID):
			self.splineNames.pop(strUID)		
		
