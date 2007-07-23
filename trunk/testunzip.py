#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil

def main():
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    
    fn = 'daf_swapbody.zip'
    
    import UnZIP

    zipdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if os.path.isdir(zipdir):
        shutil.rmtree(zipdir)

    UnZIP.unzip(fn, zipdir)

if __name__=="__main__": 
    main()