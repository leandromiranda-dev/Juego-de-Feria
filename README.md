# 🚀 Esquiva los Meteoritos — Body Dodge Game con IA

> Juego interactivo donde esquivas meteoritos usando tu cuerpo en tiempo real, detectado por Inteligencia Artificial.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.x-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🎮 ¿De qué trata?

La cámara detecta tu cuerpo usando **IA de detección de pose** y en pantalla caen meteoritos que debes esquivar moviéndote físicamente. Si un meteorito toca tu cuerpo, pierdes una vida. Si lo esquivas, ganas puntos.

- 👥 Hasta **3 jugadores** al mismo tiempo
- 🤖 **IA en tiempo real** — detecta tu pose 30 veces por segundo
- 🌟 Dificultad que **aumenta progresivamente**
- 💥 Efectos visuales de partículas al recibir impacto
- 🏆 Pantalla de ranking al final de cada partida

---

## 🧠 ¿Cómo funciona la IA?

Este proyecto usa **Computer Vision** (Visión por Computadora) para detectar el cuerpo humano en cada fotograma de la cámara.

```
Cámara (OpenCV)
    ↓
MediaPipe PoseLandmarker
    ↓
Detección de 33 puntos del cuerpo (landmarks)
    ↓
Selección de puntos clave: cabeza y cintura
    ↓
Cálculo de distancia euclidiana meteorito ↔ cuerpo
    ↓
Colisión detectada → pierde vida / esquiva → gana punto
```

La tecnología detrás es **MediaPipe**, una librería de Google entrenada con millones de imágenes de personas para reconocer posiciones del cuerpo humano en tiempo real.

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| OpenCV | Captura de cámara y renderizado |
| MediaPipe | Detección de pose del cuerpo |
| NumPy | Cálculos matemáticos |

---

## ⚙️ Instalación

### Requisitos
- Python 3.10 o superior
- Cámara web
- Windows / Linux / Mac

### Pasos

**Windows (forma rápida):**
```
1. Ejecutar instalar.bat   ← instala todo automáticamente
2. Ejecutar jugar.bat      ← abre el juego
```

**Manual:**
```bash
# Crear entorno virtual
python -m venv venv_juego
source venv_juego/bin/activate  # Linux/Mac
venv_juego\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python game.py
```

> ⚠️ **Nota:** La primera vez que ejecutes el juego, se descargará automáticamente el modelo de pose de MediaPipe (~3 MB). Necesitas conexión a internet solo esa vez.

---

## 🎯 Controles

| Tecla | Acción |
|---|---|
| Moverse físicamente | Esquivar meteoritos |
| `R` | Reiniciar partida |
| `ESPACIO` | Pausar / Continuar |
| `Q` o `ESC` | Salir |

---

## 🌍 Aplicaciones reales de esta tecnología

La misma tecnología usada en este juego se aplica en:

- 🏥 **Fisioterapia** — análisis de movimiento de pacientes
- ⚽ **Deporte** — corrección de postura en atletas
- 🎬 **Cine** — captura de movimiento (motion capture)
- 🎮 **Videojuegos** — control corporal (ej. Xbox Kinect)
- 🏢 **Seguridad** — detección de caídas en espacios públicos

---

## 📁 Estructura del proyecto

```
esquiva_meteoritos/
│
├── game.py               # Código principal del juego
├── requirements.txt      # Dependencias
├── instalar.bat          # Instalador automático (Windows)
├── jugar.bat             # Lanzador del juego (Windows)
└── README.md             # Este archivo
```

---

## 👨‍💻 Autor

Desarrollado como proyecto para feria universitaria.  
Demuestra el uso de **Inteligencia Artificial aplicada** con Computer Vision en un entorno interactivo y didáctico.

---

## 📄 Licencia

MIT — libre para usar, modificar y compartir.
