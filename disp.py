from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import glfw

class Object:
    def __init__(self, position=[0, 0, 0], angle=[0, 0, 0]):
        self.position = position
        self.angle = angle
        self.verocity = [0, 0, 0]
    def rotate(self, rotation_angle):
        self.rotation_speed = rotation_angle
        self.angle = [x + y for x, y in zip(self.angle, rotation_angle)]
    def move(self, moving_speed):
        self.moving_speed = moving_speed
        self.position = [x + y for x, y in zip(self.position, moving_speed)]

class Thing(Object):
    def __init__(self, filename, position=[0, 0, 0], angle=[0, 0, 0]):
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
        return vertices, faces, normals
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
    def __init__(self, position=[0, 0, 5], angle=[0, 0, 0]):
        super().__init__(position, angle)
        self.center = [self.position[i] + np.cos(np.radians(self.angle[i])) for i in range(3)]
        self.center = [0, 0, -10]
        self.up = [0, 1, 0]
    def move(self, moving_speed):
        # glPushMatrix()
        # gluNewQuadric()
        super().move(moving_speed)
        self.eye = self.moving_speed
        self.center = [x + y for x, y in zip(self.center, moving_speed)]
        self.up = [0, 1, 0]
        gluLookAt(*self.eye, *self.center, *self.up)

def draw_obj(things, lights):
    for light in lights:
        light.disp()
    for thing in things:
        thing.disp()
    for light in lights:
        light.disable()
    # glPopMatrix()

def change_target():
    global target_number, objects_length
    target_number += 1
    if target_number == objects_length:
        target_number = 0

def key_callback(window, key, scancode, action, mods):
    global angle, position
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_LEFT:
            angle[1] = -1
        elif key == glfw.KEY_RIGHT:
            angle[1] = 1
        elif key == glfw.KEY_UP:
            angle[0] = -1
        elif key == glfw.KEY_DOWN:
            angle[0] = 1
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_TAB:
            change_target()
        elif key == glfw.KEY_S:
            position[2] = 0.01
        elif key == glfw.KEY_W:
            position[2] = -0.01
        elif key == glfw.KEY_E:
            position[1] = 0.01
        elif key == glfw.KEY_Q:
            position[1] = -0.01
        elif key == glfw.KEY_D:
            position[0] = 0.01
        elif key == glfw.KEY_A:
            position[0] = -0.01
    elif action == glfw.RELEASE:
        if key == glfw.KEY_LEFT or key == glfw.KEY_RIGHT:
            angle[1] = 0
        elif key == glfw.KEY_UP or key == glfw.KEY_DOWN:
            angle[0] = 0
        elif key == glfw.KEY_S or key == glfw.KEY_W:
            position[2] = 0
        elif key == glfw.KEY_Q or key == glfw.KEY_E:
            position[1] = 0
        elif key == glfw.KEY_A or key == glfw.KEY_D:
            position[0] = 0


    # partial_key_callback = partial(key_callback, angle, position, target_number, objects_length)
    glfw.set_key_callback(window, key_callback)  # コールバック関数を登録


angle = [0, 0, 0]
position = [0, 0, 0]
objects_length = 0
target_number = 0

def main():
    global angle, position, objects_length, target_number
    camera = Camera(position=[0, 0, 5])
    lights = [Light(position=[10, 0, 10], diffuse=[1, 1, 1, 1])]
    things = [Thing("monkey.obj")]
    objects = [camera] + lights + things
    objects_length = len(objects)

    if not glfw.init():
        return

    window = glfw.create_window(500, 600, "OpenGL Window", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, (500 / 600), 0.1, 50.0)

    # partial_key_callback = partial(key_callback, angle, position, target_number, objects_length)
    glfw.set_key_callback(window, key_callback)  # コールバック関数を登録
    gluLookAt(*camera.position, *camera.center, *camera.up)
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for i, object in enumerate(objects):
            if i == target_number:
                object.move(position)
                object.rotate(angle)
            else:
                object.move([0, 0, 0])
                object.rotate([0, 0, 0])
        draw_obj(things, lights)

        glfw.swap_buffers(window)
        glfw.poll_events()

        for object in objects:
            print(object.position, end="")
        print()

    glfw.terminate()

if __name__ == "__main__":
    main()
