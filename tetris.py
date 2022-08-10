import pygame, random # to run game and generate random pieces
from copy import deepcopy as copy # to copy the content of a piece for the ghost
from os import path # to read highscore and font

# ================================================================================

P = 70 # cell size in pixels
input_delay = 10 # delay on keyboard input in milliseconds
delay = 50 # constant delay in milliseconds
max_grace = 4 # number of grace moves per piece
projection = True # whether the ghost piece appears
fall_speed = 4 # number of frames between every shape drop

# ================================================================================

W = 10 # playfield width in cells
H = 24 # playfield height in cells

dir = path.dirname(path.realpath(__file__))
with open(f'{dir}/high.txt','r') as f:
    highscore = f.read()
    f.close()
highscore.strip()
highscore = int(highscore)
score = 0

step = 1
paused = False
gameover = False

typestrings = ['T','S','Z','J','L','I','O']

# matches a typestring to a list of matrices that correspond to the rotations of a shape
# numbers indicate color, 0 is blank/background
shape_types = {
    'T':
    [[[1,1,1],
      [0,1,0]],
     [[1,0],
      [1,1],
      [1,0]],
     [[0,1,0],
      [1,1,1]],
     [[0,1],
      [1,1],
      [0,1]]],
    'S':
    [[[0,2,2],
      [2,2,0]],
     [[2,0],
      [2,2],
      [0,2]]],
    'Z':
    [[[3,3,0],
      [0,3,3]],
     [[0,3],
      [3,3],
      [3,0]]],
    'J':
    [[[4,0,0],
      [4,4,4]],
     [[0,4],
      [0,4],
      [4,4]],
     [[4,4,4],
      [0,0,4]],
     [[4,4],
      [4,0],
      [4,0]]],
    'L':
    [[[0,0,5],
      [5,5,5]],
     [[5,5],
      [0,5],
      [0,5]],
     [[5,5,5],
      [5,0,0]],
     [[5,0],
      [5,0],
      [5,5]]],
    'I':
    [[[6,6,6,6]],
     [[6],
      [6],
      [6],
      [6]]],
    'O':
    [[[7,7],
      [7,7]]]}

colors_classic = [
    '#282c34',
    '#c678dd',
    '#98c379',
    '#e06c75',
    '#61afef',
    '#d19a66',
    '#56b6c2',
    '#e5c07b',
    '#abb2bf',
    '#20242d']

colors_web = [
    '#f4f4f2',
    '#9b51e0',
    '#9b51e0',
    '#9b51e0',
    '#9b51e0',
    '#9b51e0',
    '#9b51e0',
    '#9b51e0',
    '#1a1a1a',
    '#f4f4f2']

color_lookup = colors_classic

class Shape:
    def __init__(self,pos:(int,int),typ:str,index:int=0):
        self.type = typ # save typestring
        self.mat = shape_types[typ][index] # the matrix that defines the shape
        self.y, self.x = pos
        self.x = min(self.x,W-len(self.mat[0])) # make sure shape is on screen
        self.enabled = True # if the shape can still be changed by the player
        self.grace = max_grace # number of grace movements before shape is added to heap
        self.index = index # index of current rotation starts 0
        self.chambers = shape_types[typ] # list of rotations the shape can have

    def chamber(self,f) -> None: # rotate the shape 90 degrees counterclockwise
        mat = self.mat
        self.index += 1 # change rotation
        self.mat = self.chambers[self.index % len(self.chambers)] # change matrix according to rotation
        if collision(self,f): # reset matrix and rotation if the rotation causes a collision
            self.index -= 1
            self.mat = mat

    def drop(self,f) -> None: # move one cell down
        self.y += 1
        if collision(self,f.mat) and self.enabled and not self.grace: # if no grace moves left on collision, add shape to heap
            f.add_shape(self,(self.x,self.y-1))
            self.enabled = False # disable the shape to tell the program to generate a new one
        elif collision(self,f.mat) and self.enabled and self.grace: # on collision, reduce grace moves
            self.grace -= 1
            self.y -= 1
        elif not collision: # if there is no collision, grace movements reset
            self.grace = max_grace

    def hard_drop(self,f) -> None: # drop until collision
        while not collision(self,f.mat):
            self.drop(f)

class Field:
    def __init__(self,w:int,h:int):
        self.mat = [[0]*w for _  in range(h)] # matrix starts as a wxh grid of 0s
        self.dimens = (w,h)

    def reset(self) -> None: # reset matrix
        self.mat = [[0]*self.dimens[0] for _ in range(self.dimens[1])]

    def clear(self,score:int) -> int: # clear filled rows
        for row in range(len(self.mat)): # set filled rows to 0
            if 0 not in self.mat[row]:
                self.mat[row] = 0
        while 0 in self.mat: # remove all rows that are 0
            self.mat.remove(0)
        score += 50*(self.dimens[1]-len(self.mat))
        while len(self.mat) != self.dimens[1]: # add empty rows on top to maintain height
            self.mat.insert(0,[0]*self.dimens[0])
        return score

    def add_shape(self,shape:Shape,off:(int,int)) -> None: # add a shape to the heap
        x,y = off
        for r in range(len(shape.mat)): # add all non-0 values from the shape matrix to the field matrix
            for c in range(len(shape.mat[0])):
                if shape.mat[r][c]: self.mat[y+r][x+c] = shape.mat[r][c]    

def draw(g,off,scr,p,shape=False) -> None: # draw a matrix with a given offset on the screen
    x, y = off
    for r in range(len(g)):
        for c in range(len(g[0])):
            if g[r][c] or not shape:  pygame.draw.rect(scr, color_lookup[g[r][c]], (x+c*p,y+r*p,p,p))
            
def collision(s,g) -> bool: # check of two matrices collide
    x, y = s.x, s.y
    for r in range(len(s.mat)):
        for c,cell in enumerate(s.mat[r]):
            try:
                if cell and g[y+r][x+c]: return True
            except IndexError: return True
    return False
                    
def new_shape(typ=None): # generate a new shape
    if typ == None:
        typ = random.choice(typestrings)
    return Shape((-1,random.randint(0,W)),typ)

def close(high) -> None: # save highscore and exit
    with open(f'{dir}/high.txt','w') as f:
        f.write(str(high))
        f.close()
    exit()

shapes = [new_shape()] # start with one random shape
nexts = [random.choice(typestrings),random.choice(typestrings),random.choice(typestrings)]
hold = 0 # the currently held shape is null
field = Field(W,H) # create the playfield
swapped = False # whether the current shape has been swapped with the held shape, starts False

# initialize pygame window and font
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((P*(W+5),P*(H+2)))
pygame.display.set_caption('Tetris')
font = pygame.font.Font(f'{dir}/font.ttf',P//2)
pygame.event.set_blocked(pygame.MOUSEMOTION) # block mouse movement

# restart prompt
rs = font.render('press R to restart',True,color_lookup[8])
rrs = rs.get_rect()
rrs.topleft = (P,P//2)

# hold text
ho = font.render('hold',True,color_lookup[8])
hor = ho.get_rect()
hor.topleft = (P*(W+2),P//2)

# next text
ne = font.render('next',True,color_lookup[8])
ner = ho.get_rect()
ner.topleft = (P*(W+2),P*3)

while __name__ == '__main__': # event loop
    screen.fill(color_lookup[9])
    shape = shapes[-1] # currently active shape

    # exit scenarios
    for event in pygame.event.get():
        if event.type == pygame.QUIT: close(highscore)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: close(highscore)
    
    if field.mat[2] != [0]*W: gameover = True # game ends when top visible has a block

    # react to input
    if keys[pygame.K_q] and not gameover: # pause
        pygame.time.delay(input_delay)
        paused = not paused

    if keys[pygame.K_r] and gameover: # restart
        gameover = False
        field.reset()
        shapes = [new_shape()]
        score = 0
        hold = 0
        nexts = [random.choice(typestrings),random.choice(typestrings),random.choice(typestrings)]
        swapped = False

    if not paused and not gameover:
        if keys[pygame.K_LEFT]: # move left
            pygame.time.delay(input_delay)
            shape.x -= 1
            if collision(shape,field.mat): shape.x += 1

        elif keys[pygame.K_RIGHT]: # move right
            pygame.time.delay(input_delay)
            shape.x += 1
            if collision(shape,field.mat): shape.x -= 1
        
        elif keys[pygame.K_UP]: # rotate
            pygame.time.delay(input_delay)
            shape.chamber(field.mat)

        elif keys[pygame.K_DOWN]: # soft drop
            pygame.time.delay(input_delay)
            shape.y += 1
            score += 1
            if collision(shape,field.mat):
                shapes[-1].y -= 1
                score -= 1

        elif keys[pygame.K_SPACE] and shape.y > 1: # hard drop
            pygame.time.delay(input_delay)
            y = shape.y
            shape.hard_drop(field)
            score += 2*(shape.y-y)

        elif keys[pygame.K_h] and not swapped: # hold
            pygame.time.delay(input_delay*2)
            if not hold:
                hold = new_shape(shape.type)
                shapes.pop()
                shapes.append(new_shape(nexts[-1]))
                nexts.pop(-1)
                nexts.insert(0,random.choice(typestrings))
            else:
                temp = copy(hold)
                hold = new_shape(shape.type)
                shapes.pop()
                shapes.append(copy(temp))
                shape = shapes[-1]
                del temp
            swapped = True

        step += 1   
        if step % fall_speed == 0: shape.drop(field)# shape drops every fall_speed frames 
    
        shape.x = max(0,min(W-len(shape.mat[0]),shapes[-1].x)) # adjust x position of shape
        highscore = max(highscore,score)
    
    score = field.clear(score) # clear filled rows and increase score
    draw(field.mat,(P,P),screen,P) # draw field

    # project shape
    if projection and shape.enabled:
        ghost = copy(shape)
        for r in range(len(ghost.mat)):
            for c in range(len(ghost.mat[0])):
                if ghost.mat[r][c]: ghost.mat[r][c] = 8
        while not collision(ghost,field.mat): ghost.y += 1    
        ghost.y -= 1
        draw(ghost.mat,(P+P*ghost.x,P+P*ghost.y),screen,P,True)

    # draw current shape
    if shapes[-1].enabled: draw(shapes[-1].mat,(P+P*shapes[-1].x,P+P*shapes[-1].y),screen,P,True)

    if not shape.enabled: # generate a new shape if the current one is disabled
        shapes.pop()
        shapes.append(new_shape(nexts[-1]))
        nexts.pop(-1)
        nexts.insert(0,random.choice(typestrings))
        swapped = False

    pygame.draw.rect(screen,color_lookup[9],(0,0,P*(W+2),P*3)) # hud background

    # render score and highscore
    sc = font.render(f'score:{score:04}',True,color_lookup[8])
    rsc = sc.get_rect()
    rsc.topleft = (P,P//2)
    if not gameover: screen.blit(sc,rsc)
    hs = font.render(f'high :{highscore:04}',True,color_lookup[8])
    rhs = hs.get_rect()
    rhs.topleft = (P,P+P//2)
    screen.blit(hs,rhs)

    if gameover: screen.blit(rs,rrs) # render restart prompt if needed
    
    # display hold and next text
    screen.blit(ho,hor)
    screen.blit(ne,ner)

    for i,n in enumerate(nexts[::-1]): # draw next shapes
        s = Shape((0,0),n)
        draw(s.mat,((W+2)*P,2*(i+2)*P),screen,P//2,True)

    if hold: draw(hold.mat,((W+2)*P,P*3//2),screen,P//2,True) # draw held shape
    
    pygame.time.delay(delay)
    pygame.display.update()