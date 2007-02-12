/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYSPINCTRLHH
#define MYSPINCTRLHH

#include "wx/wx.h"
#include <wx/spinctrl.h>

class myRenderer;

class mySpinCtrl : public wxSpinCtrl
{
  private:
    DECLARE_EVENT_TABLE();

    void (*onspin_callback) (float value);

  public:
    mySpinCtrl(wxWindow* parent, wxWindowID id, const wxString& name = _("GLCanvas"), int min = 0, int max = 100 , int initial = 10);
    virtual ~mySpinCtrl();

    void OnSpin(wxSpinEvent& event);

    void setOnSpinCallback(void (*callback) (float value));
};

#endif
