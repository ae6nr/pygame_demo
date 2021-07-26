import pygame
import random
from pygame.locals import(
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_r,
    K_q,
    KEYDOWN,
    QUIT
)

# pygame.mixer.init() # for sounds
pygame.init()

scorefont = pygame.font.SysFont("monospace", 16)
endfont = pygame.font.SysFont("monospace", 40)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

class Player(pygame.sprite.Sprite):
    
    def __init__(self):
        super(Player, self).__init__()
        # self.surf = pygame.Surface((75,25))
        # self.surf.fill((255,255,255))
        self.surf = pygame.image.load("jet.png").convert()
        self.surf.set_colorkey((255,255,255), RLEACCEL)
        self.rect = self.surf.get_rect()
    
        self.vvel = 0

    def gravity(self):
        self.vvel += 1
        self.rect.move_ip(0,self.vvel)

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.vvel -= 3
            # self.rect.move_ip(0,-5)
        if pressed_keys[K_DOWN]:
            self.vvel += 2
            # self.rect.move_ip(0,5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5,0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5,0)
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vvel = -self.vvel//2
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vvel = -5-self.vvel//2

class Enemy(pygame.sprite.Sprite):
    def __init__(self, score):
        self.score = score
        super(Enemy, self).__init__()
        # self.surf = pygame.Surface((20,20))
        # self.surf.fill((255,255,255))
        self.surf = pygame.image.load("missile.png").convert()
        self.surf.set_colorkey((255,255,255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5,20)

    def update(self):
        self.rect.move_ip(-self.speed,0)
        if self.rect.right < 0:
            self.kill()
            self.score.avoidedMissile(self)
        # if random.random() < 0.01:
        #     self.kill()

class Target(pygame.sprite.Sprite):
    def __init__(self, score):
        self.score = score
        super(Target, self).__init__()
        self.surf = pygame.image.load("target.png").convert()
        self.surf.set_colorkey((255,255,255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center = (
                random.randint(0, SCREEN_WIDTH - 200),
                random.randint(0, SCREEN_HEIGHT)
            )
        )
        self.speed = random.randint(1,3)

    def update(self):
        self.rect.move_ip(self.speed,0)
        if self.rect.left > SCREEN_WIDTH:
            self.kill()
            self.score.missedTarget(self)

    def kill(self):
        super(Target, self).kill()
        self.score.foundTarget(self)

class Score:
    
    def __init__(self):
        self.score = 0

    def foundTarget(self, target):
        x_score = (target.rect.center[0]) // 2
        y_score = (SCREEN_HEIGHT - target.rect.center[1]) // 2
        inc = 200 + x_score + y_score
        self.score += inc

    def missedTarget(self, target):
        x_score = (target.rect.center[0]) // 2
        y_score = (SCREEN_HEIGHT - target.rect.center[1]) // 2
        inc = 200 + x_score + y_score
        self.score -= inc
        self.score -= 50

    def avoidedMissile(self, target):
        self.score += 10

# Start the game
running = True
while running:

    round = True # indicates a round is actively being played
    waiting = True # indicates the wait screen should be displayed, if applicable

    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 1000)

    ADDTARGET = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDTARGET, 700)

    player = Player()
    score = Score()
    
    enemies = pygame.sprite.Group()
    targets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    clock = pygame.time.Clock()

    while round:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    round = False
                    waiting = False
                    running = False
                if event.key == K_r:
                    round = False
                    waiting = False
                if event.key == K_q:
                    round = False
                    waiting = True
            elif event.type == QUIT:
                round = False
                waiting = False
                running = False
            elif event.type == ADDENEMY:
                new_enemy = Enemy(score)
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)
            elif event.type == ADDTARGET:
                new_target = Target(score)
                targets.add(new_target)
                all_sprites.add(new_target)
        
        player.gravity()

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        enemies.update()
        targets.update()

        screen.fill((255,255,255))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            round = False

        if pygame.sprite.spritecollideany(player, targets):
            pygame.sprite.spritecollide(player, targets, True)

        scoretext = scorefont.render(f"{score.score}", 1, (0,0,0))
        screen.blit(scoretext, (SCREEN_WIDTH - 10 - scoretext.get_width(), 10))
        pygame.display.flip()
        clock.tick(30)

    screen.fill((0,0,0))
    scoretext = endfont.render(f"Final score: {score.score}", 1, (255,255,255))
    screen.blit(
        scoretext,
        (
            SCREEN_WIDTH//2 - scoretext.get_width()//2,
            SCREEN_HEIGHT//2 - scoretext.get_height()//2
        )
    )
    pygame.display.flip()

    while waiting:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    waiting = False
                    running = False
                if event.key == K_r:
                    waiting = False
                if event.key == K_q:
                    waiting = False
                    running = False
            elif event.type == QUIT:
                waiting = False
                running = False   