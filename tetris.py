import pygame, random # to run game and generate random pieces
from copy import deepcopy as copy # to copy the content of a piece for the ghost
from os import path

P = 70 # cell size in pixels
W = 10 # playfield width in cells
H = 24 # playfield height in cells
input_delay = 10 # delay on input in milliseconds
delay = 50 # constant delay in milliseconds
max_grace = 4 # number of grace moves
projection = True # whether the ghost piece appears
fall_speed = 4 # number of frames between every shape drop

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
                if shape.mat[r][c]:
                    self.mat[y+r][x+c] = shape.mat[r][c]    

def draw(g,off,scr,p,shape=False) -> None: # draw a matrix with a given offset on the screen
    x, y = off
    for r in range(len(g)):
        for c in range(len(g[0])):
            if g[r][c] or not shape: 
                pygame.draw.rect(scr, color_lookup[g[r][c]], (x+c*p,y+r*p,p,p))
            
def collision(s,g) -> bool: # check of two matrices collide
    x, y = s.x, s.y
    for r in range(len(s.mat)):
        for c,cell in enumerate(s.mat[r]):
            try:
                if cell and g[y+r][x+c]:
                    return True
            except IndexError:
                return True
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
hold = 0
field = Field(W,H)
swapped = False