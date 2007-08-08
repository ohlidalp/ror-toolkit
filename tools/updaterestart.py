import sys, os, os.path
from subprocess import Popen

def main():
    import time
    time.sleep(1)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rortoolkit.py")
    p = Popen(path, shell = True, cwd = os.path.dirname(path))
    sys.exit(0)

if __name__=="__main__": 
    main()