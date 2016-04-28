#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx 
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *

class wxOgreWindow(wx.PyWindow): 
	def __init__(self, parent, ID, name, size=wx.Size(200, 200), **kwargs): 
		"""
		@param parent: The parent wx Window
		@param size: the minimal window size
		@param kwargs: any other wx arguments
		@return: none
		"""
		wx.PyWindow.__init__(self, parent, ID, size=size, **kwargs) 
		self.parent = parent 
 
		#Event bindings 
		self.Bind(wx.EVT_CLOSE, 			self._OnCloseWindow) 
		self.Bind(wx.EVT_ERASE_BACKGROUND, self._OnEraseBackground) 

		# only_a_ptr, 02/2016: Only the first wx.PyWindow to register for this event
		#                      will receive notifications
		#                      Observed on Windows 10, x64, OpenGL renderer, PyOGRE 1.7.1
		self.Bind(wx.EVT_SIZE, self._OnSize) 

		#Ogre Initialisation 
		#self.ogreRoot = getOgreManager().getRoot()

		# create a new RenderWindow
		self.renderWindowName, self.renderWindow = getOgreManager().createRenderWindow(self, name , size[0], size[1], False, self.GetHandle())
		self.renderWindow.active = True
		
		try:
			if not self.sceneManager is None:
				pass
		except:
			self.sceneManager = None
		
		self.initialize_scene() 
		self.SetFocus()
	
	def _OnSize(self, event):
		"""
		Is called when the ogre Window is getting resized
		@param event: the sizing event
		@return: none
		"""
		try:
			self.renderWindow.windowMovedOrResized()
			event.Skip()
		except:
			pass

	def _OnEraseBackground(self, event): 
		"""
		overwrite standart background drawing routing with empty one
		@param event: the draw event
		@return: none
		"""
		# Do nothing, to avoid flashing on MSW. 
		pass 

	def _OnCloseWindow(self, event): 
		"""
		called when the ogre window gets closed
		@param event: the closing event
		@return: none
		"""
		self.Destroy() 

	def AcceptsFocus(self): 
		"""
		this window may accept keyboard focus
		"""
		return True 
	
	def initialize_scene(self): 
		"""
		default, base function, that has to be overwritten in the inherited class. It gets called after create the window, and should select a scenemanger.
		@return: none
		"""
		pass

	def on_frame_started(self): 
		"""
		default, base function, that has to be overwritten in the inherited class. gets called before rendering a frame.
		@return: none
		"""
		return 
	
	def on_frame_ended(self): 
		"""
		default, base function, that has to be overwritten in the inherited class. gets called after rendering a frame.
		@return: none
		"""
		return 

	def showOverlay(self, name, bshow=True, forceUpdate=False):
		""" show or hide an overlay defined in .overlay file 
		name - string, overlay name 
		bshow - boolean, True for showing, False for hidding.
		forceUpdate - boolean, force RenderWindow to update inmediatly
		"""
		om = ogre.OverlayManager
		singl = om.getSingleton()
		
		overlay = ogre.OverlayManager.getSingleton().getByName(name)
		if not overlay is None:
			if bshow:
				overlay.show()
			else:
				overlay.hide()
		else: log().debug('overlay with name "%s" not found on OverlayManager' % name)
		if forceUpdate:
			self.renderWindow.update()
		return (overlay is not None)

	def createFrameListener(self):
		"""Creates the FrameListener."""
		self.frameListener = RoRFrameListener(self.renderWindow, self.camera, OnFrameStarted=self.on_frame_started)
#		self.frameListener.showDebugOverlay(True)
		getOgreManager().getRoot().addFrameListener(self.frameListener)

	def Destroy(self):
#		del self.frameListener
#		getOgreManager().removeRenderWindow(self)
		if hasattr(self, "sceneManager"):
		 	if self.sceneManager is not None:
					self.sceneManager.clearScene()
					self.renderWindow.removeAllViewports()
					self.sceneManager.destroyAllCameras()
					getOgreManager().destroySceneManager(self.sceneManager)
	
class wxOgre3D(wxOgreWindow):
	""" wxOgreWindow with some utilities routines
	    to easy create nodes, entities, boxes, etc
	"""
	def __init__(self, parent, ID, name, size=wx.Size(200, 200), **kwargs):		
		wxOgreWindow.__init__(self, parent, ID, name, size, **kwargs)

	def mk_scene_node(self, strName,
					doc=""" Scene Manager New Node:
					Create a new SceneNode with given Name """):
		n = self.sceneManager.getRootSceneNode().createChildSceneNode(strName)
		return n
		
