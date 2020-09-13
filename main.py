import pygame, math, random, os, types
from pygame.locals import *
from sys import exit
import pickle, select, socket

from util import *
#*****************************************************************************************
#******************************** base **************************************************
#*****************************************************************************************
#******************************** connection *********************************************
server_addr  =   '10.28.156.99'
# server_addr  =   input('Input server address:')
s            =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_addr, 4321))
print('Connected to the server!')

#*****************************************************************************************
pygame.init()
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.mixer.set_num_channels(8)
pygame.mixer.init()

_width, _height = 1000, 650
_size=(_width,_height)
pygame.display.init()
pygame.display.set_caption("game")
screen = pygame.display.set_mode(_size,0,32)
#*****************************************************************************************
player_id  =   0
paints     =   []
pid        =   0
#*****************************************************************************************
class Canvas():
    def __init__(self):
        self.status = 0
        self.cnt    = 0
        self.pt     = 0

    def run(self, moup, mou_pos, screen):
        global paints, player_id, s, pid
        if player_id == 0:
            if moup[0]==1:
                if self.status==0: self.cnt += 1
                self.status = 1
                paints.append((pid, mou_pos, self.cnt))
                pid += 1
            else:
                self.status = 0

            if self.pt < pid:
                s.send(pickle.dumps(['up', paints[self.pt]]))
                self.pt += 1

        else:     
            s.send(pickle.dumps(['ask', pid]))
            print('send.', end='.')


        for i in range(1, len(paints)):
            if paints[i-1][-1] == paints[i][-1]:
                pygame.draw.line(screen, (0, 0, 10), paints[i-1][1], paints[i][1], 3)


#*****************************************************************************************
#*****************************************************************************************
# clock        =   pygame.time.Clock()


# def send_msg(msg):
#     s.send(msg[0].encode())
# btn = Button(800, 500, 100, 50, 1, send_msg, 'z', 'ddv')

hand = Canvas()

#*****************************************************************************************
#******************************** loop ***************************************************
while True:
    keyp=pygame.key.get_pressed()
    moup=pygame.mouse.get_pressed()
    mou_pos=pygame.mouse.get_pos()
    # timep = clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            s.close()
            exit()

    ins, outs, ex = select.select([s], [], [], 0)
    for inm in ins: 
        if player_id!=0:
            res = pickle.loads(inm.recv(4096))
            print(res)
            if res[0]==pid:
                paints.append(res[1])
                pid += 1

    screen.fill((202, 244, 255))
    hand.run(moup, mou_pos, screen)
    pygame.display.update()
