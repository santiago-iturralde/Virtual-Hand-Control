import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np

# 1. Configuración de la cámara
cap = cv2.VideoCapture(0) # '0' suele ser la webcam integrada

# Validar que la cámara se abrió correctamente
if not cap.isOpened():
    print("ERROR: No se pudo abrir la cámara.")
    exit(1)

# Establecer propiedades de la cámara para mejor rendimiento
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# 2. Cargar el modelo de manos
mp_hands = solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,            # Solo queremos detectar 1 mano para controlar el mouse
    min_detection_confidence=0.7 # Exigente (70%) para que no tiemble
)
mp_drawing = solutions.drawing_utils # Utilidad para dibujar los palitos
mp_drawing_styles = solutions.drawing_styles

print("Iniciando cámara... Pulsa 'Esc' para salir.")

while True:
    # Leer frame de la cámara
    success, image = cap.read()
    if not success: 
        print("ERROR: No se pudo leer el frame de la cámara.")
        break

    # Invertir imagen horizontalmente (efecto espejo, es más natural)
    image = cv2.flip(image, 1)
    
    h, w, c = image.shape

    # Convertir de BGR (OpenCV) a RGB (MediaPipe)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # PROCESAR LA IMAGEN 
    results = hands.process(image_rgb)

    # Si encontró manos...
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            try:
                # Dibujar los nodos y conexiones por defecto
                mp_drawing.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
                
                # Imprimir coordenada del dedo índice (ID 8) en consola
                # Accedemos al punto 8 de la lista
                dedo_indice = hand_landmarks.landmark[8]
                pixel_x = int(dedo_indice.x * w)
                pixel_y = int(dedo_indice.y * h)
                print(f"Indice X: {dedo_indice.x:.2f} | Indice Y: {dedo_indice.y:.2f} | Pixel X: {pixel_x} | Pixel Y: {pixel_y}")
            except Exception as e:
                print(f"Error procesando mano: {e}")

    # Mostrar ventana
    cv2.imshow('Prueba de Mano', image)

    # Salir con tecla ESC (código 27)
    if cv2.waitKey(5) & 0xFF == 27:
        print("Cerrando aplicación...")
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
print("Recursos liberados correctamente.")