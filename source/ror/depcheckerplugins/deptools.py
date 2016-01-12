#Thomas Fischer 06/07/2007, thomas@thomasfischer.biz
import sys, os, os.path

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from ror.logger import log
from ror.settingsManager import rorSettings

REQUIRES = 'requires'
OPTIONAL = 'optional'
PROVIDES = 'provides'
REQUIREDBY = 'requiredby'
RELATIONS = [REQUIRES, PROVIDES, OPTIONAL, REQUIREDBY]

MATERIAL = 'material'
FILE = 'file'
TYPES = [MATERIAL, FILE]
