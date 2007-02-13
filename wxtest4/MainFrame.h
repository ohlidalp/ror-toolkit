#ifndef MAINFRAME_H_
#define MAINFRAME_H_

// For compilers that don't support precompilation, include "wx/wx.h"
 #include "wx/wxprec.h"
 #ifndef WX_PRECOMP
     #include "wx/wx.h"
 #endif

class MainFrame : public wxFrame {
    public:
        /** Constructor, Creates a new MainFrame */
        MainFrame(const wxChar *title, int xpos, int ypos, int width, int height);
     
        /** Destructor */
        ~MainFrame();
        
    private:
        //wxTextCtrl *m_pTextCtrl;
        void GenerateMenus();
        
        /** Process menu File>Open */
        void OnMenuFileOpen(wxCommandEvent &event);
        
        /** Process menu File>Save */
        void OnMenuFileSave(wxCommandEvent &event);
        
        /** Process menu File>Quit */
        void OnMenuFileQuit(wxCommandEvent &event);
        
        /** Process menu About>Info */
        void OnMenuHelpAbout(wxCommandEvent &event);
        
    protected:
        DECLARE_EVENT_TABLE()
};

#endif /*MAINFRAME_H_*/
