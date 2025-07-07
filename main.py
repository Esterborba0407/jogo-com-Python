import pygame
import random
import sys
import os

pygame.init()

# aqui o comanda da  Tela
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Passarinho nas Nuvens")

# utilizei as Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 250)

# Clock e FPS
clock = pygame.time.Clock()
FPS = 60

#  criei o Caminho assets
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

def load_image(name, scale=None):
    path = os.path.join(ASSETS_PATH, name)
    image = pygame.image.load(path).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image

def load_sound(name):
    path = os.path.join(ASSETS_PATH, name)
    return pygame.mixer.Sound(path)

#  as iamgens Imagens
bird_img = load_image("passarinho.png", scale=(50, 50))
raio_img = load_image("raio.png", scale=(30, 70))
sol_img = load_image("sol.png", scale=(80, 80))
nuvem_img = load_image("nuvem.png", scale=(100, 60))

#  os Sons que utilizei 
sound_flap = load_sound("som_bater_asa.wav")
sound_gameover = load_sound("som_gameover.wav")

# as Classes que utilizei no jogo
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bird_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.speed_x = 7
        self.speed_y = 0
        self.gravity = 0.3
        self.jump_strength = -7
        self.is_jumping = False

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed_x
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed_x

        # Pulo para subir
        if keys[pygame.K_UP] and not self.is_jumping:
            self.speed_y = self.jump_strength
            self.is_jumping = True
            sound_flap.play()

        # Gravidade
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # Limite inferior
        if self.rect.bottom > HEIGHT - 30:
            self.rect.bottom = HEIGHT - 30
            self.is_jumping = False
            self.speed_y = 0

        # Limite superior (não deixar sair da tela)
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0

class Raio(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = raio_img
        self.rect = self.image.get_rect(midtop=(random.randint(20, WIDTH - 20), -70))
        self.speed = random.randint(5, 8)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Sol(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = sol_img
        self.rect = self.image.get_rect(midtop=(random.randint(80, WIDTH - 80), -80))
        self.speed_x = random.choice([-4, 4])
        self.speed_y = 2

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Rebater nas bordas horizontais
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x *= -1

        # Reiniciar se sair da tela embaixo
        if self.rect.top > HEIGHT:
            self.rect.midtop = (random.randint(80, WIDTH - 80), -80)

class Nuvem(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = nuvem_img
        self.rect = self.image.get_rect(midtop=(random.randint(0, WIDTH), random.randint(-200, -50)))
        self.speed = random.uniform(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.midtop = (random.randint(0, WIDTH), random.randint(-200, -50))

# Grupos
bird = Bird()
bird_group = pygame.sprite.Group(bird)
raio_group = pygame.sprite.Group()
sol_group = pygame.sprite.Group()
nuvem_group = pygame.sprite.Group()

for _ in range(5):
    nuvem_group.add(Nuvem())

# Eventos para spawnar raios e sol
RAIO_EVENT = pygame.USEREVENT + 1
SOL_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(RAIO_EVENT, 1500)
pygame.time.set_timer(SOL_EVENT, 5000)

# Pontuação (altura)
score = 0
font = pygame.font.SysFont(None, 36)

def draw_text(text, size, color, x, y):
    font_obj = pygame.font.SysFont(None, size)
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(topleft=(x, y))
    screen.blit(surface, rect)

def show_game_over():
    screen.fill(BLACK)
    draw_text("GAME OVER", 64, (255, 0, 0), WIDTH // 4, HEIGHT // 3)
    draw_text(f"Altura alcançada: {int(score)}", 36, WHITE, WIDTH // 4, HEIGHT // 3 + 70)
    draw_text("Pressione R para reiniciar", 28, WHITE, WIDTH // 4, HEIGHT // 3 + 120)
    pygame.display.flip()

# Loop principal
running = True
game_over = False

while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over:
            if event.type == RAIO_EVENT:
                raio_group.add(Raio())
            if event.type == SOL_EVENT:
                sol_group.add(Sol())

        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Resetar o jogo
                    raio_group.empty()
                    sol_group.empty()
                    bird.rect.center = (WIDTH // 2, HEIGHT - 100)
                    score = 0
                    game_over = False

    keys = pygame.key.get_pressed()

    if not game_over:
        bird.update(keys)
        raio_group.update()
        sol_group.update()
        nuvem_group.update()

        # Colisões
        if pygame.sprite.spritecollideany(bird, raio_group) or pygame.sprite.spritecollideany(bird, sol_group):
            sound_gameover.play()
            game_over = True

        # Pontuação baseada na altura (quanto mais perto do topo, maior)
        score += 0.1

    # Desenhar tudo
    nuvem_group.draw(screen)
    sol_group.draw(screen)
    raio_group.draw(screen)
    bird_group.draw(screen)

    draw_text(f"Altura: {int(score)}", 10, 10, 10, 10)

    if game_over:
        show_game_over()

    pygame.display.flip()

pygame.quit()
sys.exit()
