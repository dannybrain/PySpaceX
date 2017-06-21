import pygame as pg


class Explosion(pg.sprite.Sprite):
    def __init__(self, game, center, size='small'):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.size = size
        self.image = self.game.explosions_anim[size][0]
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
            if self.frame == len(self.game.explosions_anim[self.size]):
                self.kill()
            else:
                # keep center at the same place so we save the
                # center before loading the new image
                center = self.rect.center
                self.image = self.game.explosions_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
