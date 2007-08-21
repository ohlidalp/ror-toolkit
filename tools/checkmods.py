import os.path, sys, installmod, time

if sys.platform in ['linux', 'linux2']:
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_common"))
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_linux"))
elif sys.platform in ['win32']:
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_common"))
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_windows"))

from ror.logger import log
from ror.settingsManager import getSettingsManager

def getFiles(top):
	fl = {}
	for root, dirs, files in os.walk(top):
		for f in files:
			fn = os.path.join(root, f)
			fl[fn] = {}
	for fk in fl.keys():
		log().info("%10s %s" % ("", os.path.basename(fk)))

	log().info("found %d files!" % (len(fl.keys())))
	return fl

def main():
	dir = sys.argv[1]
	mode = sys.argv[2]
	files = getFiles(dir)
	valid={}
	counter = 0
	countervalid = 0
	for file in files.keys():
		log().info("## %s (%d/%d)##################################" % (os.path.basename(file), counter, len(files)))
		counter += 1
		mods = installmod.work(mode, file, verbose=(len(sys.argv)== 4 and sys.argv[3] == "--verbose"), dryrun=True)
		if len(mods) == 0:
			log().info("!!! INVALID: "+ os.path.basename(file))
		else:
			log().info("VALID: "+ os.path.basename(file))
			valid[file] = mods
		log().info("#######################################################################")
		time.sleep(0.01)
	log().info("===========================================================")
	log().info("===== FINISHED found, valid mods:")
	for f in valid.keys():
		log().info( f + str(valid[f]))
	log().info("%d of %d files containing valid mods!" % (len(valid), len(files)))


if __name__=="__main__":
	main()