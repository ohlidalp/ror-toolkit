import sys, os, os.path, glob, copy
import wx
from random import Random
from logger import log
import ogre.renderer.OGRE as ogre 

def ShowOnAbout(event = None):
	dlg = wx.MessageDialog(None, "RoR Toolkit version 0.34 %s\nAuthors: Thomas, Aperion",
						"About This", wx.OK | wx.ICON_INFORMATION)
	dlg.ShowModal()
	dlg.Destroy()


uniqueIDs = []
def randomID(num_bits=64):
	global uniqueIDs
	"""Return a string representing a bitfield num_bits long.
	Maximum artbitrarily set to 1025"""

	if num_bits < 1:
		raise RuntimeError,\
			"randomID called with negative (or zero) number of bits"
	if num_bits > 1024:
		raise RuntimeError,\
			"randomID called with too many bits (> 1024)"

	# create a num_bits string from random import Random
	rnd = Random()
	tmp_id = 0L
	for i in range(0, num_bits):
		tmp_id += long(rnd.randint(0,1)) << i
	#rof

	# The 2: removes the '0x' and :-1 removes the L
	rnd_id = hex(tmp_id)[2:-1]

	# this ensure that all ids are unique
	if rnd_id in uniqueIDs:
		rnd_id = randomID(num_bits)
	else:
		uniqueIDs.append(rnd_id)

	return rnd_id

def readResourceConfig(rordir):
	f = open(os.path.join(rordir, 'resources.cfg'), 'r')
	lines = f.readlines()
	f.close()
	normalResources = []
	zipResources = []
	isZip=False
	for line in lines:
		if line.strip() == '[Packs]' or line.strip() == '[InternalPacks]':
			isZip=True
		elif line[0] == '[':
			isZip=False
		#print line, isZip
		
		if line[:11] == 'FileSystem=':
			dir=line[11:].strip()
			dirname = dir.replace('/', '\\')
			path = os.path.join(rordir, dirname)
			if isZip:
				zipResources.append(path)
			else:
				normalResources.append(path)
	return (normalResources, zipResources)

	
def initResources(rordir):
	(normalResources, zipResources) = readResourceConfig(rordir)
	# only init things in the main window, not in shared ones!
	# setup resources
	for r in normalResources:
		print 'adding normal resource: ' + r
		ogre.ResourceGroupManager.getSingleton().addResourceLocation(r, "FileSystem", "General", False)

	for r in zipResources:
		files = glob.glob(os.path.join(r, "*.zip"))
		for file in files:
			print 'adding zip resource: ' + file
			ogre.ResourceGroupManager.getSingleton().addResourceLocation(file, "Zip", "General", False)
	
	#ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
	ogre.ResourceGroupManager.getSingleton().addResourceLocation("media", "FileSystem", "General", False)
	ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials", "FileSystem", "General", False)
	ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/models", "FileSystem", "General", False)
	
	try:
		ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()
	except Exception, e:
		print str(e)
	
def loadResourceFile(filename):
	content = []
	ds=ogre.ResourceGroupManager.getSingleton().openResource(filename, "General");
	ec=0
	while True:
		line = copy.copy(ds.getLine())
		#print line, ec
		if line.strip() == "":
			ec+=1
		if ec > 50:
			break
		content.append(line)
	#ds.close()
	return content
	
def getPlatform():
	if sys.platform in ['linux', 'linux2']:
		return 'linux'
	elif sys.platform in ['win32']:
		return 'windows'
	return 'unkown'

def checkRoRDirectory(fpath=None):
	rorexecutable = ''
	if getPlatform() == 'linux':
		rorexecutable = "RoR.bin"
	elif getPlatform() == 'windows':
		rorexecutable = "RoR.exe"

	if fpath is None:
		import settingsManager
		fpath = settingsManager.getSettingsManager().getSetting("RigsOfRods", "BasePath")
	fpath = os.path.join(fpath, rorexecutable)
	#log().info(fpath)
	return os.path.isfile(fpath)

