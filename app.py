import cv2
import mediapipe as mp
from mediapipe import solutions
import numpy as np
from flask import Flask, render_template, jsonify, request
import webbrowser
import base64
import pyautogui
import math
import time

# --- CONFIGURACIÓN ---
pyautogui.FAILSAFE = False 
SMOOTHING = 5           # Suavizado de movimiento
JITTER_THRESHOLD = 3    # Zona muerta para temblores
CLICK_THRESHOLD = 40    # Distancia en píxeles para considerar "Pellizco" (Click)
CLICK_COOLDOWN = 0.5    # Segundos de espera entre clicks (para no ametrallar)

app = Flask(__name__)

# --- VARIABLES GLOBALES ---
cap = None
hands = None
is_running = False
mp_drawing = None
mp_hands = None

# Variables de estado
plocX, plocY = 0, 0
clocX, clocY = 0, 0
last_click_time = 0     # Para controlar el tiempo entre clicks

def detect_cameras():
    cameras = []
    for i in range(3):
        try:
            cap_test = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap_test.isOpened():
                ret, _ = cap_test.read()
                if ret: cameras.append(i)
                cap_test.release()
        except: pass
    return cameras

def init_camera(camera_id):
    global cap
    if cap is not None: cap.release()
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW) 
    if not cap.isOpened(): cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap.isOpened()

def init_hands():
    global hands, mp_hands, mp_drawing
    mp_hands = solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    mp_drawing = solutions.drawing_utils

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/cameras', methods=['GET'])
def get_cameras(): return jsonify({'cameras': detect_cameras()})

@app.route('/api/start', methods=['POST'])
def start_stream():
    global is_running
    data = request.json
    if init_camera(int(data.get('camera', 0))):
        init_hands()
        is_running = True
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/stop', methods=['POST'])
def stop_stream():
    global is_running, cap
    is_running = False
    if cap is not None: cap.release()
    return jsonify({'success': True})

@app.route('/api/frame')
def get_frame():
    global cap, hands, is_running, plocX, plocY, clocX, clocY, last_click_time
    
    if not is_running or cap is None or not cap.isOpened():
        return jsonify({'success': False})
    
    success, image = cap.read()
    if not success: return jsonify({'success': False})
    
    image = cv2.flip(image, 1)
    h, w, c = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    hand_data = None
    screen_w, screen_h = pyautogui.size()
    frame_r = 120

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # --- PUNTOS CLAVE ---
            # 8: Punta Índice, 4: Punta Pulgar, 12: Punta Medio
            indice_x, indice_y = hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y
            pulgar_x, pulgar_y = hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y
            
            # Convertir a píxeles de la imagen de cámara
            px_indice = int(indice_x * w)
            py_indice = int(indice_y * h)
            px_pulgar = int(pulgar_x * w)
            py_pulgar = int(pulgar_y * h)
            
            # --- DETECCIÓN DE CLICK (PELLIZCO) ---
            # Calcular distancia entre Índice y Pulgar
            distancia_click = math.hypot(px_indice - px_pulgar, py_indice - py_pulgar)
            
            # Dibujar línea entre dedos
            color_linea = (255, 0, 0) # Azul por defecto
            
            click_detectado = False
            
            # Si los dedos están muy cerca -> CLICK
            if distancia_click < CLICK_THRESHOLD:
                cv2.circle(image, (px_indice, py_indice), 15, (0, 255, 0), cv2.FILLED)
                color_linea = (0, 255, 0) # Verde
                
                # Comprobamos el "Cooldown" (tiempo de espera)
                if time.time() - last_click_time > CLICK_COOLDOWN:
                    pyautogui.click()
                    last_click_time = time.time()
                    cv2.putText(image, "CLICK!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                click_detectado = True
                # ALERTA DE "IMÁN": Al hacer click, NO movemos el mouse (saltamos la lógica de movimiento)
                # Esto da la sensación de estabilidad.
            
            cv2.line(image, (px_indice, py_indice), (px_pulgar, py_pulgar), color_linea, 3)

            # --- LÓGICA DE MOVIMIENTO (Solo si NO estamos haciendo click) ---
            if not click_detectado:
                # Chequeo rápido: ¿Está el índice levantado y el medio abajo?
                # Simplificamos la lógica para mayor velocidad
                dedo_medio_y = hand_landmarks.landmark[12].y
                nudillo_medio_y = hand_landmarks.landmark[10].y
                
                # Si el dedo medio está abajo (y > nudillo en coordenadas de pantalla), movemos
                if dedo_medio_y > nudillo_medio_y:
                    
                    # Mapeo
                    x1 = np.interp(indice_x * w, (frame_r, w - frame_r), (0, screen_w))
                    y1 = np.interp(indice_y * h, (frame_r, h - frame_r), (0, screen_h))
                    
                    # Filtro de Temblor (Jitter)
                    if math.hypot(x1 - plocX, y1 - plocY) > JITTER_THRESHOLD:
                        clocX = plocX + (x1 - plocX) / SMOOTHING
                        clocY = plocY + (y1 - plocY) / SMOOTHING
                        
                        pyautogui.moveTo(clocX, clocY)
                        plocX, plocY = clocX, clocY

            hand_data = {'x': indice_x, 'y': indice_y}

    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'success': True, 'hand_data': hand_data, 'image': image_base64})

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)