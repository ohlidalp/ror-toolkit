import os, os.path, re
import subprocess 

def getDependencies(filename):
    return {
            "provide":{
                       "file":[os.path.basename(filename)]
                      }
           }
