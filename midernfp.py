"""
midernfp - Flappy Bird Clone
Built with pyray (raylib Python bindings)
"""

import pyray as rl
import math
import os

# Paths
SPRITES_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

# Screen
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
BG_COLOR = rl.Color(10, 10, 20, 255)
PIPE_COLOR = rl.Color(40, 160, 130, 255)
PIPE_LIGHT = rl.Color(80, 200, 170, 255)
ACCENT = rl.Color(100, 255, 180, 255)
WHITE = rl.WHITE
BIRD_COLOR = rl.Color(255, 200, 50, 255)

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.45
        self.jump_power = -7.5
        self.radius = 14
        self.rotation = 0
        self.alive = True
        
        # Load bird texture
        bird_path = os.path.join(SPRITES_DIR, "bird.png")
        if os.path.exists(bird_path):
            self.texture = rl.load_texture(bird_path)
            self.use_texture = True
        else:
            self.use_texture = False
    
    def jump(self):
        self.velocity = self.jump_power
    
    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rotation = self.velocity * 3
        
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.y > SCREEN_HEIGHT - 80 - self.radius:
            self.y = SCREEN_HEIGHT - 80 - self.radius
            self.alive = False
    
    def draw(self):
        if self.use_texture:
            # Draw texture centered on bird position
            rec = rl.Rectangle(self.x - 20, self.y - 20, 40, 40)
            rl.draw_texture_pro(
                self.texture,
                rl.Rectangle(0, 0, float(self.texture.width), float(self.texture.height)),
                rec,
                rl.Vector2(20, 20),
                self.rotation,
                rl.WHITE
            )
        else:
            # Fallback: draw circle
            rl.draw_circle(int(self.x), int(self.y), self.radius, BIRD_COLOR)
            # Beak
            rl.draw_triangle(
                rl.Vector2(self.x + 10, self.y),
                rl.Vector2(self.x + 20, self.y - 5),
                rl.Vector2(self.x + 20, self.y + 5),
                rl.Color(255, 100, 50, 255)
            )

    def get_rect(self):
        return rl.Rectangle(self.x - self.radius, self.y - self.radius, 
                            self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self, x=None):
        self.x = x if x else SCREEN_WIDTH + 50
        self.width = 55
        self.gap_size = 150
        self.top_height = 0
        self.speed = 3
        self.passed = False
        
        # Randomize gap position
        import random
        self.top_height = random.randint(80, SCREEN_HEIGHT - self.gap_size - 150)
        
        # Load pipe texture
        pipe_path = os.path.join(SPRITES_DIR, "pipe.png")
        if os.path.exists(pipe_path):
            self.texture = rl.load_texture(pipe_path)
            self.use_texture = True
        else:
            self.use_texture = False
    
    def update(self):
        self.x -= self.speed
    
    def draw(self):
        if self.use_texture:
            # Draw top pipe
            top_dest = rl.Rectangle(self.x, 0, self.width, self.top_height)
            rl.draw_texture_pro(
                self.texture,
                rl.Rectangle(0, 0, float(self.texture.width), float(self.texture.height)),
                top_dest,
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
            
            # Draw bottom pipe
            bottom_y = self.top_height + self.gap_size
            bottom_dest = rl.Rectangle(self.x, bottom_y, self.width, SCREEN_HEIGHT - bottom_y - 60)
            rl.draw_texture_pro(
                self.texture,
                rl.Rectangle(0, 0, float(self.texture.width), float(self.texture.height)),
                bottom_dest,
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
        else:
            # Fallback: draw rectangles
            rl.draw_rectangle(int(self.x), 0, self.width, self.top_height, PIPE_COLOR)
            rl.draw_rectangle(int(self.x) + 4, 0, 8, self.top_height, PIPE_LIGHT)
            
            bottom_y = self.top_height + self.gap_size
            rl.draw_rectangle(int(self.x), int(bottom_y), self.width, SCREEN_HEIGHT - int(bottom_y) - 60, PIPE_COLOR)
            rl.draw_rectangle(int(self.x) + 4, int(bottom_y), 8, SCREEN_HEIGHT - int(bottom_y) - 60, PIPE_LIGHT)
    
    def get_top_rect(self):
        return rl.Rectangle(self.x - 5, 0, self.width + 10, max(0, self.top_height - 20))
    
    def get_bottom_rect(self):
        bottom_y = self.top_height + self.gap_size
        return rl.Rectangle(self.x - 5, bottom_y + 20, self.width + 10, SCREEN_HEIGHT - bottom_y - 80)

class Game:
    def __init__(self):
        rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "midernfp - Flappy Bird")
        rl.set_target_fps(60)
        
        self.font = rl.load_font_ex(os.path.join(SPRITES_DIR, "..", "..", ".openclaw", "workspace", "midernfp.py"), 48, None, 0)
        
        # Load background
        bg_path = os.path.join(SPRITES_DIR, "background.png")
        if os.path.exists(bg_path):
            self.bg_texture = rl.load_texture(bg_path)
            self.has_bg = True
        else:
            self.has_bg = False
        
        self.high_score = 0
        
    def draw_background(self):
        if self.has_bg:
            rl.draw_texture_pro(
                self.bg_texture,
                rl.Rectangle(0, 0, float(self.bg_texture.width), float(self.bg_texture.height)),
                rl.Rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                rl.Vector2(0, 0),
                0,
                rl.WHITE
            )
        else:
            rl.clear_background(BG_COLOR)
            # Draw stars
            import random
            random.seed(42)
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT - 80)
                rl.draw_circle(x, y, 1, rl.Color(255, 255, 255, 100))
    
    def draw_ground(self):
        ground_path = os.path.join(SPRITES_DIR, "ground.png")
        if os.path.exists(ground_path):
            ground = rl.load_texture(ground_path)
            # Draw tiled ground
            for x in range(0, SCREEN_WIDTH, 50):
                rl.draw_texture(ground, x, SCREEN_HEIGHT - 60, rl.WHITE)
        else:
            rl.draw_rectangle(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60, rl.Color(25, 25, 45, 255))
        
        rl.draw_line(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, SCREEN_HEIGHT - 60, ACCENT)
    
    def draw_text(self, text, x, y, size, color):
        # Simple text drawing fallback
        rl.draw_rectangle(x - 2, y - 2, len(text) * size // 2 + 4, size + 4, rl.Color(0, 0, 0, 150))
        rl.draw_text(text, x, y, size, color)
    
    def show_menu(self):
        while True:
            if rl.window_should_close():
                return "quit"
            
            self.draw_background()
            self.draw_ground()
            
            # Title
            rl.draw_text("midernfp", SCREEN_WIDTH // 2 - 90, 100, 48, ACCENT)
            rl.draw_text("FLAPPY BIRD", SCREEN_WIDTH // 2 - 80, 170, 32, WHITE)
            
            # Start button area
            btn_x, btn_y = SCREEN_WIDTH // 2 - 80, 300
            btn_w, btn_h = 160, 50
            rl.draw_rectangle(btn_x, btn_y, btn_w, btn_h, rl.Color(40, 160, 130, 200))
            rl.draw_rectangle_lines(btn_x, btn_y, btn_w, btn_h, ACCENT)
            rl.draw_text("CLICK START", btn_x + 15, btn_y + 15, 20, WHITE)
            
            # Instructions
            rl.draw_text("SPACE or CLICK to flap", SCREEN_WIDTH // 2 - 100, 400, 16, rl.Color(100, 100, 150, 255))
            rl.draw_text(f"High Score: {self.high_score}", SCREEN_WIDTH // 2 - 60, 450, 20, ACCENT)
            
            rl.end_drawing()
            
            # Check events
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
                return "play"
            if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
                return "play"
    
    def play(self):
        bird = Bird()
        pipes = [Pipe()]
        score = 0
        
        while bird.alive:
            if rl.window_should_close():
                return "quit"
            
            # Events
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE) or rl.is_key_pressed(rl.KeyboardKey.KEY_W):
                bird.jump()
            if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
                bird.jump()
            
            bird.update()
            
            # Spawn pipes
            if pipes[-1].x < SCREEN_WIDTH - 180:
                pipes.append(Pipe())
            
            # Update pipes
            for pipe in pipes:
                pipe.update()
                
                # Collision
                top_rect = pipe.get_top_rect()
                bottom_rect = pipe.get_bottom_rect()
                bird_rect = bird.get_rect()
                
                if rl.check_collision_recs(bird_rect, top_rect) or rl.check_collision_recs(bird_rect, bottom_rect):
                    bird.alive = False
                
                # Score
                if pipe.x + pipe.width // 2 < bird.x and not pipe.passed:
                    pipe.passed = True
                    score += 1
            
            # Remove off-screen pipes
            pipes = [p for p in pipes if p.x > -70]
            
            # Draw
            self.draw_background()
            
            for pipe in pipes:
                pipe.draw()
            
            self.draw_ground()
            bird.draw()
            
            # Score
            rl.draw_text(str(score), SCREEN_WIDTH // 2 - 20, 40, 48, WHITE)
            
            rl.end_drawing()
        
        if score > self.high_score:
            self.high_score = score
        
        return "gameover"
    
    def show_game_over(self, score):
        while True:
            if rl.window_should_close():
                return "quit"
            
            self.draw_background()
            self.draw_ground()
            
            rl.draw_text("GAME OVER", SCREEN_WIDTH // 2 - 90, 150, 48, rl.Color(255, 60, 60, 255))
            rl.draw_text(f"Score: {score}", SCREEN_WIDTH // 2 - 60, 230, 32, WHITE)
            rl.draw_text(f"Best: {self.high_score}", SCREEN_WIDTH // 2 - 50, 280, 24, ACCENT)
            
            # Retry button
            btn_x, btn_y = SCREEN_WIDTH // 2 - 60, 350
            btn_w, btn_h = 120, 45
            rl.draw_rectangle(btn_x, btn_y, btn_w, btn_h, rl.Color(40, 160, 130, 200))
            rl.draw_rectangle_lines(btn_x, btn_y, btn_w, btn_h, ACCENT)
            rl.draw_text("RETRY", btn_x + 30, btn_y + 12, 24, WHITE)
            
            rl.draw_text("ESC to quit", SCREEN_WIDTH // 2 - 50, 430, 16, rl.Color(100, 100, 150, 255))
            
            rl.end_drawing()
            
            # Events
            if rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
                return "quit"
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
                return "play"
            if rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
                mouse = rl.get_mouse_position()
                if (btn_x <= mouse.x <= btn_x + btn_w and 
                    btn_y <= mouse.y <= btn_y + btn_h):
                    return "play"
    
    def run(self):
        while True:
            action = self.show_menu()
            if action == "quit":
                break
            if action == "play":
                action = self.play()
            if action == "quit":
                break
            if action == "gameover":
                # Get last score
                score = 0
                action = self.show_game_over(score)
            if action == "quit":
                break
        
        rl.close_window()

if __name__ == "__main__":
    game = Game()
    game.run()