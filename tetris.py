import pygame, random
from copy import deepcopy as copy

P = 70
W = 10
H = 22

typestrings = ['T','S','Z','J','L','I','O']

shape_types = {
    'T':
    [[1,1,1],
     [0,1,0]],
    'S':
    [[0,2,2],
     [2,2,0]],
    'Z':
    [[3,3,0],
     [0,3,3]],
    'J':
    [[4,0,0],
     [4,4,4]],
    'L':
    [[0,0,5],
     [5,5,5]],
    'I':
    [[6,6,6,6]],
    'O':
    [[7,7],
     [7,7]]
}

shape_types = {
    'T':
    [[0,0,0],
     [1,1,1],
     [0,1,0]],
    'S':
    [[0,2,2],
     [2,2,0],
     [0,0,0]],
    'Z':
    [[3,3,0],
     [0,3,3],
     [0,0,0]],
    'J':
    [[4,0,0],
     [4,4,4],
     [0,0,0]],
    'L':
    [[0,0,5],
     [5,5,5],
     [0,0,0]],
    'I':
    [[6,6,6,6],
     [0,0,0,0],
     [0,0,0,0],
     [0,0,0,0]],
    'O':
    [[7,7],
     [7,7]]
}

color_lookup = [
    '#282c34',
    '#c678dd',
    '#98c379',
    '#e06c75',
    '#61afef',
    '#d19a66',
    '#56b6c2',
    '#e5c07b',
    '#abb2bf'
]

class Shape:
    def __init__(self,pos:(int,int),typ:str):
        self.mat = shape_types[typ]
        self.y, self.x = pos
        self.x = min(self.x,W-len(self.mat[0]))
        self.enabled = True
        self.grace = 2
    
    #def rotate(self):
    #    return [ [ self.mat[y][x]
	#		for y in range(len(self.mat)) ]
    #        for x in range(len(self.mat[0]) - 1, -1, -1) ]
    
    def rotate(self):
        matrix = self.mat
        n = len(matrix)
        for row in matrix:
            row.reverse()
        for i in range(n):
            for j in range(i):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        return matrix

    def chamber(self) -> None:
        mat = self.mat

    
    def drop(self,f,ghost=False) -> None:
        self.y += 1
        if collision(self,f.mat) and self.enabled and not self.grace:
            #if not ghost:
            f.add_shape(self,(self.x,self.y-1))
            self.enabled = False
        elif collision(self,f.mat) and self.enabled and self.grace:
            self.grace -= 1
            self.y -= 1

    def hard_drop(self,f,ghost=False) -> None:
        y = self.y
        while not collision(self,f.mat):
            self.drop(f,True)
        self.y = y

class Field:
    def __init__(self,w:int,h:int):
        self.mat = [[0]*w for _  in range(h)]
        self.dimens = (w,h)
    def reset(self) -> None:
        self.mat = [[0]*self.dimens[0] for _ in range(self.dimens[1])]
    def clear(self) -> None:
        for row in range(len(self.mat)):
            if 0 not in self.mat[row]:
                self.mat[row] = 0
        
        while 0 in self.mat:
            self.mat.remove(0)

        while len(self.mat) != self.dimens[1]:
            self.mat.insert(0,[0]*self.dimens[0])

    def add_shape(self,shape:Shape,off:(int,int)) -> None:
        x,y = off
        #x = min(W-1,x)
        #if shape.enabled:
        for r in range(len(shape.mat)):
            for c in range(len(shape.mat[0])):
                if shape.mat[r][c]:
                    self.mat[y+r][x+c] = shape.mat[r][c]    

#def clear_board(w,h):
#    return [[0]*w for _ in range(h)]

#def add_shape(g,s,p) -> None:
#    for r in range(len(s)):
#        for c in range(len(s[0])):
#            g[p[0]+r][p[1]+c] = s[r][c]

def draw(g,off,scr,p,shape=False) -> None:
    x, y = off
    for r in range(len(g)):
        for c in range(len(g[0])):
            #if shape and not g[r][c]:
            #    pass
            if g[r][c] or not shape: 
                pygame.draw.rect(scr, color_lookup[g[r][c]], (x+c*p,y+r*p,p,p))
            

def collision(s,g) -> bool:
    x, y = s.x, s.y
    for r in range(len(s.mat)):
        for c,cell in enumerate(s.mat[r]):
            try:
                if cell and g[y+r][x+c]:
                    return True
            except IndexError:
                return True
    return False
                    
def new_shape():
    return Shape((-1,random.randint(0,W)),random.choice(typestrings))