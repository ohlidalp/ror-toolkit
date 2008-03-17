import sys, os, os.path

# deprecated
"""
def main():
	if sys.platform in ['linux', 'linux2']:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_common"))
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_linux"))
	elif sys.platform in ['win32']:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_common"))
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_windows"))

	guiVersion = (os.path.basename(sys.executable).lower() == "pythonw.exe")
	if guiVersion:
		import wx

		MainApp = wx.PySimpleApp(0)
		wx.InitAllImageHandlers() #you may or may not need this

		import ror.svngui
		gui = ror.svngui.svnUpdate(False)
		del gui
	else:
		#non-gui version:
		import ror.svn
		ror.svn.run()
"""
		
if __name__=="__main__":
	print "this tool is deprecated, please do not use it anymore"
	#main()