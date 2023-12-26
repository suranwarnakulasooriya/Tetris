# DEPENDENCIES ====================================================================================

from random import randint, choice # to generate random pieces
from copy import deepcopy as copy # to copy a shape to make projection
from os import path # to read high score and font
from datetime import datetime # to manage frame rate
from time import sleep        # ^
import curses # i/o

# CONFIGURATION ===================================================================================

W,H = 10,20 # playfield dimensions
target_fps = 30 # target frames per second
max_grace = 4 # number of grace moves per piece
block_character = '█' # pick from █ , # , ∎ , ■ or others

# CLASSES =========================================================================================

class Shape:
    def __init__(self,pos:(int,int),typ:str,index:int=0):
        self.type = typ # save typestring
        self.mat = shape_types[typ][index] # the matrix that defines the shape
        self.y, self.x = pos
        self.x = min(self.x,W-len(self.mat[0])) # make sure shape is on screen
        self.enabled = True # if the shape can still be changed by the player
        # shapes disable on contact with the heap
        self.grace = max_grace # number of grace movements before shape is added to heap
        self.index = index # index of current rotation starts 0
        self.chambers = shape_types[typ] # list of rotation matrices the shape can have

    def chamber(self,f) -> None: # rotate the shape 90 degrees clockwise
        mat = self.mat; self.index -= 1 # save current matrix and change rotation
        self.mat = self.chambers[self.index % len(self.chambers)] # update matrix with rotation
        if collision(self,f): # reset matrix and rotation if the rotation causes a collision
            self.index += 1; self.mat = mat

    def drop(self,f) -> None: # move one cell down
        self.y += 1
        if collision(self,f.mat) and self.enabled and not self.grace: # if no grace moves left
            f.add_shape(self,(self.x,self.y-1)) # add shape to heap on collision
            self.enabled = False # disable the shape to tell the program to generate a new one
        elif collision(self,f.mat) and self.enabled and self.grace: # reduce grace moves
            self.grace -= 1; self.y -= 1
        elif not collision: # if there is no collision, grace movements reset
            self.grace = max_grace

    def hard_drop(self,f) -> None: # drop until collision
        while not collision(self,f.mat): self.drop(f)

class Heap:
    def __init__(self,w:int,h:int):
        self.mat = [[0]*w for _  in range(h)] # matrix starts as a wxh grid of 0s
        self.w, self.h = w, h # dimensions

    def reset(self) -> None: self.mat = [[0]*self.w for _ in range(self.h)] # reset matrix

    def clear(self,score:int) -> int: # clear filled rows and update score
        for row in range(len(self.mat)): # set filled rows to 0 to represent filled
            if 0 not in self.mat[row]: self.mat[row] = 0 
        while 0 in self.mat: self.mat.remove(0) # remove filled rows
        score += {0:0,1:1,2:3,3:5,4:9}[(self.h-len(self.mat))] # update score
        while len(self.mat) != self.h: self.mat.insert(0,[0]*self.w) # add rows to retain height
        return score

    def add_shape(self,shape:Shape,offset:(int,int)) -> None: # add a shape to the heap
        x,y = offset # coordinates of the shape
        # add all non-0 values from the shape matrix to the heap matrix
        for r in range(len(shape.mat)):
            for c in range(len(shape.mat[0])):
                if shape.mat[r][c]: self.mat[y+r][x+c] = shape.mat[r][c]    

# FUNCTIONS =======================================================================================

def collision(s:Shape,g:Heap) -> bool: # check if two matrices collide
    x, y = s.x, s.y # position of shape
    for r in range(len(s.mat)):
        for c,cell in enumerate(s.mat[r]):
            try: 
                if cell and g[y+r][x+c]: return True # if s matrix and g matrix have a block at x,y
            except IndexError: return True
    return False

typestrings = ['T','S','Z','J','L','I','O']
def new_shape(typ:str=choice(typestrings)) -> Shape: return Shape((0,randint(0,W)),typ) # new shape

def close(high:int,score:int) -> None: # save high score and exit
    stdscr.keypad(0); curses.nocbreak(); curses.endwin() # end curses
    with open(f'{dir}/high.txt','w') as f:
        f.write(str(high)); f.close(); exit(f'GAME ENDED | SCORE: {score}')

def blit_block(scr:curses.window,y:int,x:int,char:int,colors:bool=True) -> None: # draw a block
    try:
        if colors: scr.addstr(y,x,block_character,curses.color_pair(char))
        else:
            if char == 8: scr.addstr(y,x,'•') # ghost
            else: scr.addstr(y,x,block_character) # regular block
    except: pass

def blit_mat(scr:curses.window,mat:list[list[int]],pos:(int,int),colors:bool=True) -> None:
    for r in range(len(mat)): # draw a matrix on a given screen
        for c in range(len(mat[0])):
            if mat[r][c]: blit_block(scr,r+1+pos[0],c+1+pos[1],mat[r][c],colors=colors)

# SETUP ===========================================================================================

if __name__ == '__main__':
    target_frametime = 1/target_fps # target time per frame in seconds
    fall_speed = 6 # number of frames between every shape drop
    tui_color = True # whether the pieces have color or not
    projection = True # whether the ghost piece appears

    # read high score from file
    dir = path.dirname(path.realpath(__file__))
    with open(f'{dir}/high.txt','r') as f: highscore = int(f.read().strip()); f.close()
    score = 0

    W = max(6,W); H = max(20,H) # clamp width and height to minimum dimensions

    step = 0; paused = False; gameover = False

    # matches a typestring to a list of matrices that correspond to the rotations of a shape
    # numbers indicate color, 0 is blank/background
    shape_types = {
        'T':[
        [[6,6,6],
         [0,6,0]],
        [[6,0],  
         [6,6],
         [6,0]],
        [[0,6,0],
         [6,6,6]],
        [[0,6],
         [6,6],
         [0,6]]],
        'S':[
        [[0,3,3],
         [3,3,0]],
        [[3,0],
         [3,3],
         [0,3]]],
        'Z':[
        [[2,2,0],
         [0,2,2]],
        [[0,2],
         [2,2],
         [2,0]]],
        'J':[
        [[5,0,0],
         [5,5,5]],
        [[0,5],
         [0,5],
         [5,5]],
        [[5,5,5],
         [0,0,5]],
        [[5,5],
         [5,0],
         [5,0]]],
        'L':[
        [[0,0,4],
         [4,4,4]],
        [[4,4],
         [0,4],
         [0,4]],
        [[4,4,4],
         [4,0,0]],
        [[4,0],
         [4,0],
         [4,4]]],
        'I':[
        [[7,7,7,7]],
        [[7],
         [7],
         [7],
         [7]]],
        'O':[
        [[4,4],
         [4,4]]]}

    shapes = [new_shape()] # start with one random shape
    nexts = [choice(typestrings),choice(typestrings),choice(typestrings)] # next three shapes
    hold = 0; swapped = False # no held shape; if the current shape has been swapped
    # only one swap is allowed until the current shape is disabled
    heap = Heap(W,max(22,H+2)) # empty playfield

    curses.initscr() # init curses window
    stdscr = curses.newwin(H+4,W+10,0,0) # whole screen
    tetrisscr = stdscr.subwin(H+2,W+2,1,1) # game
    nextscr = stdscr.subwin(10,6,5,W+3) # next pieces
    holdscr = stdscr.subwin(4,6,1,W+3) # hold piece
    scorescr = stdscr.subwin(3,6,15,W+3) # score
    highscr = stdscr.subwin(3,6,18,W+3) # highscore
    fillscr = stdscr.subwin(H-18,6,21,W+3) # empty box to fill screen

    curses.start_color(); curses.use_default_colors() # use ansi colors
    curses.cbreak(); curses.noecho(); curses.curs_set(0) # no echo and hide curser
    stdscr.nodelay(True); stdscr.keypad(True) # nonblocking keyboard input

    for i in range(0,8): # generate ansi colors, i values are used directly in color_pair()
        try: curses.init_pair(i+1,i,-1)
        except curses.ERR: pass

# EVENT LOOP ======================================================================================

while __name__ == '__main__':
    try:
        # reset clock, input, and screen
        dt1 = datetime.now()
        input_char = stdscr.getch()
        stdscr.erase()

        shape = shapes[-1] # currently active shape

        # create ghost shape
        if projection and shape.enabled:
            ghost = copy(shape)
            for r in range(len(ghost.mat)):
                for c in range(len(ghost.mat[0])):
                    if ghost.mat[r][c]: ghost.mat[r][c] = 8
            while not collision(ghost,heap.mat): ghost.y += 1    
            ghost.y -= 1

        # RENDER ==================================================================================

        if projection and not gameover: blit_mat(tetrisscr,ghost.mat,(ghost.y-2,ghost.x),tui_color)
        if hold: blit_mat(holdscr,hold.mat,(0,0),tui_color) # render held piece
        blit_mat(tetrisscr,shape.mat,(shape.y-2,shape.x),tui_color) # render active shape
        blit_mat(tetrisscr,heap.mat[2:],(0,0),tui_color) # render heap
        next_blits = [Shape((0,0),n) for _,n in enumerate(nexts[::-1])] # next shapes to render
        for i,n in enumerate(next_blits): blit_mat(nextscr,n.mat,(3*i,0),tui_color) # next shapes

        stdscr.border(); fillscr.border() # borders of boxes
        tetrisscr.border(); holdscr.border(); scorescr.border(); highscr.border(); nextscr.border()
        holdscr.addstr(0,1,'HOLD'); nextscr.addstr(0,1,'NEXT')
        scorescr.addstr(0,1,'SCOR'); scorescr.addstr(1,1,f'{score:04}')
        highscr.addstr(0,1,'HIGH'); highscr.addstr(1,1,f'{highscore:04}')

        # GAME LOGIC ==============================================================================

        if heap.mat[2] != [0]*W: gameover = True # game ends when top visible row has a block

        if input_char == ord('q'): close(highscore,score) # quit on q
        elif input_char == ord('p') and not gameover: paused ^= 1;  # pause on p
        elif input_char == ord('c'): tui_color ^= 1 # toggle colors on c
        elif input_char == ord('g'): projection ^= 1 # toggle ghost shape on g
        elif input_char == ord('r') and (gameover or paused): # restart on r
            gameover = False; score = 0; hold = 0; swapped = False; paused = False
            heap.reset(); shapes = [new_shape()]; shape = shapes[-1]
            nexts = [choice(typestrings),choice(typestrings),choice(typestrings)]

        if gameover: stdscr.addstr(0,(W+10)//2-6,'R TO RESTART')
        elif paused: stdscr.addstr(0,(W+10)//2-3,'PAUSED')
        else:
            if input_char == curses.KEY_LEFT: # move left
                shape.x -= 1
                if collision(shape,heap.mat): shape.x += 1

            elif input_char == curses.KEY_RIGHT: # move right
                shape.x += 1
                if collision(shape,heap.mat): shape.x -= 1

            # rotate
            elif input_char == curses.KEY_UP : shape.chamber(heap.mat)

            elif input_char == curses.KEY_DOWN: # soft drop
                shape.y += 1
                if collision(shape,heap.mat): shapes[-1].y -= 1

            elif input_char == ord(' ') and shape.y > 1: # hard drop
                y = shape.y; shape.hard_drop(heap)

            elif input_char == ord('h') and not swapped: # hold
                if not hold: # if this is the first held piece, hold it
                    hold = new_shape(shape.type)
                    shapes.pop(); shapes.append(new_shape(nexts[-1]))
                    nexts.pop(-1); nexts.insert(0,choice(typestrings))
                else: # if there is a held piece, swap it with the current one
                    temp = copy(hold)
                    hold = new_shape(shape.type)
                    shapes.pop(); shapes.append(copy(temp))
                    shape = shapes[-1]
                    del temp
                swapped = True

            step += 1   
            if step == fall_speed: shape.drop(heap); step = 0 # drop every fall_speed frames
            shape.x = max(0,min(W-len(shape.mat[0]),shape.x)) # adjust x position of shape
            highscore = max(highscore,score) # set high score

        score = heap.clear(score) # clear filled rows and increase score

        if not shape.enabled: # generate a new shape if the current one is disabled
            shapes.pop(); shapes.append(new_shape(nexts[-1]))
            nexts.pop(-1); nexts.insert(0,choice(typestrings))
            swapped = False;

        # sleep to maintain frame rate
        sleep(max(0,target_frametime-(datetime.now()-dt1).microseconds/1e6))
        stdscr.refresh()

    except KeyboardInterrupt: close(highscore, score) # quit on ^C
