/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYRENDERERHH
#define MYRENDERERHH

#include "wx/wx.h"
#include "wx/xrc/xmlres.h"
#include "wx/notebook.h"
#include "wx/glcanvas.h"
#include "GL/gl.h"
#include "GL/glu.h"

#include "myGLWindow.hh"
#include "mySpinCtrl.hh"

class myRenderer
{
  private:
    static myRenderer myInstance;

    GLfloat myRotationSpeed;
    GLfloat rtri, rquad;
    myRenderer(const myRenderer&);
    myRenderer &operator=(const myRenderer&);

    int myGridGLList;
    void createGrid();

  protected:
    myRenderer();

  public:
    inline static myRenderer& getInstance() { return myInstance; };

    virtual ~myRenderer();
    void init(myGLWindow *glwindow);
    void render(myGLWindow *glwindow);
    void resize(myGLWindow *glwindow);


    void setRotationSpeed(float value) { myRotationSpeed = value; };
    float getRotationSpeed(void) { return myRotationSpeed; };
};

#endif
