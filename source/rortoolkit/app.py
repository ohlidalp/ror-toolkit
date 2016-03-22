
import wx

class AppMode:
	"""
	Enum
	"""
	MAIN_MENU             = 0
	TERRAIN_IMPORT_SEARCH = 1
	TERRAIN_EDITOR        = 2

class Application:
	"""
	Application logic of RoRToolkit.
	GUI panels/tools should never perform application logic
	themselves, only invoke callbacks of Application.
	"""

	def __init__(self):
		self._gui_panels = {
			"terrain_project_manager_window": None,
			"terrain_import_selector_window": None
		}
		self._mode = AppMode.MAIN_MENU

	def init_set_main_frame(self, gui_main_frame):
		self._gui_panels["main_frame"] = gui_main_frame

	def open_terrain_projects_window(self):
		import rortoolkit.gui

		window = self._gui_panels["terrain_project_manager_window"]
		if window is None:
			main_frame = self._gui_panels["main_frame"]
			window = rortoolkit.gui.TerrainProjectManagerPanel(main_frame, self)
			self._gui_panels["terrain_project_manager_window"] = window
		def callback_import_fn():
			self.enter_mode(AppMode.TERRAIN_IMPORT_SEARCH)
		def callback_open_fn(dirname):
			self._gui_panels["main_frame"].load_terrain_from_project(dirname)
			self._mode = AppMode.TERRAIN_EDITOR
		window.callback_import_button_pressed = callback_import_fn
		window.callback_open_button_pressed = callback_open_fn
		window.populate_project_list(self.list_terrain_projects())
		window.Show()

	def list_terrain_projects(self):
		"""
		Generates list of project directory names
		"""
		from ror.settingsManager import rorSettings
		import os

		projects_dir = rorSettings().concatToToolkitHomeFolder(["map-projects"])
		proj_dirs = []
		for test_dir in os.listdir(projects_dir):
			test_path = os.path.join(projects_dir, test_dir)
			if os.path.isdir(test_path):
				json_path = os.path.join(test_path, "terrain-project.json")
				if os.path.isfile(json_path):
					proj_dirs.append(test_dir)
		return proj_dirs

	def enter_mode(self, mode):
		if mode == AppMode.MAIN_MENU:
			if self._mode == AppMode.TERRAIN_IMPORT_SEARCH:
				self._gui_panels["main_frame"].Show()
			self._mode = mode
		elif mode == AppMode.TERRAIN_IMPORT_SEARCH:
			self._enter_mode_terrn_import_select()

	def _enter_mode_terrn_import_select(self):
		import rortoolkit.gui
		import rortoolkit.resources
		import multiprocessing
		import time # DBG

		self._mode = AppMode.TERRAIN_IMPORT_SEARCH
		self._hide_all_windows()
		# Show loading progress window
		queue = multiprocessing.Queue()
		process = multiprocessing.Process(target=mp_terrn_search_progress_window, args=(queue,))
		process.start()

		# Loading
		rortoolkit.resources.init_all_known_resources() # This inits OGRE resource groups
		queue.put({"command":"set_text", "text":"Searching for importable terrains..."})
		terrns = rortoolkit.resources.search_importable_terrains()

		# Show terrn import window
		window = self._gui_panels["terrain_import_selector_window"]
		if window is None:
			main_frame = self._gui_panels["main_frame"]
			window = rortoolkit.gui.TerrainImportSelectorWindow(main_frame, self)
			def cancel_import_fn():
				self.enter_mode(AppMode.MAIN_MENU)
			def perform_import_fn(filename):
				self._import_terrn(filename)
			window.callback_cancel_import = cancel_import_fn
			window.callback_perform_import = perform_import_fn
			self._gui_panels["terrain_import_selector_window"] = window

		window.assign_terrains(terrns)
		queue.put({"command":"exit"})
		process.join()
		window.Show()

	def _hide_all_windows(self):
		# Hide toolbar windows
		self._gui_panels["main_frame"].hide_all_toolbar_windows()
		# Hide managed windows
		for window in self._gui_panels.values():
			if window is not None:
				window.Hide()

	def _import_terrn(self, filename):
		"""
		Performs an online import of .terrn: Opens the terrain,
		exports a project from it and switches app to TERRAIN_EDITOR mode.
		"""
		import os
		import os.path
		import rortoolkit.resources
		import zipfile

		# Switch app state
		self._mode = AppMode.TERRAIN_EDITOR
		self._gui_panels["main_frame"].Show()
		self._gui_panels["terrain_import_selector_window"].Hide()

		# Fire legacy loading code
		self._gui_panels["main_frame"].load_terrain_from_terrn_file(filename)

		# Export project from editor
		terrn_editor_win = self._gui_panels["main_frame"].terrainOgreWin
		terrn_project, export_data = terrn_editor_win.export_terrain_project()
		terrn_editor_win.cameraBookmark.save_to_terrain_project(terrn_project)

		# Save JSON data
		terrn_project.save_as_json()
		self._curr_terrn_editor_project = terrn_project

		# Copy heightmap
		dst_path = os.path.join(terrn_project.get_project_directory(), terrn_project.get_heightmap_filename())
		terrn_editor_win.export_heightmap(export_data["heightmap_filename"], dst_path)

		# Copy resources
		res_dir = os.path.join(terrn_project.get_project_directory(), "resources")
		if not os.path.isdir(res_dir):
			os.mkdir(res_dir)
		res_src_zip = rortoolkit.resources.get_resource_zip_path(export_data["heightmap_filename"])
		zip_stream = zipfile.ZipFile(res_src_zip)
		ext_whitelist = [
			"png", "jpg", "dds", "tga", "bmp",          # Image files
			"mesh", "odef",                             # Geometry + descriptors
			"material", "program", "cg", "hlsl", "glsl" # Materials and shaders
		]
		for filename in zip_stream.namelist():
			segments = filename.split(".")
			if segments[-1].lower() in ext_whitelist:
				zip_stream.extract(filename, res_dir)

def mp_terrn_search_progress_window(ipc_queue):
	"""
	Loading all resources + scanning takes long time. AND, Python lacks proper thread support.
	Solution: Main process controls OGRE loading, this process displays responsive GUI.
	"""
	import rortoolkit.gui
	import types

	# Setup window
	wx_app = wx.PySimpleApp(0)
	window = rortoolkit.gui.ProgressWindow(parent=None)
	window.setup(
		title = "Terrn import | RoRToolkit",
		text = "Loading all resources.\nThis may take several minutes."
		)
	window.progressbar_autopulse_start(50)
	window.Show()

	# Wait for further instructions from main process
	def check_queue(timer_event):
		try:
			message = ipc_queue.get_nowait()
		except:
			return False
		if type(message) is not types.DictionaryType:
			return False
		if "command" not in message:
			return False
		cmd = message["command"]
		if cmd == "exit":
			window.Close()
			window.Destroy()
			return True
		elif cmd == "set_text":
			window.set_status_text(message["text"])
			return False

	timer_id = wx.NewId()
	timer = wx.Timer(window, timer_id)
	wx.EVT_TIMER(window, timer_id, check_queue)
	timer.Start(50)

	wx_app.MainLoop()
