/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYAPPHH
#define MYAPPHH

#include "wx/wx.h"
#include "wx/timer.h"

class myGLWindow;
class mySpinCtrl;

class myApp: public wxApp
{
  private:
    myGLWindow *MyGLCanvas1, *MyGLCanvas2, *MyGLCanvas3, *MyGLCanvas4;
    mySpinCtrl *spin1, *spin2, *spin3, *spin4;
    wxTimer *myTimer;
    DECLARE_EVENT_TABLE();

  public:
    virtual bool OnInit();
    void OnTimer(wxTimerEvent & event);
};

#endif
