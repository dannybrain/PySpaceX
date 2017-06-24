import pygame as pg

from settings import *
from sprites.Bullet import Bullet
from webcolors import name_to_rgb as rgb

# use vector instead of regular speed/position paradigm for
# more realistic movement
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.transform.scale(game.player_img, (50, 38))
        self.image.set_colorkey(rgb('black'))
        self.rect = self.image.get_rect()
        self.radius = 20
        # pg.draw.circle(self.image, rgb('red'), self.rect.center, self.radius)
        self.shield = SHIELD_MAX
        self.shot_delay = SHOTDELAY_INIT
        self.last_shot_time = pg.time.get_ticks()
        self.hidden = False
        self.hide_timer = pg.time.get_ticks()
        self.lives = LIVES
        self.power_level = POWER_LEVEL_INIT
        self.power_timer = pg.time.get_ticks()
        # speed and position
        self.rect.bottom = HEIGHT
        self.rect.centerx = WIDTH / 2
        self.position = vec(WIDTH / 2, HEIGHT)
        self.acceleration = vec(0, 0)
        self.velocity = vec(0, 0)

    def update(self):
        if self.hidden:
            # replace the player at the center of screen if it was
            # hidden after an explosion
            if pg.time.get_ticks() - self.hide_timer > RESPAWN_TIME:
                self.hidden = False
                self.rect.bottom = self.position.y = HEIGHT
                self.rect.centerx = self.position.x = WIDTH / 2
                self.velocity.x = self.acceleration.x = 0
            else:
                # don't do anything else as long as we're hidden
                return

        # no acceleration as long as no key has been pressed
        self.acceleration.x = 0

        # return back to power_level if time is elapsed
        if self.power_level > 1 and \
           pg.time.get_ticks() - self.power_timer > POWER_LEVEL_TIME:
            self.power_level -= 1
            self.power_timer = pg.time.get_ticks()

        # manage key pressed
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            self.acceleration.x = SHIP_ACCELERATION
        if keys[pg.K_LEFT]:
            self.acceleration.x = -SHIP_ACCELERATION
        if keys[pg.K_SPACE]:
            self.shoot()

        # calculate speed/acceleration
        self.acceleration += self.velocity * SHIP_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        # check boundaries and reinitialize vectors if we reached borders
        if self.position.x < 0:
            self.position.x = self.velocity.x = 0
        elif self.position.x > WIDTH:
            self.position.x = WIDTH
            self.velocity.x = 0

        # move the ship to its new position
        self.rect.centerx = self.position.x
        self.rect.bottom = self.position.y

    def shoot(self):
        now = pg.time.get_ticks()

        # can't shoot if the player is dead obviously ;o0
        if self.hidden:
            return

        # allow users to shoot below the delay if the laser hit
        # a mob, i.e no bullets on screen
        if now - self.last_shot_time > self.shot_delay \
           or len(self.game.bullets.sprites()) == 0:
            # POWER LEVEL 1 : one bullet at a time
            if self.power_level == 1:
                self.last_shot_time = now
                bullet = Bullet(self.game, self.rect.centerx, self.rect.top)
                self.game.laser_snd.play()
                self.game.all_sprites.add(bullet)
                self.game.bullets.add(bullet)

            # POWER LEVEL 2 : two bullets at a time
            if self.power_level >= 2:
                self.last_shot_time = now
                bullet1 = Bullet(self.game, self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.game, self.rect.right, self.rect.centery)
                self.game.laser_snd.play()
                self.game.all_sprites.add(bullet1)
                self.game.all_sprites.add(bullet2)
                self.game.bullets.add(bullet1)
                self.game.bullets.add(bullet2)

    def powerup(self):
        self.power_level += 1
        self.power_timer = pg.time.get_ticks()

    def hide(self):
        ''' temporarily hide the player '''
        self.hidden = True
        self.hide_timer = pg.time.get_ticks()
        # move the player off screen so it can't be seen for a while
        self.rect.center = (0, 5000)
