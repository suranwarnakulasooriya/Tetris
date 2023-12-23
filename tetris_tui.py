# TODO:
# use block characters instead of # sign
# remove spacing in terminal app
# use switch statements (need python 3.10+)

# DEPENDENCIES ====================================================================================

from random import randint, choice # to generate random pieces
from copy import deepcopy as copy # to copy a shape to make projection
from os import path # to read high score and font
from datetime import datetime # to manage frame rate
from time import sleep        # ^
import curses # display and input

# CONFIGURATION ===================================================================================

W = 10; H = 20 # playfield dimensions
target_fps = 30
max_grace = 4 # number of grace moves per piece
projection = True # whether the ghost piece appears
fall_speed = 6 # number of frames between every shape drop
ui_color = True # whether the pieces have color or not
block_character = '#' # pick from █ , # , ∎ , ■ or others

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
        mat = self.mat
        self.index -= 1 # change rotation
        self.mat = self.chambers[self.index % len(self.chambers)] # update matrix with rotation
        if collision(self,f): # reset matrix and rotation if the rotation causes a collision
            self.index += 1; self.mat = mat

    def drop(self,f) -> None: # move one cell down
        self.y += 1
        if collision(self,f.mat) and self.enabled and not self.grace: # if no grace moves left
            f.add_shape(self,(self.x,self.y-1)) # add shape to heap on coliision
            self.enabled = False # disable the shape to tell the program to generate a new one
        elif collision(self,f.mat) and self.enabled and self.grace: # reduce grace moves
            self.grace -= 1; self.y -= 1
        elif not collision: # if there is no collision, grace movements reset
            self.grace = max_grace

    def hard_drop(self,f) -> None: # drop until collision
        while not collision(self,f.mat): self.drop(f)

class Field:
    def __init__(self,w:int,h:int):
        self.mat = [[0]*w for _  in range(h)] # matrix starts as a wxh grid of 0s
        self.w, self.h = w, h

    def reset(self) -> None: # reset matrix
        self.mat = [[0]*self.w for _ in range(self.h)]

    def clear(self,score:int) -> int: # clear filled rows
        for row in range(len(self.mat)): # set filled rows to 0 to represent filled
            if 0 not in self.mat[row]: self.mat[row] = 0 
        while 0 in self.mat: self.mat.remove(0) # remove filled rows
        score += {0:0,1:1,2:3,3:5,4:8}[(self.h-len(self.mat))]
        while len(self.mat) != self.h: self.mat.insert(0,[0]*self.w) # add rows to retain height
        return score

    def add_shape(self,shape:Shape,offset:(int,int)) -> None: # add a shape to the heap
        x,y = offset # coordinates of the shape
        # add all non-0 values from the shape matrix to the field matrix
        for r in range(len(shape.mat)):
            for c in range(len(shape.mat[0])):
                if shape.mat[r][c]: self.mat[y+r][x+c] = shape.mat[r][c]    

# FUNCTIONS =======================================================================================

def collision(s,g) -> bool: # check if two matrices collide
    x, y = s.x, s.y
    for r in range(len(s.mat)):
        for c,cell in enumerate(s.mat[r]):
            try: 
                if cell and g[y+r][x+c]: return True
            except IndexError: return True
    return False

typestrings = ['T','S','Z','J','L','I','O']
def new_shape(typ=choice(typestrings)): # generate a new random shape
    return Shape((0,randint(0,W)),typ)

def close(high:int,score:int) -> None: # save high score and exit
    stdscr.keypad(0)
    curses.nocbreak()
    curses.endwin()
    with open(f'{dir}/high.txt','w') as f:
        f.write(str(high)); f.close(); exit(f'GAME ENDED | SCORE: {score}')

def add_mat(cli,g,offset:(int,int),colors=True,ghost=False) -> None: # add a matrix to the cli
    x, y = offset
    # add a matrix with a given offset to the screen
    for r in range(len(g)):
        for c in range(len(g[0])):
            if g[r][c]: cli[r+y][c+x] = g[r][c]

def blit(char,colors=True): # draw a single block
    if colors: stdscr.addstr(block_character,curses.color_pair(color_lookup[char]))
    else:
        if char == 8: stdscr.addstr('•')
        else: stdscr.addstr(block_character)

def sidebar_blit(piece,row,offset:int=2,colors=True): # blit a shape to the sidebar
    try: # print each row of the matrix
        for cell in piece.mat[row-offset]:
            if cell: blit(cell,colors=ui_color)
            else: stdscr.addstr(' ')
        stdscr.addstr(' '*(4-len(piece.mat[row-offset]))+'│')
    except IndexError: stdscr.addstr('    │')

# SETUP ===========================================================================================

if __name__ == '__main__':
    target_frametime = 1/target_fps # target time per frame in seconds
    cli = [[' ']* W for _ in range(H)] # list of strs to display the gameq in terminal

    # read high score from file
    dir = path.dirname(path.realpath(__file__))
    with open(f'{dir}/high.txt','r') as f: highscore = f.read(); f.close()
    highscore.strip(); highscore = int(highscore)
    score = 0

    W = max(6,W); H = max(22,H+2) # clamp width and height to minimum dimensions

    step = 0; paused = False; gameover = False

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

    color_lookup = [ # map numbers from shape_types = curses.color_pair() values
        1,   # black
        136, # magenta
        43,  # green
        197, # red
        40,  # blue
        209, # orange
        52,  # cyan
        215, # yellow
        9]   # white

    shapes = [new_shape()] # start with one random shape
    # generate the next three random shapes
    nexts = [choice(typestrings),choice(typestrings),choice(typestrings)]
    hold = 0 # the currently held shape is null
    field = Field(W,H) # create the playfield
    swapped = False # whether the current shape has been swapped with the held shape, starts False
    # only one swap is allowed until the current shape is disabled

    # initialize curses window and colors
    stdscr = curses.initscr()
    curses.start_color(); curses.use_default_colors()
    curses.cbreak(); curses.noecho()
    stdscr.nodelay(True) # make curses.getch() nonblocking
    stdscr.keypad(True) # accept keypad escape sequences

    # generate 256 colors, the i values are used by color_lookup
    for i in range(0,curses.COLORS):
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
            while not collision(ghost,field.mat): ghost.y += 1    
            ghost.y -= 1

        next_blits = [Shape((0,0),n) for _,n in enumerate(nexts[::-1])] # next shapes to render

        # RENDER ==================================================================================

        cli = [[' ']* W for _ in range(H)] # game board cli
        add_mat(cli,field.mat,(0,0),colors=ui_color) # add playfield matrix to xli
        if projection and shape.enabled and not gameover: # add ghost shape
            add_mat(cli,ghost.mat,(ghost.x,ghost.y),colors=ui_color,ghost=True)
        if not gameover: # add active shape
            add_mat(cli,shape.mat,(shape.x,shape.y),colors=ui_color)

        # header text
        if gameover:
            stdscr.addstr('╭'+ '─'*((W+8-12)//2) + 'R TO RESTART' + '─'*((W+8-12)//2+W%2) + '╮\n')
        elif paused: stdscr.addstr('╭'+ '─'*((W+8-6)//2) + 'PAUSED' + '─'*((W+8-6)//2+W%2) + '╮\n')
        else: stdscr.addstr('╭'+ '─'*(W+8) + '╮\n')

        stdscr.addstr('│╭' + '─'*((W-6)//2) + 'TETRIS' + '─'*(((W-6)//2)+W%2) + '╮╭HOLD╮│\n')

        # rest of the game board
        for row in range(2,len(cli)):

            # playfield
            stdscr.addstr('││')
            for char in cli[row]:
                if char == ' ': stdscr.addstr(' ')
                else: blit(char,colors=ui_color)

            stdscr.addstr('│')
            
            # held piece ui
            if 2 <= row <= 3: # the held piece is shown in rows 2 and 3
                stdscr.addstr('│')
                if hold: sidebar_blit(hold,row,colors=ui_color)
                else: stdscr.addstr('    │')
            
            # next pieces ui 
            elif row == 5: stdscr.addstr('╭NEXT╮')
            elif row in [6,7, 9,10, 12,13]: # rows for the next pieces
                stdscr.addstr('│')
                if 6 <= row <= 7: sidebar_blit(next_blits[0],row,6,colors=ui_color)
                elif 9 <= row <= 10: sidebar_blit(next_blits[1],row,9,colors=ui_color)
                elif 12 <= row <= 13: sidebar_blit(next_blits[2],row,12,colors=ui_color)
            
            # score and highs core
            elif row == 15: stdscr.addstr('╭SCOR╮')
            elif row == 16: stdscr.addstr(f'│{score:04}│')
            elif row == 18: stdscr.addstr('╭HIGH╮')
            elif row == 19: stdscr.addstr(f'│{highscore:04}│')

            # empty box to fill up height
            elif row == 21: stdscr.addstr('╭────╮')
            elif row > 21 and row != H: stdscr.addstr('│    │')

            # sides and bottoms of sidebar panels
            elif row in [8,11]: stdscr.addstr('│    │')
            elif row in [4,14,17,20]: stdscr.addstr('╰────╯')

            stdscr.addstr('│\n') # next line

        # bottom of screen
        stdscr.addstr('│╰'+'─'*W+'╯╰────╯│\n'); stdscr.addstr('╰'+ '─'*(W+8) + '╯\n')

        # GAME LOGIC ==============================================================================

        if field.mat[2] != [0]*W: gameover = True # game ends when top visible row has a block

        # quit with q or ESC
        if input_char == ord('q'): close(highscore,score)
        
        # pause on p
        if input_char == ord('p') and not gameover: paused ^= 1; #pygame.time.delay(20)

        # restart on r
        if input_char == ord('r') and gameover:
            gameover = False; score = 0; hold = 0; swapped = False
            field.reset(); shapes = [new_shape()]
            nexts = [choice(typestrings),choice(typestrings),choice(typestrings)]

        if not paused and not gameover:
            if input_char == curses.KEY_LEFT: # move left
                shape.x -= 1
                if collision(shape,field.mat): shape.x += 1

            elif input_char == curses.KEY_RIGHT: # move right
                shape.x += 1
                if collision(shape,field.mat): shape.x -= 1
            
            # rotate
            elif input_char == curses.KEY_UP : shape.chamber(field.mat)

            elif input_char == curses.KEY_DOWN: # soft drop
                shape.y += 1
                if collision(shape,field.mat): shapes[-1].y -= 1
            
            elif input_char == ord(' ') and shape.y > 1: # hard drop
                y = shape.y; shape.hard_drop(field)

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
            if step == fall_speed: shape.drop(field); step = 0 # drop every fall_speed frames 

            shape.x = max(0,min(W-len(shape.mat[0]),shape.x)) # adjust x position of shape
            highscore = max(highscore,score) # set high score

        score = field.clear(score) # clear filled rows and increase score

        if not shape.enabled: # generate a new shape if the current one is disabled
            shapes.pop(); shapes.append(new_shape(nexts[-1]))
            nexts.pop(-1); nexts.insert(0,choice(typestrings))
            swapped = False; #score += 1

        # sleep to maintain frame rate
        sleep(max(0,target_frametime-(datetime.now()-dt1).microseconds/1e6))
        stdscr.refresh()

    except KeyboardInterrupt: close(highscore, score); exit(f'GAME ENDED | SCORE: {score}')
