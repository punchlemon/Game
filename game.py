import cv2
import numpy as np

def load_3d_object_data(filename):
    with open(filename, 'r') as f:
        vertices = []
        for line in f:
            vertex = [float(coord) for coord in line.split()]
            vertices.append(vertex)
    return np.array(vertices, dtype=np.float32)

def draw_3d_object(vertices, observer_position, angle_x, angle_y, angle_z):
    # ウィンドウを作成します
    cv2.namedWindow('3D Object', cv2.WINDOW_NORMAL)
    
    # 3Dオブジェクトを描画します
    while True:
        img = np.ones((800, 800, 3), dtype=np.uint8) * 255
        
        # 3Dオブジェクトを回転させます
        rotation_matrix_x = rotation_matrix(angle_x, 0, 0)
        rotation_matrix_y = rotation_matrix(0, angle_y, 0)
        rotation_matrix_z = rotation_matrix(0, 0, angle_z)
        rotated_vertices = np.dot(vertices, rotation_matrix_x)
        rotated_vertices = np.dot(rotated_vertices, rotation_matrix_y)
        rotated_vertices = np.dot(rotated_vertices, rotation_matrix_z)
        
        # 観測者の座標を考慮して、視点を設定します
        eye = np.array([0, 0, -5], dtype=np.float32) + observer_position
        
        # 3Dオブジェクトを描画します
        for face in faces:
            points = np.array([rotated_vertices[idx][:2] * 100 + [400, 400] for idx in face], dtype=np.int32)
            cv2.polylines(img, [points], True, (0, 0, 0), 2)
        
        # ウィンドウに画像を表示します
        cv2.imshow('3D Object', img)
        
        # キーボード入力を処理します
        key = cv2.waitKey(10)
        if key != -1:
            if key == ord('q'):  # 'q'を押すと終了します
                break
            elif key == ord('w'):  # 'w'を押すと観測者を前に移動します
                observer_position[2] += 0.1
            elif key == ord('s'):  # 's'を押すと観測者を後ろに移動します
                observer_position[2] -= 0.1
            elif key == ord('a'):  # 'a'を押すと観測者を左に移動します
                observer_position[0] -= 0.1
            elif key == ord('d'):  # 'd'を押すと観測者を右に移動します
                observer_position[0] += 0.1
            elif key == 2:  # 左矢印を押すと視点を左に回転します
                angle_y += 0.1
            elif key == 3:  # 右矢印を押すと視点を右に回転します
                angle_y -= 0.1
            elif key == 0:  # 上矢印を押すと視点を上に回転します
                angle_x += 0.1
            elif key == 1:  # 下矢印を押すと視点を下に回転します
                angle_x -= 0.1
        
    # すべてのウィンドウを閉じます
    cv2.destroyAllWindows()

# 回転行列を作成する関数を定義します
def rotation_matrix(angle_x, angle_y, angle_z):
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(angle_x), -np.sin(angle_x)],
                   [0, np.sin(angle_x), np.cos(angle_x)]], dtype=np.float32)
    Ry = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                   [0, 1, 0],
                   [-np.sin(angle_y), 0, np.cos(angle_y)]], dtype=np.float32)
    Rz = np.array([[np.cos(angle_z), -np.sin(angle_z), 0],
                   [np.sin(angle_z), np.cos(angle_z), 0],
                   [0, 0, 1]], dtype=np.float32)
    return np.dot(Rz, np.dot(Ry, Rx))

# 3Dオブジェクトの面を定義します
faces = [(0, 1, 2, 3),    # 前面
         (4, 5, 6, 7),    # 後面
         (0, 3, 7, 4),    # 左面
         (1, 2, 6, 5),    # 右面
         (0, 1, 5, 4),    # 底面
         (2, 3, 7, 6)]    # 上面

# 観測者の座標と視点の角度を初期化します
observer_position = np.array([0, 0, 0], dtype=np.float32)  # 観測者の座標
angle_x, angle_y, angle_z = 0.1, 0.1, 0  # 視点の角度

# 3Dオブジェクトのデータをファイルから読み込みます
filename = '3d_object_data.txt'
vertices = load_3d_object_data(filename)

# 3Dオブジェクトを描画して表示します
draw_3d_object(vertices, observer_position, angle_x, angle_y, angle_z)
