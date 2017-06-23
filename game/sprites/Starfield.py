import pygame as pg
import random
from webcolors import name_to_rgb as rgb
from webcolors import rgb_to_name as rgb2name


class Starfield(object):
    def __init__(self, number):
        self.stars = []

        # create about 20% of tiny stars, 30% medium
        # and keep the rest bigger
        for n in range(int(number * 0.2)):
            x = random.randrange(0, 800)
            y = random.randrange(0, 600)
            self.stars.append([x, y, rgb('grey')])

        for n in range(int(number * 0.3)):
            x = random.randrange(0, 800)
            y = random.randrange(0, 600)
            self.stars.append([x, y, rgb('lightgrey')])

        for n in range(int(number * 0.5)):
            x = random.randrange(0, 800)
            y = random.randrange(0, 600)
            self.stars.append([x, y, rgb('white')])

        random.shuffle(self.stars)

    def draw_stars(self, surface):
        for star in self.stars:
            # move the star downward (y). Speed depends on its size
            if rgb2name(star[2]) == 'white':
                speed = 0.4
                size = 2.2
            elif rgb2name(star[2]) == 'lightgrey':
                speed = 0.2
                size = 1.1
            else:
                speed = 0.1
                size = 0.8

            star[1] += speed
            if star[1] > 600:
                star[0] = random.randrange(0, 800)
                star[1] = 0

            # draw the point size based on its color
            point_to_draw = pg.Rect(star[0],
                                    star[1],
                                    size,
                                    size)
            pg.draw.rect(surface, star[2], point_to_draw)
