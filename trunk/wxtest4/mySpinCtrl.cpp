/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#include "mySpinCtrl.hh"
#include "myGLWindow.hh"
#include "myRenderer.hh"


mySpinCtrl::mySpinCtrl(wxWindow* parent, wxWindowID id, myGLWindow *win, const wxString& name, int min, int max, int initial) :
                      wxSpinCtrl(parent, id, wxEmptyString, wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS, min, max, initial, name),
                      currentValue(initial), myGL(win)
{
  setSpeed();
}

mySpinCtrl::~mySpinCtrl()
{
}

void mySpinCtrl::setSpeed()
{
  float fvalue = (float)currentValue/1000;
//  printf("spinning: %f\n", fvalue);
  myRenderer::getInstance().setRotationSpeed(fvalue);
}

void mySpinCtrl::OnSpin(wxSpinEvent& event)
{
  currentValue = event.GetPosition();
  setSpeed();
}

BEGIN_EVENT_TABLE(mySpinCtrl, wxSpinCtrl)
    EVT_SPINCTRL(-1, mySpinCtrl::OnSpin)
END_EVENT_TABLE()

