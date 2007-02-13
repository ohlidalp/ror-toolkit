/* see gpl.txt */
/* Thomas Fischer, thomas@thomasfischer.biz, 2006 */

#include "myRenderer.hh"
#include "myGLWindow.hh"


myRenderer myRenderer::myInstance;

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

  //y-grid
  float gridsize = 10;
  float gridstep = 0.2;
  glColor3f(0.5f,0.3f,0.3f);
  for (float y=-gridsize;y<gridsize;y=y+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f( -gridsize,0, y);
    glVertex3f( gridsize,0 , y);
    glEnd();
  }
  for (float x=-gridsize;x<gridsize;x=x+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f( x, 0, -gridsize);
    glVertex3f( x, 0, gridsize);
    glEnd();
  }

  //x-grid
  glColor3f(0.3f,0.5f,0.3f);
  for (float y=-gridsize;y<gridsize;y=y+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f( 0,-gridsize, y);
    glVertex3f( 0,gridsize , y);
    glEnd();
  }
  for (float x=-gridsize;x<gridsize;x=x+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f( 0,x,  -gridsize);
    glVertex3f( 0,x,  gridsize);
    glEnd();
  }

  //z-grid
  glColor3f(0.3f,0.3f,0.5f);
  for (float y=-gridsize;y<gridsize;y=y+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f( -gridsize, y,0);
    glVertex3f( gridsize , y,0);
    glEnd();
  }
  for (float x=-gridsize;x<gridsize;x=x+gridstep)
  {
    glBegin(GL_LINES);
    glVertex3f( x,  -gridsize,0);
    glVertex3f( x,  gridsize,0);
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

  glCallList(myGridGLList);

  glCallList(glwindow->gllist);


  //glLoadIdentity(); // Reset The View
  //glTranslatef(1.5f,0.0f,-7.0f);				// Move Right And Into The Screen

  glTranslatef(0,0,-3.0f);				// Move Left And Into The Screen
  glRotatef(rquad,1.0f,1.0f,1.0f);			// Rotate The Cube On X, Y & Z

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
