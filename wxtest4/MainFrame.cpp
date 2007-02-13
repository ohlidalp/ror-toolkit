#include "MainFrame.h"

MainFrame::MainFrame(  
    const wxChar *title,
    int xpos,
    int ypos, 
    int width,
    int height)
    :
    wxFrame(
        (wxFrame *) NULL,
        -1,
        title,
        wxPoint(xpos, ypos),
        wxSize(width, height)){
            
    /*m_pTextCtrl = new wxTextCtrl(this,
                                -1,
                                wxString(wxT("this is m_pTextXtrl")),
                                wxDefaultPosition,
                                wxDefaultSize,
                                wxTE_MULTILINE);*/
    
    GenerateMenus();
    //Layout();
}

MainFrame::~MainFrame(){}

void MainFrame::GenerateMenus(){
    wxMenuBar *m_pMenuBar = new wxMenuBar();
    wxMenu *m_pFileMenu = new wxMenu();
    wxMenu *m_pHelpMenu = new wxMenu();
    
    //  File Menu
    m_pFileMenu->Append(wxID_OPEN, _T("&Open"));
    m_pFileMenu->Append(wxID_SAVE, _T("&Save"));   
    m_pFileMenu->AppendSeparator();
    m_pFileMenu->Append(wxID_EXIT, _T("&Quit"));
    m_pMenuBar->Append(m_pFileMenu, _T("&File"));    
    //  About Menu
    m_pHelpMenu->Append(wxID_ABOUT, _T("&About"));
    m_pMenuBar->Append(m_pHelpMenu, _T("&Help"));
    
    SetMenuBar(m_pMenuBar);
}
// If you're doing an application by inheriting from wxApp
// be sure to change wxFrame to wxApp (or whatever component
// you've inherited your class from).
BEGIN_EVENT_TABLE(MainFrame, wxFrame)
    EVT_MENU(wxID_OPEN, MainFrame::OnMenuFileOpen)
    EVT_MENU(wxID_SAVE, MainFrame::OnMenuFileSave)
    EVT_MENU(wxID_EXIT, MainFrame::OnMenuFileQuit)
    EVT_MENU(wxID_ABOUT, MainFrame::OnMenuHelpAbout)
END_EVENT_TABLE()

/** Process menu File>Open */
void MainFrame::OnMenuFileOpen(wxCommandEvent &event){
}

/** Process menu File>Save */
void MainFrame::OnMenuFileSave(wxCommandEvent &event){
    
}

/** Process menu File>Quit */
void MainFrame::OnMenuFileQuit(wxCommandEvent &event){
    Close(false);
}

/** Process menu About>Info */
void MainFrame::OnMenuHelpAbout(wxCommandEvent &event){
    wxLogMessage(_T("The Simple Text Editor/wxWidgets Tutorial"));
}
