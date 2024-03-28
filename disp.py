import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

class Object:
    def __init__(self, position=[0, 0, 0], angle=[0, 0, 0]):
        self.position = position
        self.angle = angle
    def rotate(self, add_angle):
        self.angle = [x + y for x, y in zip(self.angle, add_angle)]
    def transfer(self, add_position):
        self.position = [x + y for x, y in zip(self.position, add_position)]

class Thing(Object):
    def __init__(self, filename, position=[0, 0, -5], angle=[0, 0, 0]):
        super().__init__(position, angle)
        self.filename = filename
        self.vertices, self.faces, self.normals = self.load_obj()
    def load_obj(self):
        vertices = []
        faces = []
        normals = []
        with open(self.filename, 'r') as f:
            for line in f:
                if line.startswith('v '):
                    vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith('f '):
                    face = [int(vertex.split('/')[0]) - 1 for vertex in line.strip().split()[1:]]
                    if len(face) == 4:  # 4つの頂点からなる面を三角形に分割
                        faces.append([face[0], face[1], face[2]])
                        faces.append([face[0], face[2], face[3]])
                    else:
                        faces.append(face)
        for face in faces: # calculate normals
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            normal = np.cross(v2 - v1, v3 - v1)
            normals.append(normal / np.linalg.norm(normal))
        return vertices, faces, normals # return values
    def disp(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.angle[0], 1, 0, 0)  # x軸周りの回転
        glRotatef(self.angle[1], 0, 1, 0)  # y軸周りの回転
        glRotatef(self.angle[2], 0, 0, 1)  # z軸周りの回転
        for i, face in enumerate(self.faces):
            glBegin(GL_TRIANGLES)
            glNormal3fv(self.normals[i])
            for vertex_id in face:
                glVertex3fv(self.vertices[vertex_id])
            glEnd()
        glPopMatrix()

class Light(Object):
    def __init__(self, position=[1, 1, 2], angle=[0, 0, 0], diffuse=[1, 1, 1, 1]):
        super().__init__(position, angle)
        self.diffuse = diffuse    # 光の強度
        self.light_id = None
    def disp(self):
        glPushMatrix()
        glTranslatef(*self.position)
        self.light_id = GL_LIGHT0
        glEnable(GL_LIGHTING)
        glEnable(self.light_id)
        glLightfv(self.light_id, GL_POSITION, self.position + [1])
        glLightfv(self.light_id, GL_DIFFUSE, self.diffuse)
        quadric = gluNewQuadric()  # 新しい球体オブジェクトを生成
        gluSphere(quadric, 0.1, 30, 30)  # 半径0.5の球を描画
        glPopMatrix()
    def disable(self):
        glDisable(self.light_id)

class Camera(Object):
    def __init__(self, position=[0, 0, 3], angle=[0, 0, 0]):
        super().__init__(position, angle)
    def enable(self):
        glPushMatrix()
        self.eye = self.position
        self.center = [self.position[i] + np.cos(np.radians(self.angle[i])) for i in range(3)]
        self.up = [0, 1, 0]
        gluLookAt(*self.eye, *self.center, *self.up)
        glPopMatrix()

def draw_obj(things, lights, camera):
    camera.enable()
    for light in lights:
        light.disp()
    for thing in things:
        thing.disp()
    for light in lights:
        light.disable()

def change_target(target_number, objects_length):
    target_number += 1
    if target_number == objects_length:
        target_number = 0
    return target_number

def main():
    camera = Camera(position=[0, 0, -3])
    lights = [Light(position=[0, -0.38, -1.3], diffuse=[1, 1, 1, 1])]
    things = [Thing("monkey.obj")]
    objects = [camera] + lights + things
    objects_length = len(objects)
    target_number = 0

    pygame.init()
    display = (500, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glEnable(GL_DEPTH_TEST)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    angle_x = 0
    angle_y = 0
    position_x = 0
    position_y = 0
    position_z = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    angle_y = -1
                elif event.key == pygame.K_RIGHT:
                    angle_y = 1
                elif event.key == pygame.K_UP:
                    angle_x = -1
                elif event.key == pygame.K_DOWN:
                    angle_x = 1
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_TAB:
                    target_number = change_target(target_number, objects_length)
                elif event.key == pygame.K_s:
                    position_z = -0.01
                elif event.key == pygame.K_w:
                    position_z = 0.01
                elif event.key == pygame.K_e:
                    position_y = -0.01
                elif event.key == pygame.K_q:
                    position_y = 0.01
                elif event.key == pygame.K_d:
                    position_x = -0.01
                elif event.key == pygame.K_a:
                    position_x = 0.01
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    angle_y = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    angle_x = 0
                elif event.key == pygame.K_s or event.key == pygame.K_w:
                    position_z = 0
                elif event.key == pygame.K_q or event.key == pygame.K_e:
                    position_y = 0
                elif event.key == pygame.K_a or event.key == pygame.K_d:
                    position_x = 0

        objects[target_number].rotate((angle_x, angle_y, 0))
        objects[target_number].transfer((-position_x, -position_y, -position_z))

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_obj(things, lights, camera)
        pygame.display.flip()
        pygame.time.wait(10)
        for object in objects:
            print(object.position, end="")
        print()

if __name__ == "__main__":
    main()
