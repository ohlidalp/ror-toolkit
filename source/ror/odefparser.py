# Updates made by Lepes
# odef definition file updated from wiki on 2009-01-20

import copy, os, os.path
import ogre.renderer.OGRE as ogre
from ror.logger import log
from ror.rorcommon import *
from ror.settingsManager import *
from ror.lputils import *


class odefbox(object):
	
	def __init__(self, main):
		self._main = main # odefClass that maintain this odefbox
		# dynamically text draw arguments
		self.arguments = []
		
		# setmeshMaterial
		self.meshMaterial = []
		# if the box has friction, it will be a list of parameters ['stdfriction', 'nameOfFriction']
		self.stdfriction = []
		# is a standard friction name??
		self.isStandardFriction = False
		self.virtual = False
		self.event = []
		self.isSpawnZone = False
		self.normal = False
		self.virtual = False
		# rotx , roty, rotz to aply to the box
		self.rotation = None
	
		# readed from file: six values with 2 vertices of Box x, x1, y, y1, z, z1
		# converted to positionClass
		self.coord0 = None
		self.coord1 = None
		self.forcecamera = None
		self.direction = None
		self.camera = None
		self.initVariables()
		self.name = ""
		
	def __del__(self):
		del self.coord0 
		del self.coord1 
		del self.rotation 		
		
	def initVariables(self):
		""" clear variables that are 
		ONLY before __init__ method"""
		self.coord0 = None
		self.coord1 = None
		self.rotation = None
		self.arguments = []
		self.meshMaterial = []
		self.stdfriction = []
		self.isStandardFriction = False
		self.virtual = False
		self.event = []
		self.isSpawnZone = False
		self.normal = False
		self.virtual = False
		self.forcecamera = None
		self.direction = None
		self.camera = None	
		self.isMesh = False	
		self.meshName = ""
		self.coord0 = positionClass()
		self.coord1 = positionClass()
		self.rotation = rotationClass()
	   
	def __str__(self):
		s = "\n"
		if self.rotation:
			s += "rotating, "
		if self.virtual:
			s += "virtual"
		
		if len(self.event) > 1:
			s += " eventname='%s' " % self.event[1]
		if len(self.event) > 2 :
			s += " triggered by '%s' \n" % self.event[2]
			
		s += " coordinates:\n 0 = " + ", ".join(self.coord0.asStrList) + "\n 1 =  " + ", ".join(self.coord1.asStrList)
		if self.rotation:
			s += " rotation: " + ", ".join(self.rotation.asStrList)
		return s
	
	def parseEvent(self, value):
		self.event = value.split(" ")
		for i in range(0, len(self.event)):
			self.event[i] = self.event[i].strip()
		if len(self.event) > 1:
			self.isSpawnZone = self.event[1].lower() == "spawnzone"
			if self.isSpawnZone: 
				self._main.isSpawnZone = True
			if hardcoded['odef']['event'].has_key(self.event[1].lower()):
				self._main.event = self.event[1].lower()
		if len(self.event) > 2:
			if not self.event[2].lower() in hardcoded['odef']['trigger']:
				if self._main: fn = self._main.filename
				else: fn = 'unknown file'
				log().error("Odefbox has a bad trigger name.\nFilename %s\n Actual value: '%s' Allowed values: %s" % (fn, self.event[1], " / ".join(hardcoded['odef']['trigger'])))
		" ".join(self.event)
	def debug(self, msg=""):
		log().info(msg + " " + self.__str__())
	
	def buildName(self):
		if self._main is None: s = randomID()
		else: s = len(self._main.boxes)
		self.name = "Box_%s" % str(s)
		if self.virtual: self.name = "virtual" + self.name
		if len(self.event) > 1:
			self.name += "_%s" % self.event[len(self.event) - 1]
		if self.forcecamera is not None:
			self.name += "_forcecamera"
		if self.camera is not None:
			self.name += "_camera"

	def getOdefboxString(self):
		""" return generated text of the odefbox to write on .odef file
		"""
		#TODO: actually only boxcoord/beginmesh is returned
		s = ';%s\n' % self.name
		if self.isMesh:
			s += 'beginmesh\nmesh %s\n' % self.meshName
		else:
			s += 'beginbox\nboxcoords %.2f, %.2f, %.2f, %.2f, %.2f, %.2f\n' % (
					self.coord0.x, self.coord1.x, self.coord0.y, self.coord1.y, self.coord0.z, self.coord1.z)
		if self.virtual:
			s += 'virtual\n'
		if len(self.event) > 1:
			s += " ".join(self.event) + '\n'
		if self.forcecamera:
			if not self.forcecamera.isZero():
				s += "forcecamera %.2f, %.2f, %.2f\n" % (self.forcecamera.x, self.forcecamera.y, self.forcecamera.z)  
		if self.camera:
			if not self.camera.nearZero():
				s += "camera %.2f, %.2f, %.2f\n" % (self.camera.x, self.camera.y, self.camera.z)
		if self.rotation:
			if not self.rotation.isZero():
				s += "rotate %.2f, %.2f, %.2f\n" % (self.rotation.rotx, self.rotation.roty, self.rotation.rotz)
		if self.isMesh:
			s += 'endmesh\n'
		else:
			s += "endbox\n"
		s += '\n\n'
		return s
			
		

# Lepes: 
# odefClass has extended features:
#- playanimation 
#- isSpawnZone
#- eventname and triggeredBy
class odefClass(object):
	""" Lepes: class for odef files """
	

	def __init__(self, odefFilename=None):
		self.initVariables()
		if not odefFilename is None:
			self.loadFromFile(odefFilename)

	def __del__(self):
		del self.boxes
		
	def initVariables(self):
		""" clear variables that are 
		ONLY before __init__ method"""
		self.boxes = []
		self.isMovable = False
		self.isSpawnZone = False
		# eventname linked to the spawnzone
		self.event = ""
		# at least one box has text parameters
		self.hasArgument = False
		#drawText doesn't need to be inside an odef box
		self.arguments = []
		
		self.meshMaterial = []
		self.scale = 1, 1, 1
		self.meshName = ""
		#playanimation <speedfactorMin> <speedfactorMax> <AnimationName>
		self.animation = []
		self.filename = ""		
	
	def loadFromFile(self, odefFilename):
		if odefFilename[ -5:] != ".odef":
			odefFilename += ".odef"
		self.filename = odefFilename
		hasLod = False
		
		try:
			content = loadResourceFile(odefFilename)
			if len(content) > 1:
				idxmesh = 0
				if content[0].strip().lower() == 'lod':
					idxmesh = 1
				self.meshName = content[idxmesh].strip()
				scalearr = [1, 1, 1]
				if len(content[idxmesh + 1].split(",")) == 3:
					scalearr = content[idxmesh + 1].split(",")
					self.scale = (float(scalearr[0]), float(scalearr[1]), float(scalearr[2]))
				actualbox = None
				for line in content[idxmesh + 2:] :
					oline = line.strip()
					line = line.strip().lower()  #BUG: all text are changed to lowercase
					if len(line) == 0 or line[0] == '/':
						continue
					elif line == "end":
						break
					elif line == "movable":
						self.isMovable = True
					elif line in ["beginbox", "beginmesh"]:
						actualbox = odefbox(self)
						actualbox.isMesh = line == "beginmesh"
					elif line[:9] == "boxcoords":
						l = line[10:].split(",")
						actualbox.coord0.asStrList = [l[0], l[2], l[4]]
						actualbox.coord1.asStrList = [l[1], l[3], l[5]]
					elif line[:6] == "rotate":
						actualbox.rotation.asStrList = line[7:].split(",")
					elif line == "virtual":
						actualbox.virtual = True
					elif line[:5] == "event":
						actualbox.parseEvent(line)
					elif line in ["endbox", "endmesh"]:
						actualbox.normal = not actualbox.virtual
						actualbox.buildName() # set the name variable
						self.boxes.append(actualbox)
						actualbox = None
					elif line[:len("playanimation")] == "playanimation":
						self.animation = line.split(" ")
						self.animation[1] = float(self.animation[1])
						self.animation[2] = float(self.animation[2])
					elif line[:len("direction")] == "direction":
						actualbox.direction = positionClass()
						actualbox.direction.asStrList = line[len("direction") + 1:].split(",")
					elif line[:len("forcecamera")] == "forcecamera":
						actualbox.forcecamera = positionClass()
						actualbox.forcecamera.asStrList = line[len("forcecamera") + 1:].split(",")
					elif line[:len("camera")] == "camera":
						actualbox.camera = positionClass()
						actualbox.camera.asStrList = line[len("camera") + 1:].split(",")
					elif line[:len("mesh")] == "mesh":
						actualbox.isMesh = True
						actualbox.meshName = oline.split(" ")[1]
#					elif line[:len("beginattach")] == "beginattach":
						
					
					
					#FIXME: the next section had NOT been debugged !!!
					elif line[:len("drawTextOnMeshTexture")].strip().lower() == "drawtextonmeshtexture":
						start = oline.find("{{") 
						finish = oline.find("}}")
						if  start != -1 and finish != -1:
							self.hasArguments = True
							if actualbox :
								actualbox.arguments.append(oline[start:(finish - start)])
							else:
								self.arguments.append(oline[start:(finish - start)])
					elif line[:len("stdfriction")].strip().lower() == "stdfriction":
						actualbox.stdfriction = oline.strip().split(" ")
						actualbox.isStandardfriction = actualbox.stdfriction[1].lower() in hardcoded['odef']['stdfriction']
					elif line[:len("friction")].strip().lower() == "friction":
						actualbox.frictionParams = line.strip() #TODO: parse this line
					elif line[:len("setMeshMaterial")].strip().lower() == "setmeshmaterial":
						if actualbox :
							actualbox.meshMaterial.append(oline.strip()) #TODO: parse this line "setMeshMaterial tracks/bigsighn/town"
						else:
							self.meshMaterial.append(oline.strip().split(' ')[1]) #TODO: parse this line "setMeshMaterial tracks/bigsighn/town"
														   
#					else:
#						log().debug('odef file: "%s" ignoring line: "%s"' % (self.filename, oline))	
		except Exception, err:
			log().error(str(err))
			log().error("Error while parsing file %s, line: %s" % (odefFilename, oline))
			if rorSettings().stopOnExceptions:
				raise 
