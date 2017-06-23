import pygame as pg
import random
from webcolors import name_to_rgb as rgb
from webcolors import rgb_to_name as rgb2name

from settings import *


class Starfield(object):
    def __init__(self, number):
        self.stars = []

        # create about 20% of tiny stars, 30% medium
        # and keep the rest bigger
        for n in range(int(number * 0.2)):
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            self.stars.append([x, y, rgb('grey')])

        for n in range(int(number * 0.3)):
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            self.stars.append([x, y, rgb('lightgrey')])

        for n in range(int(number * 0.5)):
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            self.stars.append([x, y, rgb('white')])

        random.shuffle(self.stars)

    def draw_stars(self, surface):
        for star in self.stars:
            # move the star downward (y). Speed depends on its size
            if rgb2name(star[2]) == 'white':
                speed = BIG_STARS_SPEED
                size = BIG_STARS_SIZE
            elif rgb2name(star[2]) == 'lightgrey':
                speed = MEDIUM_STARS_SPEED
                size = MEDIUM_STARS_SIZE
            else:
                speed = SMALL_STARS_SPEED
                size = SMALL_STARS_SIZE

            star[1] += speed
            if star[1] > HEIGHT:
                star[0] = random.randrange(0, 800)
                star[1] = 0

            # draw the point size based on its color
            point_to_draw = pg.Rect(star[0],
                                    star[1],
                                    size,
                                    size)
            pg.draw.rect(surface, star[2], point_to_draw)
