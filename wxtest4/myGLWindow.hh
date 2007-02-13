/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYGLWINDOWHH
#define MYGLWINDOWHH

#include "wx/wx.h"
#include "wx/xrc/xmlres.h"
#include "wx/glcanvas.h"
#include "wx/notebook.h"
#include "GL/gl.h"
#include "GL/glu.h"

#if !wxUSE_GLCANVAS
    #error "OpenGL required: set wxUSE_GLCANVAS to 1 and rebuild the library"
#endif 

class myGLWindow : public wxGLCanvas
{
  private:
    DECLARE_EVENT_TABLE();

    wxSize mySize;

  public:
    myGLWindow(wxWindow* parent, wxWindowID id, const wxPoint& pos,
               const wxSize& size, long style = 0,
               const wxString& name = _("GLCanvas"), int* attribList = 0,
               const wxPalette& palette = wxNullPalette);

    virtual ~myGLWindow();

    bool isInitiated;
    float rotx, roty, rotz;

    int gllist;

    void draw();
//     void OnIdle(wxIdleEvent& event);
    void OnIdle(wxIdleEvent& event) {
        draw();
        event.RequestMore();
    }
    void OnSize(wxSizeEvent& event);

    wxSize getSize(void) { return mySize; };
    void setRotation(float x, float y, float z) { rotx = x; roty = y; rotz = z; };
};

#endif
