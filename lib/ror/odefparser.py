def loadOdef(odefFilename):
    f=open(odefFilename, 'r')
    content = f.readlines()
    f.close()
    meshname = content[0].strip()
    scalearr = [1,1,1]
    if len(content) > 2:
        scalearr = content[1].split(",")

    return (meshname, float(scalearr[0]), float(scalearr[1]), float(scalearr[2]))
