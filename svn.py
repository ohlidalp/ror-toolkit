#Thomas Fischer 28/06/2007, thomas@thomasfischer.biz
import sys, os, os.path

URL = "http://roreditor.svn.sourceforge.net/svnroot/roreditor/trunk"

def notify(event_dict):
    print event_dict['path']

def svnupdate():
    print "checkout"
    path = os.path.dirname(os.path.abspath(__file__))
    try:
        import pysvn
        client = pysvn.Client()
        client.callback_notify = notify
        client.update(path,
                      recurse = True,
                      revision = pysvn.Revision(pysvn.opt_revision_kind.head),
                      ignore_externals = False)
    except:
        print "error while checkout!"
    
def svncheckout():
    print "update"
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