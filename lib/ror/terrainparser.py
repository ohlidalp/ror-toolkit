import wx, os, os.path

from logger import log
from settingsManager import getSettingsManager

class Object:
    x = None
    y = None
    z = None
    rotx = None
    roty = None
    rotz = None
    name = ""
    filename = ""
    additionaloptions = []
    comments = []
    mayRotate = True
    
    error = None
    
    def setPosition(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def setRotation(self, x, y, z):
        self.rotx = x
        self.roty = y
        self.rotz = z
    

class RoRTerrain:
    filename = ""
    TerrainName = ""
    TerrainConfig = ""
    filename = ""

    trucks = []
    loads = []
    objects = []
    
    UsingCaelum = False
    WaterHeight = None
    SkyColor = None
    SkyColorLine = None
    TruckStartPosition = None
    CameraStartPosition = None
    CharacterStartPosition = None

    def saveFile(self, filename, lines):
        f = open(filename, 'w')
        f.writelines(lines)
        f.close()
    
    def loadFile(self,filename):
        f=open(filename, 'r')
        content = f.readlines()
        f.close()
        return content
    
    def __init__(self, filename):
        self.filename = filename
        content = self.loadFile(filename)
        self.trucks = []
        self.loads = []
        self.objects = []
        log().info("processing terrain file: %s" % filename)
        self.processTerrnFile(content)
        self.FixTerrainConfig(os.path.join(os.path.dirname(filename), self.TerrainConfig))        
        log().info("processing of terrain finished!")

    def FixTerrainConfig(self, filename):
        content = self.loadFile(filename)
        for i in range(0, len(content)):
            if content[i].lower().find("maxpixelerror") >= 0:
                content[i] = "MaxPixelError=0\n"
                log().info("fixed terrain's MaxPixelError - error")
                break
        self.saveFile(filename, content)
        
    def processTerrnFile(self, content):
        linecounter = 0
        comm = []
        for i in range(0, len(content)):
            # convert tabs to spaces!
            content[i] = content[i].replace("\t", " ")
        
            if content[i].strip() == "":
                comm.append(content[i])
                continue
            if content[i].strip()[0:4] == "////":
                # ignore editor self made comments (usefull for those error msgs)
                continue
            if content[i].strip()[0:2] == "//":
                comm.append(content[i])
                continue
            if content[i].strip()[0:1] == ";":
                # bugfix wrong characters!
                comm.append(content[i].replace(";","//"))
                continue
            if content[i].strip().lower() == "end":
                continue
            
            # do not count empty or comment lines!
            linecounter += 1
            if linecounter == 1:
                #terrain name
                self.TerrainName = content[i].strip()
                continue
            elif linecounter == 2:
                # .cfg file
                self.TerrainConfig = content[i].strip()
                continue
            if content[i].strip()[0].lower() == "w":
                self.WaterHeight = float(content[i].strip()[2:])
                continue
            if content[i].strip().lower() == "caelum":
                self.UsingCaelum = True
                continue
            if linecounter < 10 and len(content[i].split(",")) == 3:
                # sky color
                sc = content[i].split(",")
                self.SkyColor = (float(sc[0]), float(sc[1]), float(sc[2]))
                self.SkyColorLine = content[i]
                continue
            if linecounter < 10  and len(content[i].split(",")) == 9 or len(content[i].split(",")) == 6:
                # spawning Position
                sp = content[i].split(",")
                self.TruckStartPosition = [float(sp[0]), float(sp[1]), float(sp[2])]
   
                self.CameraStartPosition = [float(sp[3]), float(sp[4]), float(sp[5])]
                if len(sp) == 9:
                    self.CharacterStartPosition = [float(sp[6]), float(sp[7]), float(sp[8])]
                continue

            arr = content[i].split(",")
            try:
                x = float(arr[0])
                y = float(arr[1])
                z = float(arr[2])
                rx = float(arr[3])
                ry = float(arr[4])
                rz = float(arr[5])
                objname = (arr[6]).strip().split(" ")
            except:
                log().error("unable to parse line: %s. ignoring it!" % content[i])
                continue
                
            #print objname
            if objname[0][0:5].lower() == "truck" and len(objname) > 1:
                truck = Object()
                truck.name = "truck"
                truck.filename = objname[-1].strip()
                truck.comments = comm
                comm = []
                truck.setPosition(x, y, z)
                truck.setRotation(rx, ry, -rz)
                truck.additionaloptions = objname[1:]
                truck.mayRotate=False
                self.trucks.append(truck)
                continue
            if objname[0][0:4] == "load" and len(objname) > 1:
                load = Object()
                load.name = "load"
                load.filename = objname[-1].strip()
                load.comments = comm
                comm = []
                load.setPosition(x, y, z)
                load.setRotation(rx, ry, -rz)
                load.additionaloptions = objname[1:]
                load.mayRotate=False
                self.loads.append(load)
                continue
            
            # now it can just be an static object
            objectname = objname[0].strip()
            obj = Object()
            obj.name = objectname
            obj.filename = objectname
            obj.comments = comm
            comm = []
            obj.setPosition(x, y, z)
            obj.setRotation(rx, ry, rz)
            obj.additionaloptions = objname[1:]
            self.objects.append(obj)

    def getObjectLines(self, object):
        lines = []

        # add comments
        if len(object.comments) > 0:
            for comment in object.comments:
                lines.append(comment)

        # construct objects name
        objname = object.name 
        if len(object.additionaloptions) > 0:
            tmp = (" " + " ".join(object.additionaloptions)).strip()
            objname += " " + tmp
        
        # add line itself
        linearray = [self.formatFloat(object.x),
                     self.formatFloat(object.y),
                     self.formatFloat(object.z), 
                     self.formatFloat(object.rotx),
                     self.formatFloat(object.roty),
                     self.formatFloat(object.rotz),
                     objname]
        line = ", ".join(linearray)
        
        if not object.error is None:
            lines.append("//// the next object had errors, so the terraineditor commented it out:\n")
            lines.append("//"+line.strip()+"\n")
        else:
            lines.append(line.strip()+"\n")
        return lines
                
    def formatFloat(self, fl):
        return "%12s" % ("%0.6f" % (float(fl)))
        
    
    def save(self, filename = None):
        if filename is None:
            filename = self.filename
        lines = []
        lines.append(self.TerrainName+"\n")
        lines.append(self.TerrainConfig+"\n")
        if not self.WaterHeight is None:
            lines.append("w "+str(self.WaterHeight)+"\n")
        if self.UsingCaelum:
            lines.append("caelum\n")
        lines.append(self.SkyColorLine.strip()+"\n")

        ar = []
        ar.append(str(self.TruckStartPosition[0]))
        ar.append(str(self.TruckStartPosition[1]))
        ar.append(str(self.TruckStartPosition[2]))
        ar.append(str(self.CameraStartPosition[0]))
        ar.append(str(self.CameraStartPosition[1]))
        ar.append(str(self.CameraStartPosition[2]))
        if not self.CharacterStartPosition is None:
            ar.append(str(self.CharacterStartPosition[0]))
            ar.append(str(self.CharacterStartPosition[1]))
            ar.append(str(self.CharacterStartPosition[2]))
        startline = ", ".join(ar)+"\n"
        lines.append(startline)

        
        #save trucks
        for truck in self.trucks:
            trucklines = self.getObjectLines(truck)
            for l in trucklines:
                lines.append(l)
        # save loads
        for load in self.loads:
            loadlines = self.getObjectLines(load)
            for l in loadlines:
                lines.append(l)
                
        # save objects                   
        for object in self.objects:
            objectlines = self.getObjectLines(object)
            for l in objectlines:
                lines.append(l)

        lines.append("end\n")
        self.saveFile(filename, lines)
        return True

        