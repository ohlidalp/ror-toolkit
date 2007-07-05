import xmlrpclib

def getFiles(category):
    s = xmlrpclib.Server('http://repository.rigsofrods.com:8000')
    package = s.getInfo(category)
    return package

    
#for item in package['data']:
#    print item
#print s.system.listMethods()