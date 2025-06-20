import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Pong")
clock = pygame.time.Clock()

# Font for score display
font = pygame.font.Font(None, 74)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 7
        self.score = 0
    
    def move(self, up=True):
        if up:
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        
        # Keep paddle on screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, 
                               HEIGHT // 2 - BALL_SIZE // 2, 
                               BALL_SIZE, BALL_SIZE)
        self.dx = random.choice([-5, 5])
        self.dy = random.choice([-5, 5])
    
    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Bounce off top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
    
    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.dx = random.choice([-5, 5])
        self.dy = random.choice([-5, 5])
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Create game objects
player_paddle = Paddle(50, HEIGHT // 2 - PADDLE_HEIGHT // 2)
opponent_paddle = Paddle(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
ball = Ball()

def draw_score():
    player_text = font.render(str(player_paddle.score), True, WHITE)
    opponent_text = font.render(str(opponent_paddle.score), True, WHITE)
    
    screen.blit(player_text, (WIDTH // 4, 20))
    screen.blit(opponent_text, (3 * WIDTH // 4, 20))

def draw_middle_line():
    for y in range(0, HEIGHT, 30):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 5, y, 5, 15))

def check_collision():
    # Check collision with paddles
    if ball.rect.colliderect(player_paddle.rect) and ball.dx < 0:
        ball.dx *= -1
        # Adjust angle based on where the ball hits the paddle
        middle_y = player_paddle.rect.y + PADDLE_HEIGHT // 2
        difference_in_y = middle_y - ball.rect.y
        reduction_factor = (PADDLE_HEIGHT // 2) / 5
        ball.dy = -difference_in_y / reduction_factor
    
    if ball.rect.colliderect(opponent_paddle.rect) and ball.dx > 0:
        ball.dx *= -1
        # Adjust angle based on where the ball hits the paddle
        middle_y = opponent_paddle.rect.y + PADDLE_HEIGHT // 2
        difference_in_y = middle_y - ball.rect.y
        reduction_factor = (PADDLE_HEIGHT // 2) / 5
        ball.dy = -difference_in_y / reduction_factor

def check_score():
    if ball.rect.left <= 0:
        opponent_paddle.score += 1
        ball.reset()
    
    if ball.rect.right >= WIDTH:
        player_paddle.score += 1
        ball.reset()

def opponent_ai():
    # Simple AI for opponent
    if opponent_paddle.rect.centery < ball.rect.centery and ball.dx > 0:
        opponent_paddle.move(False)  # Move down
    elif opponent_paddle.rect.centery > ball.rect.centery and ball.dx > 0:
        opponent_paddle.move(True)   # Move up

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Player controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_paddle.move(True)
    if keys[pygame.K_s]:
        player_paddle.move(False)
    
    # Update game objects
    ball.move()
    opponent_ai()
    check_collision()
    check_score()
    
    # Draw everything
    screen.fill(BLACK)
    draw_middle_line()
    player_paddle.draw()
    opponent_paddle.draw()
    ball.draw()
    draw_score()
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)
