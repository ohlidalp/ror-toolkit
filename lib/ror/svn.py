#Thomas Fischer 28/06/2007, thomas@thomasfischer.biz
import sys, os, os.path
import pysvn

URL = "http://roreditor.svn.sourceforge.net/svnroot/roreditor/trunk"
changes = 0

def getRootPath():
    path = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(path, "media")):
        return path
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..\\.."))
    if os.path.isdir(os.path.join(path, "media")):
        return path
    # todo: throw exception!
    return None
    
def notify(event_dict):
    global changes
    changes += 1
    #print event_dict
    print str(event_dict['action']) + ", " + event_dict['path']

def getRevision(client=None, path=None):
    if client is None:
        client = pysvn.Client()
    if  path is None:
         path = getRootPath()
    info = client.info(path)
    return info['revision'].number

def callback_ssl_server_trust_prompt(trust_data):
    return True, trust_data['failures'], True

def getLog(client, startrev, endrev):
    path = getRootPath()
    return client.log(path,
         revision_start=pysvn.Revision(pysvn.opt_revision_kind.number, startrev),
         revision_end=pysvn.Revision(pysvn.opt_revision_kind.number, endrev),
         discover_changed_paths=False,
         strict_node_history=True,
         limit=0)

def showLog(client, startrev, endrev):
    print "------------------------------------"
    print "Changelog from revision %d to revision %d\n" % (startrev, endrev)
    log = getLog(client, startrev, endrev)
    for e in log:
        print "--- r%d, author: %s:\n%s\n" %(e['revision'].number, e['author'], e['message'])
         
def svnupdate():
    global changes
    path = getRootPath()
    changes = 0
    try:
        client = pysvn.Client()
        revision_before = getRevision(client, path)
        print "updating from revision %d ..." % revision_before
        client.callback_notify = notify
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        client.update(path,
                      recurse = True,
                      revision = pysvn.Revision(pysvn.opt_revision_kind.head),
                      ignore_externals = False)
        revision_after = getRevision(client, path)
        print "updated to revision %d." % revision_after
        if revision_before == revision_after and changes == 2:
            print "already up to date!"
        elif changes > 2:
            print "updated! please restart the application!"
            showLog(client, revision_before + 1, revision_after)
    except Exception, inst:
        print "error while updating: " + str(inst)
        print "done."
    
def svncheckout():
    print "checkout"
    path = getRootPath()
    changes = 0
    try:
        client = pysvn.Client()
        client.callback_notify = notify
        client.checkout(URL, path)
    except:
        print "error while checkout!"

        
def run():
    if os.path.isdir(os.path.join(getRootPath(), "media")):
        svnupdate()
    else:
        svncheckout()
        
