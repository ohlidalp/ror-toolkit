/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#ifndef MYRENDERERHH
#define MYRENDERERHH

#include "wx/wx.h"
#include "wx/glcanvas.h"
#include "GL/gl.h"
#include "GL/glu.h"

class myGLWindow;
class mySpinCtrl;

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

    static float myDistance, myRotation;

  protected:
    myRenderer();

  public:
    inline static myRenderer& getInstance() { return myInstance; };

    virtual ~myRenderer();
    void init(myGLWindow *glwindow);
    void render(myGLWindow *glwindow);
    void resize(myGLWindow *glwindow);


    static void setRotation(float value) { myRotation = value; };
    static void setDistance(float value) { myDistance = value; };
};

#endif
