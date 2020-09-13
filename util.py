from pygame.transform import scale
from pygame.image import load

p_img=lambda x,y,z:scale(load(x).convert_alpha(),(y,z))
j_img=lambda x,y,z:scale(load(x).convert(),(y,z))

class Button():
    def __init__(self,x,y,w,h,i,f,k=0,*args):
        self.x,self.y,self.w,self.h,self.f,self.i,self.k=x,y,w,h,f,i,k
        if i>0:
            self.img0 = p_img('img/btn'+str(i)+'_0.png',w,h)
            self.img1 = p_img('img/btn'+str(i)+'_1.png',w,h)
        self.cd=0
        self.args=args
        if k!=0:
            self.k=ord(self.k)

    def run(self, timep, mou_pos, moup, keyp, screen):
        self.cd=max(0,self.cd-timep)
        oin=mou_pos[0]>=self.x and mou_pos[0]<=self.x+self.w
        oin&=mou_pos[1]>=self.y and mou_pos[1]<=self.y+self.h
        pud=(oin and moup[0]) or (keyp[self.k] if self.k>0 else 0)
        if pud and self.cd<=0:
            self.cd=200
            self.f(self.args)
        if self.i:
            screen.blit(self.img1 if oin else self.img0,(self.x,self.y))