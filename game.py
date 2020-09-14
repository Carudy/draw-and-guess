import pygame, math, random, os, types
from pygame.locals import *
from sys import exit
import pickle, select, socket
from collections import defaultdict as dd 

from util import *
#*****************************************************************************************
#******************************** btn func *********************************************
def want_play(G):
    G.s.send(pickle.dumps(['play', G.player.uid]))
    G.info0.set('准备就绪')

def new_canvas(G):
    G.player.paints = []
    G.player.pid = 0
    G.player.canvas.status =   0
    G.player.canvas.cnt    =   0
    G.player.canvas.pt     =   0

def re_draw(G):
    if G.player.type!=0: return
    G.s.send(pickle.dumps(['redraw', G.player.uid]))

def send_answer(G):
    if G.player.type!=1: return
    print(G.tb.text)
    G.s.send(pickle.dumps(['ans', G.player.uid, G.tb.text]))


#*****************************************************************************************
class Player():
    def __init__(self, name='Alice'):
        self.uid        =   -1
        self.name       =   name
        self.type       =   1   # 0: drawer  1: watcher
        self.pid        =   0
        self.paints     =   []
        self.canvas     =   Canvas()
        self.dx         =   780
        self.dy         =   [15, 180, 325, 480, 635]
        self.dis_names  =   [0] * 5
        self.dis_tps    =   [0] * 5
        self.dis_coins  =   [0] * 5

    def recv_paint(self, G, x, y, points):
        if x != self.pid: return
        self.paints += points
        self.pid = y+1

    def register(self, G, uid):
        self.uid   =  uid
        G.s.send(pickle.dumps(['name', self.uid, self.name]))
        print('Your id: ', self.uid)

    def update_user_info(self, info):
        for i in range(5):
            self.dis_names[i]  =  Label(info[i][0], pos=(self.dx, self.dy[i]))
            self.dis_tps[i]    =  Label(info[i][1], pos=(self.dx, self.dy[i] + 35))
            self.dis_coins[i]  =  Label(info[i][2], pos=(self.dx, self.dy[i] + 70))

    def run(self, G):
        cmds, outs, ex = select.select([G.s], [], [], 0)
        for msg in cmds: 
            data = msg.recv(4096) 
            if data:
                res = pickle.loads(data)
                if   res[0] == 'reg':
                    self.register(G, res[1])
                elif res[0] == 'draw':
                    self.recv_paint(G, res[1], res[2], res[3:])
                elif res[0] == 'full':
                    print('Full member!')
                elif res[0] == 'user':
                    self.update_user_info(res[1:])
                elif res[0] == 'info':
                    G.set_info(res[1], res[2])
                elif res[0] == 'tp':
                    G.player.type = res[1]
                elif res[0] == 'redraw':
                    new_canvas(G)

        # update user info
        if G.cd['user']==0: 
            G.cd['user'] = 1000
            G.s.send(pickle.dumps(['user', self.uid]))

        for lb in self.dis_names:
            if lb!=0:
                lb.run(G)
        for lb in self.dis_tps:
            if lb!=0:
                lb.run(G)
        for lb in self.dis_coins:
            if lb!=0:
                lb.run(G)
        self.canvas.run(G)


class Canvas():
    def __init__(self):
        self.status =   0
        self.cnt    =   0
        self.pt     =   0

    def yes_xy(self, pos):
        return pos[0] >= 1 and pos[0] <= 760 and pos[1] >= 50 and pos[1] <= 670

    def run(self, G):
        if self.yes_xy(G.mou_pos) and G.player.type == 0:
            if G.moup[0]==1:
                if self.status==0: self.cnt += 1
                self.status = 1
                if G.player.pid==0 or G.player.paints[-1][1]!=G.mou_pos:
                    G.player.paints.append((G.player.pid, G.mou_pos, self.cnt))
                    G.player.pid += 1
            else:
                self.status = 0

            if self.pt < G.player.pid:
                G.s.send(pickle.dumps(['up', G.player.uid, G.player.paints[self.pt]]))
                self.pt += 1

        elif G.cd['ask']==0:
            G.cd['ask'] = 200     
            G.s.send(pickle.dumps(['ask', G.player.uid, G.player.pid]))

        for i in range(1, len(G.player.paints)):
            if G.player.paints[i-1][-1] == G.player.paints[i][-1]:
                pygame.draw.line(G.screen, (210, 210, 210), G.player.paints[i-1][1], G.player.paints[i][1], 3)


class GBV():
    def __init__(self):
        # server_addr  =   '10.28.156.99'
        # name         =   input('Input your nickname:')
        # server_addr  =   input('Input server address:')
        port         =   5659

        cfg          =   open('config.txt').readlines()
        name         =   cfg[0][:-1]
        server_addr  =   cfg[1][:-1]
        print(cfg)

        self.s            =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server_addr, port))
        print('Connected to the server!')

        # GUI
        pygame.init()
        pygame.mixer.pre_init(44100, 16, 2, 4096)

        # display
        width, height = 1024, 768
        pygame.display.init()
        pygame.display.set_caption("Game")
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (280, 120)

        self.size        =   (width, height)
        self.screen      =   pygame.display.set_mode(self.size, 0, 32)

        # game
        self.cd         =   dd(int)
        self.clock      =   pygame.time.Clock()
        self.player     =   Player(name)
        self.tb         =   Textbox(180, 35, 25, 700)
        self.bg         =   j_img('img/bg.jpg', width, height)
        self.info0      =   Label("未开始", pos=(20, 10)) 
        self.info1      =   Label("未开始", pos=(400, 10)) 
        self.name_label =   Label('玩家：{}'.format(self.player.name), pos=(360, 698)) 
        self.btn_ok     =   Button(0, '猜', pos=(220, 698), f=send_answer)
        self.btn_re     =   Button(0, '重画', pos=(260, 698), f=re_draw)
        self.btn_start  =   Button(0, '开始游戏', pos=(600, 698), f=want_play)

    def set_info(self, x, y):
        if x==0:
            self.info0.set(y)
        else:
            self.info1.set(y)

    def run(self):
        for i in G.cd: G.cd[i] = max(0, G.cd[i]-G.timep)
        self.screen.blit(self.bg, (0, 0))
        self.info0.run(G)
        self.info1.run(G)
        self.btn_ok.run(G)
        self.btn_re.run(G)
        self.btn_start.run(G)
        self.name_label.run(G)

        self.player.run(G)
        self.tb.draw(G.screen)

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
                G.s.close()
                exit()
            elif event.type == pygame.KEYDOWN:
                G.tb.safe_key_down(event)

        # events
        G.timep   =  G.clock.tick(61)
        G.keyp    =  pygame.key.get_pressed()
        G.moup    =  pygame.mouse.get_pressed()
        G.mou_pos =  pygame.mouse.get_pos()

        # run
        G.run()
        pygame.display.update()