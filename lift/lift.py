#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
import argparse
import logging
import math
import multiprocessing
import os
import Queue
import sys
import threading

import pygame
from pygame.locals import *
import twisted.internet
import twisted.web.resource
import twisted.web.server
import twisted.web.static

logger = logging.getLogger(__file__)

def resolve_path(relative_path):
    return os.path.abspath(os.path.join(os.path.split(__file__)[0],
            relative_path))

class DefaultObject(object):
    def setattr(self, name, value):
        if value is None:
            value = getattr(self, 'default_%s' % name)
        setattr(self, name, value)

# ==============================================================================
# = Web server                                                                 =
# ==============================================================================

class LiftButtonResource(twisted.web.resource.Resource):
    isLeaf =True

    def __init__(self, button_press_queue):
        self.button_press_queue = button_press_queue

    def render_POST(self, request):
        self.button_press_queue.put(request.getClientIP())


def web_server_main(args, button_press_queue):
    root = twisted.web.static.File(resolve_path('static'))
    root.putChild('lift', LiftButtonResource(button_press_queue))
    twisted.internet.reactor.listenTCP(args.port, twisted.web.server.Site(root))
    logger.info('Reactor listening on port %d.' % args.port)
    twisted.internet.reactor.run()

# ==============================================================================
# = Lift game.                                                                 =
# ==============================================================================

LEFT = 'left'
RIGHT = 'right'
TEAM_1 = 'team1'
TEAM_2 = 'team2'

class LiftDoor(pygame.sprite.Sprite, DefaultObject):
    default_limit = 20

    def __init__(self, door, side, limit=None):
        super(LiftDoor, self).__init__()
        self.image = door
        self.rect = self.image.get_rect()
        self.rect.move_ip(0, 40)
        self.setattr('limit', limit)
        self.delta = 1 if side == RIGHT else -1
        self.offset = 0
        self.opening = False

    def open(self):
        self.opening = True

    def update(self):
        if self.opening:
            self.offset += self.delta
            self.rect.move_ip(self.offset, 0)
            if abs(self.offset) == self.limit:
                self.opening = False
                self.offset = 0


class Lift(object):
    def __init__(self, left, right):
        super(Lift, self).__init__()
        self.left = left
        self.right = right

    def open(self):
        self.left.open()
        self.right.open()


class Team(object):
    def __init__(self, name, lift, arrow_x):
        super(Team, self).__init__()
        self.name = name
        self.lift = lift
        self.arrow_x = arrow_x
        self.presses = 0

    def open(self):
        self.lift.open()


class LiftGame(DefaultObject):
    default_mode = (1024, 768)
    default_presses_required = 60
    default_arrow_start_angle = 15
    default_arrow_end_angle = -85
    default_tick = 30

    def __init__(self, button_press_queue, fullscreen=False,
            arrow_start_angle=None, arrow_end_angle=None, mode=None,
            presses_required=None, tick=None):
        super(LiftGame, self).__init__()

        self.button_press_queue = button_press_queue
        self.fullscreen = fullscreen

        self.setattr('arrow_start_angle', arrow_start_angle)
        self.setattr('arrow_end_angle', arrow_end_angle)
        self.setattr('mode', mode)
        self.setattr('presses_required', presses_required)
        self.setattr('tick', tick)

        self.can_press = False
        self.clear_presses = False
        self.clock = pygame.time.Clock()
        self.loop = True
        self.winner = None
        self.ips = {TEAM_1: [], TEAM_2: []}
        self.next_team = 0

        self.arrow_step = (self.arrow_end_angle - self.arrow_start_angle) \
                / self.presses_required

        pygame.mouse.set_visible(False)
        self._load_media(pygame.mixer.Sound, 'audio', ('.wav',))

    def _display_init(self):
        flags = 0
        if self.fullscreen:
            flags |= FULLSCREEN
        self.display = pygame.display.set_mode(self.mode, flags)
        self._load_media(pygame.image.load, 'images', ('.png',))
        doors = []
        for team in (1, 2):
            for side in (LEFT, RIGHT):
                doors.append(LiftDoor(getattr(self,
                        'team%d_%s' % (team, side)), side))

        self.doors = pygame.sprite.RenderPlain(doors)
        self.teams = {
                TEAM_1: Team(TEAM_1, Lift(doors[0], doors[1]),  34),
                TEAM_2: Team(TEAM_2, Lift(doors[2], doors[3]), 534)}

    def _load_media(self, loader, directory, exts):
        media_directory = resolve_path(directory)
        for item in os.listdir(media_directory):
            name, ext = os.path.splitext(item)
            path = os.path.join(media_directory, item)
            if ext in exts and os.path.isfile(path):
                setattr(self, name.replace('-', '_'), loader(path))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN \
                    and event.key == K_ESCAPE):
                self.loop = False

        while self.can_press:
            try:
                ip = self.button_press_queue.get_nowait()
            except Queue.Empty:
                break
            if self.clear_presses:
                continue

            for team_name, ips in self.ips.iteritems():
                if ip in ips:
                    break
            else:
                team_name = (TEAM_1, TEAM_2)[self.next_team]
                self.next_team  = (self.next_team + 1) % 2
                self.ips[team_name].append(ip)

            team = self.teams[team_name]
            if team.presses < self.presses_required:
                team.presses += 1
            else:
                self.winner = team
        self.clear_presses = False

    def start(self):
        self._display_init()
        self.intro.play()

        alpha = 255
        blit_black = True
        state = 1
        while self.loop:
            self.clock.tick(self.tick)
            self.handle_events()

            if state == 1:
                if alpha > 0:
                    alpha -= 3
                    self.black.set_alpha(alpha)
                else:
                    self.can_press = True
                    self.clear_presses = True
                    blit_black = False
                    self.intro.stop()
                    self.main.play()
                    state = 2
            elif state == 2:
                if self.winner is not None:
                    self.can_press = False
                    self.winner.open()
                    self.main.stop()
                    self.crash.play()
                    state = 3
            elif state == 3:
                self.doors.update()
                if not any(door.opening for door in self.doors):
                    pass#state = 4
            elif state == 4:
                self.loop = False

            self.display.blit(self.background, (0,0))
            for team in self.teams.values():
                self.blit_arrow(team)
            self.doors.draw(self.display)
            self.display.blit(self.foreground, (0, 0))
            if blit_black:
                self.display.blit(self.black, (0,0))
            pygame.display.flip()

    def blit_arrow(self, team):
        angle = self.arrow_start_angle + team.presses * self.arrow_step
        rot_arrow = rot_center(self.arrow, angle)
        self.display.blit(rot_arrow, (team.arrow_x, 80))


def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def lift_main(args, button_press_queue):
    pygame.init()
    lift_game = LiftGame(button_press_queue, fullscreen=args.fullscreen)
    lift_game.start()

# ==============================================================================

class SplitValues(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = tuple(map(int, values.split(',')))
        if len(values) != 2:
            raise ValueError
        setattr(namespace, self.dest, values)


def build_argument_parser():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-f', '--fullscreen', action='store_true')
    argument_parser.add_argument('-m', '--mode', action=SplitValues)
    argument_parser.add_argument('-p', '--port', default=8080, type=int)
    argument_parser.add_argument('-t', '--tick', type=int)
    return argument_parser

def main(argv=None):
    if argv is None:
        argv = sys.argv
    argument_parser = build_argument_parser()
    args = argument_parser.parse_args(args=argv[1:])

    button_press_queue = multiprocessing.Queue()
    web_server = multiprocessing.Process(target=web_server_main,
            args=(args, button_press_queue))
    web_server.daemon = True
    web_server.start()

    lift_main(args, button_press_queue)

    web_server.terminate()
    web_server.join()

    return 0

if __name__ == '__main__':
    exit(main())

