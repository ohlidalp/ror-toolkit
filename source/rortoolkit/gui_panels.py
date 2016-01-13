
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
		self.callback_homedir_selected = None
		self.callback_abort = None
		
		# State setup
		self.is_ror_installdir_selected = False
		self.is_ror_homedir_selected = False
	
	def setup_content(self, icon_path, window_title, banner_image_path, rendersystem_list, selected_rendersys_index, ror_homedirs):
		"""
		:param list[str] rendersystem_list: Rrendersystem names
		:param int selected_rendersys_index: Starts from 0.
		:param list[tuple(dirname, path)] ror_homedirs: Directories
		:returns: nothing
	    """
	    
		# Window icon
		icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)
	    
		# Layout conf
		help_text_width = 240
		controls_width = 150
		
		# Layout grid, tutorial: http://zetcode.com/wxpython/layout/
		grid = wx.GridBagSizer(vgap = 5, hgap = 5) 
		grid.SetEmptyCellSize(wx.Size(230,20))
		r = 0 # row
		c = 0 # column

		# Banner image
		import rortoolkit.gui_widgets
		banner = rortoolkit.gui_widgets.ImagePanelWidget(self, wx.ID_ANY, banner_image_path)
		grid.Add(banner, pos = wx.GBPosition(r,c), span = wx.GBSpan(3, 3))

		# Step1 (RoR installdir): Bullet point
		r += 4
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 1: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step1: instructions
		c += 1
		self.ror_installdir_label = wx.StaticText(self, wx.ID_ANY, "", size = (help_text_width, 40), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
		grid.Add(self.ror_installdir_label, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1), flag = wx.EXPAND)
		
		# Step1: browse button
		c += 1
		self.select_ror_installdir_btn = wx.Button(self, wx.ID_ANY, "Select RoR Folder", size = wx.Size(controls_width,20))
		grid.Add(self.select_ror_installdir_btn, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		self.Bind(wx.EVT_BUTTON, self.on_ror_installdir_selected, self.select_ror_installdir_btn)
		
		# Step2 (RoR homedir): Bullet point
		r += 1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 2: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step2: instructions
		c += 1
		self.ror_homedir_label = wx.StaticText(self, wx.ID_ANY, "Select RoR home directory to use:", size = (help_text_width, 40), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
		grid.Add(self.ror_homedir_label, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1), flag = wx.EXPAND)
		
		# Step2: RoR homedir selector
		c += 1
		self.ror_homedirs = ror_homedirs
		homedir_choices = []
		for tup in ror_homedirs:
			homedir_choices.append(tup[0]) # Dir names
		homedir_choices.insert(0, "-- select --")
		self.ror_homedir_combobox = wx.ComboBox(self, wx.ID_ANY, homedir_choices[0], size = wx.Size(controls_width,20), style=wx.CB_READONLY, choices=homedir_choices)
		self.Bind(wx.EVT_COMBOBOX, self.on_homedir_selected, self.ror_homedir_combobox)
		grid.Add(self.ror_homedir_combobox, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step3: Heading
		r +=1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 3: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step3: Instructions
		c += 1
		l = wx.StaticText(self, wx.ID_ANY, "Please select Graphic Renderer you want to use:", size = (help_text_width, 40))
		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1), flag = wx.EXPAND) 
		
		# Step3: Rendersystem selector
		c +=1
		self.renderer_selection_combobox = wx.ComboBox(self, wx.ID_ANY, rendersystem_list[selected_rendersys_index], size = wx.Size(controls_width,20), style=wx.CB_READONLY, choices=rendersystem_list)
		self.Bind(wx.EVT_COMBOBOX, self.on_renderer_selected, self.renderer_selection_combobox)
		grid.Add(self.renderer_selection_combobox, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		self.rendersystem_select_list = rendersystem_list
		self.rendersystem_selected_index = selected_rendersys_index
		
		# Step4: Heading
		r +=1
		c = 0
		dummy = wx.StaticText(self, wx.ID_ANY, "Step 4: ", size = (80, 60), style = wx.ALIGN_CENTER)
		dummy.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
		grid.Add(dummy, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))

		# Step4: Instructions
		c += 1
		l = wx.StaticText(self, wx.ID_ANY, "Complete previous steps first.", size = (help_text_width, 40))
		grid.Add(l, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1), flag = wx.EXPAND) 

		# Step4: Start button
		c += 1
		self.start_rortoolkit_button = wx.Button(self, wx.ID_ANY, "Start RoRToolkit", size = wx.Size(controls_width,40))
		self.Bind(wx.EVT_BUTTON, self.on_start_rortoolkit_button_pressed, self.start_rortoolkit_button)
		grid.Add(self.start_rortoolkit_button , pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1))
		
		# Exit button
		r += 1
		c = 2
		self.exit_button = wx.Button(self, wx.ID_CANCEL, "Exit", size = wx.Size(70, 20))
		self.Bind(wx.EVT_BUTTON, self.on_exit_button_pressed, self.exit_button)
		grid.Add(self.exit_button, pos = wx.GBPosition(r,c), span = wx.GBSpan(1, 1), flag = wx.ALIGN_RIGHT) 

		self.SetEscapeId(self.exit_button.GetId())

		self.SetAffirmativeId(self.start_rortoolkit_button.GetId())
		self.SetSizerAndFit(grid)
		self.SetAutoLayout(True)
		self.SetTitle(window_title)

		self.ror_installdir_changed(ror_installdir_path = None)
		
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
		
	def set_callback_homedir_selected(self, fn):
		"""
		Callback takes 2 args:
		1. (number) Index of selected homedir
		2. (list of tuples(dirname, path)) List of all available homedirs
		and returns nothing.
		"""
		self.callback_homedir_selected = fn

	def ror_installdir_changed(self, ror_installdir_path):
		if ror_installdir_path is None:
			self.ror_installdir_label.SetLabel("Select Rigs of Rods installation directory:")
			self.is_ror_installdir_selected = False
		else:
			self.ror_installdir_label.SetLabel("Selected Rigs of Rods directory:\n" + ror_installdir_path)
			self.is_ror_installdir_selected = True
		self.update_start_button_state()
			
	def update_start_button_state(self):
		ready = self.is_ror_installdir_selected and self.is_ror_homedir_selected
		self.start_rortoolkit_button.Enable(ready)

	def on_renderer_selected(self, id=None, func=None):
		self.rendersystem_selected_index = self.renderer_selection_combobox.GetCurrentSelection()
		if (self.callback_renderer_selected is not None):
			self.callback_renderer_selected(self.rendersystem_selected_index, self.rendersystem_select_list)
			
	def on_homedir_selected(self, id=None, func=None):
		if self.callback_homedir_selected is not None:
			sel_index = self.ror_homedir_combobox.GetCurrentSelection()
			if sel_index == 0: # Index 0 is dummy "-select-" text
				self.is_ror_homedir_selected = False
			else:
				self.is_ror_homedir_selected = True                
				if self.callback_homedir_selected is not None:
					self.callback_homedir_selected(sel_index - 1, self.ror_homedirs)
			self.update_start_button_state()				

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
			self.ror_installdir_changed(newpath)

 	def on_exit_button_pressed(self, event=None):
		if self.callback_abort is not None:
			self.callback_abort()

