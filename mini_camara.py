import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import math
import time

# --- CONFIGURACIÓN ---
pyautogui.FAILSAFE = False 
SMOOTHING = 5           
JITTER_THRESHOLD = 3    
CLICK_THRESHOLD = 40    
CLICK_COOLDOWN = 0.5    

# --- INICIALIZACIÓN DE MEDIAPIPE ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

# --- VARIABLES GLOBALES ---
current_camera_index = 0
cap = None
screen_w, screen_h = pyautogui.size()
frame_r = 100 
nombre_ventana = "Control IA - (Presiona 'C' para cambiar camara)"

# Variables de movimiento
plocX, plocY = 0, 0
clocX, clocY = 0, 0
last_click_time = 0

def iniciar_camara(index):
    """Función para cambiar de cámara de forma segura"""
    global cap
    if cap is not None:
        cap.release()
    
    print(f"Intentando abrir cámara {index}...")
    # Probamos DSHOW para Windows (más rápido)
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    
    # Si falla, probamos el método normal
    if not cap.isOpened():
        cap = cv2.VideoCapture(index)
    
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return True
    return False

# Iniciamos con la cámara 0
if not iniciar_camara(current_camera_index):
    # Si la 0 falla, intentamos la 1 automáticamente
    current_camera_index = 1
    iniciar_camara(current_camera_index)

# Configuración de la Ventana Flotante
cv2.namedWindow(nombre_ventana, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(nombre_ventana, cv2.WND_PROP_TOPMOST, 1)
cv2.resizeWindow(nombre_ventana, 320, 240)

print("\n---------------------------------------")
print("🚀 SISTEMA INICIADO")
print("👉 Si ves la pantalla negra, presiona la tecla 'C' para cambiar de cámara.")
print("👉 Presiona 'Q' para salir.")
print("---------------------------------------\n")

while True:
    if cap is None or not cap.isOpened():
        # Si no hay cámara, mostramos una imagen negra y esperamos
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "NO CAMARA", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        success, image = cap.read()
        if not success:
            image = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            # 1. Procesamiento de imagen
            image = cv2.flip(image, 1)
            h, w, c = image.shape
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)
            
            # Dibujar cuadro guía
            cv2.rectangle(image, (frame_r, frame_r), (w - frame_r, h - frame_r), (255, 0, 255), 2)
            
            # Información en pantalla
            cv2.putText(image, f"CAM: {current_camera_index}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
            cv2.putText(image, "[C] Cambiar", (10, h - 10), cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 200), 1)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Puntos clave
                    indice = hand_landmarks.landmark[8]
                    pulgar = hand_landmarks.landmark[4]
                    medio = hand_landmarks.landmark[12]
                    nudillo_medio = hand_landmarks.landmark[10]

                    x1, y1 = int(indice.x * w), int(indice.y * h)
                    x2, y2 = int(pulgar.x * w), int(pulgar.y * h)
                    
                    # --- CLICK ---
                    distancia = math.hypot(x1 - x2, y1 - y2)
                    click_activo = False
                    
                    if distancia < CLICK_THRESHOLD:
                        cv2.circle(image, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                        click_activo = True
                        if time.time() - last_click_time > CLICK_COOLDOWN:
                            pyautogui.click()
                            last_click_time = time.time()
                    
                    # --- MOVER ---
                    # Solo movemos si el dedo medio está ABAJO (y > nudillo)
                    if not click_activo and medio.y > nudillo_medio.y:
                        target_x = np.interp(indice.x * w, (frame_r, w - frame_r), (0, screen_w))
                        target_y = np.interp(indice.y * h, (frame_r, h - frame_r), (0, screen_h))
                        
                        dist_movimiento = math.hypot(target_x - plocX, target_y - plocY)
                        if dist_movimiento > JITTER_THRESHOLD:
                            clocX = plocX + (target_x - plocX) / SMOOTHING
                            clocY = plocY + (target_y - plocY) / SMOOTHING
                            pyautogui.moveTo(clocX, clocY)
                            plocX, plocY = clocX, clocY

    # Mostrar la ventanita
    cv2.imshow(nombre_ventana, image)

    # --- CONTROLES DE TECLADO ---
    key = cv2.waitKey(1) & 0xFF
    
    # Tecla 'Q' para salir
    if key == ord('q'):
        break
    
    # Tecla 'C' para CAMBIAR CÁMARA
    if key == ord('c'):
        current_camera_index += 1
        # Intentamos abrir la siguiente. Si falla, volvemos a la 0
        if not iniciar_camara(current_camera_index):
            current_camera_index = 0
            iniciar_camara(current_camera_index)

cap.release()
cv2.destroyAllWindows()