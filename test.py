import glfw
from OpenGL.GL import *
import numpy as np

class Object:
    def __init__(self, position=[0, 0, 0], angle=[0, 0, 0]):
        self.position = np.array(position, dtype=np.float32)
        self.angle = np.array(angle, dtype=np.float32)
        self.velocity = np.array([0, 0, 0], dtype=np.float32)

    def rotate(self, rotation_angle):
        self.angle += rotation_angle

    def move(self, moving_speed):
        self.position += moving_speed

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
                    if len(face) == 4:  # Triangulate quads
                        faces.append([face[0], face[1], face[2]])
                        faces.append([face[0], face[2], face[3]])
                    else:
                        faces.append(face)
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            normal = np.cross(v2 - v1, v3 - v1)
            normals.append(normal / np.linalg.norm(normal))
        return vertices, faces, normals

    def disp(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.angle[0], 1, 0, 0)
        glRotatef(self.angle[1], 0, 1, 0)
        glRotatef(self.angle[2], 0, 0, 1)
        for i, face in enumerate(self.faces):
            glBegin(GL_TRIANGLES)
            glNormal3fv(self.normals[i])
            for vertex_id in face:
                glVertex3fv(self.vertices[vertex_id])
            glEnd()
        glPopMatrix()

class Light(Object):
    def __init__(self, position=[0, -3.8, -1.3], diffuse=[1, 1, 1, 1]):
        super().__init__(position)
        self.diffuse = diffuse

    def setup(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [*self.position, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glPopMatrix()
    def disable(self):
        glDisable(GL_LIGHT0)

class Camera:
    def __init__(self, position=[0, 0, 0], angle=[0, 0, 0]):
        self.position = np.array(position, dtype=np.float32)
        self.angle = np.array(angle, dtype=np.float32)
        self.center = np.array([0, 0, -10], dtype=np.float32)
        self.up = np.array([0, 1, 0], dtype=np.float32)

    def move(self, moving_speed):
        forward = self.center - self.position
        forward /= np.linalg.norm(forward)
        self.position += forward * moving_speed[2]
        self.center += forward * moving_speed[2]

        right = np.cross(forward, self.up)
        right /= np.linalg.norm(right)
        self.position += right * moving_speed[0]
        self.center += right * moving_speed[0]

        self.position += self.up * moving_speed[1]
        self.center += self.up * moving_speed[1]

    def lookAt(self):
        matrix = np.identity(4, dtype=np.float32)
        forward = self.center - self.position
        forward /= np.linalg.norm(forward)
        side = np.cross(forward, self.up)
        side /= np.linalg.norm(side)
        up = np.cross(side, forward)

        matrix[0, :3] = side
        matrix[1, :3] = up
        matrix[2, :3] = -forward

        glMultMatrixf(matrix.T)

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

angle = [0, 0, 0]
position = [0, 0, 0]

def main():
    global angle, position
    if not glfw.init():
        return

    window = glfw.create_window(500, 600, "OpenGL Window", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)

    thing = Thing("monkey.obj")
    light = Light()
    camera = Camera()

    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        thing.move(position)
        thing.rotate(angle)

        light.setup()

        glLoadIdentity()
        # camera.move(position)
        camera.lookAt()

        thing.disp()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
