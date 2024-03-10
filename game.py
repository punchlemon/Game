import cv2
import numpy as np

# 立方体の頂点と面を定義します
vertices = np.array([[-1, -1, -1],
					 [ 1, -1, -1 ],
					 [ 1,  1, -1 ],
					 [-1,  1, -1 ],
					 [-1, -1,  1 ],
					 [ 1, -1,  1 ],
					 [ 1,  1,  1 ],
					 [-1,  1,  1 ]], dtype=np.float32)

faces = [(0, 1, 2, 3),    # 前面
		 (4, 5, 6, 7),    # 後面
		 (0, 3, 7, 4),    # 左面
		 (1, 2, 6, 5),    # 右面
		 (0, 1, 5, 4),    # 底面
		 (2, 3, 7, 6)]    # 上面

# 各面に対する色を定義します
colors = [(255, 0, 0),   # 赤 (BGR形式)
		  (0, 255, 0),   # 緑
		  (0, 0, 255),   # 青
		  (255, 255, 0), # シアン
		  (255, 0, 255), # マゼンタ
		  (0, 255, 255)] # イエロー

# ウィンドウを作成します
cv2.namedWindow('3D Object', cv2.WINDOW_NORMAL)

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

# 3Dオブジェクトを描画して回転させます
angle_x, angle_y, angle_z = 0, 0, 0
window_height = 800
window_width = 1280
while True:
	# ウィンドウを白でクリアします
	cv2.setWindowProperty('3D Object', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	img = np.ones((window_height, window_width, 3), dtype=np.uint8) * 255
	
	# 3Dオブジェクトを回転させます
	rotation_matrix_x = rotation_matrix(angle_x, 0, 0)
	rotation_matrix_y = rotation_matrix(0, angle_y, 0)
	rotation_matrix_z = rotation_matrix(0, 0, angle_z)
	
	rotated_vertices = np.dot(vertices, rotation_matrix_x)
	rotated_vertices = np.dot(rotated_vertices, rotation_matrix_y)
	rotated_vertices = np.dot(rotated_vertices, rotation_matrix_z)
	
	# 各面を描画します
	face_depths = []
	for i, face in enumerate(faces):
		# 面を形成する頂点を取得します
		points = np.array([rotated_vertices[idx][:2] * 100 + [window_width/2, window_height/2] for idx in face], dtype=np.int32)
		# 面ごとに異なる色を適用します
		cv2.fillConvexPoly(img, points, colors[i])
		# 面の奥行き（z座標の最小値）を計算します
		face_depths.append(np.min(rotated_vertices[face, 2]))

	# 面を奥行きでソートします（最も表面に近い面が最後に来るようにします）
	sorted_indices = np.argsort(face_depths)
	for idx in sorted_indices:
		face = faces[idx]
		points = np.array([rotated_vertices[idx][:2] * 100 + [window_width/2, window_height/2] for idx in face], dtype=np.int32)
		cv2.fillConvexPoly(img, points, colors[idx])

	
	# ウィンドウに画像を表示します
	cv2.imshow('3D Object', img)
	
	# キーボード入力を待ちます（10ミリ秒で待ちます）
	# 'q'が押されると、プログラムが終了します
	if cv2.waitKey(10) & 0xFF == ord('q'):
		break
	
	# 角度を更新します
	angle_x += 0.01
	angle_y += 0.01
	angle_z += 0.01

# すべてのウィンドウを閉じます
cv2.destroyAllWindows()
