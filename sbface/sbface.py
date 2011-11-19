#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from argparse import Action, ArgumentParser
from inspect import getargspec
import sys

import cv
import pygame
import pygame.locals

def set_defaults(obj, locals_):
    for arg_name in getargspec(obj.__init__).args:
        default_name = 'default_%s' % arg_name
        arg_value = locals_[arg_name]
        if arg_value is None:
            if not hasattr(obj, default_name):
                continue
            arg_value = getattr(obj, default_name)
        setattr(obj, arg_name, arg_value)

class FaceDetector(object):
    default_camera = 0
    default_haar_flags = 0
    default_haar_scale = 1.2
    default_min_neighbours = 2
    default_min_size = (20, 20)
    default_scale = 2

    def __init__(self, cascade_path, camera=None, haar_flags=None,
            haar_scale=None, min_neighbours=None, min_size=None, scale=None):
        super(FaceDetector, self).__init__()
        set_defaults(self, locals())
        self.cascade = cv.Load(self.cascade_path)
        self.capture = cv.CreateCameraCapture(self.camera)
        print(self.min_size)

    def _get_face_locations(self, image):
        iw, ih = image.width, image.height
        gray = cv.CreateImage((iw, ih), 8, 1)
        small_image = cv.CreateImage(
                (cv.Round(iw / self.scale), cv.Round(ih / self.scale)),
                8, 1)
        cv.CvtColor(image, gray, cv.CV_BGR2GRAY)
        cv.Resize(gray, small_image, cv.CV_INTER_LINEAR)
        cv.EqualizeHist(small_image, small_image)
        faces = cv.HaarDetectObjects(small_image, self.cascade,
                cv.CreateMemStorage(0), self.haar_scale, self.min_neighbours,
                self.haar_flags, self.min_size)
        locs = []
        for (sloc, n) in faces:
            locs.append(FaceLocation([int(i * self.scale) for i in sloc]))
        return locs

    def get_face_frame(self):
        frame = cv.QueryFrame(self.capture)
        image = cv.CreateImage((frame.width, frame.height),
                cv.IPL_DEPTH_8U, frame.nChannels)
        if frame.origin == cv.IPL_ORIGIN_TL:
            cv.Copy(frame, image)
        else:
            cv.Flip(frame, image, 0)
        return FaceFrame(image, self._get_face_locations(image))


class FaceLocation(object):
    def __init__(self, loc):
        self.loc = loc
        self.x = loc[0]
        self.y = loc[1]
        self.w = loc[2]
        self.h = loc[3]

    def __getitem__(self, item):
        return self.loc[item]

    @property
    def centre(self):
        return (self.x + self.w) / 2, (self.y + self.h) / 2

    def distance(self, other):
        sx, sy = self.centre
        ox, oy = other.centre
        return ((ox - sx)**2 + (oy - sy)**2)**0.5


class FaceFrame(object):
    def __init__(self, image, face_locations):
        super(FaceFrame, self).__init__()
        self.image = image
        self.face_locations = face_locations


class MultiFaceTracker(object):
    default_same = 100
    default_lag = 10

    def __init__(self, face_detector, lag=None, same=None):
        super(MultiFaceTracker, self).__init__()
        set_defaults(self, locals())
        self.faces = []

    def track(self):
        ff = self.face_detector.get_face_frame()
        locs = ff.face_locations
        visible = []
        for face in self.faces[:]:
            tracked = face.track(locs)
            if tracked:
                locs.remove(face.location)
            if tracked and face.frames >= self.lag:
                visible.append(face)
            elif not tracked and face.frames > self.lag:
                self.faces.remove(face)
        for loc in locs:
            self.faces.append(FaceTracker(loc, same=self.same))
        return ff, visible


class FaceTracker(object):
    default_same = MultiFaceTracker.default_same
    next_num = 0

    def __init__(self, location, same=None):
        super(FaceTracker, self).__init__()
        set_defaults(self, locals())
        self.num = FaceTracker.next_num
        FaceTracker.next_num += 1
        self.tracked = True
        self.frames = 1


    def track(self, new_locations):
        for new_location in new_locations:
            if self.location.distance(new_location) <= self.same:
                self.location = new_location
                if not self.tracked:
                    self.frames = 0
                self.tracked = True
                break
        else:
            if self.tracked:
                self.frames = 0
            self.tracked = False
        self.frames += 1
        return self.tracked


class SbFace(object):
    default_mode = (640, 480)
    title = 'SB Face'

    def __init__(self, face_tracker, mode=None):
        super(SbFace, self).__init__()
        set_defaults(self, locals())
        self.players = [pygame.image.load(image) for image in
                ('sb.gif', 'p.gif', 's.png', 'k.gif')]

    def start(self):
        self.screen = pygame.display.set_mode(self.mode)
        pygame.display.set_caption(self.title)

        clock = pygame.time.Clock()

        faces = []

        while True:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    return

            ff, visible = self.face_tracker.track()
            self.screen.blit(self.pygame_surface(ff.image), (0, 0))

            for face in visible:
                player = self.players[face.num % len(self.players)]
                s = pygame.transform.scale(player, face.location[2:])
                self.screen.blit(s, face.location[:2])

            pygame.display.flip()

    def pygame_surface(self, image):
        rgb = cv.CreateMat(image.height, image.width, cv.CV_8UC3)
        cv.CvtColor(image, rgb, cv.CV_BGR2RGB)
        return  pygame.image.frombuffer(rgb.tostring(), cv.GetSize(rgb), 'RGB')


class SplitValues(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = tuple(map(int, values.split(',')))
        if len(values) != 2:
            raise ValueError
        setattr(namespace, self.dest, values)


arg_parser = ArgumentParser()
arg_parser.add_argument('-c', '--camera', type=int)
arg_parser.add_argument('-f', '--haar-flags', type=int)
arg_parser.add_argument('-H', '--haar-scale', type=float)
arg_parser.add_argument('-l', '--lag', type=float)
arg_parser.add_argument('-m', '--min-size', action=SplitValues)
arg_parser.add_argument('-M', '--mode', action=SplitValues)
arg_parser.add_argument('-n', '--min-neighbours', type=int)
arg_parser.add_argument('-s', '--scale', type=float)
arg_parser.add_argument('-S', '--same', type=float)
arg_parser.add_argument('cascade')

def main(argv=None):
    if argv is None:
        argv = sys.argv

    args = arg_parser.parse_args(args=argv[1:])

    face_detector = FaceDetector(
            args.cascade,
            haar_flags=args.haar_flags,
            haar_scale=args.haar_scale,
            min_size=args.min_size,
            min_neighbours=args.min_neighbours,
            scale=args.scale)

    face_tracker = MultiFaceTracker(
            face_detector,
            lag=args.lag,
            same=args.same)

    pygame.init()

    sb_face = SbFace(
            face_tracker,
            mode=args.mode)

    sb_face.start()

    return 0

if __name__ == '__main__':
    exit(main())

