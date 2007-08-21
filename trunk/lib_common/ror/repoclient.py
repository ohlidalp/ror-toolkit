import xmlrpclib

def getFiles(category):
    s = xmlrpclib.Server('http://repository.rigsofrods.com:8000')
    package = s.getInfo(category)
    return package


#import UnRAR
# extract all the files in test.rar
#UnRAR.Archive('test.rar').extract()

    
#for item in package['data']:
#    print item
#print s.system.listMethods()