
import wx

class StartupSettingsDialog(wx.Dialog):
	
	def __init__(self, *args, **kwds):
		# Window setup
		kwds["style"] = wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX
		wx.Dialog.__init__(self, *args, **kwds)
		import roreditor.ShapedControls
		self.SetBackgroundColour(roreditor.ShapedControls.skinBackColor)
		
		# Callbacks setup
		self.callback_installdir_updated = None
		self.callback_renderer_selected = None
		self.callback_abort = None
	
	def setup_content(self, window_title, banner_image_path, rendersystem_list, selected_rendersys_index):	
		# Layout grid
		grid = wx.GridBagSizer(5,5) 
		grid.SetEmptyCellSize(wx.Size(230,20))
		r = 0
		c = 0

		# Banner image
		import rortoolkit.gui_widgets
		banner = rortoolkit.gui_widgets.ImagePanelWidget(self, wx.ID_ANY, banner_image_path)
		grid.Add(banner, pos = wx.GBPosition(r,c), span = wx.GBSpan(3, 5))

		# Step1: Heading
		r += 4
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 1: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step1: instructions
		c += 1
		self.ror_installdir_label = wx.StaticText(self, wx.ID_ANY, "", size = (210, 40), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
		grid.Add(self.ror_installdir_label, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		
		# Step1: browse button
		c += 1
		self.select_ror_installdir_btn = wx.Button(self, wx.ID_ANY, "Select RoR Folder", size = wx.Size(100,20))
		grid.Add(self.select_ror_installdir_btn, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		self.Bind(wx.EVT_BUTTON, self.on_ror_installdir_selected, self.select_ror_installdir_btn)

		# Step2: Heading
		r +=1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 2: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step2: Instructions
		c += 1
		l = wx.StaticText(self, wx.ID_ANY, "Please select Graphic Renderer you want to use:", size = (210, 40))
		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1)) 
		
		# Step2: Rendersystem selector
		c +=1
		self.renderer_selection_combobox = wx.ComboBox(self, wx.ID_ANY, rendersystem_list[selected_rendersys_index], size = wx.Size(100,20), style=wx.CB_READONLY, choices=rendersystem_list)
		self.Bind(wx.EVT_COMBOBOX, self.on_renderer_selected, self.renderer_selection_combobox)
		grid.Add(self.renderer_selection_combobox, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		self.rendersystem_select_list = rendersystem_list
		self.rendersystem_selected_index = selected_rendersys_index
		
		# Step3: Heading
		r +=1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 3: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step3: Instructions
		c += 1
		l = wx.StaticText(self, wx.ID_ANY, "Start Editor button will remain Disable until you complete previous steps.", size = (210, 40))
		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1)) 

		# Step3: Start button
		c += 1
		self.start_rortoolkit_button = wx.Button(self, wx.ID_ANY, "Start Editor", size = wx.Size(100,20))
		self.Bind(wx.EVT_BUTTON, self.on_start_rortoolkit_button_pressed, self.start_rortoolkit_button)
		grid.Add(self.start_rortoolkit_button , pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		
		# Exit button
		r += 1
		c = 3
		self.exit_button = wx.Button(self, wx.ID_CANCEL, "Exit", size = wx.Size(90,20))
		self.Bind(wx.EVT_BUTTON, self.on_exit_button_pressed, self.exit_button)
		grid.Add(self.exit_button, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1)) 

		self.SetEscapeId(self.exit_button.GetId())

		self.SetAffirmativeId(self.start_rortoolkit_button.GetId())
		self.SetSizerAndFit(grid)
		self.SetAutoLayout(True)
		self.SetTitle(window_title)

		self.revalidate_widget_states_and_captions(None)
		
	def set_callback_installdir_updated(self, fn):
		"""
		Callback takes 1 parameter (path) and must return 
		True if the directory is valid and False otherwise.
		"""
		self.callback_installdir_updated = fn
		
	def set_callback_renderer_selected(self, fn):
		"""
		Callback takes 2 args:
		1. (number) Index of selected rendersystem
		2. (list of strings) List of supported rendersystems
		and returns nothing.
		"""
		self.callback_renderer_selected = fn
		
	def set_callback_abort(self, fn):
		"""
		Callback takes no params and returns nothing
		"""
		self.callback_abort = fn

	def revalidate_widget_states_and_captions(self, ror_installdir_path):
		if ror_installdir_path is None:
			self.start_rortoolkit_button.Enable(False)
			self.ror_installdir_label.SetLabel("Please select where Rigs of Rods was Installed on your computer:")
		else:
			self.start_rortoolkit_button.Enable(True)
			self.ror_installdir_label.SetLabel("Selected Rigs of Rods Folder: " + ror_installdir_path)

	def on_renderer_selected(self, id=None, func=None):
		self.rendersystem_selected_index = self.renderer_selection_combobox.GetCurrentSelection()
		if (self.callback_renderer_selected is not None):
			self.callback_renderer_selected(self.rendersystem_selected_index, self.rendersystem_select_list)

	def on_start_rortoolkit_button_pressed(self, event=None):
		event.Skip()

	def on_ror_installdir_selected(self, event=None):
		dialog = wx.DirDialog(self, "Choose RoR Directory", "")
		res = dialog.ShowModal()
		if res == wx.ID_OK:
			newpath = dialog.GetPath()
			if (self.callback_installdir_updated is not None):
				if not self.callback_installdir_updated(newpath):
					newpath = None
			self.revalidate_widget_states_and_captions(newpath)

 	def on_exit_button_pressed(self, event=None):
		if self.callback_abort is not None:
			self.callback_abort()

