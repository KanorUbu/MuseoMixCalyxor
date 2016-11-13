# coding: utf-8
import sys
import os
import subprocess
import copy
import random
import datetime
from Queue import Queue
from threading import Timer, Thread
from time import sleep

from evdev import InputDevice, categorize, ecodes
import pygame


FPS = 60

pygame.init()
pygame.mixer.quit()
clock = pygame.time.Clock()


if os.path.islink('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-event-kbd'):
    dev = InputDevice('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-event-kbd')
elif os.path.islink('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-if01-event-mouse'):
    dev = InputDevice('/dev/input/by-id/usb-JoyLabz_Makey_Makey_v1.20aa_60000000-if01-event-mouse')
else:
    print "No MakeyMakey/Arduino Leonardo found:-("
    sys.exit(1)


inoteMap = {
    ecodes.KEY_RIGHT: 'R1',
    ecodes.KEY_LEFT: 'R2',
    ecodes.KEY_UP: 'R3',
    ecodes.KEY_DOWN: 'R4',
    ecodes.KEY_SPACE: 'GO'
}

list_question = [
    {'path': '/home/tyrus/MuseoMixESt/projet/videos/vid1.mpg',
     'response': 'R1'},
    {'path': '/home/tyrus/MuseoMixESt/projet/videos/vid2.mpg',
     'response': 'R2'},
    {'path': '/home/tyrus/MuseoMixESt/projet/videos/vid3.mpg',
     'response': 'R3'},
    {'path': '/home/tyrus/MuseoMixESt/projet/videos/vid4.mpg',
     'response': 'R4'},
]

start_video = '/home/tyrus/MuseoMixESt/projet/videos/vid5.mpg'
end_video = '/home/tyrus/MuseoMixESt/projet/videos/vid5.mpg'

events_mm = Queue()

def worker():
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            events_mm.put(event)

t1 = Thread(target=worker)
t1.start()

def play_video(path, game):
    movie = pygame.movie.Movie(path)
    screen = pygame.display.set_mode((700, 400)) #(0, 0)) , pygame.FULLSCREEN)
    movie_screen = pygame.Surface(movie.get_size()).convert()

    movie.set_display(movie_screen)
    movie.play()

    playing = True
    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print "STOP"
                movie.stop()
                playing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print "STOP ESCAPE"
                    movie.stop()
                    playing = False
                    raise Exception
        if not events_mm.empty():
            event_mm = events_mm.get_nowait()
            code = event_mm.code
            result = inoteMap.get(code)
            if result == 'GO':
                print "Début du jeu"
                movie.stop()
                playing = False
                game.launch()
                return
            elif game.in_game() and result:
                print "Réponse"
                print result
                movie.stop()
                playing = False
                game.send_response(result)
                return

        screen.blit(movie_screen,(0,0))
        pygame.display.update()
        clock.tick(FPS)
        if not movie.get_busy():
            playing = False
            return


class Game(object):

    def __init__(self):
        self.raz()

    def raz(self):
        print "RAZ"
        self._in_game = False
        self._start_game = None
        self._nb_good_question = 0
        self._l_question = copy.deepcopy(list_question)
        self._question_current = None
        screen = pygame.display.set_mode((700, 400)) #0, 0) , pygame.FULLSCREEN)
        asurf = pygame.image.load("/home/tyrus/MuseoMixESt/33cd0368b313b33b.jpeg")
        # img_screen = pygame.Surface(asurf.get_size()).convert()
        img_surf = pygame.transform.scale(asurf, screen.get_size())
        # asurf = pygame.image.load("/home/tyrus/Images/1453487059.jpg")
        playing = True
        while playing:
            screen.blit(img_surf, (0,0))
            # pygame.display.flip()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print "STOP ESCAPE"
                        playing = False
                        raise Exception
            if not events_mm.empty():
                event_mm = events_mm.get_nowait()
                code = event_mm.code
                result = inoteMap.get(code)
                if result == 'GO':
                    print "Début du jeu"
                    playing = False
                    self.launch()
                    return

    def launch(self):
        #Début du timer
        self._in_game = True
        #Remise à zero des réponses
        self.play_video_start()
        self.play_video_question()

    def in_game(self):
        #Vérifie si le jeu est en cour
        return self._in_game

    def play_video_start(self):
        #Vidéo de début
        print "Vidéo du début"
        # path = '/tmp/test2.mpg'
        play_video(start_video, self)
        self._start_game = datetime.datetime.now()

    def play_video_end(self):
        #Vidéo de fin
        play_video(start_video, self)
        #Remise à zero
        self.raz()

    def play_video_question(self):
        #Choix d'une question aléatoire
        print "play_video_question"
        try:
            question = self._l_question.pop()
            # self._l_question.remove(question)
            print question
            self._question_current = question
            play_video(question['path'], self)
        except IndexError:
            self.raz()

    def send_response(self, result):
        #Vérification de la réponse par rapport à la question en cour
            #Si OK
                #Lance la vidéo de bonne réponse
                #Si nb de bonne réponse égale à 4
                    #Lance la vidéo de Victoire
                #Si nb ≠ de 4
                    #Lance une nouvelle vidéo question
        print "send_response"
        print result
        question = self._question_current
        print self._question_current
        if question['response'] == result:
            # if not len(self._l_question):
            if self._nb_good_question == 4:
                print "Play video Victoire"
                print "Activer le tabernacle"
                #TODO
                self.raz()
            else:
                print "Play video bonne réponse"
                # print len(self._l_question)
                self._nb_good_question += 1
                print self._nb_good_question
                self.play_video_question()
        else:
            print "Echec Replay"
            print self._question_current
            play_video(question['path'], self)



global game
game = Game()
gaming = True


# def stop_game():
#     print "Stop game"
#     game.raz()


# secs = 60*2
# t2 = Timer(secs, stop_game)
# t2.start()


while gaming:
    try:
        if not events_mm.empty():
            event = events_mm.get_nowait()
            code = event.code
            result = inoteMap.get(code)
            if result == 'GO':
                print "Début du jeu"
                game.launch()
            elif game.in_game() and result:
                print "Réponse"
                print result
                game.send_response(result)
        sleep(0.1)
    except Exception,e:
        # t1.terminate()
        # t2.terminate()
        print "BUG"
        print e
        sys.exit(0)

pygame.quit()
