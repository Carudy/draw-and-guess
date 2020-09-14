import os, pygame, socket, string
from pygame.locals import *
from collections import defaultdict as dd

from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
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
            self.img = p_img('img/btn'+str(i)+'.png', self.w, self.h)
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
        if self.f and self.cd <=0 and self.ok(G.mou_pos, G.moup, G.keyp):
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

# https://blog.csdn.net/qq_39687901/article/details/104684429
class Textbox:
    def __init__(self, w, h, x, y, callback=None):
        self.font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 16)
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.text = ""  # 文本框内容
        self.callback = callback
        # 创建背景surface
        self.__surface = pygame.Surface((w, h))
        self.__surface.fill((250, 250, 250))
         
        self.dagparams = DefaultDagParams()
        self.state = 0  # 0初始状态 1输入拼音状态
        self.page = 1  # 第几页
        self.limit = 5  # 显示几个汉字
        self.pinyin = ''
        self.word_list = []  # 候选词列表
        self.word_list_surf = None  # 候选词surface
        self.buffer_text = ''  # 联想缓冲区字符串
 
    def create_word_list_surf(self):
        """
        创建联想词surface
        """
        word_list = [str(index + 1) + '.' + word for index, word in enumerate(self.word_list)]
        text = " ".join(word_list)
        self.word_list_surf = self.font.render(text, True, (250, 180, 50))
 
    def draw(self, dest_surf):
        # 创建文字surf
        text_surf = self.font.render(self.text, True, (60, 30, 3))
        # 绘制背景色
        dest_surf.blit(self.__surface, (self.x, self.y))
        # 绘制文字
        dest_surf.blit(text_surf, (self.x, self.y + (self.height - text_surf.get_height())),
                       (0, 0, self.width, self.height))
        # 绘制联想词
        if self.state == 1:
            dest_surf.blit(self.word_list_surf,
                           (self.x, self.y + (self.height - text_surf.get_height()) - 30),
                           (0, 0, self.width, self.height)
                           )
 
    def key_down(self, event):
        unicode = event.unicode
        key = event.key
 
        # 退位键
        if key == 8:
            self.text = self.text[:-1]
            if self.state == 1:
                self.buffer_text = self.buffer_text[:-1]
            return
 
        # 切换大小写键
        if key == 301:
            return
 
        # 回车键
        if key == 13:
            if self.callback:
                self.callback(self.text)
            return

        # 空格输入中文
        if self.state == 1 and key == 32:
            self.state = 0
            self.text = self.text[:-len(self.buffer_text)] + self.word_list[0]
            self.word_list = []
            self.buffer_text = ''
            self.page = 1
            return
 
        # 翻页
        if self.state == 1 and key == 61:
            self.page += 1
            self.word_list = self.py2hz(self.buffer_text)
            if len(self.word_list) == 0:
                self.page -= 1
                self.word_list = self.py2hz(self.buffer_text)
            self.create_word_list_surf()
            return
 
        # 回退
        if self.state == 1 and key == 45:
            self.page -= 1
            if self.page < 1:
                self.page = 1
            self.word_list = self.py2hz(self.buffer_text)
            self.create_word_list_surf()
            return
 
        # 选字
        if self.state == 1 and key in (49, 50, 51, 52, 53):
            self.state = 0
            if len(self.word_list) <= key - 49:
                return
            self.text = self.text[:-len(self.buffer_text)] + self.word_list[key - 49]
            self.word_list = []
            self.buffer_text = ''
            self.page = 1
            return
 
        if unicode != "":
            char = unicode
        else:
            char = chr(key)
 
        if char in string.ascii_letters:
            self.buffer_text += char
            self.word_list = self.py2hz(self.buffer_text)
            self.create_word_list_surf()
            # print(self.buffer_text)
            self.state = 1
        self.text += char
 
    def safe_key_down(self, event):
        try:
            self.key_down(event)
        except Exception as e:
            print(e)
            self.reset()
 
    def py2hz(self, pinyin):
        result = dag(self.dagparams, (pinyin,), path_num=self.limit * self.page)[
                 (self.page - 1) * self.limit:self.page * self.limit]
        data = [item.path[0] for item in result]
        return data
 
    def reset(self):
        # 异常的时候还原到初始状态
        self.state = 0  # 0初始状态 1输入拼音状态
        self.page = 1  # 第几页
        self.limit = 5  # 显示几个汉字
        self.pinyin = ''
        self.word_list = []  # 候选词列表
        self.word_list_surf = None  # 候选词surface
        self.buffer_text = ''  # 联想缓冲区字符串