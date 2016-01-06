import sys, zipfile, os, os.path, types, glob
from tempfile import *
from types import ListType, StringType

def unzip(file, dir):
	""" unzip a zipFile into directory
	"""
	try:
		os.mkdir(dir)
	except:
		pass
	try:
		zfobj = zipfile.ZipFile(file)
		for name in zfobj.namelist():
			if name.endswith('/'):
				os.mkdir(os.path.join(dir, name))
			else:
				dirnow = dir.replace("/", "\\")
				subdirs = name.split("/")
				if len(subdirs) > 0:
					for subdir in subdirs:
						dirnow = os.path.join(dirnow, subdir)
				if not os.path.isdir(os.path.dirname(dirnow)):
					os.mkdir(os.path.dirname(dirnow))
				outfile = open(dirnow, 'wb')
				outfile.write(zfobj.read(name))
				outfile.close()
	except Exception, err:
		print str(err)
		return
	   
def zip(zipfilename, filetozip=None):
	""" create zipFilename or modify its contents
	
	filetozip - a list of files to add, or a single filename or a folder
			  
	When using a list, you must include a folder as a file if you want to 
	maintain folder structure.
	
	"""
	
	def add(filename):
		thezip.write(filename)

	if filetozip is None: return
	
	mode = 'w' #mode to open the zipfile
	if os.path.isfile(zipfilename):
		mode = 'a' #append a file to the zip
	thezip = zipfile.ZipFile(zipfilename, mode, zipfile.ZIP_DEFLATED, False)
	res = thezip.testzip()
	if res is not None:
		print "The zip file %s contains a bad file inside: %s" % (zipfilename, res)
		thezip.close()
		return
	try:
		relpath = filetozip
		if isinstance(filetozip, ListType):
#			print "is a list"
			for x in filetozip:
				if os.path.isdir(x):
					os.chdir(os.path.abspath(x))
					relpath = os.path.abspath(x) + '\\'
				else:
					add(x.replace(relpath, ''))
		elif isinstance(filetozip, StringType):
			if os.path.isdir(filetozip):
#				print "getting files of folder "
				os.chdir(filetozip)
				relpath = filetozip + '\\'
				files = glob.glob(os.path.join(filetozip, '*.*'))
				for file in files:
					add(file.replace(relpath, ''))
			elif os.path.isfile(filetozip):
#				print "is a file"
				relpath = os.path.split(filetozip)[0]
				os.chdir(relpath)				
				add(filetozip.replace(relpath + '\\', ''))
		else:
			print "zip doesn't understand this filetozip: %s" % filetozip
	finally:
		thezip.close()

if __name__ == "__main__":
	zipit = zip("c:\\Myislandzip.zip", 'C:\\Documents and Settings\\Lupas\\Mis documentos\\Rigs of Rods\\terrains\\island1\\496aUID-bouy.dds')
