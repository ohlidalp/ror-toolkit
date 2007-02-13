/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#include "myGLWindow.hh"
#include "myRenderer.hh"

myGLWindow::myGLWindow(wxWindow* parent, wxWindowID id, const wxPoint& pos,
                       const wxSize& size, long style, const wxString& name,
                       int* attribList, const wxPalette& palette) :
                      wxGLCanvas(parent, id, pos, size, style, name,
                                 attribList, palette),
                      isInitiated(false)
{
  mySize = size;
}

myGLWindow::~myGLWindow()
{
}

void myGLWindow::draw()
{
  myRenderer::getInstance().render(this);
}

void myGLWindow::OnSize(wxSizeEvent& event)
{
  mySize = event.GetSize();
  myRenderer::getInstance().resize(this);
  //is that needed?
  //  event.RequestMore();
}

// void myGLWindow::OnIdle(wxIdleEvent& event)
// {
//   //draw();
//   //event.RequestMore();
// }

BEGIN_EVENT_TABLE(myGLWindow, wxGLCanvas)
//  EVT_IDLE(myGLWindow::OnIdle)
  EVT_SIZE(myGLWindow::OnSize)
END_EVENT_TABLE()

