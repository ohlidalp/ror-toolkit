#from src.lib_windows.wx.lib.agw.flatmenu import FlatToolbarItem
import sys, os, os.path, ConfigParser

import wx.lib.inspection
import wx.lib.mixins.inspection

#fancy menus
import wx.lib.agw.flatmenu as FM
from wx.lib.agw.artmanager import ArtManager, RendererBase, DCSaver
from wx.lib.agw.fmresources import ControlFocus, ControlPressed
from wx.lib.agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR
from FM_renderer import *

#ogre stuff
from wxogre.OgreManager import *
from ror.RoROgreWindow import *

from ror.logger import log
from ror.settingsManager import rorSettings
				
import ShapedControls 

from ror.rorcommon import *
from RoRTerrainOgreWindow import *
from RoRObjectPreviewOgreWindow import *
from RoRTerrainSelectedObjectOgreWindow import *
from RoRTerrainSelectedObjectTopOgreWindow import *
from RoROdefEditorOgreWindow import *
from RoRTruckOgreWindow import *
from RoRTruckUVOgreWindow import *
from RoRSkinSelection import *
from RoRTruckLinePanel import *



# GUI Tools:
from MainFrame_Tools_ObjectTree import *
from TruckPanel import *
from MainFrame_Tools import *
from MainFrame_Tools_ODefEditor import *
from MainFrame_Tools_ObjectInspector import ObjectInspector
from MainFrame_Tools_Preview import RoRPreviewCtrl
from MainFrame_Tools_MapOptions import MapOptionWindow
from MainFrame_Tools_RoadSystem import RoadSystemWindow
from MainFrame_Tools_Pivot import PivotControlWindow
from MainFrame_Tools_CameraPos import CameraWindow
from MainFrame_Tools_Race import Race
from ror.modgui import *
import RoRConstants	
import wx
import wx.grid
import wx.html
import wx.aui


import cStringIO
from subprocess import *

ID_OpenTerrainProject = wx.NewId()
ID_SaveTerrain = wx.NewId()
ID_SaveTerrainAs = wx.NewId()
ID_AddObject = wx.NewId()
ID_DeleteSelection = wx.NewId()
ID_CopySelection = wx.NewId()
ID_PasteSelection = wx.NewId()
ID_UndoAction = wx.NewId()
ID_RedoAction = wx.NewId()
ID_FindObject = wx.NewId()
ID_Quit = wx.NewId()

ID_ViewHelp = wx.NewId()

ID_CreatePerspective = wx.NewId()
ID_CopyPerspective = wx.NewId()

ID_Settings = wx.NewId()
ID_About = wx.NewId()
ID_FirstPerspective = ID_CreatePerspective + 1000
ID_StickTo02 = wx.NewId()
ID_StartRoR = wx.NewId()
ID_wxInspector = wx.NewId()
ID_hideCaptions = wx.NewId()
ID_ModTool = wx.NewId()
ID_selectSkin = wx.NewId()

class MainFrame(wx.Frame):
#		toolbuttons = [
#					{'caption': 'Object Tree', 'object': None, 'event':self.]
		def __init__(self, parent, id= -1, title="", pos=wx.DefaultPosition,
								 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | 
															wx.SUNKEN_BORDER | 
															wx.CLIP_CHILDREN):

				wx.Frame.__init__(self, parent, id, title, pos, size, style)

				import rortoolkit.resources
				import rortoolkit.app
				import ror.rorcommon
				import wxogre

				# Create application class
				# TODO: Application should manage MainFrame, not the other way around!!
				self.application = rortoolkit.app.Application()
				self.application.init_set_main_frame(self)

				self.lastFilenameUsed = ""
				# tell FrameManager to manage this frame		
				self._mgr = wx.aui.AuiManager()
				self._mgr.SetManagedWindow(self)
				self.SetIcon(wx.Icon('rortoolkit.ico', wx.BITMAP_TYPE_ICO))
				rorSettings().mainApp = self
				self._perspectives = []
				self.n = 0
				self.x = 0

				self.ConfigureSkin()
				# Lepes: move starter here since rorSettings needs a MainApp launched
				# before retrieving paths due wx.StandardPaths module
				if not ror.rorcommon.checkRoRDirectory():
					import ror.starter
					log().debug("First time Toolkit is running.")
					myFrame = ror.starter.startApp(self)
					myFrame.ShowModal()
					log().debug("Starter closed")
				
				if rorSettings().has_section("MainFrame"):
					self.SetDimensions(#int x, int y, int width, int height, int sizeFlags = wxSIZE_AUTO)  
										int(rorSettings().getSetting("MainFrame", "left")), \
										int(rorSettings().getSetting("MainFrame", "top")), \
										int(rorSettings().getSetting("MainFrame", "width")), \
										int(rorSettings().getSetting("MainFrame", "height"))\
								)
				else:
					self.SetDimensions(0, 0, 800, 600)
				self.newMyTheme = ArtManager.Get().AddMenuTheme(FM_MyRenderer())
				ArtManager.Get().SetMenuTheme(self.newMyTheme)

				# [File] menu
				file_menu = FM.FlatMenu()
				open_map_item = FM.FlatMenuItem(file_menu, ID_OpenTerrainProject, "Open terrain project", "", wx.ITEM_NORMAL)
				file_menu.AppendItem(open_map_item)
				file_menu.AppendItem(FM.FlatMenuItem(file_menu, wx.ID_EXIT, "Exit", "", wx.ITEM_NORMAL))

				self.managerInit()
				options_menu = FM.FlatMenu()
				options_menu.AppendItem(FM.FlatMenuItem(options_menu, ID_Settings, "GUI Settings Pane", "", wx.ITEM_NORMAL))
				if rorSettings().rorDebug: options_menu.AppendItem(FM.FlatMenuItem(options_menu, ID_ModTool, "mod Tool Dependences", wx.ITEM_NORMAL))
				if rorSettings().rorDebug: options_menu.AppendItem(FM.FlatMenuItem(options_menu, ID_wxInspector, "wx Widget Inspector", "", wx.ITEM_NORMAL))
				if rorSettings().rorDebug: options_menu.AppendItem(FM.FlatMenuItem(options_menu, ID_hideCaptions, "hide toolbar captions", "", wx.ITEM_NORMAL))
				options_menu.AppendItem(FM.FlatMenuItem(options_menu, ID_selectSkin, "select Skin", "", wx.ITEM_NORMAL))
				
				self._perspectives_menu = FM.FlatMenu()
				self._perspectives_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_CreatePerspective, "Create Perspective", "", wx.ITEM_NORMAL))
				#self._perspectives_menu.Append(ID_CopyPerspective, "Copy Perspective Data To Clipboard")
				self._perspectives_menu.AppendSeparator()
				self._perspectives_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_FirstPerspective + 0, "Default Startup", "", wx.ITEM_RADIO))
				self._perspectives_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_FirstPerspective + 1, "Terrain", "", wx.ITEM_RADIO))
				self._perspectives_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_FirstPerspective + 2, "ODef Editor", "", wx.ITEM_RADIO))
				self._perspectives_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_FirstPerspective + 3, "Truck Editor", "", wx.ITEM_RADIO))

				help_menu = FM.FlatMenu()
				help_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_About, "About...", "", wx.ITEM_NORMAL))
				help_menu.AppendItem(FM.FlatMenuItem(self._perspectives_menu, ID_ViewHelp, "View Help", "", wx.ITEM_NORMAL))
				

				# min size for the frame itself isn't completely done.
				# see the end up FrameManager::Update() for the test
				# code. For now, just hard code a frame minimum size
				self.SetMinSize(wx.Size(600, 400))
				self.SetTitle(rorSettings().title)
				
				# create some toolbars
				self.terraintoolbar = FM.FlatMenuBar(self, iconSize=32, spacer=5, options=FM_OPT_SHOW_TOOLBAR)
				self.terraintoolbar.Append(file_menu, "File")
				self.terraintoolbar.Append(options_menu, "Options")
				self.terraintoolbar.Append(self._perspectives_menu, "Perspectives")
				self.terraintoolbar.Append(help_menu, "Help")
				
#				self.hor_sizer.Add(self.terraintoolbar)
				self.Bind(wx.EVT_RIGHT_DOWN, self.Onterraintoolbar, self.terraintoolbar)

				self.statusbar = self.CreateStatusBar(4, 0, wx.ID_ANY, "mainstatusbar")
				self.statusbar.SetStatusWidths([300, 300, 300, 350])

				
#				self.terraintoolbar.SetToolBitmapSize(wx.Size(16,16))
#				self.terraintoolbar.AddLabelTool(ID_OpenTerrain, "Open Terrain", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
				self.terraintoolbar.AddTool(ID_SaveTerrain, "Save Terrain", wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE))
				self.terraintoolbar.AddTool(ID_SaveTerrainAs, "Save Terrain As", wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE_AS))
				self.terraintoolbar.AddSeparator()
#				self.terraintoolbar.AddLabelTool(ID_StickTo02, "Stick to 0.2 m",wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN),
#									shortHelp="Stick New Objects to 0.2 from ground")
#				self.terraintoolbar.AddLabelTool(ID_Inspector, "Object Inspector",wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN),
#									shortHelp="Stick New Objects to 0.2 from ground")				
				self.terraintoolbar.AddTool(ID_StartRoR, "Save && Start RoR", getBitmap("Save Start RoR"),
									shortHelp="Save Terrain and Start RoR loading this map")
				
#				self.terraintoolbar.AddSeparator()
#				self.terraintoolbar.EnableTool(ID_StartRoR, False)								
				 
				#self.terraintoolbar.AddTool(ID_AddObject, "Add Something", wx.ArtProvider_GetBitmap(wx.ART_NEW))
				#self.terraintoolbar.EnableTool(ID_AddObject, False)
				#self.terraintoolbar.AddTool(ID_DeleteSelection, "Delete Selection", wx.ArtProvider_GetBitmap(wx.ART_DELETE))
				#self.terraintoolbar.EnableTool(ID_DeleteSelection, False)
				#self.terraintoolbar.AddSeparator()		
				self.terraintoolbar.AddTool(ID_CopySelection, "Copy Selection", wx.ArtProvider_GetBitmap(wx.ART_COPY))
#				self.terraintoolbar.EnableTool(ID_CopySelection, False)
				self.terraintoolbar.AddTool(ID_PasteSelection, "Paste Selection", wx.ArtProvider_GetBitmap(wx.ART_PASTE))
#				self.terraintoolbar.EnableTool(ID_PasteSelection, False)
				#self.terraintoolbar.AddSeparator()		
				#self.terraintoolbar.AddTool(ID_UndoAction, "Undo last Action", wx.ArtProvider_GetBitmap(wx.ART_UNDO))
				#self.terraintoolbar.EnableTool(ID_UndoAction, False)
				#self.terraintoolbar.AddTool(ID_RedoAction, "Redo last Undo", wx.ArtProvider_GetBitmap(wx.ART_REDO))
				#self.terraintoolbar.EnableTool(ID_RedoAction, False)
				#self.terraintoolbar.AddSeparator()		
				self.terraintoolbar.AddTool(ID_FindObject, "go to...", wx.ArtProvider_GetBitmap(wx.ART_FIND), shortHelp="go to to some coordenates")
#				self.terraintoolbar.EnableTool(ID_FindObject, True)
				#self.terraintoolbar.AddSeparator()		
#				self.terraintoolbar.AddTool(ID_Quit, "Quit", wx.ArtProvider_GetBitmap(wx.ART_QUIT))

				self.terraintoolbar.PositionAUI(self._mgr)
				log().debug("creating shaped windows")
		
				#self.dummyOgreWindow = ObjectPreviewOgreWindow(self, "ogre3DDummyWindow")
				#self.dummyOgreWindow.Hide() 
				# add a bunch of panes
				# Lepes: Shaped window 
				self.RoadSystem = RoadSystemWindow(self, title="Road")
				self.RoadSystem.Show(False)
				self.RoadSystem.perspective = 1
#				self.Preview = RoRPreviewCtrl(self, 
#											  title = "Object Preview",
#											  pos = (self.GetScreenPosition().x,self.GetScreenPosition().y + shapedtop))
				self.race = Race(self, title="Manage Races")
#				self.PivotControls = PivotControlWindow(self,title = "Pivot Controls" pos = (self.GetScreenPosition().x,self.GetScreenPosition().y + shapedtop) )
#				self.PivotControls.Show(True)
#				self._mgr.AddPane(self.objectPreviewWindow, wx.aui.AuiPaneInfo().
#												  Name("object_preview").
#												  Caption("Object Preview").
#												  CenterPane().
#												  MinSize(wx.Size(200, 100)).
#												  CloseButton(True).
#												  MaximizeButton(False))

				self._mgr.AddPane(HelpPanel(self, self), wx.aui.AuiPaneInfo().
												  Name("help").
												  Caption("Help").
												  Dockable(False).
												  Float().
												  Hide().
												  CloseButton(True).
												  MaximizeButton(True))

				self._mgr.AddPane(SettingsPanel(self, self), wx.aui.AuiPaneInfo().
												  Name("settings").
												  Caption("Dock Manager Settings").
												  Dockable(False).
												  Float().
												  Fixed().
												  Hide().
												  CloseButton(True).
												  MaximizeButton(True))


				self.MapOptions = MapOptionWindow(self, title="Map Options")
				self.MapOptions.perspective = 1						  

				self.cameraBookmark = CameraWindow(self, title="Camera Bookmark")

				self.cameraBookmark.perspective = 1

				self.tbbuttons = [] #[ {'id' :ID, 'label': string, 'window' : ShapedWindow_instance} ]
				def add_toolbar_button(self, window):
					label = window.title
					window_id = wx.NewId()
					bitmap = getBitmap(label)
					buttonidx = self.terraintoolbar.AddTool(window_id, label, bitmap1=bitmap, bitmap2=bitmap, kind=wx.ITEM_CHECK)
					self.Bind(wx.EVT_MENU, self.on_toolbar_button_click, id=window_id)
					self.tbbuttons.append({'id' : window_id, 'label': label, 'window': window, 'perspective' : w.perspective, 'buttonidx': buttonidx})
					
				#create toolbarButtons for shaped windows
				# TODO: Don't rely on window iteration + isinstance(), use actual references!! ~ only_a_ptr 2016/02
				for w in wx.GetTopLevelWindows():
					if isinstance(w, ShapedWindow):
						add_toolbar_button(self, w)
						w.Hide()

				#  create the center pane(s)
				#Timer creation  (for rendering)
				self.ogreTimer = wx.Timer() 
				self.ogreTimer.SetOwner(self)
				self.Bind(wx.EVT_TIMER, self.onUpdateRender, self.ogreTimer)
				self.ogreTimer.Start(25)

				# Init OGRE
				wxogre.OgreManager.getOgreManager() # Inits singleton
				
				# the terrain editor ogre window
				# only_a_ptr, 02/2016: Must be the first 3D-rendering window created.
				#                      to receive window-resize events.
				#                      Observed on Windows 10, x64, OpenGL renderer, PyOGRE 1.7.1
				self.terrainOgreWin = RoRTerrainOgreWindow(self, wx.ID_ANY)
				self._mgr.AddPane(self.terrainOgreWin, wx.aui.AuiPaneInfo().Name("ogre_terrain_content").CenterPane().Hide())

				# Load essential media
				rortoolkit.resources.init()
				rortoolkit.resources.load_builtin_resources()
				rortoolkit.resources.scan_for_available_resources()

				self.terrainOgreWin.finalize_init() # Must be done after rortoolkit media were loaded

				# odef editor panels
				self.oddefEditorViewSettings = OdefViewPanel(self, title="Odef")
				self.oddefEditorViewSettings.perspective = 2

				self.truckEditorViewSettings = TruckViewPanel(self)
				self._mgr.AddPane(self.truckEditorViewSettings, wx.aui.AuiPaneInfo().
												  Name("truck_editor_view_settings").
												  Caption("Truck Editor View Settings").
												  MinSize(wx.Size(200, 100)).
												  Left().
												  CloseButton(True).
												  MaximizeButton(False).
												  Hide())
				# Lepes Object Inspector, only visible on RoRTerrainEditor
				self.ObjectInspector = ObjectInspector(self, title="Inspector")
				self.ObjectInspector.perspective = 1

				self.ObjectTree = RoRObjectTreeCtrl(self, title="Tree")
				self.ObjectTree.perspective = 1
				add_toolbar_button(self, self.ObjectTree)

				# Read mouse object placement mode from ObjectTree window
				# The reference is passed thru main window
				self.terrainOgreWin.update_mouse_placement_mode()

				# Map Preview
				self.MapPreview = ObjectPreviewOgreWindow(self, "mapPreview")
				self._mgr.AddPane(self.MapPreview, wx.aui.AuiPaneInfo().
								  Name("Map_Preview").
								  Caption("Map Preview").
								  MinSize(wx.Size(200, 200)).
								  CloseButton(True).
								  MaximizeButton(False).
								  Show(True).
								  CenterPane())


				#lepesnew
				# the odef editor ogre window
				self.odefEditorOgreWin = ODefEditorOgreWindow(self, wx.ID_ANY)
				self._mgr.AddPane(self.odefEditorOgreWin, wx.aui.AuiPaneInfo().Name("ogre_odef_editor_content").CenterPane().Hide())

				# the truck editor window
				self.truckEditorOgreWin = RoRTruckOgreWindow(self, wx.ID_ANY)
				self._mgr.AddPane(self.truckEditorOgreWin, wx.aui.AuiPaneInfo().Name("ogre_truck_editor_content").CenterPane().Hide())
#				self.truckEditorOgreWin.linePanel = self.sectionLine
				# the truck editor UV window
				self.truckEditorUVOgreWin = RoRTruckUVOgreWindow(self, wx.ID_ANY)
				self._mgr.AddPane(self.truckEditorUVOgreWin, wx.aui.AuiPaneInfo().Name("ogre_truck_editor_uv_content").Float().Hide())
				
				# Hide Object Inspector
				self._mgr.GetPane("object_inspector").Show(False)
				# Hide Controls
				self._mgr.GetPane("controls").Show(False)			   

				# add the toolbars to the manager
#				self._mgr.AddPane(self.terraintoolbar, wx.aui.AuiPaneInfo().
#												  Name("terrain_toolbar").
#												  Caption("General Toolbar").
#												  ToolbarPane().Left().
#												  LeftDockable(False).
#												  RightDockable(False)
##												  Hide()
#												  )

				self._mgr.GetPane("Map_Preview").Show(True)
				# make some default perspectives
				self._perspectives.append(self._mgr.SavePerspective())
				self.actualPerspective = 0
				
				self.hideAllPanes()
				log().debug("all windows created yet, creating perspectives") 
#				if rorSettings().has_section("perspectives"):
#					self._perspectives = [] 
#					for option, value in rorSettings().myConfig.items("perspectives"):
#						self._perspectives.append(value)
#				else:
				if True:
#					 terrain perspective 
					self._mgr.GetPane("terrain_toolbar").Show(True)
					self._mgr.GetPane("ogre_terrain_content").Show(True)
					self._mgr.GetPane("object_tree").Show(True)
					self._perspectives.append(self._mgr.SavePerspective())
	
					# odef editor perspective
					self.hideAllPanes()
					self._mgr.GetPane("ogre_odef_editor_content").Show(True)
					self._mgr.GetPane("odef_editor_view_settings").Show(True)
					self._mgr.GetPane("object_tree").Show(True)
					self._perspectives.append(self._mgr.SavePerspective())
	
					# truck editor perspective
					self.hideAllPanes()
#					self._mgr.GetPane("sectionLine").Show(True)
					self._mgr.GetPane("ogre_truck_editor_uv_content").Show(True)
					self._mgr.GetPane("ogre_truck_editor_content").Show(True)
					self._mgr.GetPane("truck_editor_view_settings").Show(True)
					self._perspectives.append(self._mgr.SavePerspective())
# TODO: self._perspective should be a dictionary with self._perspective_menu captions and the self._mgr.SavePerspective
#	  as a key, to be able to restore perspective with their names into menu and self._mgr
#	 bug with autoMap feature :-S
#					for i in range(len(self._perspectives)):
#						rorSettings().setSetting("perspectives", str(i), self._perspectives[i], autoSaveFile = False)
#					rorSettings().saveSettings()
				
				# load startup perspective
				self._mgr.LoadPerspective(self._perspectives[0])
				

				self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
				self.Bind(wx.EVT_SIZE, self.OnSize)
				self.Bind(wx.EVT_CLOSE, self.OnClose)

				self.Bind(wx.EVT_MENU, self.OnFileMenuOpenTerrainProject, id=ID_OpenTerrainProject)
				self.Bind(wx.EVT_MENU, self._on_save_terrain_btn_click, id=ID_SaveTerrain)
				self.Bind(wx.EVT_MENU, self._on_save_terrain_as_btn_click, id=ID_SaveTerrainAs)
				self.Bind(wx.EVT_MENU, self.OnViewHelp, id=ID_ViewHelp)
				self.Bind(wx.EVT_MENU, self.OnmodTool, id=ID_ModTool)

				self.Bind(wx.EVT_MENU, self.OnwxInspector, id=ID_wxInspector)
				self.Bind(wx.EVT_MENU, self.OnselectSkin, id=ID_selectSkin)
				self.Bind(wx.EVT_MENU, self.Onterraintoolbar, id=ID_hideCaptions)
				self.Bind(wx.EVT_TOOL, self.OnStickTo02Click, id=ID_StickTo02)
				self.Bind(wx.EVT_TOOL, self.OnStartRoRClick, id=ID_StartRoR)
				self.Bind(wx.EVT_TOOL, self.OnfindObject, id=ID_FindObject)
				
				self.Bind(wx.EVT_MENU, self.OnCreatePerspective, id=ID_CreatePerspective)
				self.Bind(wx.EVT_MENU, self.OnCopyPerspective, id=ID_CopyPerspective)
				self.Bind(wx.EVT_MENU, self.OnCopySelection, id=ID_CopySelection)
				self.Bind(wx.EVT_MENU, self.OnPasteSelection, id=ID_PasteSelection)

				self.Bind(wx.EVT_MENU, self.OnSettings, id=ID_Settings)
				
				self.Bind(wx.EVT_MENU, self.OnExit, id=ID_Quit)
				self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
				self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_About)
		
				self.Bind(wx.EVT_MENU_RANGE, self.OnRestorePerspective, id=ID_FirstPerspective,
								  id2=ID_FirstPerspective + 1000)
				
				# "commit" all changes made to FrameManager   
				self.terraintoolbar.Refresh()
#				self.terraintoolbar.Show(True)				
#				self.hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
#				self.hor_sizer.Add(self.terraintoolbar, 0, wx.EXPAND)
#				self.hor_sizer.Add(self.statusbar, 1, wx.EXPAND)
#				self.SetSizer(self.hor_sizer)
				self._mgr.GetArtProvider().SetColor(wx.aui.AUI_DOCKART_BACKGROUND_COLOUR, ShapedControls.skinBackColor)
				self._mgr.Update()
#				self.DoUpdate()
#				for s in range(len(self.tbbuttons)):
#					self.tbbuttons[s]['window'].Show(False)

				log().debug("Mainframe.__init__ finished")
				
		def OnCopySelection(self, evt):
			self.terrainOgreWin.selected.copy()
			evt.Skip()

		def OnPasteSelection(self, evt):
			self.terrainOgreWin.selected.paste()
			evt.Skip()
			
		def on_toolbar_button_click(self, evt):
			window_id = evt.GetId()
			idx = list_has_value(self.tbbuttons, 'id', window_id)
			if idx > -1:
				window = self.tbbuttons[idx]['window']
				if window.IsShown():
					window.Hide()
				else:
					window.Show(True)

		def _on_save_terrain_btn_click():
			pass # TODO

		def _on_save_terrain_as_btn_click():
			pass # TODO

		def hide_all_toolbar_windows(self):
			# TODO: Toggle button states!
			for tb_button in self.tbbuttons:
				window = tb_button["window"]
				window.Hide()
		
		def OnfindObject(self, evt):
			dlg = wx.TextEntryDialog(
							self, 'Enter position you want go separate by comma',
							'position:', '')
			
			dlg.SetValue("")
			
			if dlg.ShowModal() == wx.ID_OK:
				
				l = dlg.GetValue().split(',') 
				x = float(l[0])
				y = float(l[1])
				z = float(l[2])
				self.terrainOgreWin.setCamera((x, y, z), (0, 0, 0), 0)
			
			evt.Skip()
		def OnselectSkin(self, evt):
			w = skinSelector(self, title="Skin Selector")
			w.Show()
		def ConfigureSkin(self):
			theTheme = rorSettings().getSetting(TOOLKIT, "theme") 
			if theTheme != '':
				try:
					path = os.path.join(rorSettings().toolkitMainFolder, 'media', 'gui', 'skins', theTheme)  
					if os.path.isdir(path):
						cfg = ConfigParser.ConfigParser()
						cfg.read(os.path.join(path, "config.txt"))
						read = (cfg.get('skin', 'SkinBackgroundColor')).split(',')
						theSkinBackColor = wx.Color(int(read[0]), int(read[1]), int(read[2])) #arggggg
						read = cfg.get('skin', 'SkinTransparentColor').split(',')
						theTransparentColor = wx.Color(int(read[0]), int(read[1]), int(read[2])) #arggggg
						del cfg
					ShapedControls.skinBackColor = theSkinBackColor
					ShapedControls.skinTransparentColor = theTransparentColor
					ShapedControls.skinTheme = theTheme
				except:
					ShapedControls.skinTheme = 'RoR theme'
					ShapedControls.skinBackColor = wx.Color(254, 184, 0)
					ShapedControls.skinTransparentColor = wx.Color(0, 0, 0)

					log().error('skin %s is not valid, using default' % theTheme)
			log().debug('using skin %s' % ShapedControls.skinTheme)
		

		def hideAllPanes(self):
			""" 
			hide all _mgr Panes
			"""
			all_panes = self._mgr.GetAllPanes()
			for ii in xrange(len(all_panes)):
					if not all_panes[ii].IsToolbar():
							all_panes[ii].Hide()
			
		
		def OnStickTo02Click(self,
							 doc=" Stick new objects to 0.2 meters from ground"):
			self.terrainOgreWin.stickTo02 = not self.terrainOgreWin.stickTo02
		def OnStartRoRClick(self,
							   doc=" "):
			if self.terrainOgreWin:
				if self.terrainOgreWin.terrain:
#					self.Preview.clear()
					self.OnSaveTerrain(None)
					log().info(" ************** STARTING ROR **************")
					self.ToggleRenderAll()
					
					truck = rorSettings().getSetting(TOOLKIT, "usetruck")
					#RORBUG: launching RoR with a truck that doesn't have UID, ror doesn't load the truck
					#		 if parameter "-enter" is used, RoR crash
					if truck != "":
						truck = " -truck " + truck
					
					log().info("command line: " + rorSettings().rorFile + " -map " + self.terrainOgreWin.terrain.name + truck)
#					Popen(rorSettings().rorFile + " -map " +  self.terrainOgreWin.terrain.name, 1024, cwd = rorSettings().rorFolder )
					call(rorSettings().rorFile + " -map " + self.terrainOgreWin.terrain.name, 1024, cwd=rorSettings().rorFolder)
					log().info(" ************** ROR FINISHED **************")
					self.ToggleRenderAll()
					sleep(2)#wait a bit
					for x in self.tbbuttons:
						x['window'].restorePosition()
				else:
					log().warning("trying to execute RoR without a loaded terrain")
			else:
				log().warning("trying to execute RoR without created the Ogrewindow")

		def Onterraintoolbar(self, evt):
			#right click to show/hide captions buttons
#			actual = self.terraintoolbar.GetWindowStyle()
#			if actual == wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_VERTICAL | wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_NO_TOOLTIPS:
#				self.terraintoolbar.SetWindowStyle(wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_VERTICAL | wx.TB_NO_TOOLTIPS)
#			else:
#				self.terraintoolbar.SetWindowStyle(wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_VERTICAL | wx.TB_TEXT | wx.TB_HORZ_LAYOUT | wx.TB_NO_TOOLTIPS) 
#			self.terraintoolbar.SetBackgroundColour(ShapedControls.skinBackColor)
#			self.terraintoolbar.Realize()
#			self.terraintoolbar.Update()
			pass
		def ToggleRenderAll(self):			 
				self.activeRenders(not self.ogreTimer.IsRunning())
				if self.ogreTimer.IsRunning():
					self.ogreTimer.Stop()
					log().debug("Toolkit Render Stopped")
				else:
					self.ogreTimer.Start(-1) # use previous milliseconds.
					log().debug("Toolkit Render re-started")
		def activeRenders(self, value):
			rw = getOgreManager().renderWindows
			for w in rw.keys():
				rw[w].setActive(value)
			
		def changeEditorMode(self, id):
				self._mgr.LoadPerspective(self._perspectives[id])
				self.actualPerspective = id
				self._mgr.Update()
				
		def OnViewHelp(self, event=None):
				# show the settings pane, and float it
				floating_pane = self._mgr.GetPane("help").Float().Show()

				if floating_pane.floating_pos == wx.DefaultPosition:
						floating_pane.FloatingPosition(self.GetStartPosition())

				self._mgr.Update()
		
		def OnmodTool(self, event):
			m = ModGUI(self)
			m.Show(True)
		
		def addObjectToTerrain(self, filename):
				self.changeEditorMode(1)
				self.terrainOgreWin.addGeneralObject(filename)

		
		def previewObject(self, filename):
				try:
					if self.actualPerspective == 0:
						self.MapPreview.loadFile(filename)
						self.MapPreview.Show(True)
				except:
					log().debug("previewobject: failed to preview %s" % filename)

		def editODefFile(self, filename):
				self.odefEditorOgreWin.loadFile(filename)
				self.changeEditorMode(2)

		def editTruck(self, filename):
				print filename
				tree = self.truckEditorOgreWin.LoadTruck(filename)
				self.changeEditorMode(3)
				self.truckEditorUVOgreWin.setTree(tree)

		def updateStatusBar(self, msg=[]):
				""" msg is four strings
				"""
				for i in range(0, len(msg)):
					
					self.statusbar.SetStatusText(msg[i], i)

		def onUpdateRender(self, event=None): 
				getOgreManager().RenderAll()
				pass

		def load_terrain_from_project(self, project_dirname):
			self.changeEditorMode(1)
			self.terrainOgreWin.load_terrain_from_project(project_dirname)

		def load_terrain_from_terrn_file(self, filename, progress_window):
			progress_window.set_text("Setting editor mode...")
			self.changeEditorMode(1)
			self.terrainOgreWin.load_terrain_from_terrn_file(filename, progress_window)
			
		def OnClose(self, event):
				self.OnExit(event)
				
		def OnExit(self, event):
				log().debug("closing MainFrame...")
				self.tbbuttons = []  #dec ref count
#				getOgreManager().ogreRoot.shutdown()
				self.ogreTimer.Stop()
				log().debug("Rendering Timer stopped")
				del self.ogreTimer
				p = self.GetPosition()
				rorSettings().setSetting("MainFrame", "left", p.x)
				rorSettings().setSetting("MainFrame", "top", p.y)
				p = self.GetSize()
				rorSettings().setSetting("MainFrame", "width", p.width)
				rorSettings().setSetting("MainFrame", "height", p.height)
				
				# this event is not triggered for Child windows :F
				if self.truckEditorOgreWin:
					self.truckEditorOgreWin.close() #save settings
				try:
						all_panes = self._mgr.GetAllPanes()
						for ii in xrange(len(all_panes)):
								if not all_panes[ii].IsToolbar():
										all_panes[ii].Hide()			  
						self._mgr.UnInit()
#						del self._mgr
						log().debug("Destroying MainFrame")
						self.Destroy()
#						self.Close()
				except Exception, err:
					log().debug("exception while freeing MainFrame %s" % str(err))

		def OnAbout(self, event):
				ShowOnAbout()

		def GetDockArt(self):
				return self._mgr.GetArtProvider()

		def DoUpdate(self):
				self.GetDockArt().SetColor(wx.aui.AUI_DOCKART_BACKGROUND_COLOUR, ShapedControls.skinBackColor)		
#				self.terraintoolbar.SetBackgroundColour(ShapedControls.skinBackColor)
				self._mgr.Update()
				self.Refresh()
				self.Update()
				for x in range(len(self.tbbuttons)):
					self.tbbuttons[x]['window'].SetSize(self.tbbuttons[x]['window'].skinSize)

		def OnwxInspector(self, event):
			wx.lib.inspection.InspectionTool().Show()
			event.Skip()

		def OnEraseBackground(self, event):
				event.Skip()

		def OnSize(self, event):
				event.Skip()

		def OnSettings(self, event):
				# show the settings pane, and float it
				floating_pane = self._mgr.GetPane("settings").Float().Show()

				if floating_pane.floating_pos == wx.DefaultPosition:
						floating_pane.FloatingPosition(self.GetStartPosition())

				self._mgr.Update()

		def managerInit(self):
				flags = self._mgr.GetFlags()
				# based on default settings!
				flags |= wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE
				flags &= ~wx.aui.AUI_MGR_TRANSPARENT_DRAG
				self._mgr.SetFlags(flags)

		def OnCreatePerspective(self, event):
				dlg = wx.TextEntryDialog(self, "Enter a name for the new perspective:", "AUI Test")
				
				dlg.SetValue(("Perspective %d") % (len(self._perspectives) + 1))
				if dlg.ShowModal() != wx.ID_OK:
						return
				
				if len(self._perspectives) == 0:
						self._perspectives_menu.AppendSeparator()
				
				self._perspectives_menu.Append(ID_FirstPerspective + len(self._perspectives), dlg.GetValue())
				self._perspectives.append(self._mgr.SavePerspective())


		def OnCopyPerspective(self, event):
				s = self._mgr.SavePerspective()
				
				if wx.TheClipboard.Open():
				
						wx.TheClipboard.SetData(wx.TextDataObject(s))
						wx.TheClipboard.Close()
				
		def OnRestorePerspective(self, event):
				self._mgr.LoadPerspective(self._perspectives[event.GetId() - ID_FirstPerspective])
				self.actualPerspective = event.GetId() - ID_FirstPerspective

#				for i in range(len(self.tbbuttons)):
#					if self.tbbuttons[i]['perspective'] == self.actualPerspective:
#						self.terraintoolbar.AddTool(self.tbbuttons[i]['id'], self.tbbuttons[i]['label'])
		def GetStartPosition(self):
				self.x = self.x + 20
				x = self.x
				pt = self.ClientToScreen(wx.Point(0, 0))
				
				return wx.Point(pt.x + x, pt.y + x)

		def OnFileMenuOpenTerrainProject(self, event):
			self.application.open_terrain_projects_window()

		def MessageBox(self, type='info', text="",
					   doc=""" Show a MessageBox to the user with the Text  
							  type = 'info' is Information Box 
							  type = 'warning' is Warning Box 
							  type = 'error' is Error Box """):
			caption = ""
			flags = wx.OK
			if type.lower() == 'info':
				caption = "Information"
				flags = flags | wx.ICON_INFORMATION
			elif type.lower() == 'warning' :
				caption = "Warning"
				flags = flags | wx.ICON_EXCLAMATION 
			elif type.lower() == 'error':
				caption = "Error"
				flags = flags | wx.ICON_ERROR 
			else:
				raise Exception("type not used in MessageBox, actual: %s, valid types: info, warning, error" % type)
			
			dlg = wx.MessageDialog(self, text, caption, flags)
			dlg.ShowModal()
			dlg.Destroy()
	
		def _getlastFilenameUsed(self):
			return self._lastFilenameUsed
				
		def _setlastFilenameUsed(self, value):
			self._lastFilenameUsed = value
#			if value != "":
#				self.terraintoolbar.EnableTool(ID_SaveTerrain, True)
#				self.terraintoolbar.EnableTool(ID_StartRoR, True)							

			
		lastFilenameUsed = property(_getlastFilenameUsed, _setlastFilenameUsed,
							doc="""last filename to save terrain into """)
def startApp(MainApp):
		
		rorSettings().stopOnExceptions = False
		myFrame = MainFrame(None, -1, "") 
		MainApp.SetTopWindow(myFrame)

		rorSettings().rorDebug = False
		
	
#		if rorSettings().rorDebug:
#			myFrame.SetDimensions(0,0,1900,1000)
#			myFrame.lastFilenameUsed = "C:\Documents and Settings\Administrador\Mis documentos\Rigs of Rods\terrains\TERRENO1\Terreno1.terrn"
		myFrame.SetFocus()			
		myFrame.Show() 
		log().info("starting MainFrame.MainLoop")
		autoMap = rorSettings().getSetting(TOOLKIT, "autoopen")
		if autoMap != "":
			myFrame.openTerrain(autoMap)
			if bool(rorSettings().getSetting(TOOLKIT, "autoopeniszip")) == False:
				myFrame.lastFilenameUsed = autoMap
		else:
			# Open Tree window and update toolbar button state
			myFrame.ObjectTree.Show(True)
			idx = list_has_value(myFrame.tbbuttons, 'label', 'Tree')
			if idx != -1:
				item = myFrame.terraintoolbar.FindTool(myFrame.tbbuttons[idx]['id'])._tbItem.Toggle()
			else: print "idx not found"
				
		log().debug('starting rendering loop')
#		getOgreManager().startRendering()
		MainApp.MainLoop() 
		
