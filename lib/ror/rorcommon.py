import wx
from random import Random

def ShowOnAbout(event = None):
    rev = ""
    try:
        import ror.svn
        rev = str(ror.svn.getRevision())
    except:
        pass

    dlg = wx.MessageDialog(None, "RoR Toolkit revision %s\nAuthors: Aperion, Thomas" % rev,
                          "About This", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()          

    
    
def randomID(num_bits=64):
    """Return a string representing a bitfield num_bits long.
    Maximum artbitrarily set to 1025"""

    if num_bits < 1:
        raise RuntimeError,\
              "randomID called with negative (or zero) number of bits"
    if num_bits > 1024:
        raise RuntimeError,\
              "randomID called with too many bits (> 1024)"

    # create a num_bits string from random import Random
    rnd = Random()
    tmp_id = 0L
    for i in range(0, num_bits):
        tmp_id += long(rnd.randint(0,1)) << i
    #rof

    # The 2: removes the '0x' and :-1 removes the L
    rnd_id = hex(tmp_id)[2:-1]
    return(rnd_id)