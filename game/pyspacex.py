#!/usr/bin/env python3
import sys
import os
import random
import pygame as pg
from webcolors import name_to_rgb as rgb

FPS = 60
FILE_PATH = os.path.dirname('__file__')
IMG_PATH = os.path.join(FILE_PATH, 'img')
SND_PATH = os.path.join(FILE_PATH, 'snd')
FONT_NAME = pg.font.match_font('arial')


class BaseCommand(object):
    def __init__(self, obj):
        self._obj = obj

    def execute(self):
        print("execute from BASE")


class JumpCommand(BaseCommand):
    def execute(self):
        print("execute from Jump")
        self._obj.jump()


class HideCommand(BaseCommand):
    def execute(self):
        print("execute Hide")
        self._obj.hide()


class Mario(object):
    def jump(self):
        print("Mario jump")

    def hide(self):
        print("Mario hide")


class Luigi(object):
    def jump(self):
        print("Luigi jump")

    def hide(self):
        print("Luigi hide")


class Invoke(object):
    'Invoker class which starts a command'

    def execute(self, command):
        print("in invoker")
        command.execute()


class Client(object):
    def __init__(self):
        self._character = Mario()
        self._invoker = Invoke()

    @property
    def invoker(self):
        return self._invoker

    def press(self, cmd):
        if cmd == "jump":
            self._invoker.execute(JumpCommand(self._character))
        elif cmd == "hide":
            self.invoker.execute(HideCommand(self._character))


def draw_text(surface, text, size, pos):
    font = pg.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, rgb('white'))
    text_rect = text_surface.get_rect()
    x, y = pos
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_shield_bar(surface, x, y, shield_value):
    if shield_value <= 0:
        shield_value = 0

    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    PADDING = 2
    fill_length = (shield_value * BAR_LENGTH) / 100
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    inline_rect = pg.Rect(
        x + PADDING,
        y + PADDING,
        fill_length - PADDING,
        BAR_HEIGHT - 3
    )
    pg.draw.rect(surface, rgb('white'), outline_rect, PADDING)
    pg.draw.rect(surface, rgb('green'), inline_rect)


def draw_lives(surface, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x - 30 * i
        img_rect.y = y
        surface.blit(img, img_rect)


def respawn_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


class Mob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_original = meteor_img
        self.image_original.set_colorkey(rgb('black'))
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pg.draw.circle(self.image, rgb('red'), self.rect.center, self.radius)
        self.rect.x = random.randrange(800 - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pg.time.get_ticks()

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot += self.rot_speed % 360
            new_image = pg.transform.rotate(self.image_original, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > 600 + 10 or self.rect.left < -25 or \
                self.rect.right > 800 + 20:
            self.rect.x = random.randrange(800 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):

        pg.sprite.Sprite.__init__(self)
        self.image = laser_img
        self.image.set_colorkey(rgb('black'))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(homer_img, (50, 38))
        self.image.set_colorkey(rgb('black'))
        self.rect = self.image.get_rect()
        self.radius = 20
        # pg.draw.circle(self.image, rgb('red'), self.rect.center, self.radius)
        self.rect.bottom = 600
        self.rect.centerx = 400
        self.speedx = 1.2
        self.shield = 100
        self.shot_delay = 250
        self.last_shot_time = pg.time.get_ticks()
        self.hidden = False
        self.hide_timer = pg.time.get_ticks()
        self.lives = 3

    def update(self):
        if self.hidden:
            # replace the player at the center of screen if it was
            # hidden after an explosion
            if pg.time.get_ticks() - self.hide_timer > 3000:
                self.hidden = False
                self.rect.bottom = 600
                self.rect.centerx = 400

        keys = pg.key.get_pressed()

        if keys[pg.K_RIGHT]:
            self.rect.x += 5 * self.speedx
        if keys[pg.K_LEFT]:
            self.rect.x -= 5 * self.speedx
        if keys[pg.K_SPACE]:
            self.shoot()

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 800:
            self.rect.right = 800

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot_time > self.shot_delay:
            self.last_shot_time = now
            laser_snd.play()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def hide(self):
        ''' temporarily hide the player '''
        self.hidden = True
        self.hide_timer = pg.time.get_ticks()
        # move the player off screen so it can't be seen for a while
        self.rect.center = (0, 5000)


class Explosion(pg.sprite.Sprite):
    def __init__(self, center, size='small'):
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosions_anim[size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.rate = 60

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosions_anim[self.size]):
                self.kill()
            else:
                # keep center at the same place so we save the
                # center before loading the new image
                center = self.rect.center
                self.image = explosions_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# Initialize game
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((800, 600))
pg.display.set_caption('this is the title')
clock = pg.time.Clock()
client = Client()
cmd = None

# Load all game graphics
background = pg.image.load(
    os.path.join(IMG_PATH, 'space_background.png')
).convert()
background_rect = background.get_rect()

homer_img = pg.image.load(
    os.path.join(IMG_PATH, 'playerShip1_blue.png')
).convert()

homer_mini_img = pg.transform.scale(homer_img, (25, 19))
homer_mini_img.set_colorkey(rgb('black'))

meteor_img = pg.image.load(
    os.path.join(IMG_PATH, 'meteorBrown_med1.png')
).convert()

laser_img = pg.image.load(
    os.path.join(IMG_PATH, 'laserRed16.png')
).convert()

explosions_anim = {}
explosions_anim['large'] = []
explosions_anim['small'] = []
explosions_anim['player'] = []
for _ in range(8):
    img_path = os.path.join(IMG_PATH, "regularExplosion0{}.png".format(_))
    img = pg.image.load(img_path).convert()
    img.set_colorkey(rgb('black'))
    explosions_anim['large'].append(pg.transform.scale(img, (75, 75)))
    explosions_anim['small'].append(pg.transform.scale(img, (32, 32)))
    img_path = os.path.join(IMG_PATH, "sonicExplosion0{}.png".format(_))
    img = pg.image.load(img_path).convert()
    img.set_colorkey(rgb('black'))
    explosions_anim['player'].append(img)


# Load all sounds
laser_snd = pg.mixer.Sound(
    os.path.join(SND_PATH, 'laser.wav')
)
mobs_explode_snd = pg.mixer.Sound(
    os.path.join(SND_PATH, 'mobs_explode.wav')
)
ship_explode_snd = pg.mixer.Sound(
    os.path.join(SND_PATH, 'ship_explode.wav')
)

# Load background music
pg.mixer.music.load(
    os.path.join(SND_PATH, 'background.ogg')
)
pg.mixer.music.set_volume(0.4)


# Create group and sprites
all_sprites = pg.sprite.Group()
mobs = pg.sprite.Group()
bullets = pg.sprite.Group()

homer = Player()
all_sprites.add(homer)
score = 0

for _ in range(8):
    respawn_mob()

# Play background music and let's get started !
pg.mixer.music.play(loops=-1)
running = True

# Game loop
while running and homer:
    clock.tick(FPS)
    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWNt:
            if event.key == pg.K_SPACE:
                homer.shoot()

    # Draw
    screen.fill((0, 0, 0))
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, "Score = " + str(score), 14, (400, 10))
    draw_shield_bar(screen, 5, 5, homer.shield)
    draw_lives(screen, 700, 5, homer.lives, homer_mini_img)

    # Collision detection
    hits = pg.sprite.spritecollide(
        sprite=homer,
        group=mobs,
        dokill=True,
        collided=pg.sprite.collide_circle
    )
    bullet_collisions = pg.sprite.groupcollide(
        groupa=mobs,
        groupb=bullets,
        dokilla=True,
        dokillb=True
    )

    for bullet_collisionned in bullet_collisions:
        score += bullet_collisionned.radius
        # show and play explosion
        explosion = Explosion(bullet_collisionned.rect.center, size='large')
        all_sprites.add(explosion)
        mobs_explode_snd.play()
        respawn_mob()

    for hit in hits:
        homer.shield -= hit.radius * 2

        if homer.shield <= 0:
            # explode the ship !
            explosion = Explosion(homer.rect.center, size='player')
            all_sprites.add(explosion)
            ship_explode_snd.play()
            homer.lives -= 1
            homer.shield = 100
            homer.hide()
        else:
            # show and play explosion
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            mobs_explode_snd.play()
            respawn_mob()

    # player dies if no more shields and explosion has finished playing
    if homer.lives == 0 and not explosion.alive():
        running = False

    # Update screen
    all_sprites.update()
    pg.display.flip()


pg.quit()
sys.exit(0)
