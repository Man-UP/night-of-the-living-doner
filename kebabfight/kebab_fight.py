#!/usr/bin/env python
from __future__ import division
import argparse
import math
import freenect
import cv
import frame_convert
import numpy
import time
import pygame
from pygame.locals import *

class PunchCapture(object):

    def __init__(self, background, punch_img, kebab_roar, explosion,
            fullscreen=False):
        self.fullscreen = fullscreen
        self.prev_min_val = None
        self.punch_threshold = 100
        self.prev_time = None
        self.step_size = 4
        self.current_step = 0
        self.keep_running = True
        self.background = background
        self.background_rect = self.background.get_rect()
        self.punch_img = punch_img
        self.punch_img_rect = self.punch_img.get_rect()
        self.next_animation_frame = 0
        self.game_state = 'idle'
        self.punch_cooldown = False
        self.health = 500
        self.damage = 10
        self.kebab_roar = kebab_roar
        self.explosion = explosion

    def display_depth(self, data, timestamp):
        img = frame_convert.pretty_depth_cv(data)
        min_index = data.argmin()
        width = data.shape[1]
        i, j  = divmod(min_index, width)
        min_val = int(data[i][j])

        if not self.current_step:
            pass
        elif self.prev_time is not None:
            val_diff = min_val - self.prev_min_val
            timestamp = time.time()
            time_diff = timestamp - self.prev_time
            # no div by zero and no negative time

            if self.punch_cooldown and time_diff > 0.5:
                self.punch_cooldown = False
                if self.game_state != 'death':
                    self.game_state = 'idle'
            if not self.punch_cooldown:
                #print "val_diff: %d\t time_diff: %d" % (val_diff, time_diff)
                acc = val_diff / (timestamp - self.last_time)
                #print "acc = % 04.3f" % acc
                self.prev_time = timestamp
                if acc > self.punch_threshold and (self.game_state != 'death' and self.game_state != 'sploded'):
                    self.punch_cooldown = True
                    self.health = self.health - self.damage
                    self.kebab_roar.play()
                    if self.health > 0:
                        self.game_state = 'hit'
                    else:
                        self.game_state = 'death'
                        self.explosion.play()
                    return (j, i)
        else:
            self.prev_time = time.time()
            self.last_time = time.time()
        self.current_step = (self.current_step + 1) % self.step_size
        self.last_time = time.time()
        self.prev_min_val = min_val

        if not self.fullscreen:
            pt1 = (j - 20, i - 20)
            pt2 = (j + 20, i + 20)
            cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
            cv.ShowImage('Depth', img)
            if cv.WaitKey(10) == 27:
                keep_running = False

    def display_rgb(self, data, timestamp):
        if self.fullscreen:
            return
        cv.ShowImage('RGB', frame_convert.video_cv(data))
        if cv.WaitKey(10) == 27:
            keep_running = False

    def change_punch_threshold(self, value):
        self.punch_threshold = value


    def get_next_animation_frame(self):
        offset = 1
        mod = 20
        if self.game_state == 'idle':
            offset = 1
            mod = 20
        elif self.game_state == 'hit':
            offset = 40
            mod = 7
        elif self.game_state == 'death':
            offset = 47
            mod = 76
            if self.next_animation_frame >= 75:
                self.game_state = 'sploded'
            print self.next_animation_frame
        elif self.game_state == 'sploded':
            offset = 125
            mod = 1
        self.next_animation_frame = (self.next_animation_frame + 1) % mod
        return pygame.image.load('media/kk_animation/kingkebab%04d.png' % (self.next_animation_frame + offset))


    def run(self):
        if not self.fullscreen:
            cv.NamedWindow('Depth')
            cv.NamedWindow('RGB')
            cv.CreateTrackbar('threshold', 'Depth', self.punch_threshold, 2048,
                    self.change_punch_threshold)

        self.screen = pygame.display.set_mode((1024, 768))
        if self.fullscreen:
            pygame.display.toggle_fullscreen()

        pygame.display.set_caption('Punch up')
        pygame.mouse.set_visible(False)

        clock = pygame.time.Clock()
        punches = []
        loop = True
        while loop:
            for event in pygame.event.get():
                if event.type == QUIT:
                    loop = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        loop = False

            depth, timestamp = freenect.sync_get_depth()
            location = self.display_depth(depth, timestamp)
            video, timestamp = freenect.sync_get_video()
            self.display_rgb(video, timestamp)

            next_frame = self.get_next_animation_frame()
            self.screen.blit(next_frame, next_frame.get_rect())
            font = pygame.font.Font(None, 36)
            text = font.render("Health: %d" % self.health, 1, (255, 10, 10))
            textpos = text.get_rect(centerx=self.screen.get_width()/2)
            self.screen.blit(text, textpos)
            if location:
                location = (abs(math.floor(1.6 * location[0]) - 1024), math.floor(1.6 * location[1]))
                punches.append(Punch(location, 10))
            for punch in punches:
                self.screen.blit(self.punch_img, punch.location)
                punch.life_to_live = punch.life_to_live - 1
                if punch.life_to_live < 1:
                    punches.remove(punch)

            pygame.display.flip()


class Punch(object):
    def __init__(self, location, life):
        self.location = location
        self.life_to_live = life

def main():
    pygame.init()
    argument_parse = argparse.ArgumentParser()
    argument_parse.add_argument('-f', '--fullscreen', action='store_true')
    args = argument_parse.parse_args()
    background = pygame.image.load('media/kk_animation/kingkebab0001.png')
    punch_img = pygame.image.load('pow.png')
    background_music = pygame.mixer.Sound('battle-music.wav')
    kebab_roar = pygame.mixer.Sound('punch.wav')
    explosion = pygame.mixer.Sound('explosion.wav')
    explosion.play()
    punch_game = PunchCapture(background, punch_img, kebab_roar, explosion,
            fullscreen=args.fullscreen)
    background_music.play(loops=-1)
    punch_game.run()

if __name__ == '__main__':
    main()
