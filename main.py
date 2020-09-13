import pygame, math, random, os, types
from pygame.locals import *
from sys import exit
import pickle, select, socket

from util import *
#*****************************************************************************************
#******************************** connection *********************************************
#*****************************************************************************************
class Player():
    def __init__(self):
        self.id     =   -1
        self.type   =   1   # 0: drawer  1: watcher
        self.pid    =   0
        self.paints =   []
        self.canvas =   Canvas()

    def recv_paint(self, G, cmds):
        for msg in cmds: 
            data = msg.recv(4096) 
            if data:
                res = pickle.loads(data)
                print(res)
                if res[0]==self.pid:
                    self.paints.append(res[1])
                    self.pid += 1

    def run(self, G):
        cmds, outs, ex = select.select([G.s], [], [], 0)
        if self.type!=0:
            self.recv_paint(G, cmds)
        G.screen.fill((2, 4, 5))
        self.canvas.run(G)


class Canvas():
    def __init__(self):
        self.status = 0
        self.cnt    = 0
        self.pt     = 0

    def run(self, G):
        if G.player.type == 0:
            if G.moup[0]==1:
                if self.status==0: self.cnt += 1
                self.status = 1
                G.player.paints.append((G.player.pid, G.mou_pos, self.cnt))
                G.player.pid += 1
            else:
                self.status = 0

            if self.pt < G.player.pid:
                G.s.send(pickle.dumps(['up', G.player.paints[self.pt]]))
                self.pt += 1

        else:     
            G.s.send(pickle.dumps(['ask', G.player.pid]))

        for i in range(1, len(G.player.paints)):
            if G.player.paints[i-1][-1] == G.player.paints[i][-1]:
                pygame.draw.line(G.screen, (210, 210, 210), G.player.paints[i-1][1], G.player.paints[i][1], 3)


class GBV():
    def __init__(self):
        server_addr  =   '172.31.205.234'
        port         =   5659
        # server_addr  =   input('Input server address:')
        self.s            =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_addr, port))
        print('Connected to the server!')

        # GUI
        pygame.init()
        pygame.mixer.pre_init(44100, 16, 2, 4096)

        # display
        width, height = 1360, 900
        pygame.display.init()
        pygame.display.set_caption("Game")
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (200, 60)

        self.size        =   (width, height)
        self.screen      =   pygame.display.set_mode(self.size, 0, 32)

        # game
        self.player      =   Player()
#*****************************************************************************************
def game_init():
    global G
    G = GBV()
#******************************** loop ***************************************************
if __name__ == '__main__': 
    game_init()
    # main loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                s.close()
                exit()

        # events
        # G.timep   =  G.clock.tick(120)
        G.keyp    =  pygame.key.get_pressed()
        G.moup    =  pygame.mouse.get_pressed()
        G.mou_pos =  pygame.mouse.get_pos()

        # run
        G.player.run(G)

        pygame.display.update()