import sys, os, os.path, re
import subprocess,os,sys,signal,pty,time,errno,thread

from deptools import *

cb = rorSettings().getSetting("RoRToolkit", "OgreXMLConverterExecutable")
if cb != '':
	CONVERTERBIN = cb
else:
	CONVERTERBIN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".." "tools", "OgreCommandLineTools", "OgreXmlConverter.exe"))



REs = [r".*material\s?=[\"\']([a-zA-Z0-9_/\-\\]*)[\"\'].*"]

def readFile(filename):
	f=open(filename, 'r')
	content = f.readlines()
	f.close()
	return content

def convertToXML(filename):
	# try to convert to .mesh.xml first!
	cmd = CONVERTERBIN + " \"" + filename+"\""
	log().info("calling " + cmd)

	p = subprocess.Popen(cmd, shell = False, cwd = os.path.dirname(CONVERTERBIN), stderr = subprocess.PIPE, stdout = subprocess.PIPE)
	smart_wait_for_subprocess(p, 10)
	if not os.path.isfile(os.path.join(os.path.dirname(filename), os.path.basename(filename)+".xml")):
		log().error("conversion of mesh file %s failed!" % filename)
	log().info("mesh converted: " + filename)

def smart_wait_for_subprocess(sp,timeout=30):
	"""
	Will wait for Process given to expire, and then kill it if
	the time elapses (or never if timeout==0).
	@param sp: Subprocess to watch
	@param timeout: timeout length in seconds
	"""
	running=1
	try:
		sleeps=timeout*4
		#Just wait around for termination...

		while sp.poll()==None:
			#print>>efp,"WAITING:",sleeps
			sleeps-=1
			time.sleep(.25)
			os.kill(sp.pid,0)
			if sleeps<=0 and timeout>0:
				os.kill(sp.pid,signal.SIGTERM)
				break
			elif sleeps<=0:
				break
		#Did it REALLY exit?
		try:
			os.kill(sp.pid,0)
			sleeps=20
			while sp.poll()==None:
				#print>>efp,"KILLING:",sleeps
				sleeps-=1
				time.sleep(.25)

				#No? KILL IT!
				if sleeps<=0 and timeout>0:
					#print>>efp,"KILLING2:",sleeps
					os.kill(sp.pid,signal.SIGKILL)
					break
				elif sleeps<=0:
					break
		except:
			running=0
	except:
		#Make REALLY effing sure it exited.
		os.kill(sp.pid,signal.SIGKILL)
		#print>>efp,"KILLING2:",sleeps


def parseRE(content):
	deps = []
	for line in content:
		for r in REs:
			m = re.match(r, line)
			if not m is None and len(m.groups()) > 0:
				depname = m.groups()[0]
				if not depname in deps:
					deps.append(depname)
	return deps


def getDependencies(filename):
	xmlfilename = os.path.join(os.path.dirname(filename), os.path.basename(filename)+".xml")
	if not os.path.isfile(xmlfilename):
		convertToXML(filename)
	try:
		content = readFile(xmlfilename)
	except Exception, err:
		log().error(str(err))
		return
	dep = parseRE(content)
	if len(dep) == 0:
		log().info("no material found for file " + filename)
	else:
		return {
				OPTIONAL:{
						},
				REQUIRES:{
						MATERIAL:dep,
						},
				PROVIDES:{
						FILE:[filename],
						},
			}

