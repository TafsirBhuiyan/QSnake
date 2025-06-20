#!/usr/bin/env python3
"""
Simple Snake Game using standard library only (no pygame)
"""

import curses
import random
import time
import json
import os

# Game settings
GAME_WIDTH = 20
GAME_HEIGHT = 20
GAME_SPEED = {
    "Easy": 0.2,
    "Medium": 0.15,
    "Hard": 0.1,
    "Extreme": 0.05
}

# Define colors
SNAKE_CHAR = '#'
FOOD_CHAR = '*'
OBSTACLE_CHAR = 'X'
POWERUP_CHAR = 'P'

# Highscore file
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_highscores.json")

class Snake:
    def __init__(self):
        self.body = [(GAME_WIDTH // 2, GAME_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.grow = False
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.double_score = False
        self.double_score_timer = 0
    
    def get_head(self):
        return self.body[0]
    
    def update(self, wall_collision):
        head = self.get_head()
        dx, dy = self.direction
        new_x = head[0] + dx
        new_y = head[1] + dy
        
        # Handle wall collision based on game mode
        if wall_collision:
            # Check if snake hits the wall
            if new_x < 0 or new_x >= GAME_WIDTH or new_y < 0 or new_y >= GAME_HEIGHT:
                return True  # Game over
            new_position = (new_x, new_y)
        else:
            # Wrap around the screen
            new_position = (new_x % GAME_WIDTH, new_y % GAME_HEIGHT)
        
        # Check for collision with self (unless invincible)
        if not self.invincible and new_position in self.body[1:]:
            return True  # Game over
        
        self.body.insert(0, new_position)
        
        if not self.grow:
            self.body.pop()
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

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = "normal"  # normal, bonus, or special
        self.points = 1
        self.spawn_time = time.time()
        self.lifespan = None  # None means permanent
        self.randomize_position([])
    
    def randomize_position(self, occupied_positions):
        self.position = (random.randint(0, GAME_WIDTH - 1), 
                        random.randint(0, GAME_HEIGHT - 1))
        
        # Make sure food doesn't appear on occupied positions
        while self.position in occupied_positions:
            self.position = (random.randint(0, GAME_WIDTH - 1), 
                            random.randint(0, GAME_HEIGHT - 1))
        
        # Randomly determine food type
        food_type = random.random()
        if food_type < 0.7:  # 70% chance for normal food
            self.type = "normal"
            self.points = 1
            self.lifespan = None
        elif food_type < 0.9:  # 20% chance for bonus food
            self.type = "bonus"
            self.points = 3
            self.lifespan = 5  # 5 seconds
        else:  # 10% chance for special food (power-up)
            self.type = "special"
            self.points = 2
            self.lifespan = 7  # 7 seconds
        
        self.spawn_time = time.time()
    
    def update(self):
        # Check if temporary food should disappear
        if self.lifespan and time.time() - self.spawn_time > self.lifespan:
            return True  # Food should be replaced
        return False

class PowerUp:
    def __init__(self):
        self.position = (0, 0)
        self.active = False
        self.type = None
        self.spawn_time = 0
        self.lifespan = 10  # 10 seconds
    
    def spawn(self, occupied_positions):
        if not self.active and random.random() < 0.02:  # 2% chance per frame to spawn
            self.position = (random.randint(0, GAME_WIDTH - 1), 
                            random.randint(0, GAME_HEIGHT - 1))
            
            # Make sure it doesn't spawn on occupied positions
            while self.position in occupied_positions:
                self.position = (random.randint(0, GAME_WIDTH - 1), 
                                random.randint(0, GAME_HEIGHT - 1))
            
            # Choose a random power-up type
            self.type = random.choice(["speed", "invincible", "double_score"])
            self.active = True
            self.spawn_time = time.time()
    
    def update(self):
        if self.active and time.time() - self.spawn_time > self.lifespan:
            self.active = False

class Obstacle:
    def __init__(self):
        self.positions = []
        self.generate()
    
    def generate(self):
        self.positions = []
        # Create 5-10 random obstacles
        num_obstacles = random.randint(5, 10)
        for _ in range(num_obstacles):
            pos = (random.randint(2, GAME_WIDTH - 3), random.randint(2, GAME_HEIGHT - 3))
            # Make sure obstacles aren't too close to the center where the snake starts
            if abs(pos[0] - GAME_WIDTH // 2) > 3 or abs(pos[1] - GAME_HEIGHT // 2) > 3:
                self.positions.append(pos)

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.snake = Snake()
        self.food = Food()
        self.power_up = PowerUp()
        self.obstacles = Obstacle()
        self.score = 0
        self.high_scores = self.load_high_scores()
        self.game_over = False
        self.paused = False
        self.difficulty = "Easy"
        self.speed = GAME_SPEED[self.difficulty]
        self.wall_collision = False
        
        # Set up colors if terminal supports them
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # PowerUp
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Text
            curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Obstacle
            self.has_colors = True
        except:
            self.has_colors = False
    
    def load_high_scores(self):
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    return json.load(f)
            return {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0}
        except:
            return {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0}
    
    def save_high_scores(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f)
        except:
            pass  # Silently fail if we can't save
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        # Update game objects
        self.game_over = self.snake.update(self.wall_collision)
        
        # Check if snake ate food
        if self.snake.get_head() == self.food.position:
            self.snake.grow = True
            
            # Calculate points
            points = self.food.points
            if self.snake.double_score:
                points *= 2
            
            self.score += points
            
            # Generate new food
            occupied = self.snake.body + self.obstacles.positions
            if self.power_up.active:
                occupied.append(self.power_up.position)
            self.food.randomize_position(occupied)
        
        # Check if food needs to be replaced (temporary foods)
        if self.food.update():
            occupied = self.snake.body + self.obstacles.positions
            if self.power_up.active:
                occupied.append(self.power_up.position)
            self.food.randomize_position(occupied)
        
        # Check if snake hit an obstacle
        if self.snake.get_head() in self.obstacles.positions and not self.snake.invincible:
            self.game_over = True
        
        # Update power-up
        self.power_up.update()
        occupied = self.snake.body + self.obstacles.positions + [self.food.position]
        self.power_up.spawn(occupied)
        
        # Check if snake collected a power-up
        if self.power_up.active and self.snake.get_head() == self.power_up.position:
            if self.power_up.type == "speed":
                self.snake.speed_boost = True
                self.snake.speed_boost_timer = 20  # Duration in frames
            elif self.power_up.type == "invincible":
                self.snake.invincible = True
                self.snake.invincible_timer = 20  # Duration in frames
            elif self.power_up.type == "double_score":
                self.snake.double_score = True
                self.snake.double_score_timer = 20  # Duration in frames
            
            self.power_up.active = False
        
        # Check for game over
        if self.game_over:
            # Update high score if needed
            if self.score > self.high_scores[self.difficulty]:
                self.high_scores[self.difficulty] = self.score
                self.save_high_scores()
    
    def draw(self):
        self.stdscr.clear()
        
        # Draw border
        for i in range(GAME_WIDTH + 2):
            self.stdscr.addstr(0, i, "-")
            self.stdscr.addstr(GAME_HEIGHT + 1, i, "-")
        for i in range(GAME_HEIGHT + 2):
            self.stdscr.addstr(i, 0, "|")
            self.stdscr.addstr(i, GAME_WIDTH + 1, "|")
        
        # Draw obstacles
        for pos in self.obstacles.positions:
            x, y = pos
            if self.has_colors:
                self.stdscr.addstr(y + 1, x + 1, OBSTACLE_CHAR, curses.color_pair(5))
            else:
                self.stdscr.addstr(y + 1, x + 1, OBSTACLE_CHAR)
        
        # Draw food
        x, y = self.food.position
        food_display = FOOD_CHAR
        if self.food.type == "bonus":
            food_display = "B"
        elif self.food.type == "special":
            food_display = "S"
        
        if self.has_colors:
            self.stdscr.addstr(y + 1, x + 1, food_display, curses.color_pair(2))
        else:
            self.stdscr.addstr(y + 1, x + 1, food_display)
        
        # Draw power-up
        if self.power_up.active:
            x, y = self.power_up.position
            if self.has_colors:
                self.stdscr.addstr(y + 1, x + 1, POWERUP_CHAR, curses.color_pair(3))
            else:
                self.stdscr.addstr(y + 1, x + 1, POWERUP_CHAR)
        
        # Draw snake
        for i, pos in enumerate(self.snake.body):
            x, y = pos
            if self.has_colors:
                # Head is brighter
                if i == 0:
                    self.stdscr.addstr(y + 1, x + 1, SNAKE_CHAR, curses.color_pair(1) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(y + 1, x + 1, SNAKE_CHAR, curses.color_pair(1))
            else:
                self.stdscr.addstr(y + 1, x + 1, SNAKE_CHAR)
        
        # Draw score and info
        self.stdscr.addstr(GAME_HEIGHT + 3, 1, f"Score: {self.score}")
        self.stdscr.addstr(GAME_HEIGHT + 4, 1, f"High Score: {self.high_scores[self.difficulty]}")
        self.stdscr.addstr(GAME_HEIGHT + 3, GAME_WIDTH // 2, f"Difficulty: {self.difficulty}")
        self.stdscr.addstr(GAME_HEIGHT + 4, GAME_WIDTH // 2, f"{'Wall Collision' if self.wall_collision else 'Screen Wrap'}")
        
        # Draw active power-ups
        power_up_y = GAME_HEIGHT + 5
        if self.snake.speed_boost:
            self.stdscr.addstr(power_up_y, 1, "Speed Boost!")
            power_up_y += 1
        
        if self.snake.invincible:
            self.stdscr.addstr(power_up_y, 1, "Invincible!")
            power_up_y += 1
        
        if self.snake.double_score:
            self.stdscr.addstr(power_up_y, 1, "Double Score!")
        
        # Draw game over message
        if self.game_over:
            self.stdscr.addstr(GAME_HEIGHT // 2, GAME_WIDTH // 2 - 4, "GAME OVER")
            self.stdscr.addstr(GAME_HEIGHT // 2 + 1, GAME_WIDTH // 2 - 8, "Press R to Restart")
            self.stdscr.addstr(GAME_HEIGHT // 2 + 2, GAME_WIDTH // 2 - 7, "Press Q to Quit")
        
        # Draw pause message
        elif self.paused:
            self.stdscr.addstr(GAME_HEIGHT // 2, GAME_WIDTH // 2 - 3, "PAUSED")
            self.stdscr.addstr(GAME_HEIGHT // 2 + 1, GAME_WIDTH // 2 - 9, "Press P to Continue")
        
        # Draw controls
        self.stdscr.addstr(GAME_HEIGHT + 7, 1, "Controls: Arrows=Move, P=Pause, W=Toggle Walls, 1-4=Difficulty, Q=Quit")
        
        self.stdscr.refresh()
    
    def change_difficulty(self, difficulty):
        if difficulty in GAME_SPEED:
            self.difficulty = difficulty
            self.speed = GAME_SPEED[difficulty]
            # Hard and Extreme have wall collision by default
            if difficulty in ["Hard", "Extreme"]:
                self.wall_collision = True
            else:
                self.wall_collision = False
    
    def toggle_wall_collision(self):
        self.wall_collision = not self.wall_collision

def show_menu(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    # Set up colors if terminal supports them
    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        has_colors = True
    except:
        has_colors = False
    
    # Load high scores
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                high_scores = json.load(f)
        else:
            high_scores = {diff: 0 for diff in GAME_SPEED.keys()}
    except:
        high_scores = {diff: 0 for diff in GAME_SPEED.keys()}
    
    options = list(GAME_SPEED.keys())
    selected = 0
    
    while True:
        stdscr.clear()
        
        # Draw title
        title = "SNAKE GAME"
        stdscr.addstr(1, GAME_WIDTH // 2 - len(title) // 2, title)
        subtitle = "Select Difficulty"
        stdscr.addstr(3, GAME_WIDTH // 2 - len(subtitle) // 2, subtitle)
        
        # Draw options
        for i, option in enumerate(options):
            y = 5 + i * 2
            x = GAME_WIDTH // 2 - len(option) // 2
            
            if i == selected:
                if has_colors:
                    stdscr.addstr(y, x, option, curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.addstr(y, x, option, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, option)
            
            # Show high score
            score_text = f"High Score: {high_scores.get(option, 0)}"
            stdscr.addstr(y + 1, GAME_WIDTH // 2 - len(score_text) // 2, score_text)
        
        # Draw instructions
        stdscr.addstr(14, 1, "Use UP/DOWN arrows to select, ENTER to start")
        
        stdscr.refresh()
        
        # Handle input
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key == 10:  # Enter key
            return options[selected]
        elif key == ord('q'):
            return None

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(100) # Input timeout
    
    while True:
        # Show menu and get difficulty
        difficulty = show_menu(stdscr)
        if difficulty is None:
            break
        
        # Initialize game
        game = Game(stdscr)
        game.change_difficulty(difficulty)
        
        last_update_time = time.time()
        
        # Main game loop
        while not game.game_over:
            # Handle input
            try:
                key = stdscr.getch()
            except:
                key = -1
            
            if key == ord('q'):
                return
            elif key == ord('p'):
                game.paused = not game.paused
            elif key == ord('w'):
                game.toggle_wall_collision()
            elif key == ord('1'):
                game.change_difficulty("Easy")
            elif key == ord('2'):
                game.change_difficulty("Medium")
            elif key == ord('3'):
                game.change_difficulty("Hard")
            elif key == ord('4'):
                game.change_difficulty("Extreme")
            elif not game.paused:
                if key == curses.KEY_UP:
                    game.snake.direction = (0, -1)
                elif key == curses.KEY_DOWN:
                    game.snake.direction = (0, 1)
                elif key == curses.KEY_LEFT:
                    game.snake.direction = (-1, 0)
                elif key == curses.KEY_RIGHT:
                    game.snake.direction = (1, 0)
            
            # Update game at appropriate speed
            current_time = time.time()
            update_interval = game.speed
            if game.snake.speed_boost:
                update_interval /= 2  # Double speed with boost
            
            if current_time - last_update_time >= update_interval:
                game.update()
                last_update_time = current_time
            
            # Draw game
            game.draw()
            
            # Handle game over
            if game.game_over:
                while True:
                    key = stdscr.getch()
                    if key == ord('q'):
                        return
                    elif key == ord('r'):
                        break
                    game.draw()
                    time.sleep(0.1)
                break

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
