<img width="1738" height="905" alt="ChatGPT Image 14 may 2026, 07_48_48 p m" src="https://github.com/user-attachments/assets/812678fe-a27d-48ae-9691-2f5c77cde475" />
# 🖱️ Virtual Hand Control - Interfaz por Visión Computacional

> **Sistema avanzado de control de sistema operativo sin contacto físico, utilizando seguimiento de manos en tiempo real (Hand Tracking) y filtros matemáticos de estabilización.**

![Project Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Tech Stack](https://img.shields.io/badge/Stack-Python%20%7C%20OpenCV%20%7C%20MediaPipe-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 📖 El Problema 
La interacción tradicional con la computadora requiere periféricos físicos (mouse, trackpad), lo cual puede ser una limitación en entornos donde el usuario no puede tocar el hardware (entornos estériles, industriales, o por accesibilidad). Los sistemas de control por cámara suelen sufrir de dos grandes problemas:
1. **Latencia Alta:** Retraso entre el movimiento de la mano y el cursor.
2. **Jittering (Temblor):** El cursor salta de un píxel a otro constantemente debido a pequeñas variaciones en la detección de la cámara, haciendo imposible hacer clics precisos.

## 🚀 La Solución (Architecture)
**Virtual Hand Control** aborda estos problemas utilizando modelos de Machine Learning ultraligeros para el tracking nodal y aplicando matemáticas de suavizado en tiempo real.

### Principales Características:
* **Tracking Nodal en Tiempo Real:** Identificación de 21 puntos clave de la mano utilizando MediaPipe.
* **Filtros Anti-Temblor (Anti-Jitter):** Algoritmo de zona muerta y suavizado de interpolación para un movimiento fluido del cursor.
* **Gestos Naturales:** "Pellizco" (juntar el dedo índice y el pulgar) mapeado a la acción de Click del sistema operativo, con un *cooldown* integrado para evitar clics múltiples accidentales.
* **Interfaz de Control Web:** Panel local servido con Flask para gestionar las cámaras conectadas, iniciar/detener el stream y monitorear la detección en el navegador.

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Razón de la elección |
|------------|------------|-----------------------|
| **Core & Lógica** | **Python 3** | Ecosistema líder para scripts de automatización y visión computacional. |
| **Computer Vision**| **OpenCV** | Captura de video de alta eficiencia y manipulación de matrices de imágenes. |
| **Machine Learning**| **MediaPipe (Google)** | Tracking de manos optimizado para funcionar en CPU sin necesidad de GPUs dedicadas. |
| **OS Control** | **PyAutoGUI** | Interfaz directa con los eventos de mouse y teclado a nivel sistema operativo. |
| **Matemáticas** | **NumPy** | Cálculo vectorial veloz para la interpolación de coordenadas y cálculo de distancias. |
| **Web Server** | **Flask** | Servidor ligero para proveer la interfaz de usuario en el navegador localmente. |

## ⚡ Cómo correr el proyecto localmente

> ⚠️ **Nota Importante:** Este proyecto es una aplicación de escritorio interactiva. No puede ser desplegado en servicios en la nube (como Vercel o Render) ya que requiere acceso a los periféricos físicos del usuario (Cámara y Mouse). **Debe ejecutarse localmente.**

### Prerrequisitos
* Python 3.8 o superior instalado en tu sistema.
* Una cámara web conectada.

### Instalación Rápida
1. **Clonar el repositorio**
   ```bash
   git clone [https://github.com/santiago-iturralde/Virtual-Hand-Control.git](https://github.com/santiago-iturralde/Virtual-Hand-Control.git)
   cd Virtual-Hand-Control
   ```

2. **Crear y activar un entorno virtual (Recomendado)**
   ```bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate

   # En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install opencv-python mediapipe pyautogui flask numpy
   ```

4. **Iniciar el Sistema**
   ```bash
   # Asegúrate de ejecutar el archivo principal (ajusta el nombre si es distinto)
   python mano_test.py
   ```

5. **Abrir la Interfaz Web**
   * El script abrirá automáticamente tu navegador.
   * Si no lo hace, ingresa a `http://127.0.0.1:5000`
   * Selecciona tu cámara y presiona "Start". ¡Mueve la mano frente a la cámara para controlar el mouse!

## 📸 Screenshots

### Interfaz Web de Control y Stream
<img width="1912" height="975" alt="Captura de pantalla 2026-05-14 194138" src="https://github.com/user-attachments/assets/43d69c8f-52b9-4180-a8ae-fa63758499a9" />


### Tracking y Reconocimiento de Gestos (Click)
<img width="1738" height="905" alt="ChatGPT Image 14 may 2026, 07_48_48 p m" src="https://github.com/user-attachments/assets/dcb821d6-a078-4254-8b1a-049ce0952f5d" />



---

Desarrollado por [Santiago Iturralde](https://github.com/santiago-iturralde) 💻🖐️
