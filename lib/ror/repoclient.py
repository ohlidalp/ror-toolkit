import xmlrpclib

s = xmlrpclib.Server('http://repository.rigsofrods.com:8000')
package = s.getInfo()
for item in package['data']:
    print item

print s.system.listMethods()