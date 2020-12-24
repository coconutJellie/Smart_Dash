import pygame
import pygbutton
import random,math
import os
from aubio import tempo, source
from numpy import median, diff

#copied from: https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame
class InputBox():
    def __init__(self, x, y, w, h, text=''):
        COLOR_INACTIVE = pygame.Color('lightskyblue3')
        COLOR_ACTIVE = pygame.Color('dodgerblue2')
        FONT = pygame.font.Font(None, 32)
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        COLOR_INACTIVE = pygame.Color('lightskyblue3')
        COLOR_ACTIVE = pygame.Color('dodgerblue2')
        FONT = pygame.font.Font(None, 32)
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Ring(pygame.sprite.Sprite):
    expandSpeed=2
    def __init__(self):
        super(Ring, self).__init__()
        self.r=10
        r=random.randint(0,150)
        g=random.randint(100,255)
        b=random.randint(0,150)
        self.color=r,g,b
        self.width=10
        self.x=random.randint(0,600)
        self.y=random.randint(0,400)

    def draw(self,screen,scrollX=0):
	    pygame.draw.circle(screen,self.color,(self.x-scrollX,self.y),self.r,self.width)

    def expand(self):
        self.r+=Ring.expandSpeed
        r,g,b=self.color
        if r<5:
            r=5
        if g<5:
            g=5
        if b<5:
            b=5
        self.color=(r-5,g-5,b-5)

# triangles represent beats
class Triangle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Triangle, self).__init__()
        self.x, self.y = x, y
        self.width = 20
        self.height = self.width//2*3**0.5
        self.rect = pygame.Rect(x,y-self.height,self.width,self.height)
        self.color=(255,255,255)

    def getRect(self):  
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) 

    def update(self,screenWidth, screenHeight):
        self.getRect()     

    def draw(self,screen):
        tempX=self.x-game.gameMode.scrollX
        pygame.draw.polygon(screen,self.color,[(tempX,self.y),
                    (tempX+self.width,self.y),
                    (tempX+self.width//2,self.y-self.height)])

class Rectangle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(100,100,100)):
        super(Rectangle, self).__init__()
        self.x, self.y = x, y
        self.height = height
        self.width = width
        self.rect = pygame.Rect(x,y,self.width,self.height)
        self.color= color

    def getRect(self):  
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) 

    def update(self,screenWidth, screenHeight):
        self.getRect()

    def draw(self,screen):
        tempX=self.x-game.gameMode.scrollX
        pygame.draw.rect(screen, self.color,pygame.Rect(tempX, self.y, self.width,self.height))

# player
class Dot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Dot, self).__init__()
        self.radius = 10
        self.initialY=y
        self.x, self.y = x, y
        self.xSpeed = 10
        self.ySpeed = 0
        self.ay=2
        self.jump=False
        self.jumps=0
        self.landed=True
        self.jumpTimer=0
        self.win=False
        self.lose=False
        self.onGround=True
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        self.color=(r,g,b)
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                                2 * self.radius, 2 * self.radius)
        
    def draw(self,screen):
        tempX=int(self.x-game.gameMode.scrollX)
        pygame.draw.circle(screen, self.color,(tempX,int(self.y)),self.radius)
        
    def getRect(self):  # GET REKT
        self.rect = pygame.Rect(self.x-self.radius,self.y-self.radius,2*self.radius,2*self.radius)

    def update(self, screenWidth, screenHeight):
        if self.jump and self.jumps<2:
            self.jumps+=1
            self.ySpeed=-14
            self.jump=False
            self.landed=False
        self.x += self.xSpeed
        if self.landed==False:
            self.y += self.ySpeed
        self.ySpeed+=self.ay
        for tri in game.gameMode.triangles:
            if self.rect.colliderect(tri.rect):
                print('bump into triangles')
                self.lose=True
        if self.y>=self.initialY:
                self.y=self.initialY 
                self.landed=True 
                self.jumps=0  
        for geo in game.gameMode.geometries:
            if self.iscollidedwith(geo):
                if (self.y+self.radius>=geo.y and self.y-self.radius<=geo.y+10 
                            and geo.x-10<=self.x<=geo.x+geo.width+10):
                    self.landed=True
                    self.jumps=0
                    self.y=geo.y-self.radius   
                else:
                    print('collided')
                    self.lose=True
            elif self.y<self.initialY:
                self.landed=False 
    
        if (self.x<game.gameMode.scrollX+game.gameMode.scrollMargin):
            game.gameMode.scrollX=self.x-game.gameMode.scrollMargin
        if (self.x>game.gameMode.scrollX+game.gameMode.width-game.gameMode.scrollMargin):
            game.gameMode.scrollX=self.x-game.gameMode.width+game.gameMode.scrollMargin
        self.getRect()
    
    def iscollidedwith(self,other):
        testX = self.x;
        testY = self.y;
        if self.x<other.x:         
            testX = other.x;     
        elif self.x>other.x+other.width:
            testX = other.x+other.width;   
        if self.y<other.y:         
            testY = other.y      
        elif self.y>other.y+other.height:
            testY = other.y+other.height

        distX = self.x-testX;
        distY = self.y-testY;
        distance = math.sqrt( (distX*distX) + (distY*distY) );
 
        if distance <= self.radius:
            return True
        return False

#Frame work copied from: http://blog.lukasperaza.com/getting-started-with-pygame/
class GameMode(object):
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.isGaming=False
        self.filename=''
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.scrollX = 0
        self.scrollMargin = width//2
        self.player=Dot(0,height*2//3-10)
        self.geometries = pygame.sprite.Group()
        self.triangles = pygame.sprite.Group()
        self.rings = pygame.sprite.Group()
        self.rectangles = pygame.sprite.Group()
        space=110
        r,g,b=154,154,154
        for i in range(600):
            self.rectangles.add(Rectangle(0+space*i,self.height*2//3+10,100,120,(r,g,b)))
        self.pause=False
        self.beats=None
        self.pitchTime,self.pitches,self.confidences=None,None,None
        self.landed=True
        self.timer=0
        self.buttons=self.getButtons()
        self.filenames=[]
        self.percentage=0
        self.mode=None
        pygame.init()

    def getButtons(self):
        width=60
        height=30
        setting=pygbutton.PygButton((440,20,width,height), 'Setting')
        if self.pause==False:
            pause=pygbutton.PygButton((510,20,width,height), 'Pause')
        else:
            pause=pygbutton.PygButton((510,20,width,height), 'Unpause')
        save=pygbutton.PygButton((90,20,width,height), 'Save')
        back=pygbutton.PygButton((30,20,width,height), 'Back')
        buttons=(setting,pause,save,back)
        return buttons

    def checkButtonEvent(self,event):
        setting,pause,save,back=self.buttons
        if 'click' in setting.handleEvent(event):
            pygame.mixer.music.pause()
            game.settingMode.isGaming=True
            game.settingMode.run()
        if 'click' in save.handleEvent(event): 
            if game.gameMode.filename not in game.historyMode.filenames:
                j=game.historyMode.filenames.index(None)
                game.historyMode.filenames[j]=game.gameMode.filename
                f=open("myHistory.txt","a+")
                f.write("%s\n"%game.gameMode.filename)
                f.close()
            
            i = game.historyMode.filenames.index(game.gameMode.filename)
            with open("myHistory.txt","r+") as f:
                data = f.read()
                f.seek(data.index(game.gameMode.filename))
                f.write("%s\n"%game.gameMode.filename)
                if game.gameMode.mode == "easy":
                    if game.gameMode.percentage>game.historyMode.easyScores[i]:
                        game.historyMode.easyScores[i] = game.gameMode.percentage
                        f.write("%s\n"%game.gameMode.percentage)
                        f.write("%s\n"%game.historyMode.hardScores[i])
                else:
                    if game.gameMode.percentage>game.historyMode.hardScores[i]:
                        game.historyMode.hardScores[i] = game.gameMode.percentage
                        f.write("%s\n"%game.historyMode.easyScores[i])
                        f.write("%s\n"%game.gameMode.percentage)

        if 'click' in pause.handleEvent(event): 
            if self.pause==False:
                self.pause=True
                self.buttons=self.getButtons()
                pygame.mixer.music.pause()
            else:
                self.pause=False
                self.buttons=self.getButtons()
                pygame.mixer.music.unpause()
        if 'click' in back.handleEvent(event): 
            self.isGaming=False
            pygame.mixer.music.stop()
            game.inputMode.isGaming=True
            game.inputMode.run()
        
    #copied from: https://github.com/aubio/aubio/blob/master/python/demos/demo_pitch.py
    def getPitch(self):
        from aubio import source, pitch
        filename = self.filename
        #change downsample to test samplerate
        downsample = 10
        samplerate = 44100 // downsample
        
        win_s = 4096 // downsample # fft size
        hop_s = 512  // downsample # hop size

        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate

        tolerance = 0.8

        pitch_o = pitch("yin", win_s, hop_s, samplerate)
        pitch_o.set_unit("freq")
        pitch_o.set_tolerance(tolerance)

        times = []
        pitches = []
        confidences = []

        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            pitch = pitch_o(samples)[0]
            pitch = int(round(pitch))
            confidence = pitch_o.get_confidence()
            if confidence < 0.4: pitch = 0.
            times += [total_frames / float(samplerate)]
            pitches += [pitch]
            confidences += [confidence]
            total_frames += read
            if read < hop_s: break
        return times, pitches, confidences
    
    # copied from: https://github.com/aubio/aubio/blob/master/python/demos/demo_tempo.py
    def getBeats(self):
        win_s = 1024                 # fft size
        hop_s = win_s // 2          # hop size
        samplerate = 0
        filename = self.filename
        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        o = tempo("default", win_s, hop_s, samplerate)
        # tempo detection delay, in samples
        # default to 4 blocks delay to catch up with
        #change delay
        delay = 100. * hop_s
        # list of beats, in samples
        beats = []
        # total number of frames read
        total_frames = 0
        while self.isGaming:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = int(total_frames - delay + is_beat[0] * hop_s)
                beats+=[this_beat/ float(samplerate)]
            total_frames += read
            if read < hop_s: break
        return beats

    def addPitches(self,interval,width):
        step=30
        height=step*2
        initialh=2*self.height//3
        prei=50
        for i in range(prei,len(self.pitches),interval):
            if self.pitches[i]>=self.pitches[prei] and self.pitches[i]-self.pitches[prei]>2:
                height+=step
                x=self.pitchTime[i]*self.player.xSpeed*self.fps//3
                self.geometries.add(Rectangle(x,initialh-height,width,height))
            elif self.pitches[i]<self.pitches[prei] and self.pitches[prei]-self.pitches[i]>2:
                if height<=step:
                    height=step
                    continue
                elif i%(interval*2)==0:
                    continue
                height-=step
                x=self.pitchTime[i]*self.player.xSpeed*self.fps//3
                self.geometries.add(Rectangle(x,initialh-height,width,height,))
            else:
                height=step
                continue
            prei=i
  
    def addBeats(self,beats,interval):
        for i in range(5,len(beats)):
            if i%interval==0:
                self.triangles.add(Triangle(beats[i]*self.player.xSpeed*self.fps//3,2*self.height//3))

    def timerFired(self,time):
        for i in range(len(self.beats)):
            if i%3==0 and int(self.beats[i]*10)==int(self.timer*10):
                self.rings.add(Ring())
        if self.pause==False:
            self.player.update(self.width,self.height)
            self.timer+=3/self.fps
            if int(self.timer)==int(self.pitchTime[-1]):
                self.player.win=True
            if self.player.win:
                pygame.mixer.music.stop()
                progress=1
                self.percentage=int(progress*100)
                game.gameOverMode.isGaming=True
                game.gameOverMode.run()
            if self.player.lose:
                pygame.mixer.music.stop()
                progress=self.timer/(self.pitchTime[-1])
                self.percentage=int(progress*100)
                print('lose')
                game.gameOverMode.isGaming=True
                game.gameOverMode.run()
            for ring in self.rings:
                ring.expand()
                r,g,b=ring.color
                if r<=0 and g<=0 and b<=0:
                    self.rings.remove(ring)
               
    def keyPressed(self,key,mod):
        if key==pygame.K_SPACE:
            self.player.jump=True

    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        pass
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass

    def drawProgressBar(self,screen):
        left,top,width,height=200,30,200,20
        progress=self.timer/(self.pitchTime[-1])
        pygame.draw.rect(screen, (0,255,0), pygame.Rect(left,top,width*progress,height))
        pygame.draw.rect(screen, (128,128,128), pygame.Rect(left,top,width,height), 1)
        font = pygame.font.SysFont("comicsansms", 24)
        text = font.render(f'{int(progress*100)}%', True, (255, 255, 255))
        screen.blit(text,(290,33))

    def redrawAll(self,screen):
        for ring in self.rings:
            ring.draw(screen)
        for button in self.buttons:
            button.draw(screen)
        self.player.draw(screen)
        self.drawProgressBar(screen)
        pygame.draw.rect(screen,(194,194,194),(0,self.height*2//3,self.width,self.height//3))
        for rec in self.rectangles:
            if rec.x+rec.width-self.scrollX<0 or rec.x-self.scrollX>self.width:
                continue
            rec.draw(screen)
        for geo in self.geometries:
            if geo.x+geo.width-self.scrollX<0 or geo.x-self.scrollX>self.width:
                continue
            geo.draw(screen)
        for tri in self.triangles:
            if tri.x+tri.width-self.scrollX<0 or tri.x-self.scrollX>self.width:
                continue
            tri.draw(screen)
            
    def isKeyPressed(self, key):
        if key==pygame.K_SPACE:
            return self._keys.get(key, False)
        ''' return whether a specific key is being held '''

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()

        if game.preMode==game.settingMode:
            pygame.mixer.music.set_volume(game.settingMode.volume)
        else:
            pygame.mixer.music.load(self.filename)
            pygame.mixer.music.set_volume(game.settingMode.volume)
            pygame.mixer.music.play()
        while self.isGaming:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isGaming = False
                self.checkButtonEvent(event)      
            screen.fill((0,0,0))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit()

class SplashScreenMode(object):
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.width = width
        self.height = height
        self.fps = fps
        self.timer=0
        self.title = title
        self.isSplashScreen=True
        png = pygame.image.load('smartdash.png')
        self.image = pygame.transform.scale(png,(400,80))
        self.buttons=self.getButtons()
        self.rings = pygame.sprite.Group()
        pygame.init()

    def getButtons(self):
        width=200
        height=30
        playButton=pygbutton.PygButton(((self.width-width)//2,self.height//2,width,height), 'Play')
        historyButton=pygbutton.PygButton(((self.width-width)//2,self.height//2+35,width,height), 'History')
        helpButton=pygbutton.PygButton(((self.width-width)//2,self.height//2+70,width,height), 'Help')
        settingButton=pygbutton.PygButton(((self.width-width)//2,self.height//2+105,width,height), 'Setting')
        buttons=(playButton,historyButton,helpButton,settingButton)
        return buttons

    def timerFired(self,time):
        self.timer+=1
        for ring in self.rings:
            ring.expand()
            r,g,b=ring.color
            if r==0 and g==0 and b==0:
                self.rings.remove(ring)
        if self.timer%self.fps==0:
            self.rings.add(Ring())
        if self.timer%self.fps==10:
            self.rings.add(Ring())

    def keyPressed(self,key,mod):
        pass
    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        pass
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass
    def redrawAll(self,screen):
        for ring in self.rings:
            ring.draw(screen)
        screen.blit(self.image,(100,70)) 
        for button in self.buttons:
            button.draw(screen)
        
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)
    def checkButtonEvent(self,event):
        play,history,helpmode,setting=self.buttons
        if 'click' in play.handleEvent(event): 
            self.isSplashScreen=False
            game.inputMode.isGaming=True
            game.inputMode.run()
        if 'click' in history.handleEvent(event): 
            self.isSplashScreen=False
            game.historyMode.isGaming=True
            game.historyMode.run()
        if 'click' in helpmode.handleEvent(event): 
            self.isSplashScreen=False
            game.helpMode.isGaming=True
            game.helpMode.run()
        if 'click' in setting.handleEvent(event): 
            self.isSplashScreen=False
            game.preMode=game.splashScreen
            game.settingMode.isGaming=True
            game.settingMode.run()

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        #self.__init__()
        playing = True
        while self.isSplashScreen:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isSplashScreen = False
                self.checkButtonEvent(event)
            screen.fill((0, 0, 0))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit()

class HistoryMode(object):
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.premode=None
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.isGaming=False
        self.buttons=self.getButtons()
        numMusFiles=self.getNumMusFiles('musicfiles')
        self.filenames=[None]*numMusFiles
        self.easyScores=[0]*numMusFiles
        self.hardScores=[0]*numMusFiles
        self.updateFiles()
        pygame.init()

    def getNumMusFiles(self,path,suffix='.wav'):
        if os.path.isfile(path):
            if path.endswith(suffix):
                return 1
            else:
                return 0
        else:
            count=0
            for filename in os.listdir(path):
                count+=self.getNumMusFiles(path+'/'+filename)
            return count

    def updateFiles(self):
        f=open("myHistory.txt","r")
        f1=f.readlines()
        count = 0
        index = 0
        for info in f1:
            if count%3==0:
                self.filenames[index]=info.strip('\n')
            elif count%3==1:
                self.easyScores[index]=int(info)
            elif count%3==2:
                self.hardScores[index]=int(info)
            count+=1
            index = count // 3

    def getButtons(self):
        width=100
        height=30
        play1=pygbutton.PygButton((470,60,width,height), 'Play (easy)')
        play2=pygbutton.PygButton((470,100,width,height), 'Play (hard)')
        play3=pygbutton.PygButton((470,160,width,height), 'Play (easy)')
        play4=pygbutton.PygButton((470,200,width,height), 'Play (hard)')
        play5=pygbutton.PygButton((470,260,width,height), 'Play (easy)')
        play6=pygbutton.PygButton((470,300,width,height), 'Play (hard)')
        back=pygbutton.PygButton((50,350,width,height), 'Back')
        return (play1,play2,play3,play4,play5,play6,back)

    def timerFired(self,time):
        pass
    def keyPressed(self,key,mod):
        pass
    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        pass
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass
    def redrawAll(self,screen):
        font = pygame.font.SysFont("comicsansms", 32)
        topText = font.render("My Favorites", True, (255,255,255))
        screen.blit(topText,(250,25))
        space=100
        y1=0
        y2=0
        y3=0

        # blit txt file to screen
        try:
            f=open("myHistory.txt","r")
            f1=f.readlines()
            count=0
            for filename in f1:
                if count>=9:
                    break
                elif count%3==0:
                    text = font.render(filename.strip('\n'), True, (255,255,255))
                    screen.blit(text,(70,70+y1))
                    y1+=space
                elif count%3==1:
                    easy=filename.strip('\n')
                    text = font.render(f'Easy mode: {easy}%', True, (255,255,255))
                    screen.blit(text,(70,110+y2))
                    y2+=space
                elif count%3==2:
                    hard=filename.strip('\n')
                    text = font.render(f'Hard mode: {hard}%', True, (255,255,255))
                    screen.blit(text,(250,110+y3))
                    y3+=space
                count+=1
        except:
            pass
        left=50
        width=400
        height=80
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(left,60,width,height), 3)
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(left,160,width,height), 3)
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(left,260,width,height), 3)
        for button in self.buttons:
            button.draw(screen)
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def checkButtonEvent(self,event):
        play1,play2,play3,play4,play5,play6,back=self.buttons
        if 'click' in play1.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='easy'
            game.gameMode.filename=self.filenames[0]
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,10)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(20,35)
            game.gameMode.run()
        if 'click' in play2.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='hard'
            game.gameMode.filename=self.filenames[0]
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,2)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(15,25)
            game.gameMode.run()
        if 'click' in play3.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='easy'
            game.gameMode.filename=self.filenames[1]
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,10)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(20,35)
            game.gameMode.run()
        if 'click' in play4.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='hard'
            game.gameMode.filename=self.filenames[1]
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,2)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(15,25)
            game.gameMode.run()
        if 'click' in play5.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='easy'
            game.gameMode.filename=self.filenames[2]
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,10)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(20,35)
            game.gameMode.run()
        if 'click' in play6.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='hard'
            game.gameMode.filename=self.filenames[2]
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,2)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(15,25)
            game.gameMode.run()
        if 'click' in back.handleEvent(event): 
            self.isGaming=False
            game.splashScreen.isSplashScreen=True
            game.splashScreen.run()

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()
        while self.isGaming:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isGaming = False
                self.checkButtonEvent(event)
            screen.fill((0,0,0))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit()
            
class MusicInputMode():
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.isGaming=False
        self.buttons=self.getButtons()
        self.inputBox=InputBox(60, 100, 300, 32)
        self.filename=''
        self.files=self.listFiles('musicfiles')
        pygame.init()

    def listFiles(self,path,suffix='.wav'):
        if os.path.isfile(path):
            if path.endswith(suffix):
                return [path]
            else:
                return []
        else:
            files = []
            for filename in os.listdir(path):
                files+=self.listFiles(path+'/'+filename)
            return files

    def getButtons(self):
        width=100
        height=30
        easy=pygbutton.PygButton((450,70,width,height), 'Easy mode')
        hard=pygbutton.PygButton((450,110,width,height), 'Hard mode')
        history=pygbutton.PygButton((200,300,200,height), 'View History')
        back=pygbutton.PygButton((50,350,width,height), 'Back')
        return (easy,hard,history,back)

    def timerFired(self,time):
        self.inputBox.update()
        self.filename=self.inputBox.text

    def keyPressed(self,key,mod):
        pass
    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        pass 
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass
    def drawFiles(self,screen):
        font = pygame.font.SysFont("comicsansms", 24)
        space=0
        for filename in self.files:
            text = font.render(filename, True, (255,255,255))
            screen.blit(text,(80,150+space))
            space+=25

    def drawInstruction(self,screen):
        font = pygame.font.SysFont("comicsansms", 36)
        text1 = font.render("Start a new game:", True, (255,255,255))
        text2 = font.render("Play a saved song?", True, (255,255,255))
        screen.blit(text1,(60,50))
        screen.blit(text2,(60,250))

    def redrawAll(self,screen):
        self.inputBox.draw(screen)
        self.drawInstruction(screen)
        self.drawFiles(screen)
        for button in self.buttons:
            button.draw(screen)
        
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def checkButtonEvent(self,event):
        easy,hard,history,back=self.buttons
        if 'click' in easy.handleEvent(event): 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.mode='easy'
            game.gameMode.filename=self.filename
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,10)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(20,35)
            game.gameMode.run()
        if 'click' in hard.handleEvent(event): 
            self.isGaming=False
            game.gameMode.mode='hard'
            game.preMode=game.gameMode
            game.gameMode.filename=self.filename
            game.gameMode.isGaming=True
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.addBeats(game.gameMode.beats,2)
            game.gameMode.pitchTime,game.gameMode.pitches,game.gameMode.confidences=game.gameMode.getPitch()
            game.gameMode.addPitches(15,25)
            game.gameMode.run()
        if 'click' in history.handleEvent(event): 
            self.isGaming=False
            game.historyMode.isGaming=True
            game.historyMode.run()
        if 'click' in back.handleEvent(event): 
            self.isGaming=False
            game.splashScreen.isSplashScreen=True
            game.splashScreen.run()
    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        #self.__init__()
        while self.isGaming:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isGaming = False
                self.inputBox.handle_event(event)
                self.checkButtonEvent(event)
            screen.fill((0,0,0))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit()

class GameOverMode(object):
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.isGaming=False
        self.buttons=self.getButtons()
        self.text=None
        self.premode=None
        congrats=pygame.image.load('congratulations.png')
        lose=pygame.image.load('cry.png')
        self.congrats=pygame.transform.scale(congrats,(500,100))
        self.cry = pygame.transform.scale(lose,(150,150))
        pygame.init()

    def getButtons(self):
        width=100
        height=30
        save=pygbutton.PygButton((150,300,width,height), 'Save')
        restart=pygbutton.PygButton((350,300,width,height), 'Restart')
        back=pygbutton.PygButton((50,350,width,height), 'Back')
        return (save,restart,back)
    def timerFired(self,time):
        self.text=f'Your progress is: {int(game.gameMode.percentage)} %'
    def keyPressed(self,key,mod):
        pass
    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        pass
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass

    def redrawAll(self,screen):
        font = pygame.font.SysFont("comicsansms", 36)
        text = font.render(self.text, True, (255,255,255))
        screen.blit(text,(60,250))
        if game.gameMode.player.win:
            screen.blit(self.congrats,(50,50))
        else:
            screen.blit(self.cry,(225,50))
        for button in self.buttons:
            button.draw(screen)
        
    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def checkButtonEvent(self,event):
        save,restart,back=self.buttons
        if 'click' in save.handleEvent(event):
            # if filename exists, overwrite filename in txt
            if game.gameMode.filename not in game.historyMode.filenames:
                j=game.historyMode.filenames.index(None)
                game.historyMode.filenames[j]=game.gameMode.filename
                f=open("myHistory.txt","a+")
                f.write("%s\n"%game.gameMode.filename)
                f.close()
            
            # overwrite scores
            i = game.historyMode.filenames.index(game.gameMode.filename)
            with open("myHistory.txt","r+") as f:
                data = f.read()
                f.seek(data.index(game.gameMode.filename))
                f.write("%s\n"%game.gameMode.filename)
                if game.gameMode.mode == "easy":
                    if game.gameMode.percentage>game.historyMode.easyScores[i]:
                        game.historyMode.easyScores[i] = game.gameMode.percentage
                        f.write("%s\n"%game.gameMode.percentage)
                        f.write("%s\n"%game.historyMode.hardScores[i])
                else:
                    if game.gameMode.percentage>game.historyMode.hardScores[i]:
                        game.historyMode.hardScores[i] = game.gameMode.percentage
                        f.write("%s\n"%game.historyMode.easyScores[i])
                        f.write("%s\n"%game.gameMode.percentage)

        if 'click' in restart.handleEvent(event):
            self.premode=game.gameMode.mode
            filename=game.gameMode.filename 
            self.isGaming=False
            game.preMode=game.gameMode
            game.gameMode.__init__()
            game.gameMode.isGaming=True
            game.gameMode.filename=filename
            game.gameMode.beats=game.gameMode.getBeats()
            game.gameMode.pitchTime,game.gameMode.pitches,\
                            game.gameMode.confidences=game.gameMode.getPitch()
            if self.premode=='easy':
                interval,width=20,35
                beatInterval=10
            elif self.premode=='hard':
                interval,width=15,25
                beatInterval=2
            game.gameMode.addPitches(interval,width)
            game.gameMode.addBeats(game.gameMode.beats,beatInterval)
            game.gameMode.mode=self.premode
            game.gameMode.run()
        if 'click' in back.handleEvent(event): 
            self.isGaming=False
            game.splashScreen.isSplashScreen=True
            game.gameMode.__init__()
            game.splashScreen.run()

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()
        while self.isGaming:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isGaming = False
                self.checkButtonEvent(event)
            screen.fill((0,0,0))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit() 

class HelpMode(object):
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.isGaming=False
        self.buttons=self.getButtons()
        self.page=1
        pygame.init()

    def getButtons(self):
        width=100
        height=30
        nextPage=pygbutton.PygButton((450,350,width,height), 'Next')
        back=pygbutton.PygButton((50,350,width,height), 'Back')
        return (nextPage,back)

    def timerFired(self,time):
        pass
    def keyPressed(self,key,mod):
        pass
    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        pass
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass

    def redrawAll(self,screen):
        space= 30
        font = pygame.font.SysFont("comicsansms", 20)
        if self.page==1:
            text1 = font.render('Welcome to Smart Dash! :)', True, (255,255,255))
            text2 = font.render('This is a wonderful place where you can create your own map.', True, (255,255,255))
            text3 = font.render('Type in the path of the music file you want to play, and the game will automatically', True, (255,255,255))
            text4 = font.render('design a map based on your input. Watch out for those pesky rectangles and triangles!', True, (255,255,255))
            text5 = font.render('Use the space bar to jump over the obstacles. If you choose easy mode, the game will', True, (255,255,255))
            text6 = font.render('be easier for you to play. However, if you choose hard mode, the game will be', True, (255,255,255))
            text7 = font.render('significantly harder. Good luck navigating through your custom map!', True, (255,255,255))
            text8 = font.render('Also, one last thing, you can only jump two times before you land again.', True, (255,255,255))
            text9 = font.render('(click next to see more awesome features)', True, (255,255,255))
        elif self.page==2:
            text1 = font.render('As an additional feature, you can track your progress on your favorite songs!', True, (255,255,255))
            text2 = font.render('When you die, remember to click save to save your progress! Then, from the history', True, (255,255,255))
            text3 = font.render('screen, you can choose to play the easy/hard mode of your saved songs.', True, (255,255,255))
            text4 = font.render('You can also save in the middle of playing the game! There are also pause/unpause', True, (255,255,255))
            text5 = font.render('buttons for you to use at your convenience. If the volume of the music is bothering you,', True, (255,255,255))
            text6 = font.render('you can adjust that in settings.', True, (255,255,255))
            text7 = font.render('                                                         GOOD LUCK                                           ', True, (255,255,255))
            text8 = font.render('                                                         WITH YOUR                                           ', True, (255,255,255))
            text9 = font.render('                                                         JOURNEY! :)                                           ', True, (255,255,255))
        texts=[text1,text2,text3,text4,text5,text6,text7,text8,text9]
        for i in range(len(texts)):
            screen.blit(texts[i],(30,30+space*i))
        if self.page==2:
            self.buttons[1].draw(screen)
        else:
            for button in self.buttons:
                button.draw(screen)

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def checkButtonEvent(self,event):
        nextPage,back=self.buttons
        if 'click' in nextPage.handleEvent(event): 
            self.page+=1
        if 'click' in back.handleEvent(event): 
            if self.page==1:
                self.isGaming=False
                game.splashScreen.isSplashScreen=True
                game.splashScreen.run()
            else:
                self.page-=1

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()

        while self.isGaming:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isGaming = False
                self.checkButtonEvent(event)
            screen.fill((0,0,0))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit()  

# volume rectangles 
class VolRect(object):
    def __init__(self,x,y,w,h):
        self.x,self.y,self.width,self.height=x,y,w,h
        self.color=(0,0,0)

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,pygame.Rect(self.x,self.y,self.width,self.height))

class SettingMode(object):
    def __init__(self, width=600, height=400, fps=60, title="Smart Dash"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.volumes = []
        w=25
        h=5
        widthstep=2
        heightstep=5
        for i in range(11):
            self.volumes.append(VolRect(150+(w+widthstep)*i,130-(h+heightstep*i),w,h+heightstep*i))
        png = pygame.image.load('volume.png')
        self.image = pygame.transform.scale(png,(50,50))
        self.testSound='musicfiles/sample.wav'
        self.volume=1.0
        self.isGaming=False
        self.buttons=self.getButtons()
        pygame.init()

    def getButtons(self):
        width=100
        height=30
        back=pygbutton.PygButton((50,350,width,height), 'Back')
        test=pygbutton.PygButton((450,100,width,height), 'test')
        return (back,test)

    def timerFired(self,time):
        pass
    def keyPressed(self,key,mod):
        pass
    def keyReleased(self,key,mod):
        pass
    def mousePressed(self,x,y):
        for i in range(len(self.volumes)):
            vol=self.volumes[i]
            if vol.x<=x<=vol.x+vol.width and vol.y<=y<=vol.y+vol.height:
                self.volume=i*0.1
    def mouseReleased(self,x,y):
        pass
    def mouseDragged(self,x,y):
        pass
    def mouseMotion(self,x,y):
        pass

    def drawVolumeBar(self,screen):
        for rect in self.volumes:
            rect.draw(screen)

    def redrawAll(self,screen):
        font = pygame.font.SysFont("comicsansms", 20)
        text = font.render(f'Current volume: {int(self.volume*10)/10}', True, (0,0,0))
        screen.blit(text,(240,150))
        self.drawVolumeBar(screen)
        screen.blit(self.image,(80,90)) 
        for button in self.buttons:
            button.draw(screen)

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def checkButtonEvent(self,event):
        back,test=self.buttons
        if 'click' in back.handleEvent(event): 
            if game.preMode==game.splashScreen:
                self.isGaming=False
                game.splashScreen.isSplashScreen=True
                game.splashScreen.run()
            elif game.preMode==game.gameMode:
                self.isGaming=False
                game.preMode=game.settingMode
                game.gameMode.isGaming=True
                game.gameMode.run()
        if 'click' in test.handleEvent(event): 
            test=pygame.mixer.Sound(self.testSound)
            test.set_volume(self.volume)
            test.play()

    def run(self):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()
        while self.isGaming:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDragged(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    self.isGaming = False
                self.checkButtonEvent(event)
            screen.fill((255,255,255))
            self.redrawAll(screen)
            pygame.display.flip()
        pygame.quit() 

class Pygame(object):
    def __init__(self): 
        self.gameMode=GameMode()
        self.gameOverMode=GameOverMode()
        self.splashScreen=SplashScreenMode()
        self.helpMode=HelpMode()
        self.historyMode=HistoryMode()
        self.inputMode=MusicInputMode()
        self.settingMode=SettingMode()
        self.preMode=None

def main(game):
    game.splashScreen.run()

if __name__=="__main__":
    game=Pygame()
    main(game)
