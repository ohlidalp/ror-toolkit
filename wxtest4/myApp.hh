/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYAPPHH
#define MYAPPHH

#include "wx/wx.h"
#include "wx/timer.h"
#include "myGLWindow.hh"
#include "mySpinCtrl.hh"
#include "myGLWindow.hh"
#include "mySpinCtrl.hh"
#include "MainFrame.h"

class myApp: public wxApp
{
  private:
    myGLWindow *MyGLCanvas1, *MyGLCanvas2, *MyGLCanvas3, *MyGLCanvas4;
    mySpinCtrl *spin1, *spin2, *spin3, *spin4;
    wxTimer *myTimer;
    
    void GenerateMenu(wxFrame *frame);
        
    /** Process menu File>Open */
    void OnMenuFileOpen(wxCommandEvent &event);
    
    /** Process menu File>Save */
    void OnMenuFileSave(wxCommandEvent &event);
    
    /** Process menu File>Quit */
    void OnMenuFileQuit(wxCommandEvent &event);
    
    /** Process menu About>Info */
    void OnMenuHelpAbout(wxCommandEvent &event);
    DECLARE_EVENT_TABLE();

  public:
    virtual bool OnInit();
    void OnTimer(wxTimerEvent & event);
};

#endif
