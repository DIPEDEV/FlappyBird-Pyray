"""
midernfp - Flappy Bird Clone
Built with pyray (raylib Python bindings)

Buenas prácticas:
- Texturas cargadas una sola vez al iniciar
- Sprites con canal alpha (PNG transparentes)
- Audio cargado al inicio, reproducido bajo demanda
- Recursos liberados al cerrar
"""

import pyray as rl
import math
import os
import random

# ═══════════════════════════════════════════════════════════════
# RUTAS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════
SPRITES_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colores del tema neon cyberpunk
BG_COLOR = rl.Color(10, 10, 20, 255)
PIPE_COLOR = rl.Color(40, 160, 130, 255)
PIPE_LIGHT = rl.Color(80, 200, 170, 255)
ACCENT = rl.Color(100, 255, 180, 255)
WHITE = rl.WHITE


# ═══════════════════════════════════════════════════════════════
# ASSET MANAGER - Carga todos los recursos una sola vez
# ═══════════════════════════════════════════════════════════════
class AssetManager:
    """Carga y administra todos los recursos del juego (texturas + audio).
    Se instancia una vez y se comparte en todo el juego."""
    
    _instance = None
    
    def __new__(cls):
        # Singleton para evitar cargar assets múltiples veces
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.loaded = False
        return cls._instance
    
    def load(self):
        """Carga todos los recursos. Solo se ejecuta una vez."""
        if self.loaded:
            return
        
        # ─── Texturas ───
        self.bird = self._load_texture("bird.png")
        self.pipe = self._load_texture("pipe.png")
        self.background = self._load_texture("background.png")
        self.ground = self._load_texture("ground.png")
        
        # ─── Audio ───
        rl.init_audio_device()
        self.jump_sound = self._load_sound("jump.wav")
        self.score_sound = self._load_sound("score.wav")
        self.death_sound = self._load_sound("death.wav")
        self.music = self._load_music("music.mp3")
        
        self.loaded = True
        rl.trace_log(3, f"Assets cargados desde: {SPRITES_DIR}")
    
    def _load_texture(self, filename):
        path = os.path.join(SPRITES_DIR, filename)
        if os.path.exists(path):
            tex = rl.load_texture(path)
            rl.trace_log(3, f"Textura cargada: {filename}")
            return tex
        else:
            rl.trace_log(3, f"Textura no encontrada: {filename} (usando fallback)")
            return None
    
    def _load_sound(self, filename):
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            sound = rl.load_sound(path)
            rl.trace_log(3, f"Sound cargado: {filename}")
            return sound
        return None
    
    def _load_music(self, filename):
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            music = rl.load_music_stream(path)
            rl.trace_log(3, f"Music cargada: {filename}")
            return music
        return None
    
    def play_jump(self):
        if self.jump_sound:
            rl.play_sound(self.jump_sound)
    
    def play_score(self):
        if self.score_sound:
            rl.play_sound(self.score_sound)
    
    def play_death(self):
        if self.death_sound:
            rl.play_sound(self.death_sound)
    
    def play_music(self):
        if self.music:
            rl.play_music_stream(self.music)
    
    def update_music(self):
        if self.music:
            rl.update_music_stream(self.music)
    
    def unload_all(self):
        """Liberar todos los recursos cuando el juego cierra."""
        if self.bird:
            rl.unload_texture(self.bird)
        if self.pipe:
            rl.unload_texture(self.pipe)
        if self.background:
            rl.unload_texture(self.background)
        if self.ground:
            rl.unload_texture(self.ground)
        if self.jump_sound:
            rl.unload_sound(self.jump_sound)
        if self.score_sound:
            rl.unload_sound(self.score_sound)
        if self.death_sound:
            rl.unload_sound(self.death_sound)
        if self.music:
            rl.unload_music_stream(self.music)
        rl.close_audio_device()
        rl.trace_log(3, "Todos los recursos liberados")


# ═══════════════════════════════════════════════════════════════
# BIRD - El jugador
# ═══════════════════════════════════════════════════════════════
class Bird:
    """El pájaro del jugador. No carga texturas, las recibe del AssetManager."""
    
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.45
        self.jump_power = -7.5
        self.radius = 14
        self.rotation = 0
        self.alive = True
        self._anim_frame = 0
    
    def jump(self):
        self.velocity = self.jump_power
        assets = AssetManager()
        assets.play_jump()
    
    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rotation = max(-30, min(30, self.velocity * 3))
        
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - 80 - self.radius:
            self.y = SCREEN_HEIGHT - 80 - self.radius
            self.alive = False
        
        self._anim_frame += 1
    
    def draw(self):
        assets = AssetManager()
        
        if assets.bird:
            # Textura con canal alpha
            rec = rl.Rectangle(self.x - 20, self.y - 20, 40, 40)
            rl.draw_texture_pro(
                assets.bird,
                rl.Rectangle(0, 0, float(assets.bird.width), float(assets.bird.height)),
                rec,
                rl.Vector2(20, 20),
                self.rotation,
                rl.WHITE  # WHITE mantiene el alpha de la textura
            )
        else:
            # Fallback si no hay textura
            rl.draw_circle(int(self.x), int(self.y), self.radius, rl.Color(255, 200, 50, 255))
            rl.draw_triangle(
                rl.Vector2(self.x + 10, self.y),
                rl.Vector2(self.x + 20, self.y - 5),
                rl.Vector2(self.x + 20, self.y + 5),
                rl.Color(255, 100, 50, 255)
            )
    
    def get_rect(self):
        return rl.Rectangle(self.x - self.radius, self.y - self.radius,
                            self.radius * 2, self.radius * 2)


# ═══════════════════════════════════════════════════════════════
# PIPE - Obstáculo
# ═══════════════════════════════════════════════════════════════
class Pipe:
    """Tubos obstaculos. No cargan texturas, reciben referencia de AssetManager."""
    
    def __init__(self, x=None):
        self.x = x if x is not None else SCREEN_WIDTH + 50
        self.width = 55
        self.gap_size = 150
        self.speed = 3
        self.passed = False
        
        # Posición aleatoria del gap
        self.top_height = random.randint(80, SCREEN_HEIGHT - self.gap_size - 150)
    
    def update(self):
        self.x -= self.speed
    
    def draw(self):
        assets = AssetManager()
        
        if assets.pipe:
            # Pipe superior
            top_dest = rl.Rectangle(self.x, 0, self.width, self.top_height)
            rl.draw_texture_pro(
                assets.pipe,
                rl.Rectangle(0, 0, float(assets.pipe.width), float(assets.pipe.height)),
                top_dest,
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
            
            # Pipe inferior
            bottom_y = self.top_height + self.gap_size
            bottom_h = SCREEN_HEIGHT - bottom_y - 60
            bottom_dest = rl.Rectangle(self.x, bottom_y, self.width, bottom_h)
            rl.draw_texture_pro(
                assets.pipe,
                rl.Rectangle(0, 0, float(assets.pipe.width), float(assets.pipe.height)),
                bottom_dest,
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
        else:
            # Fallback
            rl.draw_rectangle(int(self.x), 0, self.width, self.top_height, PIPE_COLOR)
            rl.draw_rectangle(int(self.x) + 4, 0, 8, self.top_height, PIPE_LIGHT)
            
            bottom_y = self.top_height + self.gap_size
            rl.draw_rectangle(int(self.x), int(bottom_y), self.width,
                              SCREEN_HEIGHT - int(bottom_y) - 60, PIPE_COLOR)
            rl.draw_rectangle(int(self.x) + 4, int(bottom_y), 8,
                              SCREEN_HEIGHT - int(bottom_y) - 60, PIPE_LIGHT)
    
    def get_top_rect(self):
        return rl.Rectangle(self.x - 5, 0, self.width + 10, max(0, self.top_height - 20))
    
    def get_bottom_rect(self):
        bottom_y = self.top_height + self.gap_size
        return rl.Rectangle(self.x - 5, bottom_y + 20,
                            self.width + 10, SCREEN_HEIGHT - bottom_y - 80)


# ═══════════════════════════════════════════════════════════════
# GAME - Controlador principal
# ═══════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "midernfp - Flappy Bird")
        rl.set_target_fps(60)
        
        # Cargar todos los assets UNA SOLA VEZ
        self.assets = AssetManager()
        self.assets.load()
        
        self.high_score = 0
        self.current_score = 0
    
    def draw_background(self):
        assets = self.assets
        
        if assets.background:
            rl.draw_texture_pro(
                assets.background,
                rl.Rectangle(0, 0, float(assets.background.width),
                              float(assets.background.height)),
                rl.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
        else:
            rl.clear_background(BG_COLOR)
            random.seed(42)
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT - 80)
                rl.draw_circle(x, y, 1, rl.Color(255, 255, 255, 100))
    
    def draw_ground(self):
        assets = self.assets
        
        if assets.ground:
            # Tile horizontal del suelo
            for x in range(0, SCREEN_WIDTH, 50):
                rl.draw_texture(assets.ground, x, SCREEN_HEIGHT - 60, rl.WHITE)
        else:
            rl.draw_rectangle(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60,
                              rl.Color(25, 25, 45, 255))
        
        rl.draw_line(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, SCREEN_HEIGHT - 60, ACCENT)
    
    def show_menu(self):
        while True:
            if rl.window_should_close():
                return "quit"
            
            self.draw_background()
            self.draw_ground()
            
            rl.draw_text("midernfp", SCREEN_WIDTH // 2 - 90, 100, 48, ACCENT)
            rl.draw_text("FLAPPY BIRD", SCREEN_WIDTH // 2 - 80, 170, 32, WHITE)
            
            # Botón start
            btn_x, btn_y = SCREEN_WIDTH // 2 - 80, 300
            btn_w, btn_h = 160, 50
            rl.draw_rectangle(btn_x, btn_y, btn_w, btn_h,
                              rl.Color(40, 160, 130, 200))
            rl.draw_rectangle_lines(btn_x, btn_y, btn_w, btn_h, ACCENT)
            rl.draw_text("CLICK START", btn_x + 15, btn_y + 15, 20, WHITE)
            
            rl.draw_text("SPACE or CLICK to flap",
                          SCREEN_WIDTH // 2 - 100, 400, 16,
                          rl.Color(100, 100, 150, 255))
            rl.draw_text(f"High Score: {self.high_score}",
                          SCREEN_WIDTH // 2 - 60, 450, 20, ACCENT)
            
            rl.end_drawing()
            
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
                return "play"
            if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
                return "play"
    
    def play(self):
        bird = Bird()
        pipes = [Pipe()]
        self.current_score = 0
        
        while bird.alive:
            if rl.window_should_close():
                return "quit"
            
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE) or \
               rl.is_key_pressed(rl.KeyboardKey.KEY_W):
                bird.jump()
            if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
                bird.jump()
            
            bird.update()
            
            # Spawn nuevo pipe
            if pipes[-1].x < SCREEN_WIDTH - 180:
                pipes.append(Pipe())
            
            # Update pipes y detectar colisiones
            for pipe in pipes:
                pipe.update()
                
                top_rect = pipe.get_top_rect()
                bottom_rect = pipe.get_bottom_rect()
                bird_rect = bird.get_rect()
                
                if rl.check_collision_recs(bird_rect, top_rect) or \
                   rl.check_collision_recs(bird_rect, bottom_rect):
                    bird.alive = False
                    self.assets.play_death()
                
                # Score
                if pipe.x + pipe.width // 2 < bird.x and not pipe.passed:
                    pipe.passed = True
                    self.current_score += 1
                    self.assets.play_score()
            
            pipes = [p for p in pipes if p.x > -70]
            
            # Actualizar música
            self.assets.update_music()
            
            self.draw_background()
            
            for pipe in pipes:
                pipe.draw()
            
            self.draw_ground()
            bird.draw()
            
            rl.draw_text(str(self.current_score), SCREEN_WIDTH // 2 - 20, 40, 48, WHITE)
            
            rl.end_drawing()
        
        if self.current_score > self.high_score:
            self.high_score = self.current_score
        
        return "gameover"
    
    def show_game_over(self, score):
        while True:
            if rl.window_should_close():
                return "quit"
            
            self.draw_background()
            self.draw_ground()
            
            rl.draw_text("GAME OVER", SCREEN_WIDTH // 2 - 90, 150, 48,
                         rl.Color(255, 60, 60, 255))
            rl.draw_text(f"Score: {score}", SCREEN_WIDTH // 2 - 60, 230, 32, WHITE)
            rl.draw_text(f"Best: {self.high_score}", SCREEN_WIDTH // 2 - 50, 280, 24, ACCENT)
            
            # Botón retry
            btn_x, btn_y = SCREEN_WIDTH // 2 - 60, 350
            btn_w, btn_h = 120, 45
            rl.draw_rectangle(btn_x, btn_y, btn_w, btn_h,
                              rl.Color(40, 160, 130, 200))
            rl.draw_rectangle_lines(btn_x, btn_y, btn_w, btn_h, ACCENT)
            rl.draw_text("RETRY", btn_x + 30, btn_y + 12, 24, WHITE)
            
            rl.draw_text("ESC to quit", SCREEN_WIDTH // 2 - 50, 430, 16,
                         rl.Color(100, 100, 150, 255))
            
            rl.end_drawing()
            
            if rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
                return "quit"
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
                return "play"
            if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
                mouse = rl.get_mouse_position()
                if btn_x <= mouse.x <= btn_x + btn_w and \
                   btn_y <= mouse.y <= btn_y + btn_h:
                    return "play"
    
    def run(self):
        while True:
            action = self.show_menu()
            if action == "quit":
                break
            if action == "play":
                action = self.play()
            if action == "gameover":
                action = self.show_game_over(self.current_score)
            if action == "quit":
                break
        
        self.assets.unload_all()
        rl.close_window()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()