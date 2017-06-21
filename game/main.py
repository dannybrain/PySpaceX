#!/usr/bin/env python3
''' PySpaceX, a simple game shooter made in Pygame

Inspired by the wonderful KidsCanCode videos on youtube
https://www.youtube.com/channel/UCNaPQ5uLX5iIEHUCLmfAgKg
'''
import os
import glob
import random
import pygame as pg
from webcolors import name_to_rgb as rgb

from settings import *
from sprites.Explosion import Explosion
from sprites.Mob import Mob
from sprites.Player import Player
from sprites.PowerUp import PowerUp


class Game(object):
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        # Load graphics and sound
        self._load_gfx()
        self._load_snd()
        # Running indicates the game is in an active state
        self.running = True

    def new(self):
        ''' start up a brand new game '''
        # Create group and sprites
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.powerups = pg.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.score = 0

        for _ in range(8):
            self._respawn_mob()

        # Play background music and let's get started !
        pg.mixer.music.play(loops=-1)
        self.run()

    def run(self):
        ''' main game loop after initialization '''
        # Playing indicates the game has actually started
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.draw()
            self.events()
            self.update()
            # Loop condition to end the game
            if self.player.lives == 0 and not self.explosion.alive():
                self.playing = False
                print(self.score)

    def draw(self):
        ''' draw objects on screen '''
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)
        Game.draw_text(self.screen, "Score = {}".format(self.score),
                       size=14,
                       pos=(400, 10))
        Game.draw_shield_bar(self.screen, 5, 5, self.player.shield)
        Game.draw_lives(self.screen, 700, 5,
                        self.player.lives, self.player_mini_img)
        self._detect_collisions()

    def _detect_collisions(self):
        self._laser_with_mobs_collision()
        self._player_with_powerup_collision()
        self._player_with_mobs_collision()

    def _laser_with_mobs_collision(self):
        hits = pg.sprite.groupcollide(
            groupa=self.mobs,
            groupb=self.bullets,
            dokilla=True,
            dokillb=True
        )
        for hit in hits:
            self.score += hit.radius
            # show and play explosion
            self.explosion = Explosion(self, hit.rect.center, size='large')
            self.all_sprites.add(self.explosion)
            self.mobs_explode_snd.play()
            self._respawn_mob()
            # randomly yield bonus under the collided mob
            if random.random() > BONUS_ODD:
                shield = PowerUp(self, hit.rect.center)
                self.powerups.add(shield)
                self.all_sprites.add(shield)

    def _player_with_powerup_collision(self):
        hits = pg.sprite.spritecollide(
            sprite=self.player,
            group=self.powerups,
            dokill=True
        )
        for hit in hits:
            if hit.type == 'shield':
                self.player.shield += random.randrange(10, 30)
                self.powerup_shield_snd.play()
                if self.player.shield > SHIELD_MAX:
                    self.player.shield = SHIELD_MAX
            if hit.type == 'bolt_silver':
                self.player.shot_delay -= 150
                self.powerup_laser_snd.play()
                if self.player.shot_delay < SHOTDELAY_MAX:
                    self.player.shot_delay = SHOTDELAY_MAX
            if hit.type == 'bolt_gold':
                self.powerup_laser_snd.play()
                self.player.powerup()

    def _player_with_mobs_collision(self):
        hits = pg.sprite.spritecollide(
            sprite=self.player,
            group=self.mobs,
            dokill=True,
            collided=pg.sprite.collide_circle
        )
        for hit in hits:
            self.player.shield -= hit.radius * 2

            if self.player.shield <= 0:
                # explode the ship !
                position = self.player.rect.center
                explosion = Explosion(self, position, size='player')
                self.all_sprites.add(explosion)
                self.ship_explode_snd.play()
                self.player.lives -= 1
                self.player.power_level = 1
                self.player.shield = SHIELD_MAX
                self.player.shot_delay = SHOTDELAY_INIT
                self.player.hide()
            else:
                # show and play explosion
                explosion = Explosion(self, hit.rect.center)
                self.all_sprites.add(explosion)
                self.mobs_explode_snd.play()
                self._respawn_mob()

    def events(self):
        ''' manage events/interactions with users '''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.shoot()

    def update(self):
        ''' update screen after drawing and checking events '''
        self.all_sprites.update()
        pg.display.flip()

    def show_title(self):
        pass

    def show_gameover(self):
        pass

    def _load_gfx(self):
        ''' Load all game graphics '''
        self.background = pg.image.load(
            os.path.join(IMG_PATH, 'Background/space_background.png')
        ).convert()
        self.background_rect = self.background.get_rect()

        self.player_img = pg.image.load(
            os.path.join(IMG_PATH, 'Ships/playerShip1_blue.png')
        ).convert()

        self.player_mini_img = pg.transform.scale(self.player_img, (25, 19))
        self.player_mini_img.set_colorkey(rgb('black'))

        self.laser_img = pg.image.load(
            os.path.join(IMG_PATH, 'Lasers/laserRed16.png')
        ).convert()

        self.meteors_img = []
        for meteor_path in glob.glob(os.path.join(IMG_PATH, "Meteors/*.png")):
            self.meteors_img.append(pg.image.load(meteor_path).convert())

        self.powerups_img = {}
        self.powerups_img['shield'] = pg.image.load(
            os.path.join(IMG_PATH, 'Powerups/shield_gold.png')
        ).convert()
        self.powerups_img['bolt_silver'] = pg.image.load(
            os.path.join(IMG_PATH, 'Powerups/bolt_silver.png')
        ).convert()
        self.powerups_img['bolt_gold'] = pg.image.load(
            os.path.join(IMG_PATH, 'Powerups/bolt_gold.png')
        ).convert()

        self.explosions_anim = {}
        self.explosions_anim['large'] = []
        self.explosions_anim['small'] = []
        self.explosions_anim['player'] = []
        for _ in range(8):
            img_path = os.path.join(
                EXPLOD_PATH,
                "regularExplosion0{}.png".format(_)
            )
            img = pg.image.load(img_path).convert()
            img.set_colorkey(rgb('black'))
            self.explosions_anim['large'].append(
                pg.transform.scale(img, (75, 75))
            )

            self.explosions_anim['small'].append(
                pg.transform.scale(img, (32, 32))
            )
            img_path = os.path.join(
                EXPLOD_PATH,
                "sonicExplosion0{}.png".format(_)
            )
            img = pg.image.load(img_path).convert()
            img.set_colorkey(rgb('black'))
            self.explosions_anim['player'].append(img)

    def _load_snd(self):
        # Load all sounds
        self.laser_snd = pg.mixer.Sound(
            os.path.join(SND_PATH, 'laser.wav')
        )
        self.mobs_explode_snd = pg.mixer.Sound(
            os.path.join(SND_PATH, 'mobs_explode.wav')
        )
        self.ship_explode_snd = pg.mixer.Sound(
            os.path.join(SND_PATH, 'ship_explode.wav')
        )
        self.powerup_laser_snd = pg.mixer.Sound(
            os.path.join(SND_PATH, 'powerup_laser.wav')
        )
        self.powerup_shield_snd = pg.mixer.Sound(
            os.path.join(SND_PATH, 'powerup_shield.wav')
        )
        # Load background music
        pg.mixer.music.load(
            os.path.join(SND_PATH, 'background.ogg')
        )
        pg.mixer.music.set_volume(0.4)

    def _respawn_mob(self):
        ''' Create a mob sprite and add it to all_sprites and mobs
        sprites group'''
        m = Mob(self)
        self.all_sprites.add(m)
        self.mobs.add(m)

    @staticmethod
    def draw_text(surface, text, size, pos):
        # font = pg.font.Font(FONT_NAME, size)
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, rgb('white'))
        text_rect = text_surface.get_rect()
        x, y = pos
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)

    @staticmethod
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

    @staticmethod
    def draw_lives(surface, x, y, lives, img):
        for i in range(lives):
            img_rect = img.get_rect()
            img_rect.x = x - 30 * i
            img_rect.y = y
            surface.blit(img, img_rect)


if __name__ == "__main__":
    spacex = Game()
    spacex.show_title()

    while spacex.running:
        spacex.new()
        spacex.show_gameover()

    pg.quit()
