import os, pygame, socket
from pygame.locals import *
from collections import defaultdict as dd

#******************** tool func **************************   
def p_img(file, w, h):
    return pygame.transform.scale(pygame.image.load(file).convert_alpha(), (w, h))

def j_img(file, w, h):
    return pygame.transform.scale(pygame.image.load(file).convert(), (w, h))

#******************* classes **************************   
class Bk():  # backgrounds
    def __init__(self, src, w, h):
        # self.bk=[src + f for f in os.listdir(src) if f.startswith('bk') and f.endswith(('jpg'))]
        self.x, self.w, self.h = -1, w, h

        self.bk = dd(str)
        for i in os.listdir(src):
            if i.endswith(('jpg', 'png')):
                self.bk[i[:-4]] = src + i

    def set(self, x):
        self.x = x
        if x!=0: self.img = j_img(self.bk[x], self.w, self.h)

    def run(self, G):
        if self.x!=0: G.screen.blit(self.img, (4, 10))


class Button():
    def __init__(self, i=-1, txt='', ts=30, pos=(0, 0), w=0, h=0, key=0, f=None, G=None):
        self.key, self.f, self.w, self.h, self.pos  = key, f, w, h, pos
        self.img, self.txt = None, txt
        if i>=0:
            if w==0: self.w, self.h = len(txt) * (ts+4), (ts+14)
            self.img = p_img('img/btn/btn'+str(i)+'.png', self.w, self.h)
            tx = pos[0] + (self.w - len(txt) * ts) * 0.5
            ty = pos[1] + (self.h - ts) * 0.5
            self.cont0 = Label(txt, size=ts, pos=(tx, ty))
            self.cont1 = Label(txt, size=ts, pos=(tx, ty), color=(255, 204, 22))

        self.cd=0
        if isinstance(self.key, str): self.key=ord(self.key)

    def mouse_in(self, mou_pos):
        _ok  = mou_pos[0] > self.pos[0] and mou_pos[0] < self.pos[0]+self.w
        return _ok & (mou_pos[1] > self.pos[1] and mou_pos[1] < self.pos[1]+self.h)

    def ok(self, mou_pos, moup, keyp):
        if self.key>0 and keyp[self.key]: return True
        return moup[0] and self.mouse_in(mou_pos)

    def run(self, G):
        self.cd = max(0, self.cd-G.timep)
        if self.cd <=0 and self.ok(G.mou_pos, G.moup, G.keyp):
            # G.sound.play(27)
            self.cd = 300
            self.f(G)
        if self.img:
            G.screen.blit(self.img, self.pos)
            if self.mouse_in(G.mou_pos):
                self.cont1.run(G)
            else:
                self.cont0.run(G)


class Label():
    def __init__(self, x, size = 30, color=(0, 0, 0), pos=(0, 0)):
        self.font = pygame.font.Font("font/hanyi.ttf", size)
        self.color = color
        self.cont = self.font.render(x, True, color)
        self.pos = pos

    def set(self, x):
        self.cont = self.font.render(x, True, self.color)

    def run(self, G):
        G.screen.blit(self.cont, self.pos)


class Sound:
    def __init__(self, src):
        self.sd = dd()
        for i in [src + f for f in os.listdir(src) if f.endswith(('mp3', 'wav'))]:
            now = pygame.mixer.Sound(i)
            now.set_volume(.5)
            self.sd[int(i[len(src)+3:-4])] = now

        self.sd[0].set_volume(.3)
        self.sd[21].set_volume(.2)

    def play(self, x):
        self.sd[x].play()


class Bgm:
    ing = now = 0
    def __init__(self, src):        # src: the music folder
        # self.bgms = [src + f for f in os.listdir(src) if f.endswith(('mp3', 'wav'))]
        self.bgms = dd(str)
        for i in os.listdir(src):
            if i.endswith(('mp3', 'wav')):
                self.bgms[i[:-4]] = src + i
        self.player = pygame.mixer.music

    def set(self, x):
        if self.now == x: return
        self.now = x
        self.ing = 1
        self.player.stop()
        self.player.load(self.bgms[x])
        self.player.play(-1)

    def play(self):
        self.ing = 1
        self.player.play(-1)

    def pause(self):
        if self.ing == 1:
            self.ing = 0
            self.player.pause()
        else:
            self.ing = 1
            self.player.unpause()
