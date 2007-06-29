import sys, os, os.path

def main():
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
    import ror.svn
    ror.svn.run()

if __name__=="__main__": 
    main()