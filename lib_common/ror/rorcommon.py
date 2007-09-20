import sys, os, os.path
import wx
from random import Random
from logger import log

def ShowOnAbout(event = None):
	rev = ""
	try:
		import ror.svn
		rev = str(ror.svn.getRevision())
	except:
		pass

	dlg = wx.MessageDialog(None, "RoR Toolkit revision %s\nAuthors: Aperion, Thomas" % rev,
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

