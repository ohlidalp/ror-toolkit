/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYSPINCTRLHH
#define MYSPINCTRLHH

#include "wx/wx.h"
#include "wx/spinctrl.h"
#include "myGLWindow.hh"

class mySpinCtrl : public wxSpinCtrl
{
  private:
    int currentValue;
    myGLWindow *myGL;
    DECLARE_EVENT_TABLE();
    void setSpeed();

  public:
    mySpinCtrl(wxWindow* parent, wxWindowID id, myGLWindow *win, const wxString& name = _("GLCanvas"), int min = 0, int max = 100 , int initial = 10);
    virtual ~mySpinCtrl();

    void OnSpin(wxSpinEvent& event);
};

#endif
