# old format:
from ror.logger import log
from ror.settingsManager import getSettingsManager

def loadOdef_old(odefFilename):
    f=open(odefFilename, 'r')
    content = f.readlines()
    f.close()
    meshname = content[0].strip()
    scalearr = [1,1,1]
    if len(content) > 2:
        scalearr = content[1].split(",")

    return (meshname, float(scalearr[0]), float(scalearr[1]), float(scalearr[2]))

class odefbox:
    rotating=False
    virtual=False
    eventname=""
    coords=[]
    rotation = []
    
    # for 3d
    uuid = None
    node=None
    entity=None
    def __str__(self):
        s = ""
        if self.rotating:
            s+= "rotating, "
        if self.virtual:
            s+= "virtual, "
        s += " eventname='%s'" % self.eventname
        s += " coordinates: " + str(self.coords)
        s += " rotation: " + str(self.rotation)
        return s
    
def loadOdef(odefFilename):
    try:
        f=open(odefFilename, 'r')
        content = f.readlines()
        f.close()
        ismovable = False
        meshname = content[0].strip()
        scalearr = [1,1,1]
        boxes = []
        actualbox = None
        if len(content[1].split(",")) > 2:
            scalearr = content[1].split(",")
        for line in content[1:]:
            line = line.strip().lower()
            if len(line) == 0 or line[0] == '/':
                continue
            elif line == "end":
                break
            elif line == "movable":
                ismovable = True
            elif line in ["beginbox", "beginmesh"]:
                actualbox = odefbox()
            elif line[:9] == "boxcoords":
                actualbox.coords = line[10:].split(",")
            elif line[:6] == "rotate":
                actualbox.rotating=True
                actualbox.rotation = line[7:].split(",")
            elif line == "virtual":
                actualbox.virtual=True
            elif line[:5] == "event":
                actualbox.eventname=line[6:]
            elif line == "endbox":
                boxes.append(actualbox)
        print  meshname, float(scalearr[0]), float(scalearr[1]), float(scalearr[2]), ismovable
        print "boxes:"
        for b in boxes:
            print b
        return meshname, float(scalearr[0]), float(scalearr[1]), float(scalearr[2]), ismovable, boxes
    except Exception, err:
        log().error(str(err))
        return None, None, None, None, None