#Thomas Fischer 28/06/2007, thomas@thomasfischer.biz
import sys, os, os.path

URL = "http://roreditor.svn.sourceforge.net/svnroot/roreditor/trunk"

def notify(event_dict):
    print str(event_dict['action']) + ", " + event_dict['path']

def getRevision(client, path):
    info = client.info(path)
    return info['revision'].number
    
def svnupdate():
    path = os.path.dirname(os.path.abspath(__file__))
    try:
        import pysvn
        client = pysvn.Client()
        revision_before = getRevision(client, path)
        print "updating from revision %d ..." % revision_before
        client.callback_notify = notify
        client.update(path,
                      recurse = True,
                      revision = pysvn.Revision(pysvn.opt_revision_kind.head),
                      ignore_externals = False)
        revision_after = getRevision(client, path)
        print "updated to revision %d" % revision_after
        if revision_before == revision_after:
            print "already up to date!"
    except:
        print "error while checkout!"
    
def svncheckout():
    print "checkout"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svnco")
    try:
        import pysvn
        client = pysvn.Client()
        client.callback_notify = notify
        client.checkout(URL, path)
    except:
        print "error while checkout!"

def main():
    """
    main method
    """
    
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

    if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")):
        svnupdate()
    else:
        svncheckout()


if __name__=="__main__": 
    main()