#-----------------------------------------------------------------------------
# Name:        img2pyartprov.py
# Purpose:     
#
# Author:      Riaan Booysen
#
# RCS-ID:      $Id: img2pyartprov.py 51004 2008-01-03 08:17:39Z RD $
# Copyright:   (c) 2006
# Licence:     wxPython
#-----------------------------------------------------------------------------
""" ArtProvider class that publishes images from modules generated by img2py.

Image modules must be generated with the -u and -n <name> parameters.

Typical usage:
>>> import wx, wx.lib.art.img2pyartprov, myimagemodule
>>> wx.ArtProvider.PushProvider(wx.lib.art.img2pyartprov.Img2PyArtProvider(myimagemodule))

If myimagemodule.catalog['MYIMAGE'] is defined, it can be accessed as:
>>> wx.ArtProvider.GetBitmap('wxART_MYIMAGE')

"""

import wx

_NULL_BMP = wx.NullBitmap
class Img2PyArtProvider(wx.ArtProvider):
    def __init__(self, imageModule, artIdPrefix='wxART_'):
        self.catalog = {}
        self.index = []
        self.UpdateFromImageModule(imageModule)
        self.artIdPrefix = artIdPrefix

        wx.ArtProvider.__init__(self)

    def UpdateFromImageModule(self, imageModule):
        try:
            self.catalog.update(imageModule.catalog)
        except AttributeError:
            raise Exception, 'No catalog dictionary defined for the image module'

        try:
            self.index.extend(imageModule.index)
        except AttributeError:
            raise Exception, 'No index list defined for the image module'

    def GenerateArtIdList(self):
        return [self.artIdPrefix+name for name in self.index]
            
    def CreateBitmap(self, artId, artClient, size):
        if artId.startswith(self.artIdPrefix):
            name = artId[len(self.artIdPrefix):]
            if name in self.catalog:
                return self.catalog[name].GetBitmap()

        return _NULL_BMP

