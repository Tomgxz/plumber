# ============================== #

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"]="hide" # removes the output statement at the start of the code

import pygame
import random
import numpy as np
import time

# ============================== #

class Map(object):
    def __init__(self, r, c):

        # create matrix list for the map based on rows and columns
        y=[0]*r
        for i in range(r):
            y[i]=[0]*c
        
        # create matrix list for the map based on rows and columns
        z=[0]*r
        for i in range(r):
            z[i]=[Pipe([0, 0, 0, 0],0,"corner")]*c

        self.matrix=z       # map
        self.columns=c      # columns
        self.rows=r         # rows
        self.level=1        # used to work out the seed for the map
        self.index_r=0      # index c and index r represent the coords of the last blue piece
        self.index_c=0
        self.flow_matrix=y  # used to stop pipes staying blue after a rotation
        self.path_list=[(0,0)]
        self.seed=123

    def getPipes(self):
        # set the randomiser
        random.seed(self.seed*self.level)

        # all possible corner types (ie rotations)
        corner=[Pipe([1, 1, 0, 0], 0, "corner"), Pipe([0, 1, 1, 0], 1, "corner"),Pipe([0, 0, 1, 1], 2, "corner"), Pipe([1, 0, 0, 1], 3, "corner")]

        # all the possible straight types (ie rotations)
        straight=[Pipe([1, 0, 1, 0], 0, "straight"), Pipe([0, 1, 0, 1], 1, "straight")]

        # all the possible pipes
        pipes=[corner, straight]

        # sample used to generate map
        sample=np.sort(np.array(random.sample(range(self.columns), self.rows-1)))

        for i in range(self.rows):
            for j in range(self.columns):
                try:
                    if i < (self.rows-1) and sample[i]==j:                                                      # if there is still space for a pipe and the randomisation says this should be a corner
                        a=random.sample(range(4), 1)[0]                                                         # create a random number used to fetch a random pipe from the corner list
                        self.matrix[i][j]=Pipe(corner[a].orientation, corner[a].rotation, corner[a].type)       # create a pipe using the random number
                    elif i > 0 and sample[i-1]==j:                                                              # if there is still space for a pipe and the randomisation says this should be a corner
                        a=random.sample(range(4), 1)[0]                                                         # create a random number used to fetch a random pipe from the corner list
                        self.matrix[i][j]=Pipe(corner[a].orientation, corner[a].rotation, corner[a].type)       # create a pipe using the random number
                    elif i==0 and j < sample[i]:                                                                # if there is still space for a pipe and the randomisation says this should be a corner
                        a=random.sample(range(2), 1)[0]                                                         # create a random number used to fetch a random pipe from the straight list
                        self.matrix[i][j]=Pipe(straight[a].orientation, straight[a].rotation, straight[a].type) # create a pipe using the random number
                    elif i > 0 and sample[i-1] < j < sample[i]:                                                 # if there is still space for a pipe and the randomisation says this should be a corner
                        a=random.sample(range(2), 1)[0]                                                         # create a random number used to fetch a random pipe from the straight list
                        self.matrix[i][j]=Pipe(straight[a].orientation, straight[a].rotation, straight[a].type) # create a pipe using the random number
                    else:
                        # random numbers to randomise whether it is a straight or corner pipe and aits rotations
                        a=random.sample(range(2), 1)[0]
                        b=random.sample(range(len(pipes[a])), 1)[0]
                        self.matrix[i][j]=Pipe(pipes[a][b].orientation, pipes[a][b].rotation, pipes[a][b].type)
                except IndexError:
                    pass

        # set all pipes to white
        for l in self.matrix:
            for pipe in l:
                pipe.colour="white"

    def resetForNewLevel(self):
        self.level+=1       # increase to change seed
        self.index_r=0
        self.index_c=0
        self.getPipes()     # create a new path

    def path(self):
        """ Create the colours for the pipes """
        
        # if the starting piece is pointing left make it blue
        if self.index_r==self.index_c==0 and self.matrix[0][0].orientation[3]==1:
            self.matrix[0][0].colour="blue"
            self.flow_matrix[0][0]=self.matrix[0][0].rotation
            
            # if start piece is pointing out left  and if the right adgacent piece is pointing to the left (and the start piece is blue)
            if self.matrix[0][0].orientation[1]==1 and self.matrix[0][1].orientation[3]==1:
                self.index_c=1      # set the index to the right adjacent piece, as the last part of the water flow is that piece
                
            # if start piece is pointing out down (180)  and if the piece below is pointing up (0) (and the start piece is blue)
            if self.matrix[0][0].orientation[2]==1 and self.matrix[1][0].orientation[0]==1:
                self.index_r=1      # set the index to the piece underneath, as the last part of the water flow is that piece

        # if the starting piece is not pointing left make it white
        elif self.index_r==0 and self.index_c==0 and self.matrix[0][0].orientation[3] != 1:
                self.matrix[0][0].colour="white"

        # if we are past the first piece (ie past the top left piece)
        elif self.index_r > 0 or self.index_c > 0:
            # if the index coords are the final piece of the maze and the final piece is pointing right (90)
            if self.index_r==self.rows-1 and self.index_c==self.columns -1 and self.matrix[self.index_r][self.index_c].orientation[1]==1:
                return True         # tells the code to move to the next level screen
            else:
                # set the index piece as blue
                self.matrix[self.index_r][self.index_c].colour="blue"
                # add the index piece to the path list
                if (self.index_r, self.index_c) not in self.path_list:
                    self.path_list.append((self.index_r, self.index_c))
                breaking_point=-1
                i=0
                while i < len(self.path_list) and breaking_point==-1:   # until the path list is finished iterating
                    # fetch pipe based on path_list[i]:  if rotation is the same as that in the flow matrix
                    if self.matrix[self.path_list[i][0]][self.path_list[i][1]].rotation != self.flow_matrix[self.path_list[i][0]][self.path_list[i][1]]:
                        breaking_point=self.path_list[i]    # exit loop
                    i=i+1
                if breaking_point != -1:    # if the while loop was exited because of the breaking point
                    end=self.path_list[-1]
                    while end != breaking_point:    # while the last value of the path list is not the breaking point (i.e if the last value of the path list is not connected to water)
                        self.path_list.remove(end)  # remove this value from the list
                        self.matrix[end[0]][end[1]].colour="white"  # turn it white
                        end=self.path_list[-1]      # reset the end value
                        
                # set the index to the last value of the path list
                self.index_r=self.path_list[-1][0]  
                self.index_c=self.path_list[-1][1]

                # following code makes sure that there are no pipes that stay blue when the path is changed at a position which isnt the last one

                # if index is pointing up
                # and the penultimate item in the path list is pointing down
                # and the index column is the same as the column of the penultimate item in the path list
                # or
                # if index is pointing right
                # and the penultimate item in the path list is pointing left
                # and the index row is the same as the row of the penultimate item in the path list
                # or
                # if index is pointing down
                # and the penultimate item in the path list is pointing up
                # and the index column is the same as the column of the penultimate item in the path list
                # or
                # if index is pointing left
                # and the penultimate item in the path list is pointing right
                # and the index row is the same as the row of the penultimate item in the path list
                
                if  (self.matrix[self.index_r][self.index_c].orientation[0]==1 and                      
                    self.matrix[self.path_list[-2][0]][self.path_list[-2][1]].orientation[2]==1 and     
                    self.index_c==self.path_list[-2][1]) \
                or \
                   (self.matrix[self.index_r][self.index_c].orientation[1]==1 and                       
                    self.matrix[self.path_list[-2][0]][self.path_list[-2][1]].orientation[3]==1 and     
                    self.index_r==self.path_list[-2][0]) \
                or \
                   (self.matrix[self.index_r][self.index_c].orientation[2]==1 and                       
                    self.matrix[self.path_list[-2][0]][self.path_list[-2][1]].orientation[0]==1 and     
                    self.index_c==self.path_list[-2][1]) \
                or \
                   (self.matrix[self.index_r][self.index_c].orientation[3]==1 and                       
                    self.matrix[self.path_list[-2][0]][self.path_list[-2][1]].orientation[1]==1 and    
                    self.index_r==self.path_list[-2][0]):                                               

                    # if any of these three line statements are true
                    self.flow_matrix[self.index_r][self.index_c]=self.matrix[self.index_r][self.index_c].rotation # add this rotation to the flow matrix

                    # designated pipe coords
                    r=self.index_r
                    c=self.index_c

                    # if the pipe is pointing up, and the pipe above is not in the path list, and there is a pipe above and the pipe above is pointing down
                    if self.matrix[r][c].orientation[0]==1 and (r-1, c) not in self.path_list and r-1 >= 0 and self.matrix[r-1][c].orientation[2]==1:
                        self.index_r=r-1    # set the index as the pipe above
                    # if the pipe to us pointing right and the pipe to the right is not in the path list and there is a pipe to the right and the pipe to the right is pointing left
                    elif self.matrix[r][c].orientation[1]==1 and (r, c+1) not in self.path_list and c+1 <= self.columns-1 and self.matrix[r][c+1].orientation[3]==1:
                        self.index_c=c+1    # set the index to the pipe on the right
                    # if the pipe is pointing down and the pipe below is not in the path list and there is a pipe below and the pipe below is pointing up
                    elif self.matrix[r][c].orientation[2]==1 and (r+1, c) not in self.path_list and r+1 <= self.rows-1 and self.matrix[r+1][c].orientation[0]==1:
                        self.index_r=r+1    # set the index as the pipe below
                    # if the pipe is pointing left and the pipe to the left is not in the path list and there is a pipe to the left and the pipe to the left is pointing right
                    elif self.matrix[r][c].orientation[3]==1 and (r, c-1) not in self.path_list and c-1 >= 0 and self.matrix[r][c-1].orientation[1]==1:
                        self.index_c=c-1    # set the index to the pipe to the left

        # if the game is not won
        return False

class Pipe(object):
    def __init__(self, o, r, t):
        """ Create a pipe object """
        if len(o)==4 and type(o)==list and r in [0, 1, 2, 3]:
            self.orientation=o  # binary list representing the four possible outputs of the pipe going 0 90 180 270. 1 means the pipe is going out of this side
            self.rotation=r     # int between 0 and 3 representing the rotation going 0 90 180 270
            self.type=t         # string either straight or corner
            self.colour="white" # water or not?
        else:
            raise Exception("Wrong orientation vector")
        
    def __repr__(self):
        """ What to return when this object is printed """
        return f"{self.colour} {self.rotation}"
    
    def rotate(self):
        """ Rotate the pipe based on the current orientation vector and the pipe's shape """
        self.rotation += 1
        if self.type=="corner" and self.rotation > 3:
            self.rotation=0
        elif self.type=="straight" and self.rotation > 1:
            self.rotation=0
        if self.type=="corner":
            if self.rotation==0:
                self.orientation=list([1, 1, 0, 0])
            elif self.rotation==1:
                self.orientation=list([0, 1, 1, 0])
            elif self.rotation==2:
                self.orientation=list([0, 0, 1, 1])
            elif self.rotation==3:
                self.orientation=list([1, 0, 0, 1])
        elif self.type=="straight":
            if self.rotation==0:
                self.orientation=list([1, 0, 1, 0])
            elif self.rotation==1:
                self.orientation=list([0, 1, 0, 1])


class Slider():
    #(self.w-100,self.h-100)
    def __init__(self, name, val, maxi, mini, pos, game):
        self.val = val  # start value
        self.maxi = maxi  # maximum at slider position right
        self.mini = mini  # minimum at slider position left
        self.xpos = pos[0]
        self.ypos = pos[1]
        self.surf = pygame.surface.Surface((132+100,100), pygame.SRCALPHA, 32).convert_alpha()
        self.hit = False  # the hit attribute indicates slider movement due to mouse interaction
        self.game=game
        
        # Static graphics-slider background #
        pygame.draw.rect(self.surf,(255,255,255),[0,30,132,5],) # line

        # dynamic graphics-button surface #
        self.button_surf = pygame.surface.Surface((20, 20))
        self.button_surf.fill((1, 1, 1))
        self.button_surf.set_colorkey((1, 1, 1))
        pygame.draw.circle(self.button_surf, WHITE, (10, 10), 10, 0)
        pygame.draw.circle(self.button_surf, MEDCYAN, (10, 10), 8, 0)
        
    def draw(self):
        """ Combination of static and dynamic graphics in a copy of the basic slide surface"""

        # static
        surf = self.surf.copy()

        # dynamic
        pos = (10+int((self.val-self.mini)/(self.maxi-self.mini)*122), 33)
        self.button_rect = self.button_surf.get_rect(center=pos)
        surf.blit(self.button_surf, self.button_rect)
        self.button_rect.move_ip(self.xpos, self.ypos)  # move of button box to correct screen position

        # screen
        self.game.window.blit(surf, (self.xpos, self.ypos))

    def move(self):
        """The dynamic part; reacts to movement of the slider button."""
        
        self.val = (pygame.mouse.get_pos()[0]-self.xpos-10)/122*(self.maxi-self.mini)+self.mini
        if self.val < self.mini:
            self.val = self.mini
        if self.val > self.maxi:
            self.val = self.maxi
        

# ============================== #


GOLD=(255,99,71)
GREEN=(0, 155, 0)
BLUE=(0, 0, 229)
GRAY=(202, 225, 255)
WHITE=(202,238,240)
BLACK=(0,0,0)
ORANGE=(200, 100, 50)


DARKCYAN=(14,79,84)
MEDCYAN=(20,122,148)
CYAN=(82,211,245)


class Game():
    def __init__(self,*a,**k):
        """Plumber Game"""
        # initialize pygame
        pygame.init()
        pygame.mixer.init(buffer=64)

        # set width and height of screen. These variables change on pygame.VIDEORESIZE
        self.w=1700
        self.h=1000
        
        # set size of map
        self.r=5
        self.c=5

        # set size of tiles
        self.imgSize=90

        # start the display
        self.initializeDisplaySettings()
        self.initializeDisplay()

        # pygame clock
        self.clock=pygame.time.Clock()

        # load all images, sounds and music into attributes, dictionaries and lists
        self.initializeImages()
        self.initializeSounds()
        self.initializeMusic()

        # used in conjunction with the sfx button
        self.sfxEnabled=True
        
        # create the music volume slider from the custom slider class
        self.musicVolumeSliderPositionAlgorithm=lambda:(5,self.h-100)       # command used to work out the position of the slider throughout the code
        self.musicVolumeSlider=Slider("Volume",75,100,0,self.musicVolumeSliderPositionAlgorithm(),self)
        self.setMusicVolume(self.musicVolumeSlider.val)

        # create the sfx volume slider from the custom slider class
        self.sfxVolumeSliderPositionAlgorithm=lambda:(self.w-137,self.h-100)# command used to work out the position of the slider throughout the code
        self.sfxVolumeSlider=Slider("SFX",75,100,0,self.sfxVolumeSliderPositionAlgorithm(),self)
        self.setSFXVolume(self.sfxVolumeSlider.val)

        # false until the intro screen ends
        self.gameActive=False

        # initialize the map and generate the first level
        self.map=Map(self.r,self.c)
        self.map.getPipes()

        self.stopMusic()

    def run(self):
        """Start the Game"""
        fadeIn=True
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:     # alt f4 quits game
                    pygame.quit()
                    raise SystemExit
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:  # escape key quits game
                        pygame.quit()
                        raise SystemExit
                if event.type==pygame.VIDEORESIZE:  # allows the window size to be changed
                    self.w=event.w      # resize the width and height variables so that other parts of the code work
                    self.h=event.h
                    self.setBackground()    # reset background
                    self.resizeVignettes()  # reset grime and vignette
                    self.resizeSliders()    # reset the slider positions
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if event.button==1:
                        if self.gameActive: # if the game is active, move a piece
                            p=pygame.mouse.get_pos()    # get mouse pos as p
                            x=(p[0]-self.pushToRight)//self.imgSize         # change x and y coordinates so that they can be used to access the map matrix
                            y=((p[1]-self.getHeaderSize())//self.imgSize)

                            # if the position of the mouse is inside the constraints of the map
                            if p[0] > self.pushToRight and (self.imgSize*self.r)+self.getHeaderSize() > p[1] and not(p[1] < self.getHeaderSize()):
                                try:
                                    self.map.matrix[y][x].rotate()  # rotate the piece (by changing the values in the orientation list)
                                    self.playRandomHighShot()   # play sfx
                                except IndexError:
                                    pass
                        if self.stopMusicBtnCollider.collidepoint(event.pos):           # if inside the constraints of the music button, toggle whether music is playing
                            self.toggleMusic()
                        elif self.musicVolumeSlider.button_rect.collidepoint(event.pos):# if inside the constraints of the music slider, toggle the slider hit variable
                            self.musicVolumeSlider.hit=True
                            
                        elif self.stopSFXBtnCollider.collidepoint(event.pos):           # if inside the constraints of the sfx button, toggle whether sfx is on
                            self.toggleSFX()
                        elif self.sfxVolumeSlider.button_rect.collidepoint(event.pos):  # if inside the constraints of the sfx slider, toggle the slider hit variable
                            self.sfxVolumeSlider.hit=True
                            
                        else:
                            if not self.gameActive:
                                self.playSound("waterfx1")  # play whooshing sound effect
                                self.gameActive=True        # move from intro scene to game

                if event.type==pygame.MOUSEBUTTONUP:        # make sure that sliders are deactivated
                    self.musicVolumeSlider.hit=False
                    self.sfxVolumeSlider.hit=False

            if self.musicVolumeSlider.hit:  # move music slider and set the music volume to the slider value
                self.musicVolumeSlider.move()
                self.setMusicVolume(self.musicVolumeSlider.val)
                
            if self.sfxVolumeSlider.hit:    # move sfx slider and set the sfx volume to the slider value
                self.sfxVolumeSlider.move()
                self.setSFXVolume(self.sfxVolumeSlider.val)

            self.setBackground()            # display the gradient and background image
            self.displaySoundButtons()      # display buttons and sliders
            
            if not self.gameActive:     # if the game is not active (ie the intro screen)
                def showMenu():
                    """Show intro menu. Used as a function to allow for a fade in"""
                    self.setBackground()
                    self.displaySoundButtons()
                    
                    font=self.getLargeFont()

                    tH=font.get_height()    # used to organise text

                    # create text objects
                    t1=font.render("Click a pipe to rotate it",True,WHITE)
                    t1r=t1.get_rect(center=(self.w//2,(self.h//2)-tH))

                    t2=font.render("Press anywhere to begin",True,WHITE)
                    t2r=t2.get_rect(center=(self.w//2,(self.h//2)+tH))

                    t3=font.render("Press escape at any time to exit",True,WHITE)
                    t3r=t3.get_rect(center=(self.w//2,(self.h//2)+tH*2))

                    # display text
                    self.window.blit(t1,t1r)
                    self.window.blit(t2,t2r)
                    self.window.blit(t3,t3r)

                if fadeIn:                  # fade in happens on the first iteration of this while loop
                    self.fadeIn(showMenu)

                showMenu()

            if self.gameActive:                 # if the game is currently active
                hasCompleted=self.map.path()    # the path function returns a boolean based on whether the maze has been completed
                if hasCompleted:
                    self.map.matrix[self.r-1][self.c-1].colour="blue"   # make sure the final one is blue, sometimes it doesnt work
                    self.nextLevelScreen()      # display the next level screen
                else:
                    self.displayMap()           # otherwise, display the map

                self.setHeader()                # show the "Level x" text

            self.displayVignette()      # show vignette and grime
            pygame.display.update()     # update screen
            self.clock.tick(16)         # 16 fps

            fadeIn=False    # make sure it doesnt constantly fade in

    def fadeIn(self,cmd):
        """ Fade into a scene defined by cmd argument"""
        x=pygame.Surface((self.w,self.h))   # create surface. This is the black screen that fades out to give a fade in effect
        x.fill(BLACK)                       # fill surface with black
        for i in range(255,0,-5):       # decrease by 5 for each step. "i" is used for the alpha level
            x.set_alpha(i)              # set alpha
            cmd()                       # display the screen
            self.displayVignette()      # display the vignette
            self.window.blit(x,(0,0))   # display the surface
            pygame.display.update()     # update the screen
            pygame.time.wait(1)         # wait one milisecond

            for event in pygame.event.get():    # make sure the events are still happening. This is the same as in the run command so I wont comment it
                if event.type==pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
                if event.type==pygame.VIDEORESIZE:
                    self.w=event.w
                    self.h=event.h
                    x=pygame.Surface((self.w,self.h))   # reset the size of the surface so that it still works
                    x.fill(BLACK)
                    self.resizeVignettes()
                    self.resizeSliders() 
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if event.button==1:
                        if self.stopMusicBtnCollider.collidepoint(event.pos):
                            self.toggleMusic()
                        elif self.musicVolumeSlider.button_rect.collidepoint(event.pos):
                            self.musicVolumeSlider.hit=True
                            
                        elif self.stopSFXBtnCollider.collidepoint(event.pos):
                            self.toggleSFX()
                        elif self.sfxVolumeSlider.button_rect.collidepoint(event.pos):
                            self.sfxVolumeSlider.hit=True
                            
                        else:
                            return
                if event.type==pygame.MOUSEBUTTONUP:
                    self.musicVolumeSlider.hit=False
                    self.sfxVolumeSlider.hit=False
                    
            if self.musicVolumeSlider.hit:
                self.musicVolumeSlider.move()
                self.setMusicVolume(self.musicVolumeSlider.val)
                
            if self.sfxVolumeSlider.hit:
                self.sfxVolumeSlider.move()
                self.setSFXVolume(self.sfxVolumeSlider.val)

            # everything from for event in pygame.event.get() is duplicated (for the most part) from the run command
              
    def getHeaderSize(self):
        """ Get the header height relative to the font size, which is relative to the screen size """
        font=self.getMediumFont()
        hGap=font.get_height()+40
        font=self.getSmallFont()
        bh=font.get_height()
        return hGap+bh+40

    def setHeader(self):
        """ Set the header for when the game is commencing """
        font=self.getMediumFont()
        t=font.render(f"Level {self.map.level}",True,WHITE)
        tr=t.get_rect(center=(self.w//2,t.get_height()//2))
        self.window.blit(t,tr)

    def nextLevelScreen(self):
        """ Display the next level screen """
        self.playSound("waterfx1")                  # play a transition sound
        x=True
        while x:
            # create object for title
            font=self.getMediumFont()
            th=font.get_height()
            t=font.render(f"Congratulations! Level {self.map.level} completed!",True,WHITE)
            tr=t.get_rect(center=(self.w//2,th//2))

            # create buttons
            
            font=self.getSmallFont()
            b1t=font.render("Exit",True,WHITE)      # create text for buttons
            b1tw=b1t.get_width()+20                 # get width and height for the button borders
            b1th=b1t.get_height()+5

            b2t=font.render("Continue to next level",True,WHITE) # same as above
            b2tw=b2t.get_width()+20
            b2th=b2t.get_height()+5
     
            cGap=100    # horizontal gap between buttons
            hGap=th+40  # vertical gap between the buttons and text

            # get rectangle for the button border
            b1r=pygame.Rect(                    
                (self.w//2-cGap-b1tw)-b1tw//2,
                hGap-b1th//2,
                b1tw,
                b1th)

            # get rectangle for the button border
            b2r=pygame.Rect(                    
                (self.w//2+cGap)-b2tw//2,
                hGap-b2th//2,
                b2tw,
                b2th)

            # display background and map. map is frozen because in the event loop there is no code to rotate the pieces
            self.setBackground()                
            self.displayMap()
    
            # get rects for the text                
            b1tr=b1t.get_rect(center=((self.w//2-cGap-b1tw),hGap))
            b2tr=b2t.get_rect(center=((self.w//2+cGap),hGap))

            # display all text
            self.window.blit(t,tr)
            self.window.blit(b1t,b1tr)
            self.window.blit(b2t,b2tr)

            # display button borders
            pygame.draw.rect(self.window,WHITE,b1r,2)
            pygame.draw.rect(self.window,WHITE,b2r,2)

            # display sound buttons and vignettes
            self.displaySoundButtons()
            self.displayVignette()
        
            for event in pygame.event.get():        # make sure the events are still happening. This is the same as in the run command so I wont comment it
                if event.type==pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
                if event.type==pygame.VIDEORESIZE:
                    self.w=event.w
                    self.h=event.h
                    self.setBackground()
                    self.resizeVignettes()
                    self.resizeSliders() 
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if event.button==1:
                        if b1r.collidepoint(event.pos):     # exit button generated earlier
                            pygame.quit()
                            raise SystemExit
                        if b2r.collidepoint(event.pos):     # next level button generated earlier
                            self.map.resetForNewLevel()     
                            x=False
                            
                        if self.stopMusicBtnCollider.collidepoint(event.pos):
                            self.toggleMusic()
                        elif self.musicVolumeSlider.button_rect.collidepoint(event.pos):
                            self.musicVolumeSlider.hit=True
                            
                        elif self.stopSFXBtnCollider.collidepoint(event.pos):
                            self.toggleSFX()
                        elif self.sfxVolumeSlider.button_rect.collidepoint(event.pos):
                            self.sfxVolumeSlider.hit=True
                        
                if event.type==pygame.MOUSEBUTTONUP:
                    self.musicVolumeSlider.hit=False
                    self.sfxVolumeSlider.hit=False

            if self.musicVolumeSlider.hit:
                self.musicVolumeSlider.move()
                self.setMusicVolume(self.musicVolumeSlider.val)
                
            if self.sfxVolumeSlider.hit:
                self.sfxVolumeSlider.move()
                self.setSFXVolume(self.sfxVolumeSlider.val)

            # everything from for event in pygame.event.get() is duplicated (for the most part) from the run command

            # update screen and 16 fps
            pygame.display.update()
            self.clock.tick(16)

        # after moving to next level, reset the background and play the water transition effect
        self.setBackground()
        self.playSound("waterfx2")

    def resizeSliders(self):
        """ Resize the sliders so that they stay inside the window and dont move around on pygame.VIDEORESIZE """
        # used to make getting all the values easier
        m=self.musicVolumeSlider
        s=self.sfxVolumeSlider

        # replace the old sliders with newly created ones. all values except for the position are carried over
        # the position is generated by the lambda command created in the initializer
        self.musicVolumeSlider=Slider("Volume",m.val,m.maxi,m.mini,self.musicVolumeSliderPositionAlgorithm(),self)
        self.setMusicVolume(m.val)

        self.sfxVolumeSlider=Slider("SFX",s.val,s.maxi,s.mini,self.sfxVolumeSliderPositionAlgorithm(),self)
        self.setSFXVolume(s.val)

    def displayMap(self):
        """ Show the map of the pipes """
        
        # variables used to calculate positions
        topHeight=self.getHeaderSize()
        center=self.w//2
        totalWidth=(self.r+2)*self.imgSize
        furthestLeft=center-totalWidth//2

        self.pushToRight=furthestLeft+self.imgSize # x position of the first piece
        
        self.window.blit(self.pipes["sw"],(furthestLeft,0+topHeight)) # start piece
        self.window.blit(self.pipes["s"],(furthestLeft+(self.c*self.imgSize)+self.imgSize,(self.r*self.imgSize)-self.imgSize+topHeight)) # end piece

        # for every row and column
        for i in range(self.c):
            for j in range(self.r):
                # pixel coordinates for images
                x=(self.imgSize*(i+1))+furthestLeft
                y=(self.imgSize*j)+topHeight

                # get the color of the image needed based on the color attribute of the current pipe, fetched from the map's matrix
                # variable "color" is used when fetching the image from the self.pipes dictionary
                if self.map.matrix[j][i].colour=="white":
                    color=""
                else:
                    color="w"

                # code fetches the shape and color of the piece
                # from there it generates a string (p) used to fetch the correct image from the self.pipes dictionary
                # then, it will rotate the image corresponding to the rotation attribute of the pipe, and place it at (x,y) on the screen

                t=self.map.matrix[j][i].type # straight or corner
                if t=="straight":
                    p=f"s{color}"
                    if self.map.matrix[j][i].rotation==0:
                        self.window.blit(pygame.transform.rotate(self.pipes[p],-90),(x,y))
                    elif self.map.matrix[j][i].rotation==1:
                        self.window.blit(self.pipes[p],(x,y))
                if t=="corner":
                    p=f"c{color}"
                    if self.map.matrix[j][i].rotation==0:
                        self.window.blit(pygame.transform.rotate(self.pipes[p],-180),(x,y))
                    elif self.map.matrix[j][i].rotation==1:
                        self.window.blit(pygame.transform.rotate(self.pipes[p],-270),(x,y))
                    elif self.map.matrix[j][i].rotation==2:
                        self.window.blit(self.pipes[p],(x,y))
                    elif self.map.matrix[j][i].rotation==3:
                        self.window.blit(pygame.transform.rotate(self.pipes[p],-90),(x,y))
                    
    def initializeSounds(self):
        """ Fetch all of the sounds at the start so as not to cause unnessesary lag """
        self.sounds={
            "waterfx1":pygame.mixer.Sound("resources/sounds/waterfx1.wav"),
            "waterfx2":pygame.mixer.Sound("resources/sounds/waterfx2.wav"),
            "nextlevel":pygame.mixer.Sound("resources/sounds/nextlevel.wav"),
            "highshot1":pygame.mixer.Sound("resources/sounds/highshot01.wav"),
            "highshot2":pygame.mixer.Sound("resources/sounds/highshot02.wav"),
            "highshot3":pygame.mixer.Sound("resources/sounds/highshot03.wav"),
            "highshot4":pygame.mixer.Sound("resources/sounds/highshot04.wav"),
            "highshot5":pygame.mixer.Sound("resources/sounds/highshot05.wav"),
            "highshot6":pygame.mixer.Sound("resources/sounds/highshot06.wav"),
            "highshot7":pygame.mixer.Sound("resources/sounds/highshot07.wav"),
            "highshot8":pygame.mixer.Sound("resources/sounds/highshot08.wav"),
            "highshot9":pygame.mixer.Sound("resources/sounds/highshot09.wav"),
            "highshot10":pygame.mixer.Sound("resources/sounds/highshot10.wav")
            }
        
        for x in self.sounds:   # x represents the key
            # set all sound volume to 0.5 and all highshot volume to 0.25
            self.sounds[x].set_volume(0.5)
            if x[:8]=="highshot":
                self.sounds[x].set_volume(0.25)

    def initializeDisplaySettings(self):
        """ Create the caption and logo for the pygame window """
        pygame.display.set_caption("PLUMBING GAME")
        icon=pygame.image.load("resources/images/icon.png")
        pygame.display.set_icon(icon)

    def initializeDisplay(self):
        """ Create the pygame window. The display settings should be set up before this"""
        self.window=pygame.display.set_mode((self.w,self.h),pygame.RESIZABLE) # resizeable allows the window size to be changed. Used in conjunction with the pygame.VIDEORESIZE event

    def initializeImages(self):
        """ Fetch all of the images at the start of the game so as not to cause unnessesary lag """
        
        # convert alpha optimises the images to stop game lag. Without it the program becomes really slow and, therefore, not very fun to play

        # pipe images
        self.pipes={
            "s":pygame.image.load("resources/images/pipeStraight.png").convert_alpha(),
            "sw":pygame.image.load("resources/images/pipeStraightBlue.png").convert_alpha(),
            "c":pygame.image.load("resources/images/pipeCorner.png").convert_alpha(),
            "cw":pygame.image.load("resources/images/pipeCornerBlue.png").convert_alpha()
            }

        # vignette and grime used as an overlay
        self.vignettes={
            "gr":pygame.transform.scale(pygame.image.load("resources/images/grime.png").convert_alpha(),(self.w,self.h)),
            "vig":pygame.transform.scale(pygame.image.load("resources/images/vignette.png").convert_alpha(),(self.w,self.h))
        }

        # fetch the background image and set paramaters for it
        img=pygame.image.load("resources/images/bg.png").convert_alpha()
        img.set_alpha(20)
        w,h=img.get_size()
        scale=self.h//(h//2)
        self.backgroundImage=pygame.transform.scale(img,(self.w,self.h))

    def initializeMusic(self):
        """ Load the music and start it playing """
        self.music=pygame.mixer.music.load("resources/sounds/music.wav")
        pygame.mixer.music.play(-1,fade_ms=1000) # -1 means that it plays continuously
        self.music_playing=True

    def displaySoundButtons(self):
        """ Displays the sound toggle buttons and the volume sliders """
        
        font=self.getSmallFont()

        # change the text corresponding to whether music is on or off
        x="Start"
        if self.checkMusic():
            x="Stop"

        # create button text
        bt=font.render(f"{x} Music",True,WHITE)
        btw=bt.get_width()+20
        bth=bt.get_height()+5

        # create button border rect
        br=pygame.Rect(
            5,
            self.h-bth-5,
            btw-10,
            bth-5)

        # set text position and draw
        btr=bt.get_rect(center=(btw//2,self.h-bth//2-10))
        self.window.blit(bt,btr)

        # draw button outline
        pygame.draw.rect(self.window,WHITE,br,2)

        # set the music button collider for usage in event loops
        self.stopMusicBtnCollider=br

        # draw the music volume slider
        self.musicVolumeSlider.draw()

        # change the text corresponding to whether the sfx are on or off
        x="Enable"
        if self.sfxEnabled:
            x="Disable"

        # create button text
        bt=font.render(f"{x} sfx",True,WHITE)
        btw=bt.get_width()+20
        bth=bt.get_height()+5

        # create button border rect
        br=pygame.Rect(
            self.w-btw,
            self.h-bth-5,
            btw-10,
            bth-5)

        # set text position and draw
        btr=bt.get_rect(center=(self.w-(btw//2)-5,self.h-bth//2-10))
        self.window.blit(bt,btr)

        # draw button outline
        pygame.draw.rect(self.window,WHITE,br,2)

        # set the sfx button collider for usage in event loops
        self.stopSFXBtnCollider=br

        # draw sfx volume slider
        self.sfxVolumeSlider.draw()

    def setSFXVolume(self,i):
        """ Sets the sound effects volume """

        # the "i" input is between 0 and 100
        # the set_volume argument must be between 0 and 1
        # the code sets it to be between 0 and 0.5
        for x in self.sounds:
            self.sounds[x].set_volume(i/200)
            if x[:8]=="highshot":
                self.sounds[x].set_volume(i/400)

    def checkMusic(self):
        """ Check whether music is playing """
        return self.music_playing

    def toggleMusic(self):
        """ Turn music on or off - used in conjunction with the music toggle button"""
        if self.checkMusic():
            self.stopMusic()
            return
        self.playMusic()

    def toggleSFX(self):
        """ Turn sfx on or off - used in conjunction with the sfx toggle button"""
        self.sfxEnabled=not(self.sfxEnabled)

    def playRandomHighShot(self):
        """ Get a random highshot noise and play it """
        i=random.randint(1,10)
        self.playSound(f"highshot{i}")

    def playMusic(self):
        """ Play the background music until stopped """
        self.music_playing=True
        pygame.mixer.music.play(-1,fade_ms=500)

    def stopMusic(self):
        """ Stop the background music using a fadeout """
        self.music_playing=False
        pygame.mixer.music.fadeout(500)

    def setMusicVolume(self,x):
        """ Set music volume"""
        pygame.mixer.music.set_volume(x/200)

    def playSound(self,sound):
        """ play a sound from self.sounds """
        if self.sfxEnabled:
            try:
                self.sounds[sound].play()
                return True
            except KeyError:
                return False

    def resizeVignettes(self):
        """ Make sure the vignettes cover the screen """
        self.vignettes["gr"]=pygame.transform.scale(self.vignettes["gr"],(self.w,self.h))
        self.vignettes["vig"]=pygame.transform.scale(self.vignettes["vig"],(self.w,self.h))
    
    def getSmallFont(self,relative=True):
        """ Get small font relative to the width of the screen """
        if relative:
            return pygame.font.SysFont("SegoeUI",self.w//64)
        return pygame.font.SysFont("SegoeUI",25)

    def getMediumFont(self,relative=True):
        """ Get medium font relative to the width of the screen """
        if relative:
            return pygame.font.SysFont("SegoeUI",self.w//32)
        return pygame.font.SysFont("SegoeUI",50)

    def getLargeFont(self,relative=True,bold=True):
        """ Get large font relative to the width of the screen """
        f=pygame.font.SysFont("SegoeUI",80)
        if relative:
            f=pygame.font.SysFont("SegoeUI",self.w//18)
        if bold:
            f.set_bold(True)
        return f

    def displayVignette(self,alpha=100):
        """ Overlay the vignettes onto the screen """
        gr=self.vignettes["gr"]
        gr.set_alpha(alpha)
        self.window.blit(gr,(0,0))
        
        vig=self.vignettes["vig"]
        vig.set_alpha(alpha)
        self.window.blit(vig,(0,0))

    def setBackground(self):
        """ Display the gradient and background image. Use this command instead of self.window.fill() """
        self.window.fill(WHITE)
        self.gradient(color1=MEDCYAN,color2=DARKCYAN,target=pygame.Rect(0,0,self.w,self.h))
        self.displayBackgroundImage()

    def displayBackgroundImage(self):
        """ Display the background image """
        self.window.blit(self.backgroundImage,(0,0))

    def gradient(self,color1=(0,0,0),color2=(0,0,0),target=None):
        """ Create a gradient based on arguments """
        colorRect=pygame.Surface((2,2))
        # draw two vertical lines of color onto the surface
        pygame.draw.line(colorRect,color1,(0,0),(0,1))
        pygame.draw.line(colorRect,color2,(1,0),(1,1))
        # blend the colors together in accordance with the target rectangle's dimensions
        colorRect=pygame.transform.smoothscale(colorRect,(target.width,target.height))
        self.window.blit(colorRect,target)


if __name__=="__main__":
    game=Game()
    game.run()
