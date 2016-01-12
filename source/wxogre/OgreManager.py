#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys
import wx
import ogre.renderer.OGRE as ogre
from ror.logger import log

from ror.settingsManager import rorSettings
from ror.rorcommon import *


# singleton implementation of OgreManager
_ogremanager = None
def getOgreManager():
	global _ogremanager
	if _ogremanager is None:
		_ogremanager = OgreManager()
	return _ogremanager


class OgreManager(object):


	def restart(self):
		self.ogreRoot.shutdown()
		self.init()

	def __init__(self):
		self.renderWindows = {}
		self.init()
	
	def __del__(self):
#		del self.renderWindows
#		self.currentLog.removeListener(self.myLog)
		pass
	
	def init(self):
		renderWindows = {}
		#Root creation
		pluginsfile = 'plugins.cfg'
		if sys.platform in ['linux', 'linux2']:
			pluginsfile = 'plugins_linux.cfg'
		elif sys.platform in ['win32']:
			pluginsfile = 'plugins_windows.cfg'

#		self.logMgr = ogre.LogManager()
#		self.currentLog = ogre.LogManager.getSingleton().createLog("ogre.log" , True, False, False)
#		self.myLog = MyLog()
#		self.currentLog.addListener ( self.myLog )
#		ogre.LogManager.getSingleton().setDefaultLog(currentLog)
		plugin = self.getConfigPath(pluginsfile)
		ogrecfg = self.getConfigPath('ogre.cfg')
		logfolder = rorSettings().concatToToolkitHomeFolder(["logs", "Ogre.log"], True)
		self.ogreRoot = ogre.Root(plugin, ogrecfg, logfolder)

		if not self.tryDetectRenderer():
			self.ogreRoot.showConfigDialog()
		self.ogreRoot.initialise(False)

	def tryDetectRenderer(self):
		for rs in self.ogreRoot.getAvailableRenderers():
			try :
				rs.setConfigOption("Full Screen", "No")
				rs.setConfigOption("Video Mode", "800 x 600 @ 32-bit colour")
				self.ogreRoot.setRenderSystem(rs)
				log().info("successfully autodeteced renderer : %s" % rs.getName())
				return True
			except:
				log().info("not able to auto-detect renderer! showing ogre config dialog instead")
				return False

	def getRoot(self):
		return self.ogreRoot

	def getConfigPath(self, filename):
		"""Return the absolute path to a valid config file."""
		import sys
		import os
		import os.path

		paths = [os.path.join(os.getcwd(), filename),
				os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)]

		for path in paths:
			if os.path.exists(path):
				print path
				return path

		log().warning("\n"
			"** Unable to locate a suitable " + filename + " file.\n"
			"** Please check your ogre installation and copy a\n"
			"** working plugins.cfg file to the current directory.\n\n")
		#raise ogre.Exception(0, "can't locate the '%s' file" % filename, "")

	def createRenderWindow(self, wxOgrewin, name, width, height, fullscreen, handle):
		renderParameters = ogre.NameValuePairList()
		#TODO: For some reason passing renderParameters causes the renderer not to start, passing Null is a work around
		
		if getPlatform() == 'windows':
			renderParameters['externalWindowHandle'] = str(handle)
		elif getPlatform() == 'linux':
			renderParameters['externalWindowHandle'] = 0
		finalname = "%s_%s" % (name , str(randomID()))
#		print "wxOgreWin %s name %s" %( wxOgrewin, name)
		renderWindow = self.ogreRoot.createRenderWindow(finalname, width, height, fullscreen, renderParameters)
		#renderWindow.active = True
		self.renderWindows[wxOgrewin] = renderWindow
		return finalname, renderWindow

	def removeRenderWindow(self, wxOgrewin):
		self.ogreRoot.detachRenderTarget(self.renderWindows[wxOgrewin])
		del self.renderWindows[wxOgrewin]

	def startRendering(self):
		self.ogreRoot.startRendering()

	def RenderAll(self):
		for ogrewin in self.renderWindows.keys():
			try:
				ogrewin.OnFrameStarted()
			except ogre.OgreException, e:
				log().debug('fail to render targetwindow %s' % ogrewin.renderWindowName)
				log().debug(str(e))
				continue

		try:
			self.ogreRoot.renderOneFrame()
		except ogre.OgreException, e:
			log().error('## EXCEPTION ## OgreManager.RenderAll()')
			log().error(str(e))
			sys.exit("## EXCEPTION ## OgreManager.RenderAll()")

		for ogrewin in self.renderWindows.keys():
			try:
				ogrewin.OnFrameEnded()
			except:
				continue

	def createSceneManager(self, type):
		return self.ogreRoot.createSceneManager(type, "SceneManager" + str(randomID()))

	def destroySceneManager(self, sm):
		return self.ogreRoot.destroySceneManager(sm)
			
