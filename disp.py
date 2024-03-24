import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def load_obj(filename):
    vertices = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertices.append(list(map(float, line.strip().split()[1:])))
    return vertices

def draw_obj(vertices):
    glBegin(GL_POINTS)
    for vertex in vertices:
        glVertex3fv(vertex)
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    vertices = load_obj("monkey.obj")

    rotate_x = 0
    rotate_y = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rotate_y = -1
                elif event.key == pygame.K_RIGHT:
                    rotate_y = 1
                elif event.key == pygame.K_UP:
                    rotate_x = -1
                elif event.key == pygame.K_DOWN:
                    rotate_x = 1
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
            else:
                rotate_x = 0
                rotate_y = 0

        glRotatef(rotate_x, 1, 0, 0)
        glRotatef(rotate_y, 0, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_obj(vertices)
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()