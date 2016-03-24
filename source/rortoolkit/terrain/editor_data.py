
# terrainparser.py
# ----------------
# Terrain editor context data objects

#Authors:
# Thomas Fischer: original author
# Lepes:          various updates
# only_a_ptr:     2016's reboot
 

from ror.logger import log
from ror.settingsManager import *
from ror.rorcommon import *
from ror.lputils import *
from roreditor.RoRConstants import *

from types import *

strErrors = "Errors: \n"
noRotateObjects = ['truck', 'load', 'machine', 'airplane', 'boat', 'fixed']
noRotateExt = ['.truck', '.load', '.machine', '.airplane', '.boat', '.fixed']

class EditorObject(object):
# Lepes: those variables are initialized with the module instantiation instead of the object instance 
#		 so they are moved to __init__ method :-|
#	x = None
#	y = None
#	z = None
#	rotx = None
#	roty = None
#	rotz = None
#	name = ""
#	line = 0
#	additionalOptions = []
#	comments = []
#	mayRotate = True
#	type = ""
#	error = None
#	deleted = False
#	modified = True

	
	def __del__(self):
#		super(Object, self).__del__()
		pass

	def __init__(self):
		self._scale = 1, 1, 1
		self._fileWithExt = ""
		self.barename = ""
		self.ext = ""

		""" clear variables that are 
		ONLY before __init__ method"""
		self.x = None
		self.y = None
		self.z = None
		self.rotx = None
		self.roty = None
		self.rotz = None
		self.name = ""
		self.line = 0 
		self.additionalOptions = []
		self.comments = []
		self.mayRotate = True
		self.type = ""
		self.error = None
		self.deleted = False
		self.isBeam = False #needed to know if it is linked into beamObjs or Objects to free memory
		self.line = -1 # there is no file line for this object
		self.spline = ''
		
		self.modified = True
		""" when loading and saving to file is changed to False
		   if TerrainOgreWindow create an object, it will be True.
		"""
		
		self.strPosRot = [] 
		# position and rotation readed from .terrn file in string format, avoid to convert
		# from string to float and viceversa due floats imprecision if object wasn't modified by user

	def getallposition(self):
		return self.x, self.y, self.z

	def setallposition(self, value):
		self.x, self.y, self.z = value

	def getallrotation(self):
		return self.rotx, self.roty, self.rotz

	def setallrotation(self, value):
		self.rotx, self.roty, self.rotz = value

	def getpositionRotation(self):
		return position, rotation

	def setpositionRotation(self, value):
		self.x, self.y, self.z, self.rotx, self.roty, self.rotz = value

	def allowSection72(self):
		""" return true if this entry allow custom
		7-2 section of terrain, in example 'village Coldwater'
		
		Special entries as Truckshop doesn't allow
		that user uses custom values
		"""

		return self.type == hardcoded['terrain']['objecttype']['.odef'] and not self.name in FIXEDENTRIES
	
	def clearAdditionalOptions(self):
		self.additionalOptions = []
	
	def CheckNewAdditionalOptions(self, qualifier, name):
		""" Object Inspector allows to set up section 7-2 
		for example: observatory qualifier Name
		
		qualifier is hardcoded for files in textures.zip with "icon_" prefix
		name already uses underscores instead spaces.
		
		"""
		if self.allowSection72():
			self.additionalOptions = []
			self.additionalOptions.append(qualifier)
			self.additionalOptions.append(name)
			return True
		else:
			return False

	def getScale(self):
		return self._scale

	def setScale(self, value):
		self._scale = value

	def _getfileWithExt(self):
		if self.ext == "": return self._fileWithExt + '.odef' 
		return self._fileWithExt

	def _setfileWithExt(self, value):
		""" can receive:  
		chapel.odef
		wrecker.truck """
		import os.path
		self.barename, self.ext = os.path.splitext(os.path.basename(value))
		self.name = self.barename 
		# only filename with ext (without path) 
		self._fileWithExt = value
		if self.ext != "":
			if hardcoded['terrain']['objecttype'].has_key(self.ext.lower()):
				self.type = hardcoded['terrain']['objecttype'][self.ext.lower()]

	fileWithExt = property(_getfileWithExt, _setfileWithExt,
					 doc="""Only Filename with Extension""")

	scale = property(getScale, setScale,
				 doc="sometimes used")

	position = property(getallposition, setallposition,
				 doc="Shortcuta to x, y, z variables")

	rotation = property(getallrotation, setallrotation,
				 doc="Shortcuta to rotx, roty, rotz")

	positionRotation = property(getpositionRotation, setpositionRotation,
				 doc="")	
	
	def setPosition(self, value):
		setallposition(value)

	def setRotation(self, value):
		setallrotation(value)

	def __str__(self):
		return "Terrain entry: " + self._fileWithExt

	def vector(self, text):
		return ("%12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %12.6f, %s" % (self.x, self.y, self.z, self.rotx, self.roty, self.rotz, text))

	def logPosRot(self, text):
		log().info(self.vector(text))

class TerrainEditorContext(object):

	from __builtin__ import staticmethod

	def geterrorSaving(self):
		return self._errorSaving

	def seterrorSaving(self, value):
		if value == "" or value == None:
			self._errorSaving = ""
		else:
			if self._errorSaving is "":
				self._errorSaving = strErrors 
			self._errorSaving += "\n- " + value 

	errorSaving = property(geterrorSaving, seterrorSaving,
				 doc="string error with errors while saving")   

	def __init__(self):
		"""
		Constructor, does essential init.
		"""
		import ror.lputils
		self.TruckStartPosition     = ror.lputils.positionClass()
		self.CameraStartPosition    = ror.lputils.positionClass()
		self.CharacterStartPosition = ror.lputils.positionClass()

		self.project       = None
		self.objects       = []
		self.beamobjs      = []
		self.procroads     = []
		# only filename with extension
		self.filename      = ''
		# name is filename without extension, useful for launching RoR command line
		self.name          = ''
		self.TerrainConfig = ''
		#name to show on Menu
		self.TerrainName   = ''
		self.UsingCaelum   = False
		self.WaterHeight   = None
		self.SkyColor      = None
		self.SkyColorLine  = None
		self.worldX        = None
		self.worldZ        = None
		self.worldMaxY     = None
		self.author        = []
		self.cubemap       = None

	@staticmethod
	def create_from_project(project):
		"""
		Factory method. Loads a terrain project.
		"""
		ctx = TerrainEditorContext()
		ctx.project = project
		ctx.project_title = project.header["name"]
		ctx.TerrainName   = project.header["name"]
		ctx.WaterHeight   = project.physics["global_water_height"]
		ctx.cubemap       = project.visuals["cubemap_name"]
		ctx.UsingCaelum   = project.visuals["use_caelum"]

		def load_position(pos_class, xyz_list):
			pos_class.x = xyz_list[0]
			pos_class.y = xyz_list[1]
			pos_class.z = xyz_list[2]

		load_position(ctx.TruckStartPosition    , project.gameplay["spawn_pos_truck_xyz"])
		load_position(ctx.CameraStartPosition   , project.gameplay["spawn_pos_camera_xyz"])
		load_position(ctx.CharacterStartPosition, project.gameplay["spawn_pos_character_xyz"])

		for project_obj in project.static_objects:
			editor_obj = EditorObject()
			editor_obj.type              = project_obj.type
			editor_obj.fileWithExt       = project_obj.filename
			editor_obj.additionalOptions = project_obj.extra_options
			editor_obj.position          = project_obj.position_xyz
			editor_obj.rotation          = project_obj.rotation_rx_ry_rz
			editor_obj.strPosRot         = None # Str
			editor_obj.line              = None # Str
			editor_obj.modified          = False
			editor_obj.spline            = None # Spline roads, obsolete
			editor_obj.isBeam            = False
			ctx.objects.append(editor_obj)

		for project_rig in project.rig_objects:
			editor_obj = EditorObject()
			editor_obj.isBeam      = True
			editor_obj.line        = None # str
			editor_obj.fileWithExt = project_rig.filename
			editor_obj.position    = project_rig.position_xyz
			editor_obj.rotation    = project_rig.rotation_rx_ry_rz
			editor_obj.strPosRot   = None # Str
			editor_obj.modified    = False
			ctx.beamobjs.append(editor_obj)

		return ctx

	@staticmethod
	def create_from_terrn_file(filename, progress_window):
		"""
		Classic constructor. Builds the terrain from .terrn file
		Since 2016 used only for .terrn import.
		"""
		object = TerrainEditorContext()
		object.project_title = filename

		progress_window.set_text("Processing file {0}".format(filename))
		import os.path
		object.name = os.path.split(filename)[1].split(".")[0]
		content = loadResourceFile(filename)
		log().info("processing terrain file: %s" % filename)
		if len(content) > 2:
			object.processTerrnFile(content)
			object.getTerrainSize(object.TerrainConfig)
		else:
			log().error("valid terrain must have at least 3 lines")
		log().info("processing of terrain finished!")
		return object

	def __del__(self):
		del self.objects
		del self.beamobjs
		del self.procroads
		del self.TruckStartPosition
		del self.CameraStartPosition
		del self.CharacterStartPosition
#		super(RoRTerrain, self).__del__()
	
	def getTerrainSize(self, cfgFile):
		try:
			lines = loadResourceFile(cfgFile)
			for line in lines:
				if line.lower().strip()[:11] == 'pageworldx=':
					self.worldX = int(line.lower().strip()[11:])
				if line.lower().strip()[:11] == 'pageworldz=':
					self.worldZ = int(line.lower().strip()[11:])
				if line.lower().strip()[:10] == 'maxheight=':
					self.worldMaxY = float(line.lower().strip()[10:])
				
		except:
			log().info("can not get size of the terrain (world dimensions) file: %s" % cfgFile)
			
	def isInWorld(self, vector):
		if self.worldX and self.worldZ:
			if vector.x > 0 and vector.x < self.worldX:
				if vector.z > 0 and vector.z < self.worldZ:
					return True
		return False
	
	def FixTerrainConfig(self, filename):
		# this is deprecated!
		return
		content = self.loadFile(filename)
		for i in range(0, len(content)):
			if content[i].lower().find("maxpixelerror") >= 0:
				content[i] = "MaxPixelError=0\n"
				log().info("fixed terrain's MaxPixelError - error")
				break
		self.saveFile(filename, content)
		
	def processTerrnFile(self, content):
		currentspline = ''
		self._errorSaving = ""
		linecounter = 0
		comm = [] #comments added to the next object added
		treemode = False
		procroad = False
		procroadlines = []
		for i in range(0, len(content)):
			# convert tabs to spaces!
			content[i] = content[i].replace("\t", " ")
			if treemode:
				comm.append(content[i])
				if content[i].strip()[:8] == "tree_end":
					treemode = False
				continue
			if content[i].lower()[:10] == '// splines':
				v = content[i].lower().split(' ')
				if len(v) > 2:
					currentspline = v[2]
				else:
					currentspline = ''
				continue
			
			if procroad:
				if content[i].strip()[:20] == "end_procedural_roads":
					procroad = False
					self.procroads.append(procroadlines[:len(procroadlines)])
					procroadlines = [] #clear for next procroad
					# process now
				else:
					procroadlines.append(content[i].strip().split(','))
				continue
				
			if content[i].strip() == "":
				comm.append(content[i])
				continue
			if content[i].strip()[0:4] == "////":
				# ignore editor self made comments (usefull for those error msgs)
				continue
			if content[i].strip()[:2] == "//":
				if content[i].strip().find("author") != -1:
					self.author.append(content[i].strip()[2:])
				else:
					comm.append(content[i])
				continue
			if content[i].strip()[:5] == "grass":
				comm.append(content[i])
				continue
			if content[i].strip()[:16] == "sandstormcubemap":
				comm.append(content[i])
				self.cubemap = content[i][17:]
				continue

			if content[i].strip()[:16] == "sandstormcubemap":
				comm.append(content[i])
				continue
			if content[i].strip()[:7] == "mapsize": # deprecated !!
				comm.append(content[i])
				continue
			if content[i].strip()[:7] == "mpspawn":
				comm.append(content[i])
				continue
			if content[i].strip()[:10] == "tree_begin":
				comm.append(content[i])
				treemode = True
				continue
			if content[i].strip()[:len('landuse-config')] == 'landuse-config':
				comm.append(content[i])
				continue
			if content[i].strip()[:len('trees ')] == 'trees ':
				comm.append(content[i])
				continue			
			if content[i].strip()[:22] == "begin_procedural_roads":
				procroad = True
				continue
				
			
			if content[i].strip()[0:1] == ";":
				# bugfix wrong characters!
				comm.append(content[i].replace(";", "//"))
				continue
			if content[i].strip().lower() == "end":
				continue
			# do not count empty or comment lines!
			linecounter += 1
			if linecounter == 1:
				#terrain name
				self.TerrainName = content[i].strip()
				continue
			elif linecounter == 2:
				# .cfg file
				self.TerrainConfig = content[i].strip()
				continue
			if content[i].strip()[0].lower() == "w":
				self.WaterHeight = float(content[i].strip()[2:])
				continue
			if content[i].strip().lower() == "caelum":
				self.UsingCaelum = True
				continue
			if linecounter < 10 and len(content[i].split(",")) == 3:
				# sky color
				sc = content[i].split(",")
				self.SkyColor = (float(sc[0]), float(sc[1]), float(sc[2]))
				self.SkyColorLine = content[i]
				continue
			if linecounter < 10  and len(content[i].split(",")) == 9 or len(content[i].split(",")) == 6:
				# spawning Position
				sp = content[i].split(",")
				self.TruckStartPosition.asStrList = [sp[0], sp[1], sp[2] ]
   
				self.CameraStartPosition.asStrList = [sp[3], sp[4], sp[5] ]
				if len(sp) == 9:
					self.CharacterStartPosition.asStrList = [ sp[6], sp[7], sp[8] ]
				continue

			arr = content[i].split(",")
			try:
				x = round(float(arr[0]), 6)
				y = round(float(arr[1]), 6)
				z = round(float(arr[2]), 6)
				rx = round(float(arr[3]), 1)
				ry = round(float(arr[4]), 1)
				rz = round(float(arr[5]), 1)
				objname = (arr[6]).strip().split(" ")
				strPosRot = [arr[0], arr[1], arr[2], arr[3], arr[4], arr[5]]
				objname = [ele.strip() for ele in objname] #strip each element
				strPosRot = [("%12s" % ele.strip()) for ele in strPosRot] #strip each element 
			except:
				log().error("unable to parse line %d: %s. ignoring it!" % (i, content[i]))
				comm.append(content[i])
				self._errorSaving += " %6d : %s \n" % (i, content[i])
				continue
				
			# truck wrecker.truck	
			if objname[0].lower() in noRotateObjects and len(objname) > 1:
				#print "truck"
				truck = EditorObject()
				truck.line = i
				truck.isBeam = True
				truck.fileWithExt = objname[1]
				truck.comments = comm
				comm = []
				truck.position = x, y, z
				truck.rotation = rx, ry, rz
				truck.strPosRot = strPosRot 
				truck.line = i
				self.beamobjs.append(truck)
				log().info('adding beamobjs ' + str(truck))
				truck.modified = False
				continue
			
			#print "object"
			# now it can just be an static object
			obj = EditorObject()
			obj.line = i
			
			#check section 7-2 Terrn_file_description
			lobj = len(objname)
			if lobj == 1:													   # chapel
				obj.fileWithExt = objname[0] 
				
			elif lobj == 2:													   
				if objname[0] in hardcoded['terrain']['objecttype'].values():   #truck wrecker.truck
					obj.fileWithExt = objname[1]
					
				else:														   #smallhouse farm
					obj.fileWithExt = objname[0]
					obj.additionalOptions = objname[1:]
					
			elif lobj == 3:													   
				if objname[1] in hardcoded['odef']['event'].values():		   #load-spawner sale Coldwater / bigsign_town sign parameter1 parameter2?? / truckshop shop
					obj.fileWithExt = objname[0] 
					obj.type = objname[1]
					obj.additionalOptions = objname[2:]
				if obj.type.strip() == "":									  # we are not lucky, may be "smallhouse farm Jhonston"
					obj.fileWithExt = objname[0]
					obj.additionalOptions = objname[1:]
			obj.comments = comm
			obj.line = i
			comm = []
			obj.position = x, y, z
			obj.rotation = rx, ry, rz
			obj.strPosRot = strPosRot
			self.objects.append(obj)
			obj.modified = False
			obj.spline = currentspline
			
		log().debug("number of procedural roads: %d" % len(self.procroads))

	def getObjectLines(self, obj):
		lines = []
		linearray = []
		objname = ""
		line = "" 
		# add comments
		if len(obj.comments) > 0:
			for comment in obj.comments:
				lines.append(comment + "\n")
		if obj.modified:
			linearray = [self.formatFloat(obj.x),
						 self.formatFloat(obj.y),
						 self.formatFloat(obj.z),
						 self.formatFloatR(obj.rotx),
						 self.formatFloatR(obj.roty),
						 self.formatFloatR(obj.rotz)]
			obj.strPosRot = [self.formatFloat(obj.x),
						 self.formatFloat(obj.y),
						 self.formatFloat(obj.z),
						 self.formatFloatR(obj.rotx),
						 self.formatFloatR(obj.roty),
						 self.formatFloatR(obj.rotz)]
			#FIXME: update strPosRot to the new coordenate ofrdelete strPosRot and test with round
		else:
			linearray = obj.strPosRot[:] #new allocated memory

		if obj.type in hardcoded['odef']['event'].values():
		  objname = obj.barename + " " + obj.type

		elif obj.type != "" and obj.type in hardcoded['terrain']['objecttype'].values():
			objname = obj.type + " " + obj.fileWithExt
		else:
			objname = obj.barename
		
		if len(obj.additionalOptions) > 0: 
			objname = objname + " " + " ".join(obj.additionalOptions)
		# add line itself
		linearray.append(objname)
		line = ", ".join(linearray) 
		if obj.deleted:
			line = "//" + line
		
		if not obj.error is None:
			lines.append("//// the next obj had errors, so the terrain editor commented it out:\n")
			lines.append("//" + line.strip() + "\n")
		else:
			lines.append(line.strip() + "\n")
		return lines
				
	def formatFloat(self, fl):
		return "%12s" % ("%0.6f" % (float(fl)))
		
	def formatFloatR(self, fl):
		return "%12s" % ("%0.6f" % round(float(fl), 1))
	
	""" 
	OBSOLETE, TO BE REMOVED
	Left around for reference

	def save(self, filename=None):
		if filename is None:
			ERR "you must supply a filename to save"
			return False

		log().debug("saving terrain as %s" % filename)
		lines = []
		lines.append(self.TerrainName + "\n")
		lines.append(self.TerrainConfig + "\n")
		if not self.WaterHeight is None:
			if self.WaterHeight != 0.0:
				lines.append("w " + str(self.WaterHeight) + "\n")
		if self.UsingCaelum:
			lines.append("caelum\n")
		lines.append(self.SkyColorLine.strip() + "\n")
		errores = ""
		ar = []
		try:
			ar.append(str(self.TruckStartPosition.x))
			ar.append(str(self.TruckStartPosition.y))
			ar.append(str(self.TruckStartPosition.z))
		except Exception, err:
			ERR "Bad Truck Start Position"
		try:
			ar.append(str(self.CameraStartPosition.x))
			ar.append(str(self.CameraStartPosition.y))
			ar.append(str(self.CameraStartPosition.z))
		except Exception, err:
			log().error(str(err))
			ERR "Bad Camera Start Position"
			
		if not self.CharacterStartPosition is None:
			try:
				ar.append(str(self.CharacterStartPosition.x))
				ar.append(str(self.CharacterStartPosition.y))
				ar.append(str(self.CharacterStartPosition.z))
			except Exception, err:
				log().error(str(err))
				ERR "Bad Character Start Position"
		startline = ", ".join(ar) + "\n"
		lines.append(startline)


		#save trucks
		for truck in self.beamobjs:
			trucklines = self.getObjectLines(truck)
			for l in trucklines:
				lines.append(l)
			truck.modified = False
		
		#Lepes: save procroads XD
		for p in self.procroads:
			lines.append('begin_procedural_roads\n')
			for l in p:
				lines.append(', '.join(l) + '\n')
			lines.append('end_procedural_roads\n')
		
		# save objects
		lastspline = ''				   
		for objectline in self.objects:
			objectlines = self.getObjectLines(objectline)
			if lastspline != objectline.spline:
				objectlines.insert(0, "// splines %s\n" % objectline.spline)
				lastspline = objectline.spline
			for l in objectlines:
				lines.append(l)
			objectline.modified = False
		lines.append("end\n")
		try:
			f = open(filename, 'w')
			f.writelines(lines)
			f.close()
		except Exception, err:
			log().error(str(err))
			ERR  ("Can not save Terrain, error accessing to disk file:\n %s \n\n Try with Save As...\n" + self._errorSaving) % filename
			# if exception ocourr, we assert to set modified to True, so it will saved when user choose save As
			for truck in self.beamobjs:
				truck.modified = True
			for objectline in self.objects:
				objectline.modified = True

		"""

		
