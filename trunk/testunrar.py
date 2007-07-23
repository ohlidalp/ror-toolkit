#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil

def main():
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    
    fn = 'MudFest_v1-isc-d.rar'
    
    import UnRAR
    #extract all the files in test.rar
    zipdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if os.path.isdir(zipdir):
        shutil.rmtree(zipdir)
        os.rmdir(zipdir)
    os.mkdir(zipdir)
    dst = os.path.join(zipdir, fn)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), fn)
    shutil.copyfile(src, dst)
    os.chdir(zipdir)
    
    UnRAR.Archive(fn).extract()

if __name__=="__main__": 
    main()