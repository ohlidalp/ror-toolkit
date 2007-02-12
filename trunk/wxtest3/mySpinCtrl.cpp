/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#include "mySpinCtrl.hh"
#include "myRenderer.hh"

using namespace std;


mySpinCtrl::mySpinCtrl(wxWindow* parent, wxWindowID id, const wxString& name, int min, int max, int initial) :
                      wxSpinCtrl(parent, id, wxEmptyString, wxDefaultPosition, wxDefaultSize, wxSP_ARROW_KEYS, min, max, initial, name),
                      onspin_callback(0)
{
}

mySpinCtrl::~mySpinCtrl()
{
}

void mySpinCtrl::setOnSpinCallback(void (*callback) (float value))
{
  onspin_callback = callback;
}

void mySpinCtrl::OnSpin(wxSpinEvent& event)
{
  float fvalue = (float)event.GetPosition()/10;
  if (onspin_callback != 0)
    onspin_callback(fvalue);
}

BEGIN_EVENT_TABLE(mySpinCtrl, wxSpinCtrl)
    EVT_SPINCTRL(-1, mySpinCtrl::OnSpin)
END_EVENT_TABLE()

