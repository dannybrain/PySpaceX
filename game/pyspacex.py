#!/usr/bin/env python3
''' PySpaceX, a simple game shooter made in Pygame

Inspired by the wonderful KidsCanCode videos on youtube
https://www.youtube.com/channel/UCNaPQ5uLX5iIEHUCLmfAgKg
'''

import sys
import os
import glob
import random
import pygame as pg
from webcolors import name_to_rgb as rgb

# CONSTANTS
FPS = 60
FILE_PATH = os.path.dirname('__file__')
IMG_PATH = os.path.join(FILE_PATH, 'img')
# needed to keep the columns short enough to comply with pep8
EXPLOD_PATH = os.path.join(IMG_PATH, 'Explosions')
SND_PATH = os.path.join(FILE_PATH, 'snd')
FONT_NAME = pg.font.match_font('arial')
WIDTH = 800
HEIGHT = 600
LIVES = 3
SHIELD_MAX = 100
SHOTDELAY_INIT = 500
SHOTDELAY_MAX = 200
POWER_LEVEL_INIT = 1
POWER_LEVEL_TIME = 10000


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


class PowerUp(pg.sprite.Sprite):
    def __init__(self, center):
        pg.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'bolt_silver', 'bolt_gold'])
        self.image = powerups_img[self.type]
        self.image.set_colorkey(rgb('black'))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the screen
        if self.rect.top > HEIGHT:
            self.kill()


class Mob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_original = random.choice(meteors_img)
        self.image_original.set_colorkey(rgb('black'))
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pg.draw.circle(self.image, rgb('red'), self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
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
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or \
                self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
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
        self.rect.bottom = HEIGHT
        self.rect.centerx = WIDTH / 2
        self.speedx = 1.2
        self.shield = SHIELD_MAX
        self.shot_delay = SHOTDELAY_INIT
        self.last_shot_time = pg.time.get_ticks()
        self.hidden = False
        self.hide_timer = pg.time.get_ticks()
        self.lives = LIVES
        self.power_level = POWER_LEVEL_INIT
        self.power_timer = pg.time.get_ticks()

    def update(self):
        if self.power_level > 1 and \
           pg.time.get_ticks() - self.power_timer > POWER_LEVEL_TIME:
            self.power_level -= 1
            self.power_timer = pg.time.get_ticks()

        if self.hidden:
            # replace the player at the center of screen if it was
            # hidden after an explosion
            if pg.time.get_ticks() - self.hide_timer > 3000:
                self.hidden = False
                self.rect.bottom = HEIGHT
                self.rect.centerx = WIDTH / 2

        keys = pg.key.get_pressed()

        if keys[pg.K_RIGHT]:
            self.rect.x += 5 * self.speedx
        if keys[pg.K_LEFT]:
            self.rect.x -= 5 * self.speedx
        if keys[pg.K_SPACE]:
            self.shoot()

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        now = pg.time.get_ticks()

        # can't shoot if the player is dead obviously ;o0
        if homer.hidden:
            return

        # allow users to shoot below the delay if the laser hit
        # a mob, i.e no bullets on screen
        if now - self.last_shot_time > self.shot_delay \
           or len(bullets.sprites()) == 0:
            if self.power_level == 1:
                self.last_shot_time = now
                bullet = Bullet(self.rect.centerx, self.rect.top)
                laser_snd.play()
                all_sprites.add(bullet)
                bullets.add(bullet)

            if self.power_level >= 2:
                self.last_shot_time = now
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                laser_snd.play()
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)

    def powerup(self):
        self.power_level += 1
        self.power_timer = pg.time.get_ticks()

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


# ===================================================================
# Initialize game
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('this is the title')
clock = pg.time.Clock()
cmd = None

# Load all game graphics
background = pg.image.load(
    os.path.join(IMG_PATH, 'Background/space_background.png')
).convert()
background_rect = background.get_rect()

homer_img = pg.image.load(
    os.path.join(IMG_PATH, 'Ships/playerShip1_blue.png')
).convert()

homer_mini_img = pg.transform.scale(homer_img, (25, 19))
homer_mini_img.set_colorkey(rgb('black'))

laser_img = pg.image.load(
    os.path.join(IMG_PATH, 'Lasers/laserRed16.png')
).convert()

meteors_img = []
for meteor_path in glob.glob(os.path.join(IMG_PATH, "Meteors/*.png")):
    meteors_img.append(pg.image.load(meteor_path).convert())

powerups_img = {}
powerups_img['shield'] = pg.image.load(
    os.path.join(IMG_PATH, 'Powerups/shield_gold.png')
).convert()
powerups_img['bolt_silver'] = pg.image.load(
    os.path.join(IMG_PATH, 'Powerups/bolt_silver.png')
).convert()
powerups_img['bolt_gold'] = pg.image.load(
    os.path.join(IMG_PATH, 'Powerups/bolt_gold.png')
).convert()

explosions_anim = {}
explosions_anim['large'] = []
explosions_anim['small'] = []
explosions_anim['player'] = []
for _ in range(8):
    img_path = os.path.join(EXPLOD_PATH, "regularExplosion0{}.png".format(_))
    img = pg.image.load(img_path).convert()
    img.set_colorkey(rgb('black'))
    explosions_anim['large'].append(pg.transform.scale(img, (75, 75)))
    explosions_anim['small'].append(pg.transform.scale(img, (32, 32)))
    img_path = os.path.join(EXPLOD_PATH, "sonicExplosion0{}.png".format(_))
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
powerup_laser_snd = pg.mixer.Sound(
    os.path.join(SND_PATH, 'powerup_laser.wav')
)
powerup_shield_snd = pg.mixer.Sound(
    os.path.join(SND_PATH, 'powerup_shield.wav')
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
powerups = pg.sprite.Group()

homer = Player()
all_sprites.add(homer)
score = 0

for _ in range(8):
    respawn_mob()

# Play background music and let's get started !
pg.mixer.music.play(loops=-1)
running = True

# ===================================================================
# Game loop
while running and homer:
    clock.tick(FPS)
    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
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
    # collision between laser and mobs
    hits = pg.sprite.groupcollide(
        groupa=mobs,
        groupb=bullets,
        dokilla=True,
        dokillb=True
    )
    for hit in hits:
        score += hit.radius
        # show and play explosion
        explosion = Explosion(hit.rect.center, size='large')
        all_sprites.add(explosion)
        mobs_explode_snd.play()
        respawn_mob()
        # randomly yield bonus
        #if random.random() > 0.95:
        if random.random() > 0.1:
            shield = PowerUp(hit.rect.center)
            powerups.add(shield)
            all_sprites.add(shield)

    # collision between player and bonus/powerups
    hits = pg.sprite.spritecollide(
        sprite=homer,
        group=powerups,
        dokill=True
    )
    for hit in hits:
        if hit.type == 'shield':
            homer.shield += random.randrange(10, 30)
            powerup_shield_snd.play()
            if homer.shield > SHIELD_MAX:
                homer.shield = SHIELD_MAX
        if hit.type == 'bolt_silver':
            homer.shot_delay -= 150
            powerup_laser_snd.play()
            if homer.shot_delay < SHOTDELAY_MAX:
                homer.shot_delay = SHOTDELAY_MAX
        if hit.type == 'bolt_gold':
            powerup_laser_snd.play()
            homer.powerup()

    # collision between player and mobs
    hits = pg.sprite.spritecollide(
        sprite=homer,
        group=mobs,
        dokill=True,
        collided=pg.sprite.collide_circle
    )
    for hit in hits:
        homer.shield -= hit.radius * 2

        if homer.shield <= 0:
            # explode the ship !
            explosion = Explosion(homer.rect.center, size='player')
            all_sprites.add(explosion)
            ship_explode_snd.play()
            homer.lives -= 1
            homer.power_level = 1
            homer.shield = SHIELD_MAX
            homer.shot_delay = SHOTDELAY_INIT
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
