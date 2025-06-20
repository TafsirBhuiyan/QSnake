import pygame
import sys
import random
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Difficulty settings
DIFFICULTY_LEVELS = {
    "Easy": {"speed": 8, "color": GREEN},
    "Medium": {"speed": 12, "color": BLUE},
    "Hard": {"speed": 16, "color": RED},
    "Extreme": {"speed": 20, "color": YELLOW}
}

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Font for text display
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Start moving right
        self.grow = False
        self.color = GREEN  # Default color
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        # Check for collision with self
        if new_position in self.positions[1:]:
            return True  # Game over
        
        self.positions.insert(0, new_position)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        
        return False  # Game continues
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def grow_snake(self):
        self.grow = True
    
    def draw(self):
        for position in self.positions:
            rect = pygame.Rect(position[0] * GRID_SIZE, position[1] * GRID_SIZE, 
                              GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)  # Border

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, 
                          GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect)
        pygame.draw.rect(screen, WHITE, rect, 1)  # Border

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.difficulty = "Easy"
        self.speed = DIFFICULTY_LEVELS[self.difficulty]["speed"]
        self.snake.color = DIFFICULTY_LEVELS[self.difficulty]["color"]
    
    def update(self):
        if not self.game_over:
            self.game_over = self.snake.update()
            
            # Check if snake ate food
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow_snake()
                self.food.randomize_position()
                # Make sure food doesn't appear on snake
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()
                self.score += 1
    
    def draw(self):
        screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))
        
        # Draw game elements
        self.snake.draw()
        self.food.draw()
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw difficulty
        diff_text = font.render(f"Difficulty: {self.difficulty}", True, DIFFICULTY_LEVELS[self.difficulty]["color"])
        screen.blit(diff_text, (WIDTH - diff_text.get_width() - 10, 10))
        
        # Draw game over message
        if self.game_over:
            game_over_text = large_font.render("GAME OVER", True, RED)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    
    def change_difficulty(self, difficulty):
        if difficulty in DIFFICULTY_LEVELS:
            self.difficulty = difficulty
            self.speed = DIFFICULTY_LEVELS[difficulty]["speed"]
            self.snake.color = DIFFICULTY_LEVELS[difficulty]["color"]

def show_difficulty_menu():
    menu_active = True
    selected = 0
    options = list(DIFFICULTY_LEVELS.keys())
    
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
        
        title_text = large_font.render("Select Difficulty", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        for i, option in enumerate(options):
            color = DIFFICULTY_LEVELS[option]["color"] if i == selected else WHITE
            option_text = font.render(option, True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, 200 + i * 50))
        
        pygame.display.flip()
        clock.tick(10)
    
    return options[selected]

def main():
    # Show difficulty menu
    selected_difficulty = show_difficulty_menu()
    
    # Initialize game
    game = Game()
    game.change_difficulty(selected_difficulty)
    
    # Main game loop
    while True:
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
                    # Change difficulty during gameplay
                    elif event.key == pygame.K_1:
                        game.change_difficulty("Easy")
                    elif event.key == pygame.K_2:
                        game.change_difficulty("Medium")
                    elif event.key == pygame.K_3:
                        game.change_difficulty("Hard")
                    elif event.key == pygame.K_4:
                        game.change_difficulty("Extreme")
                else:
                    if event.key == pygame.K_r:
                        # Restart game
                        game = Game()
                        game.change_difficulty(selected_difficulty)
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(game.speed)

if __name__ == "__main__":
    main()
