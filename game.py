"""
🎮 ESQUIVA LOS METEORITOS - Juego de Feria con IA
==================================================
Detecta el cuerpo con MediaPipe y esquiva objetos que caen.
Hasta 3 jugadores simultáneos.

Controles:
  Q / ESC → Salir
  R       → Reiniciar juego
  ESPACIO → Pausar
"""

# ── Suprimir warnings de TensorFlow / Protobuf antes de importar mediapipe ──
import os
import warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"          # silencia logs de TF
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"          # desactiva oneDNN
os.environ["GLOG_minloglevel"] = "3"               # silencia logs de mediapipe
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import cv2
import mediapipe as mp
import numpy as np
import random
import time
import math

# ─────────────────────────────────────────
#  CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────
WINDOW_NAME = "🚀 ESQUIVA LOS METEORITOS"
CAMERA_INDEX = 0          # Cambia a 1 si tienes cámara externa
FRAME_W, FRAME_H = 1280, 720

MAX_PLAYERS   = 3
BODY_RADIUS   = 18        # Radio de colisión por punto clave (px)
INITIAL_LIVES = 3

# Velocidad inicial y tasa de aumento de dificultad
INITIAL_SPEED     = 3
SPEED_INCREMENT   = 0.10  # por cada 10 pts de score total
MAX_OBJECTS       = 10
SPAWN_INTERVAL    = 1.0   # segundos entre meteoritos

# Colores BGR
COLOR_BG_OVERLAY = (10, 5, 30)
COLORS_PLAYER    = [
    (0, 255, 100),    # Verde neón – Jugador 1
    (0, 180, 255),    # Naranja/azul – Jugador 2
    (255, 0, 200),    # Magenta – Jugador 3
]
COLOR_METEOR    = (60, 100, 255)
COLOR_HIT       = (0, 0, 255)
COLOR_STAR      = (255, 220, 100)
COLOR_WHITE     = (255, 255, 255)
COLOR_YELLOW    = (0, 220, 255)
COLOR_RED       = (50, 50, 255)
COLOR_GREEN     = (80, 220, 80)

# Puntos clave de MediaPipe que forman el "cuerpo"
# Puntos clave de MediaPipe que forman el "cuerpo"
BODY_LANDMARKS = [
    0,       # nariz (cabeza)
    23, 24,  # caderas (cintura)
]

# ─────────────────────────────────────────
#  CLASE: METEORITO
# ─────────────────────────────────────────
class Meteor:
    SHAPES = ["circle", "square", "triangle", "star"]

    def __init__(self, speed: float):
        self.x = random.randint(30, FRAME_W - 30)
        self.y = random.randint(-120, -20)
        self.r = random.randint(18, 34)
        self.speed = speed + random.uniform(-1, 1.5)
        self.angle = random.uniform(-0.6, 0.6)   # deriva lateral
        self.rot   = 0
        self.rot_speed = random.uniform(-4, 4)
        self.shape = random.choice(self.SHAPES)
        self.hit   = False
        self.hit_timer = 0
        # Color con variación
        b = random.randint(140, 255)
        g = random.randint(60, 140)
        r = random.randint(30, 80)
        self.color = (b, g, r)

    @property
    def alive(self):
        return self.y < FRAME_H + 60

    def update(self):
        self.y += self.speed
        self.x += math.sin(self.angle + self.y * 0.008) * 1.2
        self.rot = (self.rot + self.rot_speed) % 360
        if self.hit:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit = False

    def mark_hit(self):
        self.hit = True
        self.hit_timer = 8

    def draw(self, frame):
        color = COLOR_HIT if self.hit else self.color
        cx, cy, r = int(self.x), int(self.y), self.r

        if self.shape == "circle":
            cv2.circle(frame, (cx, cy), r, color, -1)
            cv2.circle(frame, (cx, cy), r, COLOR_WHITE, 1)
            # Brillo
            cv2.circle(frame, (cx - r//4, cy - r//4), r//4, (200,220,255), -1)

        elif self.shape == "square":
            rad = math.radians(self.rot)
            corners = []
            for angle in [45, 135, 225, 315]:
                a = math.radians(angle) + rad
                corners.append([int(cx + r * math.cos(a)),
                                 int(cy + r * math.sin(a))])
            pts = np.array(corners, np.int32)
            cv2.fillPoly(frame, [pts], color)
            cv2.polylines(frame, [pts], True, COLOR_WHITE, 1)

        elif self.shape == "triangle":
            rad = math.radians(self.rot)
            corners = []
            for angle in [90, 210, 330]:
                a = math.radians(angle) + rad
                corners.append([int(cx + r * math.cos(a)),
                                 int(cy + r * math.sin(a))])
            pts = np.array(corners, np.int32)
            cv2.fillPoly(frame, [pts], color)
            cv2.polylines(frame, [pts], True, COLOR_WHITE, 1)

        elif self.shape == "star":
            rad = math.radians(self.rot)
            pts = []
            for i in range(10):
                a = math.radians(i * 36) + rad
                radius = r if i % 2 == 0 else r // 2
                pts.append([int(cx + radius * math.cos(a)),
                             int(cy + radius * math.sin(a))])
            pts = np.array(pts, np.int32)
            cv2.fillPoly(frame, [pts], color)
            cv2.polylines(frame, [pts], True, COLOR_WHITE, 1)

    def collides_with(self, points: list) -> bool:
        """Verifica colisión con una lista de (x, y) puntos del cuerpo."""
        for px, py in points:
            dist = math.hypot(self.x - px, self.y - py)
            if dist < self.r + BODY_RADIUS:
                return True
        return False


# ─────────────────────────────────────────
#  CLASE: JUGADOR
# ─────────────────────────────────────────
class Player:
    def __init__(self, player_id: int):
        self.id    = player_id
        self.color = COLORS_PLAYER[player_id % len(COLORS_PLAYER)]
        self.score = 0
        self.lives = INITIAL_LIVES
        self.body_points = []   # (x, y) de cada landmark
        self.active = False
        self.hit_flash = 0      # frames de efecto al ser golpeado

    @property
    def alive(self):
        return self.lives > 0

    def take_hit(self):
        if self.hit_flash == 0:   # evita doble golpe por mismo frame
            self.lives -= 1
            self.hit_flash = 25
            return True
        return False

    def add_score(self, pts=1):
        self.score += pts

    def update(self):
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw_body(self, frame):
        if not self.body_points:
            return
        alpha = 0.4 if self.hit_flash == 0 else 0.7
        color = self.color if self.hit_flash == 0 else COLOR_HIT

        overlay = frame.copy()
        for (x, y) in self.body_points:
            cv2.circle(overlay, (x, y), BODY_RADIUS, color, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Borde de puntos
        for (x, y) in self.body_points:
            cv2.circle(frame, (x, y), BODY_RADIUS, color, 1)


# ─────────────────────────────────────────
#  CLASE: PARTÍCULAS (efectos visuales)
# ─────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(-15, 15)
        self.y = y + random.randint(-15, 15)
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, -1)
        self.life = random.randint(15, 30)
        self.color = color
        self.size = random.randint(2, 6)

    @property
    def alive(self):
        return self.life > 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25   # gravedad
        self.life -= 1

    def draw(self, frame):
        if 0 <= int(self.x) < FRAME_W and 0 <= int(self.y) < FRAME_H:
            cv2.circle(frame, (int(self.x), int(self.y)),
                       self.size, self.color, -1)


# ─────────────────────────────────────────
#  CLASE PRINCIPAL: JUEGO
# ─────────────────────────────────────────
class DodgeGame:
    def __init__(self):
        # MediaPipe nueva API (0.10.x)
        BaseOptions        = mp.tasks.BaseOptions
        PoseLandmarker     = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode  = mp.tasks.vision.RunningMode

        # Descargar modelo si no existe
        model_path = "pose_landmarker_lite.task"
        if not os.path.exists(model_path):
            print("📥 Descargando modelo de pose (~3 MB)...")
            import urllib.request
            url = ("https://storage.googleapis.com/mediapipe-models/"
                   "pose_landmarker/pose_landmarker_lite/float16/latest/"
                   "pose_landmarker_lite.task")
            urllib.request.urlretrieve(url, model_path)
            print("✅ Modelo descargado.")

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            num_poses=MAX_PLAYERS,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.detector = PoseLandmarker.create_from_options(options)
        self.mp_image_format = mp.ImageFormat.SRGB

        # Estado del juego
        self.players   = [Player(i) for i in range(MAX_PLAYERS)]
        self.meteors   = []
        self.particles = []
        self.stars     = self._gen_stars()

        self.game_state   = "waiting"  # waiting | playing | paused | gameover
        self.total_score  = 0
        self.last_spawn   = time.time()
        self.start_time   = None
        self.elapsed      = 0
        self.speed        = INITIAL_SPEED

        # Cámara
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    # ── Fondo de estrellas ──────────────────
    def _gen_stars(self):
        return [(random.randint(0, FRAME_W),
                 random.randint(0, FRAME_H),
                 random.randint(1, 3),
                 random.random()) for _ in range(180)]

    def _draw_stars(self, frame):
        t = time.time()
        for (sx, sy, sr, phase) in self.stars:
            bright = int(120 + 120 * math.sin(t * 2 + phase * 6))
            c = (bright, bright, bright)
            cv2.circle(frame, (sx, sy), sr, c, -1)

    # ── Overlay oscuro ──────────────────────
    def _dark_overlay(self, frame, alpha=0.55):
        overlay = np.full_like(frame, COLOR_BG_OVERLAY)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # ── Texto con sombra ────────────────────
    @staticmethod
    def _text(frame, text, pos, scale=0.9, color=COLOR_WHITE,
              thickness=2, shadow=True):
        x, y = pos
        font = cv2.FONT_HERSHEY_DUPLEX
        if shadow:
            cv2.putText(frame, text, (x+2, y+2), font,
                        scale, (0, 0, 0), thickness + 1, cv2.LINE_AA)
        cv2.putText(frame, text, (x, y), font,
                    scale, color, thickness, cv2.LINE_AA)

    # ── Detectar cuerpos ────────────────────
    def _detect_bodies(self, frame):
        """
        Nueva API de MediaPipe (0.10.x): PoseLandmarker detecta
        hasta MAX_PLAYERS poses en un solo frame.
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=self.mp_image_format, data=rgb)
        result = self.detector.detect(mp_img)

        # Resetear todos los jugadores
        for player in self.players:
            player.active = False
            player.body_points = []

        active_count = 0
        for i, pose_landmarks in enumerate(result.pose_landmarks):
            if i >= MAX_PLAYERS:
                break
            player = self.players[i]
            player.active = True
            active_count += 1
            pts = []
            for idx in BODY_LANDMARKS:
                if idx >= len(pose_landmarks):
                    continue
                lm = pose_landmarks[idx]
                if lm.visibility > 0.35:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    px = max(0, min(w - 1, px))
                    py = max(0, min(h - 1, py))
                    pts.append((px, py))
            player.body_points = pts

        return active_count

    # ── Spawnear meteorito ──────────────────
    def _maybe_spawn(self):
        now = time.time()
        interval = max(0.25, SPAWN_INTERVAL - self.total_score * 0.003)
        if (now - self.last_spawn >= interval and
                len(self.meteors) < MAX_OBJECTS):
            self.meteors.append(Meteor(self.speed))
            self.last_spawn = now

    # ── Colisiones ─────────────────────────
    def _check_collisions(self):
        for meteor in self.meteors:
            if meteor.hit:
                continue
            for player in self.players:
                if not player.active or not player.alive:
                    continue
                if meteor.collides_with(player.body_points):
                    meteor.mark_hit()
                    if player.take_hit():
                        # Partículas de impacto
                        mx, my = int(meteor.x), int(meteor.y)
                        for _ in range(20):
                            self.particles.append(
                                Particle(mx, my, player.color))
                    break   # un meteorito golpea a un solo jugador

    # ── Actualizar velocidad ────────────────
    def _update_speed(self):
        self.speed = INITIAL_SPEED + (self.total_score // 10) * SPEED_INCREMENT

    # ── HUD: vidas, puntos, tiempo ──────────
    def _draw_hud(self, frame, active_count):
        # Barra superior
        cv2.rectangle(frame, (0, 0), (FRAME_W, 70), (20, 15, 50), -1)
        cv2.line(frame, (0, 70), (FRAME_W, 70), (80, 60, 120), 2)

        # Puntos por jugador
        panel_w = FRAME_W // MAX_PLAYERS
        for i, player in enumerate(self.players):
            x0 = i * panel_w + 10
            label = f"J{i+1}"
            score_txt = f"{player.score:04d}"
            lives_txt  = "♥ " * player.lives + "♡ " * (INITIAL_LIVES - player.lives)

            if player.active and player.alive:
                self._text(frame, label,       (x0, 28),
                           0.7, player.color, 2)
                self._text(frame, score_txt,   (x0 + 35, 28),
                           0.9, COLOR_YELLOW, 2)
                self._text(frame, lives_txt,   (x0, 55),
                           0.55, COLOR_RED, 1)
            elif not player.active:
                self._text(frame, f"J{i+1}: esperando...",
                           (x0, 40), 0.5, (100, 100, 100), 1)

        # Tiempo y velocidad (centro superior)
        elapsed_str = f"{int(self.elapsed // 60):02d}:{int(self.elapsed % 60):02d}"
        level = int(self.total_score // 10) + 1
        cx = FRAME_W // 2 - 80
        self._text(frame, f"TIEMPO {elapsed_str}",
                   (cx, 28), 0.65, COLOR_WHITE, 1)
        self._text(frame, f"NIVEL {level}",
                   (cx, 55), 0.65, COLOR_STAR, 2)

    # ── Pantalla de espera ──────────────────
    def _draw_waiting(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (FRAME_W//2-320, FRAME_H//2-160),
                      (FRAME_W//2+320, FRAME_H//2+160), (20, 10, 50), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        cv2.rectangle(frame, (FRAME_W//2-320, FRAME_H//2-160),
                      (FRAME_W//2+320, FRAME_H//2+160), (120, 80, 200), 2)

        self._text(frame, "ESQUIVA LOS METEORITOS",
                   (FRAME_W//2-270, FRAME_H//2-110),
                   1.1, COLOR_YELLOW, 2)
        self._text(frame, "Ponte frente a la camara",
                   (FRAME_W//2-210, FRAME_H//2-55),
                   0.75, COLOR_WHITE, 1)
        self._text(frame, "para comenzar el juego",
                   (FRAME_W//2-185, FRAME_H//2-20),
                   0.75, COLOR_WHITE, 1)
        self._text(frame, "Hasta 3 jugadores al mismo tiempo",
                   (FRAME_W//2-245, FRAME_H//2+30),
                   0.65, COLOR_STAR, 1)
        t = time.time()
        dots = "." * (int(t * 2) % 4)
        self._text(frame, f"Detectando jugadores{dots}",
                   (FRAME_W//2-185, FRAME_H//2+90),
                   0.7, (150, 200, 255), 1)
        self._text(frame, "Q=Salir  R=Reiniciar",
                   (FRAME_W//2-150, FRAME_H//2+135),
                   0.55, (120, 120, 120), 1)

    # ── Pantalla de pausa ───────────────────
    def _draw_pause(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (FRAME_W, FRAME_H), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        self._text(frame, "PAUSA",
                   (FRAME_W//2-80, FRAME_H//2),
                   2.0, COLOR_YELLOW, 3)
        self._text(frame, "Presiona ESPACIO para continuar",
                   (FRAME_W//2-260, FRAME_H//2+60),
                   0.8, COLOR_WHITE, 1)

    # ── Pantalla de Game Over ───────────────
    def _draw_gameover(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (FRAME_W, FRAME_H), (0, 0, 30), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        self._text(frame, "GAME OVER",
                   (FRAME_W//2-200, FRAME_H//2-120),
                   2.0, COLOR_RED, 3)

        # Tabla de puntajes
        self._text(frame, "PUNTUACIONES FINALES:",
                   (FRAME_W//2-190, FRAME_H//2-50),
                   0.9, COLOR_YELLOW, 2)

        active = [p for p in self.players if p.score > 0 or p.active]
        if not active:
            active = self.players

        active_sorted = sorted(active, key=lambda p: p.score, reverse=True)
        medals = ["🥇", "🥈", "🥉"]
        for rank, player in enumerate(active_sorted):
            y = FRAME_H//2 + rank * 42
            medal = medals[rank] if rank < 3 else "  "
            txt = f"{medal} Jugador {player.id+1}: {player.score} pts"
            self._text(frame, txt, (FRAME_W//2-200, y),
                       0.85, player.color, 2)

        self._text(frame, f"Total combinado: {self.total_score} pts",
                   (FRAME_W//2-190, FRAME_H//2+165),
                   0.8, COLOR_WHITE, 1)
        self._text(frame, "Presiona R para jugar de nuevo",
                   (FRAME_W//2-235, FRAME_H//2+210),
                   0.75, COLOR_STAR, 1)

    # ── Reset ────────────────────────────────
    def reset(self):
        self.players   = [Player(i) for i in range(MAX_PLAYERS)]
        self.meteors   = []
        self.particles = []
        self.total_score = 0
        self.speed = INITIAL_SPEED
        self.last_spawn = time.time()
        self.start_time = None
        self.elapsed    = 0
        self.game_state = "waiting"

    # ── Loop principal ───────────────────────
    def run(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, FRAME_W, FRAME_H)

        print("\n🚀 Esquiva los Meteoritos iniciado")
        print("   Controles: Q/ESC=Salir | R=Reiniciar | SPACE=Pausa\n")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️  Error: no se pudo leer la cámara.")
                break

            frame = cv2.flip(frame, 1)          # espejo
            frame = cv2.resize(frame, (FRAME_W, FRAME_H))

            # Fondo oscuro + estrellas
           # self._dark_overlay(frame, 0.45)
            self._draw_stars(frame)

            # ── Detectar cuerpos ──
            active_count = self._detect_bodies(frame)

            # ── Lógica de estado ──
            if self.game_state == "waiting":
                if active_count > 0:
                    self.game_state = "playing"
                    self.start_time = time.time()
                    self.last_spawn = time.time()
                else:
                    self._draw_waiting(frame)

            elif self.game_state == "playing":
                # Tiempo
                self.elapsed = time.time() - self.start_time

                # Spawn y actualizar meteoritos
                self._maybe_spawn()
                for m in self.meteors:
                    m.update()
                    m.draw(frame)

                    # Si el meteorito pasa sin golpear → punto para TODOS
                    if not m.alive and not m.hit:
                        for p in self.players:
                            if p.active and p.alive:
                                p.add_score(1)
                                self.total_score += 1

                # Limpiar meteoritos fuera de pantalla
                self.meteors = [m for m in self.meteors if m.alive]

                # Colisiones
                self._check_collisions()
                self._update_speed()

                # Dibujar jugadores
                for player in self.players:
                    player.update()
                    if player.active:
                        player.draw_body(frame)

                # Partículas
                for p in self.particles:
                    p.update()
                    p.draw(frame)
                self.particles = [p for p in self.particles if p.alive]

                # HUD
                self._draw_hud(frame, active_count)

                # ¿Todos sin vidas?
                active_players = [p for p in self.players if p.active]
                if active_players and all(not p.alive for p in active_players):
                    self.game_state = "gameover"

                # Si nadie activo durante > 3 s → pausar
                if active_count == 0:
                    self.game_state = "paused"

            elif self.game_state == "paused":
                self._draw_hud(frame, active_count)
                self._draw_pause(frame)
                if active_count > 0:
                    self.game_state = "playing"

            elif self.game_state == "gameover":
                self._draw_gameover(frame)

            # ── Mostrar frame ──
            cv2.imshow(WINDOW_NAME, frame)

            # ── Teclas ──
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):    # Q o ESC
                break
            elif key == ord('r'):        # Reiniciar
                self.reset()
            elif key == ord(' '):        # Pausa manual
                if self.game_state == "playing":
                    self.game_state = "paused"
                elif self.game_state == "paused":
                    self.game_state = "playing"

        self.cap.release()
        cv2.destroyAllWindows()
        print("👋 ¡Gracias por jugar!")


# ─────────────────────────────────────────
#  ENTRADA
# ─────────────────────────────────────────
if __name__ == "__main__":
    import sys
    print(f"✅ Python   : {sys.version.split()[0]}")
    print(f"✅ OpenCV   : {cv2.__version__}")
    print(f"✅ MediaPipe: {mp.__version__}")
    print(f"✅ NumPy    : {np.__version__}")

    try:
        game = DodgeGame()
        game.run()
    except Exception as e:
        print(f"\n❌ Error al iniciar el juego: {e}")
        print("\n🔧 Solución: ejecuta estos comandos en la terminal:")
        print("   pip install protobuf==4.25.3")
        print("   pip install --upgrade mediapipe opencv-python numpy")
        import traceback
        traceback.print_exc()