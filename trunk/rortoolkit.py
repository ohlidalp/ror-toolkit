#!/bin/env python
#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

def main():
	"""
	main method
	"""
	if sys.platform in ['linux', 'linux2']:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_common"))
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_linux"))
	elif sys.platform in ['win32']:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_common"))
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_windows"))

	# Import Psyco if available
	try:
		import psyco
		#psyco.full()
		#psyco.log()
		#psyco.profile()
	except ImportError:
		pass

	import ror.starter
	ror.starter.startApp()


if __name__=="__main__":
	main()