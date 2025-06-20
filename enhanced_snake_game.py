import pygame
import sys
import random
import time
import os
import json

# Initialize pygame
pygame.init()
print(f"Pygame initialized: {pygame.get_init()}")

# Initialize sound mixer with specific settings for better compatibility
try:
    pygame.mixer.quit()  # Reset the mixer if it was already initialized
    pygame.mixer.init(44100, -16, 2, 512)  # CD quality audio
    print(f"Pygame mixer initialized: {pygame.mixer.get_init()}")
    print(f"Mixer settings: frequency={pygame.mixer.get_init()[0]}, size={pygame.mixer.get_init()[1]}, channels={pygame.mixer.get_init()[2]}")
except Exception as e:
    print(f"Error initializing mixer: {e}")

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Game settings
FPS = 60
DEFAULT_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_game_assets")
USER_SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

# Print the actual paths for debugging
print(f"Default assets directory: {DEFAULT_ASSETS_DIR}")
print(f"User sounds directory: {USER_SOUNDS_DIR}")
HIGHSCORE_FILE = os.path.join(DEFAULT_ASSETS_DIR, "highscores.json")

# Difficulty settings
DIFFICULTY_LEVELS = {
    "Easy": {"speed": 8, "color": GREEN, "wall_collision": False},
    "Medium": {"speed": 12, "color": BLUE, "wall_collision": False},
    "Hard": {"speed": 16, "color": RED, "wall_collision": True},
    "Extreme": {"speed": 20, "color": YELLOW, "wall_collision": True}
}

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Snake Game")
clock = pygame.time.Clock()

# Font for text display
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# Load sounds
try:
    print("\n--- SOUND SYSTEM DEBUGGING ---")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if sound directories exist
    print(f"Default assets sounds directory exists: {os.path.exists(os.path.join(DEFAULT_ASSETS_DIR, 'sounds'))}")
    print(f"User sounds directory exists: {os.path.exists(USER_SOUNDS_DIR)}")
    
    # List all files in sound directories
    print("\nFiles in default assets sounds directory:")
    try:
        sound_files = os.listdir(os.path.join(DEFAULT_ASSETS_DIR, 'sounds'))
        for file in sound_files:
            print(f"  - {file}")
    except Exception as e:
        print(f"  Error listing files: {e}")
    
    print("\nFiles in user sounds directory:")
    try:
        sound_files = os.listdir(USER_SOUNDS_DIR)
        for file in sound_files:
            print(f"  - {file}")
    except Exception as e:
        print(f"  Error listing files: {e}")
    
    # Try to load WAV files first, then MP3 if WAV not found
    # Check both the default assets directory and the user's sounds directory
    def try_load_sound(filename):
        print(f"\nAttempting to load sound: {filename}")
        
        # Try in the default assets directory first (since you moved files there)
        default_path = os.path.join(DEFAULT_ASSETS_DIR, "sounds", filename)
        if os.path.exists(default_path):
            print(f"  Found sound file in default directory: {default_path}")
            try:
                sound = pygame.mixer.Sound(default_path)
                print(f"  Successfully loaded sound from: {default_path}")
                return sound
            except Exception as e:
                print(f"  Error loading sound from default directory {filename}: {e}")
        else:
            print(f"  File not found in default directory: {default_path}")
        
        # Try in the user's sounds directory
        try:
            normal_path = os.path.join(USER_SOUNDS_DIR, filename)
            if os.path.exists(normal_path):
                print(f"  Found sound file: {normal_path}")
                sound = pygame.mixer.Sound(normal_path)
                print(f"  Successfully loaded sound from: {normal_path}")
                return sound
            else:
                print(f"  File not found: {normal_path}")
        except Exception as e:
            print(f"  Error loading sound {filename}: {e}")
        
        # Try with double extension
        try:
            # Check for files with double extensions (e.g., eat.wav.wav)
            double_ext = os.path.join(USER_SOUNDS_DIR, filename + "." + filename.split(".")[-1])
            if os.path.exists(double_ext):
                print(f"  Found sound file with double extension: {double_ext}")
                sound = pygame.mixer.Sound(double_ext)
                print(f"  Successfully loaded sound from: {double_ext}")
                return sound
            else:
                print(f"  File not found with double extension: {double_ext}")
        except Exception as e:
            print(f"  Error loading double extension sound {filename}: {e}")
        
        print(f"  Could not find or load sound: {filename}")
        return None
    
    # Load eat sound
    eat_sound = try_load_sound("eat.wav")
    if eat_sound is None:
        eat_sound = try_load_sound("eat.mp3")
    
    # Load game over sound
    game_over_sound = try_load_sound("game_over.wav")
    if game_over_sound is None:
        game_over_sound = try_load_sound("game_over.mp3")
    
    # Load powerup sound
    powerup_sound = try_load_sound("powerup.wav")
    if powerup_sound is None:
        powerup_sound = try_load_sound("powerup.mp3")
    
    # Set maximum volume for all sounds
    if eat_sound:
        eat_sound.set_volume(1.0)
        print("Eat sound volume set to maximum")
    if game_over_sound:
        game_over_sound.set_volume(1.0)
        print("Game over sound volume set to maximum")
    if powerup_sound:
        powerup_sound.set_volume(1.0)
        print("Power-up sound volume set to maximum")
    
except Exception as e:
    print(f"Warning: Error loading sound files: {e}")
    eat_sound = None
    game_over_sound = None
    powerup_sound = None

# Try to load background music
try:
    print("\n--- BACKGROUND MUSIC DEBUGGING ---")
    
    # Define a function to try loading music from different locations
    def try_load_music(filename):
        print(f"Attempting to load music: {filename}")
        
        # Try in the default assets directory first (since you moved files there)
        default_path = os.path.join(DEFAULT_ASSETS_DIR, "sounds", filename)
        if os.path.exists(default_path):
            print(f"  Found music file in default directory: {default_path}")
            try:
                pygame.mixer.music.load(default_path)
                print(f"  Successfully loaded music from: {default_path}")
                return True
            except Exception as e:
                print(f"  Error loading music from default directory {filename}: {e}")
        else:
            print(f"  File not found in default directory: {default_path}")
        
        # Try in the user's sounds directory with normal extension
        normal_path = os.path.join(USER_SOUNDS_DIR, filename)
        if os.path.exists(normal_path):
            print(f"  Found music file: {normal_path}")
            try:
                pygame.mixer.music.load(normal_path)
                print(f"  Successfully loaded music from: {normal_path}")
                return True
            except Exception as e:
                print(f"  Error loading music {filename}: {e}")
        else:
            print(f"  File not found: {normal_path}")
        
        # Try with double extension
        double_ext = os.path.join(USER_SOUNDS_DIR, filename + "." + filename.split(".")[-1])
        if os.path.exists(double_ext):
            print(f"  Found music file with double extension: {double_ext}")
            try:
                pygame.mixer.music.load(double_ext)
                print(f"  Successfully loaded music from: {double_ext}")
                return True
            except Exception as e:
                print(f"  Error loading music with double extension {filename}: {e}")
        else:
            print(f"  File not found with double extension: {double_ext}")
        
        print(f"  Could not find or load music: {filename}")
        return False
    
    # Try to load background music (MP3 first, then WAV)
    has_bg_music = try_load_music("background.mp3")
    if not has_bg_music:
        has_bg_music = try_load_music("background.wav")
    
    print(f"Background music loaded: {has_bg_music}")
    
except Exception as e:
    print(f"Warning: Error loading background music: {e}")
    has_bg_music = False

# Particle effect class
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.life = 30
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.grow = False
        self.color = GREEN  # Default color
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.double_score = False
        self.double_score_timer = 0
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self, wall_collision):
        head = self.get_head_position()
        x, y = self.direction
        
        # Calculate new position
        new_x = head[0] + x
        new_y = head[1] + y
        
        # Handle wall collision based on game mode
        if wall_collision:
            # Check if snake hits the wall
            if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                return True  # Game over
            new_position = (new_x, new_y)
        else:
            # Wrap around the screen
            new_position = (new_x % GRID_WIDTH, new_y % GRID_HEIGHT)
        
        # Check for collision with self (unless invincible)
        if not self.invincible and new_position in self.positions[1:]:
            return True  # Game over
        
        self.positions.insert(0, new_position)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        
        # Update power-up timers
        if self.speed_boost:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        if self.double_score:
            self.double_score_timer -= 1
            if self.double_score_timer <= 0:
                self.double_score = False
        
        return False  # Game continues
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def grow_snake(self):
        self.grow = True
    
    def draw(self):
        # Draw snake body
        for i, position in enumerate(self.positions):
            rect = pygame.Rect(position[0] * GRID_SIZE, position[1] * GRID_SIZE, 
                              GRID_SIZE, GRID_SIZE)
            
            # Special effects for power-ups
            if i == 0:  # Head
                color = self.color
                if self.invincible:
                    # Flashing effect for invincibility
                    if pygame.time.get_ticks() % 200 < 100:
                        color = WHITE
            elif self.speed_boost and i < 3:
                # Speed boost effect on first few segments
                color = YELLOW
            elif self.double_score and i < 3:
                # Double score effect on first few segments
                color = PURPLE
            else:
                # Normal body color with gradient effect
                color = self.color
                
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)  # Border

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = "normal"  # normal, bonus, or special
        self.color = RED
        self.points = 1
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = None  # None means permanent
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(0, GRID_HEIGHT - 1))
        
        # Randomly determine food type
        food_type = random.random()
        if food_type < 0.7:  # 70% chance for normal food
            self.type = "normal"
            self.color = RED
            self.points = 1
            self.lifespan = None
        elif food_type < 0.9:  # 20% chance for bonus food
            self.type = "bonus"
            self.color = ORANGE
            self.points = 3
            self.lifespan = 5000  # 5 seconds
        else:  # 10% chance for special food (power-up)
            self.type = "special"
            self.color = PURPLE
            self.points = 2
            self.lifespan = 7000  # 7 seconds
        
        self.spawn_time = pygame.time.get_ticks()
    
    def update(self):
        # Check if temporary food should disappear
        if self.lifespan and pygame.time.get_ticks() - self.spawn_time > self.lifespan:
            return True  # Food should be replaced
        return False
    
    def draw(self):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, 
                          GRID_SIZE, GRID_SIZE)
        
        # Pulsating effect for special foods
        if self.type != "normal":
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            size_mod = int(GRID_SIZE * (0.8 + 0.2 * pulse))
            pulse_rect = pygame.Rect(
                self.position[0] * GRID_SIZE + (GRID_SIZE - size_mod) // 2,
                self.position[1] * GRID_SIZE + (GRID_SIZE - size_mod) // 2,
                size_mod, size_mod
            )
            pygame.draw.rect(screen, self.color, pulse_rect)
        else:
            pygame.draw.rect(screen, self.color, rect)
        
        pygame.draw.rect(screen, WHITE, rect, 1)  # Border

class Obstacle:
    def __init__(self):
        self.positions = []
        self.generate()
    
    def generate(self):
        self.positions = []
        # Create 5-10 random obstacles
        num_obstacles = random.randint(5, 10)
        for _ in range(num_obstacles):
            pos = (random.randint(2, GRID_WIDTH - 3), random.randint(2, GRID_HEIGHT - 3))
            # Make sure obstacles aren't too close to the center where the snake starts
            if abs(pos[0] - GRID_WIDTH // 2) > 3 or abs(pos[1] - GRID_HEIGHT // 2) > 3:
                self.positions.append(pos)
    
    def draw(self):
        for position in self.positions:
            rect = pygame.Rect(position[0] * GRID_SIZE, position[1] * GRID_SIZE, 
                              GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, (100, 100, 100), rect)
            pygame.draw.rect(screen, WHITE, rect, 1)  # Border

class PowerUp:
    def __init__(self):
        self.position = (0, 0)
        self.active = False
        self.type = None
        self.spawn_time = 0
        self.lifespan = 10000  # 10 seconds
    
    def spawn(self, snake_positions):
        if not self.active and random.random() < 0.02:  # 2% chance per frame to spawn
            self.position = (random.randint(0, GRID_WIDTH - 1), 
                            random.randint(0, GRID_HEIGHT - 1))
            
            # Make sure it doesn't spawn on the snake
            while self.position in snake_positions:
                self.position = (random.randint(0, GRID_WIDTH - 1), 
                                random.randint(0, GRID_HEIGHT - 1))
            
            # Choose a random power-up type
            self.type = random.choice(["speed", "invincible", "double_score"])
            self.active = True
            self.spawn_time = pygame.time.get_ticks()
    
    def update(self):
        if self.active and pygame.time.get_ticks() - self.spawn_time > self.lifespan:
            self.active = False
    
    def draw(self):
        if self.active:
            rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, 
                              GRID_SIZE, GRID_SIZE)
            
            if self.type == "speed":
                color = YELLOW
            elif self.type == "invincible":
                color = WHITE
            else:  # double_score
                color = PURPLE
            
            # Pulsating effect
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            size_mod = int(GRID_SIZE * (0.7 + 0.3 * pulse))
            pulse_rect = pygame.Rect(
                self.position[0] * GRID_SIZE + (GRID_SIZE - size_mod) // 2,
                self.position[1] * GRID_SIZE + (GRID_SIZE - size_mod) // 2,
                size_mod, size_mod
            )
            
            pygame.draw.rect(screen, color, pulse_rect)
            pygame.draw.rect(screen, WHITE, rect, 1)  # Border

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.obstacles = Obstacle()
        self.power_up = PowerUp()
        self.score = 0
        self.high_scores = self.load_high_scores()
        self.game_over = False
        self.paused = False
        self.difficulty = "Easy"
        self.speed = DIFFICULTY_LEVELS[self.difficulty]["speed"]
        self.wall_collision = DIFFICULTY_LEVELS[self.difficulty]["wall_collision"]
        self.snake.color = DIFFICULTY_LEVELS[self.difficulty]["color"]
        self.particles = []
        self.last_update_time = pygame.time.get_ticks()
        self.frame_time = 0
        
        # Print sound file paths for debugging
        print(f"Looking for sounds in: {USER_SOUNDS_DIR} and {DEFAULT_ASSETS_DIR}/sounds")
        
        # Start background music if available
        if has_bg_music:
            try:
                print("Starting background music...")
                pygame.mixer.music.set_volume(1.0)  # Set to maximum volume
                pygame.mixer.music.play(-1)  # Loop indefinitely
                print("Background music started successfully")
            except Exception as e:
                print(f"Error playing background music: {e}")
    
    def load_high_scores(self):
        try:
            highscore_file = os.path.join(DEFAULT_ASSETS_DIR, "highscores.json")
            if os.path.exists(highscore_file):
                with open(highscore_file, 'r') as f:
                    return json.load(f)
            return {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0}
        except:
            print("Error loading high scores")
            return {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0}
    
    def save_high_scores(self):
        try:
            highscore_file = os.path.join(DEFAULT_ASSETS_DIR, "highscores.json")
            os.makedirs(os.path.dirname(highscore_file), exist_ok=True)
            with open(highscore_file, 'w') as f:
                json.dump(self.high_scores, f)
        except:
            print("Error saving high scores")
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        # Calculate delta time for smooth movement
        current_time = pygame.time.get_ticks()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Accumulate frame time
        self.frame_time += dt
        
        # Only update game logic at the specified speed
        update_interval = 1000 // self.speed
        if self.snake.speed_boost:
            update_interval = update_interval // 2  # Double speed with boost
        
        if self.frame_time >= update_interval:
            self.frame_time = 0
            
            # Update game objects
            self.game_over = self.snake.update(self.wall_collision)
            
            # Check if snake ate food
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow_snake()
                
                # Calculate points
                points = self.food.points
                if self.snake.double_score:
                    points *= 2
                
                self.score += points
                
                # Create particle effect at food position
                self.create_particles(
                    self.food.position[0] * GRID_SIZE + GRID_SIZE // 2,
                    self.food.position[1] * GRID_SIZE + GRID_SIZE // 2,
                    self.food.color
                )
                
                # Play sound effect with debug info
                if eat_sound:
                    try:
                        print(f"Playing eat sound...")
                        eat_sound.play()
                        print(f"Eat sound played successfully")
                    except Exception as e:
                        print(f"Error playing eat sound: {e}")
                else:
                    print("Eat sound not available")
                
                # Generate new food
                self.food.randomize_position()
                # Make sure food doesn't appear on snake or obstacles
                while (self.food.position in self.snake.positions or 
                      self.food.position in self.obstacles.positions):
                    self.food.randomize_position()
            
            # Check if food needs to be replaced (temporary foods)
            if self.food.update():
                self.food.randomize_position()
                while (self.food.position in self.snake.positions or 
                      self.food.position in self.obstacles.positions):
                    self.food.randomize_position()
            
            # Check if snake hit an obstacle
            if self.snake.get_head_position() in self.obstacles.positions and not self.snake.invincible:
                self.game_over = True
            
            # Update power-up
            self.power_up.update()
            self.power_up.spawn(self.snake.positions)
            
            # Check if snake collected a power-up
            if self.power_up.active and self.snake.get_head_position() == self.power_up.position:
                if self.power_up.type == "speed":
                    self.snake.speed_boost = True
                    self.snake.speed_boost_timer = 100  # Duration in frames
                elif self.power_up.type == "invincible":
                    self.snake.invincible = True
                    self.snake.invincible_timer = 100  # Duration in frames
                elif self.power_up.type == "double_score":
                    self.snake.double_score = True
                    self.snake.double_score_timer = 100  # Duration in frames
                
                # Create particle effect at power-up position
                self.create_particles(
                    self.power_up.position[0] * GRID_SIZE + GRID_SIZE // 2,
                    self.power_up.position[1] * GRID_SIZE + GRID_SIZE // 2,
                    WHITE
                )
                
                # Play power-up sound with debug info
                if powerup_sound:
                    try:
                        print(f"Playing powerup sound...")
                        powerup_sound.play()
                        print(f"Powerup sound played successfully")
                    except Exception as e:
                        print(f"Error playing powerup sound: {e}")
                else:
                    print("Powerup sound not available")
                
                self.power_up.active = False
        
        # Update particles regardless of game speed
        self.update_particles()
        
        # Check for game over
        if self.game_over:
            # Update high score if needed
            if self.score > self.high_scores[self.difficulty]:
                self.high_scores[self.difficulty] = self.score
                self.save_high_scores()
            
            # Play game over sound with debug info
            if game_over_sound:
                try:
                    print(f"Playing game over sound...")
                    game_over_sound.play()
                    print(f"Game over sound played successfully")
                except Exception as e:
                    print(f"Error playing game over sound: {e}")
            else:
                print("Game over sound not available")
    
    def create_particles(self, x, y, color):
        # Create explosion effect
        for _ in range(20):
            self.particles.append(Particle(x, y, color))
    
    def update_particles(self):
        # Update and remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self):
        screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))
        
        # Draw game elements
        self.obstacles.draw()
        self.food.draw()
        if self.power_up.active:
            self.power_up.draw()
        self.snake.draw()
        
        # Draw particles
        for particle in self.particles:
            particle.draw()
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw high score
        high_score_text = font.render(f"High Score: {self.high_scores[self.difficulty]}", True, WHITE)
        screen.blit(high_score_text, (10, 50))
        
        # Draw difficulty
        diff_text = font.render(f"Difficulty: {self.difficulty}", True, DIFFICULTY_LEVELS[self.difficulty]["color"])
        screen.blit(diff_text, (WIDTH - diff_text.get_width() - 10, 10))
        
        # Draw wall mode
        wall_text = small_font.render(
            f"{'Wall Collision' if self.wall_collision else 'Screen Wrap'}", 
            True, WHITE
        )
        screen.blit(wall_text, (WIDTH - wall_text.get_width() - 10, 50))
        
        # Draw active power-ups
        power_up_y = 80
        if self.snake.speed_boost:
            speed_text = small_font.render("Speed Boost!", True, YELLOW)
            screen.blit(speed_text, (WIDTH - speed_text.get_width() - 10, power_up_y))
            power_up_y += 25
        
        if self.snake.invincible:
            invincible_text = small_font.render("Invincible!", True, WHITE)
            screen.blit(invincible_text, (WIDTH - invincible_text.get_width() - 10, power_up_y))
            power_up_y += 25
        
        if self.snake.double_score:
            double_text = small_font.render("Double Score!", True, PURPLE)
            screen.blit(double_text, (WIDTH - double_text.get_width() - 10, power_up_y))
        
        # Draw game over message
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
            
            game_over_text = large_font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to Restart", True, WHITE)
            menu_text = font.render("Press M for Menu", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
            screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 40))
        
        # Draw pause overlay
        elif self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
            
            pause_text = large_font.render("PAUSED", True, WHITE)
            continue_text = font.render("Press P to Continue", True, WHITE)
            
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 20))
    
    def change_difficulty(self, difficulty):
        if difficulty in DIFFICULTY_LEVELS:
            self.difficulty = difficulty
            self.speed = DIFFICULTY_LEVELS[difficulty]["speed"]
            self.wall_collision = DIFFICULTY_LEVELS[difficulty]["wall_collision"]
            self.snake.color = DIFFICULTY_LEVELS[difficulty]["color"]
    
    def toggle_wall_collision(self):
        self.wall_collision = not self.wall_collision

def show_difficulty_menu():
    menu_active = True
    selected = 0
    options = list(DIFFICULTY_LEVELS.keys())
    
    # Load high scores
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                high_scores = json.load(f)
        else:
            high_scores = {diff: 0 for diff in options}
    except:
        high_scores = {diff: 0 for diff in options}
    
    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    menu_active = False
        
        screen.fill(BLACK)
        
        title_text = large_font.render("Snake Game", True, GREEN)
        subtitle_text = font.render("Select Difficulty", True, WHITE)
        
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 150))
        
        for i, option in enumerate(options):
            color = DIFFICULTY_LEVELS[option]["color"] if i == selected else WHITE
            option_text = font.render(option, True, color)
            
            # Show high score for each difficulty
            score_text = small_font.render(f"High Score: {high_scores.get(option, 0)}", True, WHITE)
            
            # Show if this mode has wall collision
            wall_text = small_font.render(
                f"{'Wall Collision' if DIFFICULTY_LEVELS[option]['wall_collision'] else 'Screen Wrap'}", 
                True, WHITE
            )
            
            y_pos = 200 + i * 70
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, y_pos))
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y_pos + 30))
            screen.blit(wall_text, (WIDTH // 2 - wall_text.get_width() // 2, y_pos + 50))
        
        controls_text = small_font.render("Controls: Arrow Keys to move, P to pause, W to toggle wall collision", True, WHITE)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 50))
        
        pygame.display.flip()
        clock.tick(10)
    
    return options[selected]

def main():
    # Create asset directories if they don't exist
    os.makedirs(os.path.join(DEFAULT_ASSETS_DIR, "sounds"), exist_ok=True)
    os.makedirs(os.path.join(DEFAULT_ASSETS_DIR, "images"), exist_ok=True)
    
    while True:
        # Show difficulty menu
        selected_difficulty = show_difficulty_menu()
        
        # Initialize game
        game = Game()
        game.change_difficulty(selected_difficulty)
        
        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if not game.game_over:
                        if event.key == pygame.K_UP:
                            game.snake.change_direction((0, -1))
                        elif event.key == pygame.K_DOWN:
                            game.snake.change_direction((0, 1))
                        elif event.key == pygame.K_LEFT:
                            game.snake.change_direction((-1, 0))
                        elif event.key == pygame.K_RIGHT:
                            game.snake.change_direction((1, 0))
                        # Pause game
                        elif event.key == pygame.K_p:
                            game.paused = not game.paused
                        # Toggle wall collision
                        elif event.key == pygame.K_w:
                            game.toggle_wall_collision()
                        # Change difficulty during gameplay
                        elif event.key == pygame.K_1:
                            game.change_difficulty("Easy")
                        elif event.key == pygame.K_2:
                            game.change_difficulty("Medium")
                        elif event.key == pygame.K_3:
                            game.change_difficulty("Hard")
                        elif event.key == pygame.K_4:
                            game.change_difficulty("Extreme")
                        # Mute/unmute music
                        elif event.key == pygame.K_m and has_bg_music:
                            if pygame.mixer.music.get_volume() > 0:
                                pygame.mixer.music.set_volume(0)
                            else:
                                pygame.mixer.music.set_volume(1)
                    else:
                        if event.key == pygame.K_r:
                            # Restart game with same difficulty
                            game = Game()
                            game.change_difficulty(selected_difficulty)
                        elif event.key == pygame.K_m:
                            # Return to menu
                            running = False
            
            game.update()
            game.draw()
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()
