/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */
#include "myApp.hh"

bool myApp::OnInit()
{
  //wxFrame* frame = new wxFrame((wxFrame *)NULL, -1,  _("Hello GL World"), wxPoint(50,50), wxSize(800,600) );
  MainFrame *frame = new MainFrame(wxT("RoREditor"), 100, 100, 800, 600);

  wxBoxSizer *sizer = new wxBoxSizer(wxHORIZONTAL);

  wxStaticBoxSizer *panel0 = new wxStaticBoxSizer(wxVERTICAL, frame, _("Information") );
  sizer->Add(panel0, 0, 0, 0);
  
  // GRID
  wxGridSizer *item0 = new wxGridSizer( 2, 1, 1 );


  MyGLCanvas1 = new myGLWindow(frame, -1, wxPoint(-1,-1), wxSize(30,30), wxSUNKEN_BORDER, _("some text"));
  item0->Add( MyGLCanvas1, 1, wxEXPAND, 0);
  //MyGLCanvas1->SetCurrent();
  MyGLCanvas1->gllist = glGenLists(1);
  MyGLCanvas1->SetToolTip(_T("MyGLCanvas1"));
  glNewList(MyGLCanvas1->gllist, GL_COMPILE);
    glRotatef(90 ,0.0f, 1.0f, 0.0f);
  glEndList();

  MyGLCanvas2 = new myGLWindow(frame, -1, wxPoint(-1,-1), wxSize(30,30), wxSUNKEN_BORDER, _("some text"));
  MyGLCanvas2->setRotation(0,1,0);
  item0->Add( MyGLCanvas2, 1, wxEXPAND, 0 );
  MyGLCanvas2->SetToolTip(_T("MyGLCanvas2"));
  //MyGLCanvas2->SetCurrent();
  MyGLCanvas2->gllist = glGenLists(1);
  glNewList(MyGLCanvas2->gllist, GL_COMPILE);
    glRotatef(90 ,1.0f, 0.0f, 0.0f);
  glEndList();

  MyGLCanvas3 = new myGLWindow(frame, -1, wxPoint(-1,-1), wxSize(30,30), wxSUNKEN_BORDER, _("some text"));
  MyGLCanvas3->setRotation(4,0,0);
  item0->Add( MyGLCanvas3, 1, wxEXPAND, 0 );
  MyGLCanvas4->SetToolTip(_T("MyGLCanvas3"));
  //MyGLCanvas3->SetCurrent();

  MyGLCanvas4 = new myGLWindow(frame, -1, wxPoint(-1,-1), wxSize(30,30), wxSUNKEN_BORDER, _("some text"));
  MyGLCanvas4->setRotation(0,0,0);
  item0->Add( MyGLCanvas4, 1, wxEXPAND, 0 );
  MyGLCanvas4->SetToolTip(_T("MyGLCanvas4"));
  //MyGLCanvas4->SetCurrent();


  // PANEL
  wxStaticText *text1 = new wxStaticText(frame, -1, _("Rotation Speed"), wxDefaultPosition, wxDefaultSize, 0, _("StaticText"));
  panel0->Add(text1, 0, 0, 0);
  spin1 = new mySpinCtrl(frame, -1, MyGLCanvas1, _("Spin-Control"), -600, 600, 30);
  panel0->Add(spin1, 0, 0, 0);


  sizer->Add(item0, 1, wxEXPAND, 0);
  frame->SetSizer(sizer);
  frame->Show(TRUE);

  //frame->SetSizer(item0);
/*  wxNotebook* book = new wxNotebook(frame, -1, wxPoint(-1,-1), wxSize(200,200));

  GL_Window* MyGLCanvas1 = new GL_Window(1, book, -1, wxPoint(-1,-1), wxSize(200,200), wxSUNKEN_BORDER, _("some text"));
  book->AddPage(MyGLCanvas1, _("One"));

  GL_Window* MyGLCanvas2 = new GL_Window(0, book, -1, wxPoint(-1,-1), wxSize(200,200), wxSUNKEN_BORDER, _("some text"));
  book->AddPage(MyGLCanvas2, _("Two"));

  GL_Window* MyGLCanvas3 = new GL_Window(0, frame, -1, wxPoint(-1,-1), wxSize(200,200), wxSUNKEN_BORDER, _("some text"));

  wxBoxSizer *sizer = new wxBoxSizer(wxVERTICAL);
  sizer->Add(book, 0, 0, 0);
  sizer->Add(MyGLCanvas3, 0, 0, 0);

  frame->SetSizer(sizer);*/

  // initiate timer


  myTimer = new wxTimer(this);
  myTimer->Start(5);

  return TRUE;
}

void myApp::OnTimer(wxTimerEvent & event)
{
  static float u = 0;
  u = u + 1;
  MyGLCanvas1->setRotation(0,0,u);

  MyGLCanvas1->draw();
  MyGLCanvas2->draw();
  MyGLCanvas3->draw();
  MyGLCanvas4->draw();
}

BEGIN_EVENT_TABLE(myApp, wxApp)
    EVT_TIMER(-1, myApp::OnTimer)
END_EVENT_TABLE()


IMPLEMENT_APP(myApp)
