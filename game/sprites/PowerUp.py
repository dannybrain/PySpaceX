import pygame as pg
import random

from settings import *
from webcolors import name_to_rgb as rgb


class PowerUp(pg.sprite.Sprite):
    def __init__(self, game, center):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.type = random.choice(['shield', 'bolt_silver', 'bolt_gold'])
        self.image = self.game.powerups_img[self.type]
        self.image.set_colorkey(rgb('black'))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the screen
        if self.rect.top > HEIGHT:
            self.kill()
