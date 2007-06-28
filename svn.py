#Thomas Fischer 28/06/2007, thomas@thomasfischer.biz
import sys, os, os.path

URL = "http://roreditor.svn.sourceforge.net/svnroot/roreditor/trunk"

def notify(event_dict):
    print event_dict['path']

def svnupdate():
    import pysvn
    print "checkout"
    client = pysvn.Client()
    path = os.path.dirname(os.path.abspath(__file__))
    client.update(path,
                  recurse = True,
                  revision=pysvn.Revision(pysvn.opt_revision_kind.head),
                  ignore_externals = False)
    
def svncheckout():
    import pysvn
    print "update"
    client = pysvn.Client()
    #check out the current version of the pysvn project
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "svnco")
    client.callback_notify = notify
    client.checkout(URL, path)

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