#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
from wxogre.OgreManager import *
from ror.RoROgreWindow import *
from ror.rorcommon import *
from subprocess import Popen
import subprocess

from ror.logger import log
from ror.settingsManager import *
import roreditor.MainFrame
import roreditor.ShapedControls 

import wx, os, os.path

RENDERSYSTEMS = ['OpenGL', 'DirectX9']

DIRECTXLINE = "Plugin=RenderSystem_Direct3D9.dll"
OPENGLLINE = "Plugin=RenderSystem_GL.dll"
SPLASHIMAGE = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media","gui", "splash.bmp"],True)


class ImagePanel(wx.Panel):
	""" class Panel1 creates a panel with an image on it, inherits wx.Panel """
	def __init__(self, parent, id, imageFile):
		wx.Panel.__init__(self, parent, id)
		try:
			jpg1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			wx.StaticBitmap(self, wx.ID_ANY, jpg1, (0, 0), (jpg1.GetWidth(), jpg1.GetHeight()))
		except IOError:
			log().error("Image file %s not found" % imageFile)
			raise SystemExit


class SettingsDialog(wx.Dialog):
	rordir = None
	def __init__(self, *args, **kwds):
		log().debug("starter is being created")
		kwds["style"] = wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetBackgroundColour(roreditor.ShapedControls.skinBackColor)
		grid = wx.GridBagSizer(5,5) 
		grid.SetEmptyCellSize(wx.Size(230,20))
		r = 0
		c = 0

		self.image = ImagePanel(self, wx.ID_ANY, SPLASHIMAGE)
		grid.Add(self.image, pos = wx.GBPosition(r,c), span = wx.GBSpan(3, 5))

		r += 4
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 1: ", size = (80, 60), style = wx.ALIGN_CENTER)
		#dummy.SetForegroundColour(wx.BLUE)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		
		c += 1
		self.lblRoRDir = wx.StaticText(self, wx.ID_ANY, "Please select folder where Rigs of Rods is installed:", size = (210, 40), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
		grid.Add(self.lblRoRDir, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		
		c += 1
		self.btnSelectRoRDir = wx.Button(self, wx.ID_ANY, "Select RoR Folder", size = wx.Size(100,20))
		grid.Add(self.btnSelectRoRDir, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		self.Bind(wx.EVT_BUTTON, self.OnSelectRoRDir, self.btnSelectRoRDir)

		#self.btnStartRoR = wx.Button(self.panel, wx.ID_ANY, "Start RoR")
		#self.Bind(wx.EVT_BUTTON, self.OnStartRoR, self.btnStartRoR)

		r +=1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 2: ", size = (80, 60), style = wx.ALIGN_CENTER)
		#dummy.SetForegroundColour(wx.BLUE)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		c += 1
		l = wx.StaticText(self, wx.ID_ANY, "Please select Graphic Renderer you want to use:", size = (210, 40))
		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1)) 
		

		c +=1
		self.cbbRenderEngine = wx.ComboBox(self, wx.ID_ANY, RENDERSYSTEMS[1], size = wx.Size(100,20), style=wx.CB_READONLY, choices=RENDERSYSTEMS)
		self.Bind(wx.EVT_COMBOBOX, self.OnSelectRenderer, self.cbbRenderEngine)
		grid.Add(self.cbbRenderEngine, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

#		r += 1
#		c = 0
#		l = wx.StaticText(self, wx.ID_ANY, "Once the button bellow will be enabled, you can start RoR Toolkit.", size = (120, 40), style = wx.ALIGN_CENTRE | wx.ST_NO_AUTORESIZE)
#		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 2)) 
		
		r +=1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 3: ", size = (80, 60), style = wx.ALIGN_CENTER)
		#dummy.SetForegroundColour(wx.BLUE)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		c += 1
		l = wx.StaticText(self, wx.ID_ANY, "Start Editor button will remain Disable until you complete previous steps.", size = (210, 40))
		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1)) 

		c += 1
		self.btnStartTerrainEditor = wx.Button(self, wx.ID_ANY, "Start Editor", size = wx.Size(100,20))
		self.Bind(wx.EVT_BUTTON, self.OnTerrainEditor, self.btnStartTerrainEditor)
		grid.Add(self.btnStartTerrainEditor , pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		#self.btnBugReport = wx.Button(self.panel, wx.ID_ANY, "Report a Bug")
		#self.Bind(wx.EVT_BUTTON, self.OnBugReport, self.btnBugReport)
		#if sys.platform != 'win32':
		#self.btnBugReport.Enable(False)

		#self.btnUpdate = wx.Button(self.panel, wx.ID_ANY, "Update")
		#self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.btnUpdate)
		#self.btnUpdate.Enable(False)

		#self.btnDepGraph = wx.Button(self.panel, wx.ID_ANY, "Dependency Graph")
		#self.Bind(wx.EVT_BUTTON, self.OnDepGraph, self.btnDepGraph)
		#if sys.platform != 'win32':
		#	self.btnDepGraph.Enable(False)

		#self.btnModUninstaller = wx.Button(self.panel, wx.ID_ANY, "Mod Uninstaller")
		#self.Bind(wx.EVT_BUTTON, self.OnModUninstaller, self.btnModUninstaller)

		#self.btnRepClient = wx.Button(self.panel, wx.ID_ANY, "Repository Client")
		#self.Bind(wx.EVT_BUTTON, self.OnRepClient, self.btnRepClient)

		r += 1
		c = 3
		self.btnExit = wx.Button(self, wx.ID_CANCEL, "Exit", size = wx.Size(90,20))
		self.Bind(wx.EVT_BUTTON, self.OnAbort, self.btnExit)
		grid.Add(self.btnExit, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1)) 

		self.SetEscapeId(self.btnExit.GetId())
		self.SetAffirmativeId(self.btnStartTerrainEditor.GetId())
		self.SetSizerAndFit(grid)
		self.SetAutoLayout(True)
		self.rordir = rorSettings().rorFolder
		self.checkRoRDir(self.rordir)

		#print self.rordir

		self.displayRoRDir()
		self.__set_properties()

		self.renderSystem = 1
		self.updateRenderer()

	def OnRepClient(self, event=None):
		import repomanager
		repomanager.main()

	def displayRoRDir(self):
		if self.rordir == "":
			#self.btnStartRoR.Enable(False)
			#self.btnStartTruckEditor.Enable(False)
			self.btnStartTerrainEditor.Enable(False)
			#self.btnBugReport.Enable(False)
			self.lblRoRDir.SetLabel("Please select where Rigs of Rods was Installed on your computer:")
		else:
			#self.btnStartRoR.Enable(True)
			#self.btnStartTruckEditor.Enable(True)
			self.btnStartTerrainEditor.Enable(True)
			#self.btnBugReport.Enable(True)
			self.lblRoRDir.SetLabel("Selected Rigs of Rods Folder: " + self.rordir)

	def OnSelectRenderer(self, id=None, func=None):
		self.renderSystem = self.cbbRenderEngine.GetCurrentSelection()
		self.updateRenderer()

	def updateRenderer(self):
		log().debug("updateRenderer: retrieving plugins_windows.cfg")
		filename = os.path.join(os.getcwd(), "plugins_windows.cfg")
		f=open(filename, 'r')
		content = f.readlines()
		f.close()
		log().info("selected rendersystem: %s" % RENDERSYSTEMS[self.renderSystem])
		for i in range(0, len(content)):
			if content[i].find(DIRECTXLINE) >= 0:
				if self.renderSystem == 1:
					content[i] = DIRECTXLINE+"\n"
				else:
					content[i] = "#"+DIRECTXLINE+"\n"
			elif content[i].find(OPENGLLINE) >= 0:
				if self.renderSystem == 0:
					content[i] = OPENGLLINE+"\n"
				else:
					content[i] = "#"+OPENGLLINE+"\n"

		f=open(filename, 'w')
		f.writelines(content)
		f.close()

	def OnDepGraph(self, event=None):
		import ror.depchecker
		ror.depchecker.RoRDepChecker(self.rordir, "all", "")
		file = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "graphs", "alldependencies.png"))
		#print file
		if os.path.isfile(file):
			dlg = wx.MessageDialog(self, "Graph successfully created:\n"+file, "Info", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			cmd = file
			p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE, stdout = subprocess.PIPE)
		else:
			dlg = wx.MessageDialog(self, "Graph creation failed :(", "Info", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()

	def OnModUninstaller(self, event=None):
		import modgui
		gui = modgui.ModGUI(None, -1, "")
		gui.Show()
		del gui

	#def OnUpdate(self, event=None):
		#import svngui
		#gui = svngui.svnUpdate()
		#del gui

	#def checkForUpdate(self):
	#	import svn
	#	return svn.checkForUpdate()


	def OnStartRoR(self, event=None):
		rorexecutable = ''
		if sys.platform in ['linux', 'linux2']:
			rorexecutable = "RoR"
		elif sys.platform in ['win32']:
			rorexecutable = "RoR.exe"
		
		try:
			path = os.path.join(self.rordir, rorexecutable)
			log().info("starting RoR: %s" % path)
			p = Popen(path, shell = False, cwd = self.rordir)
			#sts = os.waitpid(p.pid, 0)
		except Exception, e:
			log().exception(str(e))

	# def OnTruckEditor(self, event=None):
		# try:
			# import rortruckeditor.MainFrame
			# self.Close()
			# log().info("starting Truckeditor")
			# app = rortruckeditor.MainFrame.startApp()
			# del app
		# except Exception, e:
			# log().exception(str(e))

	def OnBugReport(self, event=None):
		try:
			if self.checkForUpdate():
				dlg = wx.MessageDialog(self, "Update Available!\nPlease update prior submitting a BugReport!", "Info", wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
				#self.btnBugReport.Enable(False)
				return

			log().info("starting bugreporter")
			import ror.bugreport
			ror.bugreport.showBugReportFrame()
		except Exception, e:
			log().exception(str(e))

	def OnTerrainEditor(self, event=None):
		event.Skip()

	def checkRoRDir(self, fn):
		return checkRoRDirectory(fn)

	def OnSelectRoRDir(self, event=None):
		dialog = wx.DirDialog(self, "Choose RoR Directory", "")
		res = dialog.ShowModal()
		if res == wx.ID_OK:
			newpath = dialog.GetPath()
			if not self.checkRoRDir(newpath):
				return

			# no need to escape here!
			#newpath = newpath.replace(" ", "\ ")
			self.rordir = newpath
			rorSettings().setSetting("RigsOfRods", "BasePath", newpath)
			rorSettings().rorFolder = newpath
			log().debug("starter: saved BasePath")
			self.displayRoRDir()

	def OnAbort(self, event=None):
		log().debug('starter finalize RoR Toolkit')
		sys.exit(0)

	def __set_properties(self):
		self.SetTitle(rorSettings().title)

def startApp(MainApp):
# Lepes: No new application needed, just a ShowModal() Frame
#	MainApp = wx.PySimpleApp()
#	wx.InitAllImageHandlers() #you may or may not need this
	myFrame = SettingsDialog(MainApp, -1, "")

	# add icon to the window
	icon = wx.Icon("ror.ico",wx.BITMAP_TYPE_ICO)
	myFrame.SetIcon(icon)
	return myFrame
