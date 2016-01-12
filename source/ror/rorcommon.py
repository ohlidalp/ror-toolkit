#Max98 fix 0.38
import sys, os, os.path, glob, copy, errno
import wx
from random import Random
from types import *
from tempfile import mkstemp
from logger import log
import ogre.renderer.OGRE as ogre
from settingsManager import rorSettings 


hardcoded = {
			'odef':{
					# harcoded events on odef files
					'event':{
							  # event shopboat (marina) need a sufix of "sale" on terrn file, and unique name
							   'shopboat' : 'sale',
							   'shoptruck': 'shop',
							   'shopplane': 'sale',
							   'repair'   : 'repair',
							   'shopextension':'sale',
							   # well this is not an event, but it works at the same way
							   'dynamicdraw':'sign' 
							 },
					
					# availables triggers 
					'trigger':['avatar', 'truck', 'airplane'],
					
					
					# harcoded standard frictions
					'stdfriction':['concrete', 'asphalt', 'gravel', 'rock', 'ice', 'snow', 'metal', 'grass', 'sand']
					},
			
			
			# prefix used before a spawning object
			'terrain':{
					   'objecttype':{'.truck'   : 'truck',
									 '.airplane': 'truck',
									 '.fixed'   : 'machine',
									 '.load'	: 'load',
									 '.boat'	: 'boat',
									 '.trailer' : 'load',
									 '.odef'	: '',
									 '.car'	    : 'truck'
							   
							  		}
					   
					   },
					
			'ingamemap':['< None >', 'farm', 'missing', 'observatory', 'other', 'racestart', 'village']
			}







#list of strings with all ResourceGroups created.
# when loading .splines files I need to know path of the terrain
resourceGroupNames = {}  # { groupname as string : path added as string}

#files to be deleted when closing (terrain cfg file without custom materials)
deletefiles = []







def ShowOnAbout(event=None):
	dlg = wx.MessageDialog(None, "RoR Toolkit version 0.36 \nAuthors: Thomas, Aperion, Lepes",
						"About This", wx.OK | wx.ICON_INFORMATION)
	dlg.ShowModal()
	dlg.Destroy()


uniqueIDs = []
def randomID(num_bits=64):
	global uniqueIDs
	"""Return a string representing a bitfield num_bits long.
	Maximum artbitrarily set to 1025"""

	if num_bits < 1:
		raise RuntimeError, \
			"randomID called with negative (or zero) number of bits"
	if num_bits > 1024:
		raise RuntimeError, \
			"randomID called with too many bits (> 1024)"

	# create a num_bits string from random import Random
	rnd = Random()
	tmp_id = 0L
	for i in range(0, num_bits):
		tmp_id += long(rnd.randint(0, 1)) << i
	#rof

	# The 2: removes the '0x' and :-1 removes the L
	rnd_id = hex(tmp_id)[2:-1]

	# this ensure that all ids are unique
	if rnd_id in uniqueIDs:
		rnd_id = randomID(num_bits)
	else:
		uniqueIDs.append(rnd_id)

	return rnd_id

def readResourceConfig():
	from settingsManager import rorSettings
	normalResources = []
	zipResources = []
	
	if rorSettings().onlyParseTrucks:
		normalResources.append(os.path.join(rorSettings().rorHomeFolder, 'terrains'))
		normalResources.append(os.path.join(rorSettings().rorHomeFolder, 'vehicles'))
		zipResources.append(os.path.join(rorSettings().rorFolder, 'resources'))
		return (normalResources, zipResources)
	 
	log().debug("reading main resource: %s" % (rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ['resources.cfg'], True)))
	f = open(rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ['resources.cfg'], True), 'r')
	lines = f.readlines()
	f.close()
	isZip = False
	basePath = ""
	for line in lines:
		try:
			if '#' in line:
				continue
			# all lines readed after [RoR] section will use 
			# RoR folder on program files.
			elif line.strip() == '[zipRoR]' :
				isZip = True
				basePath = rorSettings().rorFolder
			elif line.strip() == '[zipRoRHome]':
				isZip = True
				basePath = rorSettings().rorHomeFolder
			elif line.strip() == '[folderRoR]':
				isZip = False
				basePath = rorSettings().rorFolder
			
			elif line.strip() == '[folderRoRHome]':
				isZip = False
				basePath = rorSettings().rorHomeFolder
			
			elif line[:11] == 'FileSystem=':
				dir = line[11:].strip()
				dirname = dir.replace('/', '\\')
				path = os.path.join(basePath, dirname)
				log().info("adding resource: %s isZip: %s" % (path, str(isZip)))
				if isZip:
					zipResources.append(path)
				else:
					normalResources.append(path)
		except:
			pass
	return (normalResources, zipResources)

_loaded = False	
def initResources():
	global _loaded
	if _loaded:
		return
	counter = 1
	
	# aabb offset setup to zero
	ogre.MeshManager.getSingleton().setBoundsPaddingFactor(0.0)

	log().debug("init Resources")
	#ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
	media = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media"])
	mat = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media", "materials"])
	models = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media", "models"])
	overlay = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media", "overlay"])
#	etm = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media", "ET"])

	ogre.ResourceGroupManager.getSingleton().addResourceLocation(mat, "FileSystem", "ToolkitBase", False)
	ogre.ResourceGroupManager.getSingleton().addResourceLocation(models, "FileSystem", "ToolkitBase", False)
	ogre.ResourceGroupManager.getSingleton().addResourceLocation(overlay, "FileSystem", "ToolkitBase", False)
#	ogre.ResourceGroupManager.getSingleton().addResourceLocation(etm, "FileSystem", "ToolkitBase", False)
	ogre.ResourceGroupManager.getSingleton().initialiseResourceGroup("ToolkitBase")	
	resourceGroupNames["ToolkitBase"] = None #multiples paths
	
	(normalResources, zipResources) = readResourceConfig()
	# only init things in the main window, not in shared ones!
	# setup resources
	
	for r in zipResources:
		files = glob.glob(os.path.join(r, "*.zip"))
		for file in files:
			try:
				if Ignore(file): 
					continue
				groupName = "General-%d" % counter
				ogre.ResourceGroupManager.getSingleton().addResourceLocation(file, "Zip", groupName, False)
				counter += 1
				resourceGroupNames[groupName] = file
				ogre.ResourceGroupManager.getSingleton().initialiseResourceGroup(groupName)
			except:
				log().debug("error adding or initialising Zip Resource group %s of file %s" % (groupName, file))
				continue
		
	# normalResources are uncompressed folders and may have subfolders with maps/vehicles
	# only first level of subfolders is scanned
	for r in normalResources:
		subfolder = os.listdir(r)
		for s in subfolder:
			try:
				fullname = os.path.join(r, s) 
				#print 'adding normal resource: ' + fullname
				if os.path.isdir(fullname):
					groupName = "General-%d" % counter
					ogre.ResourceGroupManager.getSingleton().addResourceLocation(fullname, "FileSystem", groupName, False)
					counter += 1
					resourceGroupNames[groupName] = fullname
					ogre.ResourceGroupManager.getSingleton().initialiseResourceGroup(groupName)
			except:
				log().debug("error adding or initialising Zip Resource group %s of file %s" % (groupName, file))
				
	log().info("loaded %d all resource Groups" % counter)
	_loaded = True
	
def loadResourceFile(filename):
	content = []
	group = ogreGroupFor(filename)
	if group != "":
		try:
			ds = ogre.ResourceGroupManager.getSingleton().openResource(filename, group, True);
		except Exception, err:
			log().error("Resource file %s not loaded" % filename)
			log().error(str(err))
		else:
			while not ds.eof():
				line = copy.copy(ds.getLine())
				content.append(line)
			#ds.close() don't close
	return content

def openConfigFile(filename=""):
	group = ogreGroupFor(filename)
	if group != "":
		try:
			ds = ogre.ResourceGroupManager.getSingleton().openResource(filename, group);
		except Exception, err:
			log().error("Resource file %s not loaded" % filename)
			log().error(str(err))
	
		cfg = ogre.ConfigFile()
		cfg.load(ds)
	
		#return a ogre.ConfigFile
		return cfg

def disableCustomMaterial(cfgfile):
	""" ogre doesn't have any way (at least documented) for modifying on the fly the cfg file
	so... we make a copy :-(
	"""
	fd, fullpath = mkstemp()
	lines = loadResourceFile(cfgfile)
	for i in range(len(lines)):
		if lines[i].find('CustomMaterialName') == -1:
			os.write(fd, lines[i] + '\n')
	os.close(fd)
	deletefiles.append(fullpath)
	return fullpath
	
def deleteFileList():
	for i in range(len(deletefiles)):
		os.remove(deletefiles[i])

def ogreGroupFor(filename=""):
	try:
	   group = ogre.ResourceGroupManager.getSingleton().findGroupContainingResource (filename)
	except:
		log().debug('group for "%s" not found' % filename) 
		group = ""
	return group

def loadResourceLine(filename, Line=0):
	""" return a single line of the filename """
	try:
		group = ogre.ResourceGroupManager.getSingleton().findGroupContainingResource (filename)
	except:
		log().debug("group for %s not found" % filename) 
		group = ""
	
	if group != "":
		try:
			ds = ogre.ResourceGroupManager.getSingleton().openResource(filename, group);
		except Exception, err:
			log().error("Resource file %s not loaded" % filename)
			log().error(str(err))
		cont = 0
		while not ds.eof() and cont < Line:
			cont += 1
		line = copy.copy(ds.getLine())
		#ds.close() don't close
	return line
	
def getPlatform():
	if sys.platform in ['linux', 'linux2']:
		return 'linux'
	elif sys.platform in ['win32', 'win64']:
		return 'windows'
	return 'unkown'

def checkRoRDirectory(fpath=None):
	""" Return True if RoR.exe is found physically in disk 
	"""
	 
	rorexecutable = ''
	if getPlatform() == 'linux':
		rorexecutable = "RoR.bin"
	elif getPlatform() == 'windows':
		rorexecutable = "RoR.exe"

	if fpath is None:
		from settingsManager import  rorSettings
		fpath = rorSettings().rorFolder
	fpath = os.path.join(fpath, rorexecutable)
	#log().info(fpath)
	return os.path.isfile(fpath)

def Ignore(filename):
	ignorelist = ['overlays.zip']
	for t in ignorelist:
		if filename.find(t) > -1:
			log().debug("found a file to ignore: %s" % filename)
			return True
	return False
	
def list_has_key(listOfDict, keyToSearch=''):
	""" search for a key of the dict iterating over the list
	    return -1 if not found, otherwise it return the index of the list
	    where the dictionary has the key searched
	"""
	try:
		if not isinstance(listOfDict, ListType): 
			raise Exception("parameter of type list expected")
		if len(listOfDict) > 0:
			for i in range(len(listOfDict)):
				if isinstance(listOfDict[i], DictType):
					if listOfDict[i].has_key(keyToSearch):
						return i
				else: raise Exception("this list has not dictionaries inside ")
	except:
		raise
	return - 1
def list_has_value(listOfDict, keyToSearch='', value=None):
	""" search if the value is in the list of Dictionary
	
	return -1 or the list index where it was found
	
	"""
	
	idx = list_has_key(listOfDict, keyToSearch)
	if idx == -1: return None
	for i in range(idx, len(listOfDict)):
		if listOfDict[i].has_key(keyToSearch):
			if value is None:
				if listOfDict[i][keyToSearch] is None: return i
			else:
				if listOfDict[i][keyToSearch] == value : return i
	return - 1

def showInfo(title, text):
	import roreditor.RoRScrolledText
	dlg = roreditor.RoRScrolledText.scrolledText(None, title, text)
	dlg.Show()
	
def pause(text="pause"):
	dlg = wx.MessageDialog(rorSettings().mainApp, text, "pause", 0)
	dlg.ShowModal()
	dlg.Destroy()
	
def getBitmap(title):
	""" get The image that represent the toolbar button glyph
	- replace spaces by underscore
	- extension  .png
	
	return wx.Bitmap
	"""
	imgfile = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ['media', 'gui', title.replace(" ", "_") + ".png"], True)
	print "image to load for toolbar labeled %s " % imgfile
	if os.path.isfile(imgfile):
		return wx.Bitmap(imgfile, wx.BITMAP_TYPE_PNG)
	else:
		return wx.Bitmap(rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ['media', 'gui', "blank.png"], True))
