/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#include "myRenderer.hh"
#include "myGLWindow.hh"

using namespace std;

myRenderer myRenderer::myInstance;

float myRenderer::myDistance = 3;
float myRenderer::myRotation = 0;


myRenderer::myRenderer()
{
}

myRenderer::~myRenderer()
{
}

void myRenderer::init(myGLWindow *glwindow)
{
  //printf("init\n");
  glwindow->SetCurrent();
  resize(glwindow);
  glShadeModel(GL_SMOOTH);                            // Enables Smooth Shading
  glClearColor(0.0f, 0.0f, 0.0f, 0.0f);               // Black Background
  glClearDepth(1.0f);                                 // Depth Buffer Setup
  glEnable(GL_DEPTH_TEST);                            // Enables Depth Testing
  glDepthFunc(GL_LEQUAL);                             // The Type Of Depth Test To Do
  glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);  // Really Nice Perspective Calculations
  glwindow->isInitiated = true;

  //init models
  createGrid();
}

void myRenderer::resize(myGLWindow *glwindow)
{
  //printf("resize\n");
  glwindow->SetCurrent();
  glViewport(0, 0, glwindow->getSize().GetWidth(), glwindow->getSize().GetHeight());
  glMatrixMode(GL_PROJECTION);              // Select The Projection Matrix
  glLoadIdentity();                         // Reset The Projection Matrix

  // Calculate The Aspect Ratio Of The Window
  // fov = 45 = normal
  gluPerspective(95.0f, (GLfloat)glwindow->getSize().GetWidth() / (GLfloat)glwindow->getSize().GetHeight(), 0.1f, 500.0f);

  glMatrixMode(GL_MODELVIEW);               // Select The Modelview Matrix
  glLoadIdentity();                         // Reset The Modelview Matrix
}

void myRenderer::createGrid()
{
  myGridGLList = glGenLists(1);
  glNewList(myGridGLList, GL_COMPILE);

  float gridsize = 10;
  float gridstep = 0.2;

  // red xz-grid
  glColor3f(0.5f,0.3f,0.3f);
  for (float a=-gridsize;a<gridsize;a=a+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f(-gridsize,0, a);
    glVertex3f(gridsize, 0, a);
    glEnd();
  }
  for (float a=-gridsize;a<gridsize;a=a+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f(a, 0, -gridsize);
    glVertex3f(a, 0, gridsize);
    glEnd();
  }

  // green yz-grid
  glColor3f(0.3f,0.5f,0.3f);
  for (float a=-gridsize;a<gridsize;a=a+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f(0, -gridsize, a);
    glVertex3f(0, gridsize, a);
    glEnd();
  }
  for (float a=-gridsize;a<gridsize;a=a+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f(0, a, -gridsize);
    glVertex3f(0, a, gridsize);
    glEnd();
  }

  // blue xy-grid
  glColor3f(0.3f,0.3f,0.5f);
  for (float a=-gridsize;a<gridsize;a=a+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f(-gridsize, a, 0);
    glVertex3f(gridsize, a, 0);
    glEnd();
  }
  for (float a=-gridsize;a<gridsize;a=a+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f(a, -gridsize,0);
    glVertex3f(a, gridsize,0);
    glEnd();
  }
  glEndList();
}

void myRenderer::render(myGLWindow *glwindow)
{
  if (!glwindow->isInitiated)
    init(glwindow);

  glwindow->SetCurrent();

  // copy & paste of http://nehe.gamedev.net/data/lessons/lesson.asp?lesson=05

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	// Clear The Screen And The Depth Buffer

  glLoadIdentity();


  //glLoadIdentity(); // Reset The View
  //glTranslatef(1.5f,0.0f,-7.0f);				// Move Right And Into The Screen

  glTranslatef(0,0,-myDistance);				// Move Left And Into The Screen
  glRotatef(glwindow->rota, glwindow->rotx, glwindow->roty, glwindow->rotz);
  glRotatef(myRotation,1.0f,0.0f,0.0f);			// Rotate The Cube On X, Y & Z
  glCallList(myGridGLList);


  glBegin(GL_QUADS);					// Start Drawing The Cube
    glColor3f(0.0f,1.0f,0.0f);			// Set The Color To Green
    glVertex3f( 1.0f, 1.0f,-1.0f);			// Top Right Of The Quad (Top)
    glVertex3f(-1.0f, 1.0f,-1.0f);			// Top Left Of The Quad (Top)
    glVertex3f(-1.0f, 1.0f, 1.0f);			// Bottom Left Of The Quad (Top)
    glVertex3f( 1.0f, 1.0f, 1.0f);			// Bottom Right Of The Quad (Top)

    glColor3f(1.0f,0.5f,0.0f);			// Set The Color To Orange
    glVertex3f( 1.0f,-1.0f, 1.0f);			// Top Right Of The Quad (Bottom)
    glVertex3f(-1.0f,-1.0f, 1.0f);			// Top Left Of The Quad (Bottom)
    glVertex3f(-1.0f,-1.0f,-1.0f);			// Bottom Left Of The Quad (Bottom)
    glVertex3f( 1.0f,-1.0f,-1.0f);			// Bottom Right Of The Quad (Bottom)

    glColor3f(1.0f,0.0f,0.0f);			// Set The Color To Red
    glVertex3f( 1.0f, 1.0f, 1.0f);			// Top Right Of The Quad (Front)
    glVertex3f(-1.0f, 1.0f, 1.0f);			// Top Left Of The Quad (Front)
    glVertex3f(-1.0f,-1.0f, 1.0f);			// Bottom Left Of The Quad (Front)
    glVertex3f( 1.0f,-1.0f, 1.0f);			// Bottom Right Of The Quad (Front)

    glColor3f(1.0f,1.0f,0.0f);			// Set The Color To Yellow
    glVertex3f( 1.0f,-1.0f,-1.0f);			// Bottom Left Of The Quad (Back)
    glVertex3f(-1.0f,-1.0f,-1.0f);			// Bottom Right Of The Quad (Back)
    glVertex3f(-1.0f, 1.0f,-1.0f);			// Top Right Of The Quad (Back)
    glVertex3f( 1.0f, 1.0f,-1.0f);			// Top Left Of The Quad (Back)

    glColor3f(1.0f,0.0f,1.0f);			// Set The Color To Violet
    glVertex3f( 1.0f, 1.0f,-1.0f);			// Top Right Of The Quad (Right)
    glVertex3f( 1.0f, 1.0f, 1.0f);			// Top Left Of The Quad (Right)
    glVertex3f( 1.0f,-1.0f, 1.0f);			// Bottom Left Of The Quad (Right)
    glVertex3f( 1.0f,-1.0f,-1.0f);			// Bottom Right Of The Quad (Right)
  glEnd();						// Done Drawing The Quad

  rtri += myRotationSpeed;						// Increase The Rotation Variable For The Triangle
  rquad -= myRotationSpeed;						// Decrease The Rotation Variable For The Quad

  glwindow->SwapBuffers();
}
