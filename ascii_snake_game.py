#!/usr/bin/env python3
"""
Simple ASCII Snake Game using only standard library
"""

import os
import sys
import time
import random
import json
import threading
import signal

# Game settings
WIDTH = 20
HEIGHT = 10
DIFFICULTY_LEVELS = {
    "Easy": 0.3,      # seconds per move
    "Medium": 0.2,
    "Hard": 0.1,
    "Extreme": 0.05
}

# Game elements
SNAKE_HEAD = 'O'
SNAKE_BODY = 'o'
FOOD = '*'
BONUS_FOOD = '$'
SPECIAL_FOOD = '@'
POWERUP = 'P'
OBSTACLE = 'X'
EMPTY = ' '
BORDER = '#'

# Highscore file
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_highscores.json")

# Global variables for input handling
direction_queue = []
current_direction = (1, 0)  # Start moving right
game_running = True
game_paused = False

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_high_scores():
    """Load high scores from file."""
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                return json.load(f)
        return {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0}
    except:
        return {"Easy": 0, "Medium": 0, "Hard": 0, "Extreme": 0}

def save_high_scores(high_scores):
    """Save high scores to file."""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(high_scores, f)
    except:
        pass  # Silently fail if we can't save

def get_key():
    """Get a single keypress from the user."""
    global direction_queue, game_running, game_paused
    
    while game_running:
        try:
            import termios, fcntl, sys, os
            fd = sys.stdin.fileno()
            
            # Save old terminal settings
            oldterm = termios.tcgetattr(fd)
            newattr = termios.tcgetattr(fd)
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
            
            oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
            
            try:
                while game_running:
                    try:
                        c = sys.stdin.read(1)
                        if c:
                            # Handle arrow keys (they send escape sequences)
                            if c == '\x1b':
                                c2 = sys.stdin.read(1)
                                if c2 == '[':
                                    c3 = sys.stdin.read(1)
                                    if c3 == 'A':  # Up arrow
                                        direction_queue.append((0, -1))
                                    elif c3 == 'B':  # Down arrow
                                        direction_queue.append((0, 1))
                                    elif c3 == 'C':  # Right arrow
                                        direction_queue.append((1, 0))
                                    elif c3 == 'D':  # Left arrow
                                        direction_queue.append((-1, 0))
                            elif c == 'w':  # Up
                                direction_queue.append((0, -1))
                            elif c == 's':  # Down
                                direction_queue.append((0, 1))
                            elif c == 'a':  # Left
                                direction_queue.append((-1, 0))
                            elif c == 'd':  # Right
                                direction_queue.append((1, 0))
                            elif c == 'p':  # Pause
                                game_paused = not game_paused
                            elif c == 'q':  # Quit
                                game_running = False
                            elif c == '1':  # Easy
                                return '1'
                            elif c == '2':  # Medium
                                return '2'
                            elif c == '3':  # Hard
                                return '3'
                            elif c == '4':  # Extreme
                                return '4'
                            elif c == 'w':  # Toggle wall collision
                                return 'w'
                            elif c == 'r':  # Restart
                                return 'r'
                    except IOError:
                        pass
                    time.sleep(0.05)
            finally:
                # Restore terminal settings
                termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
                fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        except:
            # Fallback for systems where termios is not available
            if sys.platform == 'win32':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'w':
                        direction_queue.append((0, -1))
                    elif key == b's':
                        direction_queue.append((0, 1))
                    elif key == b'a':
                        direction_queue.append((-1, 0))
                    elif key == b'd':
                        direction_queue.append((1, 0))
                    elif key == b'p':
                        game_paused = not game_paused
                    elif key == b'q':
                        game_running = False
                    elif key == b'1':
                        return '1'
                    elif key == b'2':
                        return '2'
                    elif key == b'3':
                        return '3'
                    elif key == b'4':
                        return '4'
                    elif key == b'w':
                        return 'w'
                    elif key == b'r':
                        return 'r'
            time.sleep(0.1)

def show_menu():
    """Display the game menu and return the selected difficulty."""
    clear_screen()
    high_scores = load_high_scores()
    options = list(DIFFICULTY_LEVELS.keys())
    selected = 0
    
    while True:
        clear_screen()
        print("\n" + "=" * 40)
        print("           SNAKE GAME")
        print("=" * 40)
        print("\nSelect Difficulty:")
        
        for i, option in enumerate(options):
            if i == selected:
                print(f" > [{option}] - High Score: {high_scores.get(option, 0)}")
            else:
                print(f"   {option}  - High Score: {high_scores.get(option, 0)}")
        
        print("\nControls:")
        print("  Arrow Keys or WASD: Move")
        print("  P: Pause/Resume")
        print("  W: Toggle Wall Collision")
        print("  1-4: Change Difficulty")
        print("  Q: Quit")
        
        print("\nUse Up/Down arrows to select, Enter to start")
        
        # Get key input
        key = get_key()
        
        if key == 'w' or key == '\x1b[A':  # Up arrow
            selected = (selected - 1) % len(options)
        elif key == 's' or key == '\x1b[B':  # Down arrow
            selected = (selected + 1) % len(options)
        elif key == '\n' or key == '\r':  # Enter
            return options[selected]
        elif key == 'q':
            return None

def create_board(snake, food, obstacles, power_up):
    """Create the game board with all elements."""
    # Create empty board
    board = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # Add obstacles
    for x, y in obstacles:
        board[y][x] = OBSTACLE
    
    # Add food
    x, y = food[0]
    food_type = food[1]
    if food_type == "normal":
        board[y][x] = FOOD
    elif food_type == "bonus":
        board[y][x] = BONUS_FOOD
    else:  # special
        board[y][x] = SPECIAL_FOOD
    
    # Add power-up
    if power_up[0]:
        x, y = power_up[1]
        board[y][x] = POWERUP
    
    # Add snake body
    for i, (x, y) in enumerate(snake):
        if i == 0:
            board[y][x] = SNAKE_HEAD
        else:
            board[y][x] = SNAKE_BODY
    
    return board

def print_board(board, score, high_score, difficulty, wall_collision, power_ups):
    """Print the game board and game information."""
    clear_screen()
    
    # Print top border
    print(BORDER * (WIDTH + 2))
    
    # Print board with side borders
    for row in board:
        print(BORDER + ''.join(row) + BORDER)
    
    # Print bottom border
    print(BORDER * (WIDTH + 2))
    
    # Print game information
    print(f"Score: {score}  High Score: {high_score}")
    print(f"Difficulty: {difficulty}  {'Wall Collision' if wall_collision else 'Screen Wrap'}")
    
    # Print active power-ups
    power_up_text = []
    if power_ups.get("speed_boost", 0) > 0:
        power_up_text.append("Speed Boost")
    if power_ups.get("invincible", 0) > 0:
        power_up_text.append("Invincible")
    if power_ups.get("double_score", 0) > 0:
        power_up_text.append("Double Score")
    
    if power_up_text:
        print("Active Power-ups: " + ", ".join(power_up_text))

def game_over_screen(score, high_score):
    """Display the game over screen."""
    clear_screen()
    print("\n" + "=" * 40)
    print("           GAME OVER")
    print("=" * 40)
    print(f"\nYour Score: {score}")
    print(f"High Score: {high_score}")
    print("\nPress R to Restart or Q to Quit")

def main():
    global direction_queue, current_direction, game_running, game_paused
    
    # Start input thread
    input_thread = threading.Thread(target=get_key)
    input_thread.daemon = True
    input_thread.start()
    
    while True:
        # Show menu and get difficulty
        difficulty = show_menu()
        if difficulty is None or not game_running:
            break
        
        # Game initialization
        snake = [(WIDTH // 2, HEIGHT // 2)]
        food = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)), "normal"]
        obstacles = []
        power_up = [False, (0, 0), None]  # [active, position, type]
        score = 0
        high_scores = load_high_scores()
        game_over = False
        game_paused = False
        wall_collision = difficulty in ["Hard", "Extreme"]
        speed = DIFFICULTY_LEVELS[difficulty]
        grow = False
        power_ups = {"speed_boost": 0, "invincible": 0, "double_score": 0}
        
        # Generate obstacles
        num_obstacles = random.randint(3, 8)
        for _ in range(num_obstacles):
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            # Make sure obstacles aren't too close to the snake start
            if abs(x - WIDTH // 2) > 3 or abs(y - HEIGHT // 2) > 3:
                obstacles.append((x, y))
        
        # Make sure food isn't on an obstacle or the snake
        while food[0] in obstacles or food[0] in snake:
            food[0] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        
        # Reset direction
        current_direction = (1, 0)
        direction_queue = []
        
        # Game loop
        last_update_time = time.time()
        food_spawn_time = time.time()
        food_lifespan = None
        
        while not game_over and game_running:
            # Process input from queue
            if direction_queue and not game_paused:
                new_dir = direction_queue.pop(0)
                # Prevent 180-degree turns
                if (new_dir[0] * -1, new_dir[1] * -1) != current_direction:
                    current_direction = new_dir
            
            current_time = time.time()
            
            # Update game state at appropriate intervals
            if not game_paused and current_time - last_update_time >= speed:
                last_update_time = current_time
                
                # Apply speed boost if active
                if power_ups["speed_boost"] > 0:
                    power_ups["speed_boost"] -= 1
                    effective_speed = speed / 2
                else:
                    effective_speed = speed
                
                # Update other power-ups
                if power_ups["invincible"] > 0:
                    power_ups["invincible"] -= 1
                
                if power_ups["double_score"] > 0:
                    power_ups["double_score"] -= 1
                
                # Move snake
                head_x, head_y = snake[0]
                dx, dy = current_direction
                new_x = head_x + dx
                new_y = head_y + dy
                
                # Handle wall collision based on game mode
                if wall_collision:
                    if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
                        game_over = True
                        continue
                else:
                    new_x = new_x % WIDTH
                    new_y = new_y % HEIGHT
                
                new_head = (new_x, new_y)
                
                # Check for collision with self
                if new_head in snake[1:] and power_ups["invincible"] <= 0:
                    game_over = True
                    continue
                
                # Check for collision with obstacles
                if new_head in obstacles and power_ups["invincible"] <= 0:
                    game_over = True
                    continue
                
                # Move snake
                snake.insert(0, new_head)
                if not grow:
                    snake.pop()
                else:
                    grow = False
                
                # Check if snake ate food
                if new_head == food[0]:
                    grow = True
                    
                    # Calculate points
                    points = 1
                    if food[1] == "bonus":
                        points = 3
                    elif food[1] == "special":
                        points = 2
                    
                    if power_ups["double_score"] > 0:
                        points *= 2
                    
                    score += points
                    
                    # Generate new food
                    food[0] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                    while food[0] in obstacles or food[0] in snake or (power_up[0] and food[0] == power_up[1]):
                        food[0] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                    
                    # Randomly determine food type
                    food_type = random.random()
                    if food_type < 0.7:  # 70% chance for normal food
                        food[1] = "normal"
                        food_lifespan = None
                    elif food_type < 0.9:  # 20% chance for bonus food
                        food[1] = "bonus"
                        food_lifespan = 5  # 5 seconds
                    else:  # 10% chance for special food
                        food[1] = "special"
                        food_lifespan = 7  # 7 seconds
                    
                    food_spawn_time = current_time
                
                # Check if temporary food should disappear
                if food_lifespan and current_time - food_spawn_time > food_lifespan:
                    food[0] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                    while food[0] in obstacles or food[0] in snake or (power_up[0] and food[0] == power_up[1]):
                        food[0] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                    food[1] = "normal"
                    food_lifespan = None
                    food_spawn_time = current_time
                
                # Handle power-up spawning
                if not power_up[0] and random.random() < 0.02:  # 2% chance per update
                    power_up[0] = True
                    power_up[1] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                    while power_up[1] in obstacles or power_up[1] in snake or power_up[1] == food[0]:
                        power_up[1] = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                    power_up[2] = random.choice(["speed", "invincible", "double_score"])
                    power_up_spawn_time = current_time
                
                # Check if power-up should disappear
                if power_up[0] and current_time - power_up_spawn_time > 10:  # 10 seconds lifespan
                    power_up[0] = False
                
                # Check if snake collected power-up
                if power_up[0] and new_head == power_up[1]:
                    if power_up[2] == "speed":
                        power_ups["speed_boost"] = 20  # Duration in updates
                    elif power_up[2] == "invincible":
                        power_ups["invincible"] = 20
                    elif power_up[2] == "double_score":
                        power_ups["double_score"] = 20
                    power_up[0] = False
            
            # Create and print the board
            board = create_board(snake, food, obstacles, power_up)
            print_board(board, score, high_scores.get(difficulty, 0), difficulty, wall_collision, power_ups)
            
            # Show pause message if paused
            if game_paused:
                print("\nGAME PAUSED - Press P to continue")
            
            # Sleep to control game speed
            time.sleep(0.05)
        
        # Update high score if needed
        if score > high_scores.get(difficulty, 0):
            high_scores[difficulty] = score
            save_high_scores(high_scores)
        
        # Game over screen
        game_over_screen(score, high_scores.get(difficulty, 0))
        
        # Wait for restart or quit
        restart = False
        while not restart and game_running:
            key = get_key()
            if key == 'r':
                restart = True
            elif key == 'q':
                game_running = False
            time.sleep(0.1)
        
        if not game_running:
            break

if __name__ == "__main__":
    # Set up signal handler for clean exit
    def signal_handler(sig, frame):
        global game_running
        game_running = False
        print("\nExiting...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        clear_screen()
        print("Thanks for playing Snake!")
