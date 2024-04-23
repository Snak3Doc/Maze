#maze.py
#? Homework Tasks
#? - L1 use layout_template (excalidraw is  great tool for this) to design map/walls, 
#?      place enemies and show the enemies direction of movement
#? - L2 Create Wall and Enemy Objects
#? - Complete any other unfinsihed sections of code from 
#?      the lesson, check the homework_template that is formated for discord markdown

#pyinstaller --onefile --noconsole --icon=<ico_path> file_name.py

### Imports ###
import pygame
pygame.init()
from pathlib import Path
import sys
import time 
from random import choice

### Constants ###
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

SPRITE_WIDTH = 40
SPRITE_HEIGHT = 40

FPS = 60

WORK_DIR = Path.cwd()

BG_IMG_PATH_1 = WORK_DIR/"assets"/"tiles"/"Sand"/"tile_0064.png"
BG_IMG_PATH_2 = WORK_DIR/"assets"/"tiles"/"Sand"/"tile_0037.png" 
BG_IMG_PATH_3 = WORK_DIR/"assets"/"tiles"/"Sand"/"tile_0070.png" 

WALL_IMG_PATH = WORK_DIR/"assets"/"tiles"/"stone"/"tile_0003.png" 

PLAYER_IMG_PATH = WORK_DIR/"assets"/"sprites"/"hero.png"
ENEMY_IMG_PATH = WORK_DIR/"assets"/"sprites"/"cyborg.png"

DIAMOND_IMG_PATH = WORK_DIR/"assets"/"sprites"/"diamond.png"

BG_AUDIO_PATH = WORK_DIR/"assets"/"audio_files"/"jungles.ogg" 
KICK_AUDIO_PATH = WORK_DIR/"assets"/"audio_files"/"kick.ogg" 
MONEY_AUDIO_PATH = WORK_DIR/"assets"/"audio_files"/"money.ogg"

BG_IMG_1 = pygame.transform.scale(pygame.image.load(BG_IMG_PATH_1), (SPRITE_WIDTH, SPRITE_HEIGHT)) 
BG_IMG_2 = pygame.transform.scale(pygame.image.load(BG_IMG_PATH_2), (SPRITE_WIDTH, SPRITE_HEIGHT)) 
BG_IMG_3 = pygame.transform.scale(pygame.image.load(BG_IMG_PATH_3), (SPRITE_WIDTH, SPRITE_HEIGHT)) 

WALL_IMG = pygame.transform.scale(pygame.image.load(WALL_IMG_PATH), (SPRITE_WIDTH, SPRITE_HEIGHT)) 

### Variables ###
game_over = False

### Lists ###
X_DIRECTIONS = ["left", "right"]
Y_DIRECTIONS = ["up", "down"]
BG_IMG_TILES = [BG_IMG_1, BG_IMG_2, BG_IMG_3] 

### Window Setup ###
main_win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze")
clock = pygame.time.Clock()

### Classes ###
class SpriteBase(pygame.sprite.Sprite): 
    def __init__(self, img_path, x_pos, y_pos, scale_width, scale_height, step, show_outline): #* Add extra parameters as needed
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(img_path), (scale_width, scale_height))

        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

        self.lives = 3

        self.step = step

        self.width = scale_width
        self.height = scale_height

        self.x_start = x_pos 
        self.y_start = y_pos 

        #* For visualising hitboxes, set show_outline param to False when creating sprites to disable
        if show_outline:
            outline_surface = pygame.Surface(self.image.get_size())
            outline_surface.set_colorkey((0, 0, 0))
            pygame.draw.rect(outline_surface, (255, 16, 240), outline_surface.get_rect(), width=1)
            self.image.blit(outline_surface, (0, 0))

class PlayerSprite(SpriteBase):
    def update(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_w]:
            self.rect.y -= self.step
            if pygame.sprite.spritecollide(self, wall_tile_group, False): 
                self.rect.y += self.step

        if pressed[pygame.K_s]:
            self.rect.y += self.step
            if pygame.sprite.spritecollide(self, wall_tile_group, False): 
                self.rect.y -= self.step

        if pressed[pygame.K_a]:
            self.rect.x -= self.step
            if pygame.sprite.spritecollide(self, wall_tile_group, False): 
                self.rect.x += self.step

        if pressed[pygame.K_d]:
            self.rect.x += self.step
            if pygame.sprite.spritecollide(self, wall_tile_group, False): 
                self.rect.x -= self.step

    def hit_reg(self): 
        if pygame.sprite.spritecollide(self, enemy_sprite_group, False):
            kick_sfx.play()
            self.lives -= 1
            self.rect.x = self.x_start
            self.rect.y = self.y_start
    
    def check_lives(self):
        if self.lives <= 0:
            rect = pygame.Rect(245, 350, 210, 50)
            pygame.draw.rect(main_win, (34, 41, 48), rect)
            font = pygame.font.Font(None, 50)
            text = font.render("Game Over!", True, (161, 26, 11))
            main_win.blit(text, (250, 360))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            sys.exit()
        else:
            rect = pygame.Rect(15, 10, 75, 20)
            pygame.draw.rect(main_win, (34, 41, 48), rect)
            font = pygame.font.Font(None, 25)
            text = font.render(f"Lives: {str(self.lives)}", True, (230, 224, 224))
            main_win.blit(text, (20, 12))
    
    def check_win(self):
        if pygame.sprite.collide_rect(self, diamond):
            money_sfx.play()
            rect = pygame.Rect(245, 350, 210, 50)
            pygame.draw.rect(main_win, (34, 41, 48), rect)
            font = pygame.font.Font(None, 50)
            text = font.render("Victory!", True, (60, 179, 113))
            main_win.blit(text, (285, 360))
            pygame.display.update()
            time.sleep(1)
            pygame.quit()
            sys.exit()

class EnemySprite(SpriteBase):
    def __init__(self, img_path, x_pos, y_pos, scale_width, scale_height, move_x, move_y, step=None, show_outline=False):  
        super().__init__(img_path, x_pos, y_pos, scale_width, scale_height, step, show_outline)
        self.move_x = move_x
        self.move_y = move_y
        self.direction = None

    def update(self):
        #* Move on the x axis
        if self.move_x:
            if self.direction is None:
                self.direction = choice(X_DIRECTIONS)
            
            if self.direction == "left":
                self.rect.x -= self.step
                if pygame.sprite.spritecollide(self, wall_tile_group, False):
                    self.rect.x += self.step
                    self.direction = "right"

            elif self.direction == "right":
                self.rect.x += self.step
                if pygame.sprite.spritecollide(self, wall_tile_group, False):
                    self.rect.x -= self.step
                    self.direction = "left"

        #* Move on the y axis
        elif self.move_y:
            if self.direction is None:
                self.direction = choice(Y_DIRECTIONS)

            if self.direction == "up":
                self.rect.y -= self.step
                if pygame.sprite.spritecollide(self, wall_tile_group, False):
                    self.rect.y += self.step
                    self.direction = "down"

            elif self.direction == "down":
                self.rect.y += self.step
                if pygame.sprite.spritecollide(self, wall_tile_group, False):
                    self.rect.y -= self.step
                    self.direction = "up"

### Functions ###
def check_exit():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

def get_mouse_pos(): # Prints the x,y of a click on the main window
    pressed = pygame.mouse.get_pressed()
    if pressed[0] is True:
        x, y = pygame.mouse.get_pos()
        print(f"Mouse X: {x}\nMouse Y: {y}")

def create_bg_tiles():
    #* Create a grid of tile sprites
    num_cols = SCREEN_WIDTH // SPRITE_WIDTH + 1
    num_rows = SCREEN_HEIGHT // SPRITE_HEIGHT + 1

    for row in range(num_rows):
        for col in range(num_cols):
            bg_tile = pygame.sprite.Sprite()
            bg_tile.image = choice(BG_IMG_TILES)
            bg_tile.rect = bg_tile.image.get_rect()
            bg_tile.rect.x = col * SPRITE_WIDTH
            bg_tile.rect.y = row * SPRITE_HEIGHT
            bg_tile_group.add(bg_tile)

def create_wall_tiles(axis, num_tiles, start_x, start_y):
    x_pos = start_x
    y_pos = start_y
    if axis == "x":
        for i in range(num_tiles):
            wall_tile = pygame.sprite.Sprite()
            wall_tile.image = WALL_IMG
            wall_tile.rect = wall_tile.image.get_rect()
            wall_tile.rect.x = x_pos
            wall_tile.rect.y = y_pos
            wall_tile_group.add(wall_tile)
            x_pos += SPRITE_WIDTH
    elif axis == "y":
        for i in range(num_tiles):
            wall_tile = pygame.sprite.Sprite()
            wall_tile.image = WALL_IMG
            wall_tile.rect = wall_tile.image.get_rect()
            wall_tile.rect.x = x_pos
            wall_tile.rect.y = y_pos
            wall_tile_group.add(wall_tile)
            y_pos += SPRITE_HEIGHT

### Objects & Groups ###
##Create Groups
all_sprite_group = pygame.sprite.Group() 
enemy_sprite_group = pygame.sprite.Group() 
wall_tile_group = pygame.sprite.Group() 
bg_tile_group = pygame.sprite.Group()

##Create Objects
player = PlayerSprite(PLAYER_IMG_PATH, 50, 600, SPRITE_WIDTH, SPRITE_HEIGHT, 5, False)

enemy_sprite_1 = EnemySprite(ENEMY_IMG_PATH, 180, 480, SPRITE_WIDTH, SPRITE_HEIGHT, False, True, 3, False)
enemy_sprite_2 = EnemySprite(ENEMY_IMG_PATH, 60, 200, SPRITE_WIDTH, SPRITE_HEIGHT, False, True, 3, False) 
enemy_sprite_3 = EnemySprite(ENEMY_IMG_PATH, 440, 280, SPRITE_WIDTH, SPRITE_HEIGHT, False, True, 3, False) 
enemy_sprite_4 = EnemySprite(ENEMY_IMG_PATH, 640, 480, SPRITE_WIDTH, SPRITE_HEIGHT, False, True, 3, False) 
enemy_sprite_5 = EnemySprite(ENEMY_IMG_PATH, 320, 60, SPRITE_WIDTH, SPRITE_HEIGHT, True, False, 3, False) 
enemy_sprite_6 = EnemySprite(ENEMY_IMG_PATH, 400, 320, SPRITE_WIDTH, SPRITE_HEIGHT, True, False, 3, False)
enemy_sprite_7 = EnemySprite(ENEMY_IMG_PATH, 440, 480, SPRITE_WIDTH, SPRITE_HEIGHT, True, False, 3, False)

create_bg_tiles()

#Exterior Walls 
create_wall_tiles("x", 18, 0, 0)
create_wall_tiles("y", 16, 680, 40)
create_wall_tiles("x", 18, 0, 680)
create_wall_tiles("y", 16, 0, 40) 

#Internal Walls
create_wall_tiles("y", 4, 120, 520)
create_wall_tiles("y", 14, 240, 120) 
create_wall_tiles("y", 4, 360, 120) 
create_wall_tiles("y", 11, 520, 40)
create_wall_tiles("y", 3, 120, 40)
create_wall_tiles("x", 3, 40, 400)
create_wall_tiles("x", 3, 120, 280)
create_wall_tiles("x", 3, 400, 120)
create_wall_tiles("x", 3, 280, 400)
create_wall_tiles("x", 6, 360, 520)
create_wall_tiles("x", 2, 600, 120)
create_wall_tiles("x", 2, 560, 240)
create_wall_tiles("x", 2, 600, 360)
create_wall_tiles("x", 2, 560, 440)
create_wall_tiles("x", 1, 280, 600)
create_wall_tiles("x", 1, 360, 600)
create_wall_tiles("x", 1, 400, 560)
create_wall_tiles("x", 1, 440, 640)
create_wall_tiles("x", 1, 480, 600)
create_wall_tiles("x", 1, 560, 560)
create_wall_tiles("x", 1, 560, 640)

diamond = SpriteBase(DIAMOND_IMG_PATH, 618, 64, SPRITE_WIDTH, SPRITE_HEIGHT, None, False)

## Add sprites to groups
all_sprite_group.add(player) 
all_sprite_group.add(enemy_sprite_1) 
all_sprite_group.add(enemy_sprite_2) 
all_sprite_group.add(enemy_sprite_3) 
all_sprite_group.add(enemy_sprite_4) 
all_sprite_group.add(enemy_sprite_5) 
all_sprite_group.add(enemy_sprite_6) 
all_sprite_group.add(enemy_sprite_7) 
all_sprite_group.add(diamond)

enemy_sprite_group.add(enemy_sprite_1) 
enemy_sprite_group.add(enemy_sprite_2) 
enemy_sprite_group.add(enemy_sprite_3) 
enemy_sprite_group.add(enemy_sprite_4) 
enemy_sprite_group.add(enemy_sprite_5) 
enemy_sprite_group.add(enemy_sprite_6) 
enemy_sprite_group.add(enemy_sprite_7)

### Audio ###
pygame.mixer.music.load(BG_AUDIO_PATH) #* Add to playlist
kick_sfx = pygame.mixer.Sound(KICK_AUDIO_PATH) #* Create SFX object
money_sfx = pygame.mixer.Sound(MONEY_AUDIO_PATH) #* Create SFX object


### Game Loop ###
pygame.mixer.music.play() #* Play BG Music
while not game_over:
    bg_tile_group.draw(main_win)
    wall_tile_group.draw(main_win)

    all_sprite_group.update()
    all_sprite_group.draw(main_win)

    player.hit_reg()
    player.check_lives()
    player.check_win()

    get_mouse_pos()

    check_exit()
    pygame.display.update()
    clock.tick(FPS)