# 🚀 ESQUIVA LOS METEORITOS
### Juego de IA para Feria Universitaria
---

## 🎮 ¿Qué hace este juego?
La cámara detecta tu cuerpo en tiempo real usando **MediaPipe Pose**.
Aparecen meteoritos cayendo desde arriba y debes **esquivarlos con tu cuerpo real**.

- Hasta **3 jugadores** al mismo tiempo
- Dificultad que **aumenta** automáticamente
- Efectos de partículas y fondo espacial
- Ranking final de puntajes

---

## 🛠️ Instalación (1 sola vez)

### Requisitos
- Python 3.8 o superior
- Cámara web (la de la laptop funciona)

### Pasos
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el juego
python game.py
```

---

## 🎯 Controles
| Tecla | Acción |
|-------|--------|
| `Q` o `ESC` | Salir |
| `R` | Reiniciar juego |
| `ESPACIO` | Pausar / Continuar |

---

## 👥 Cómo jugar en la feria
1. Colocar la laptop con la cámara mirando hacia los jugadores
2. Los jugadores se ponen **de pie frente a la cámara** (a ~1.5-2 metros)
3. El juego detecta automáticamente y empieza
4. **¡Esquiva los meteoritos moviéndote!**
5. Si un meteorito toca tu cuerpo → pierdes una vida ♥
6. Si un meteorito pasa sin tocarte → ¡ganas un punto!

---

## 🔧 Ajustes rápidos (en `game.py`)

```python
CAMERA_INDEX = 0      # Cambiar a 1 si usas cámara externa
INITIAL_LIVES = 3     # Vidas por jugador
INITIAL_SPEED = 4     # Velocidad inicial de meteoritos
MAX_PLAYERS = 3       # Jugadores simultáneos (máx 3)
BODY_RADIUS = 18      # Sensibilidad de colisión (px)
```

---

## 💡 Tips para la feria
- Pon el cartel: **"Esquiva los meteoritos usando solo tu cuerpo – IA detecta tu pose en tiempo real"**
- Asegúrate de tener **buena iluminación** (la detección mejora mucho)
- Un espacio libre de ~2x2 metros frente a la cámara es ideal
- La distancia óptima es **1 a 2.5 metros** de la cámara

---

## 🏗️ Arquitectura del proyecto

```
Cámara (OpenCV)
    ↓
MediaPipe Pose (detección de 33 puntos del cuerpo)
    ↓
Extracción de landmarks (hombros, codos, caderas, etc.)
    ↓
Generación de meteoritos (posición, velocidad, forma)
    ↓
Detección de colisión (distancia euclidiana punto-a-punto)
    ↓
Actualización de puntaje y vidas
    ↓
Renderizado en pantalla (OpenCV)
```

---

## 🐛 Problemas comunes

**"No se pudo leer la cámara"**
→ Cambia `CAMERA_INDEX = 0` a `CAMERA_INDEX = 1`

**Detección lenta**
→ Cierra otras aplicaciones. El modelo usa `model_complexity=0` (el más rápido)

**No detecta el cuerpo**
→ Mejorar iluminación, alejarse un poco más de la cámara

---

Creado con ❤️ usando Python + OpenCV + MediaPipe
