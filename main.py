from tetris import *

screen = pygame.display.set_mode((P*(W+2),P*(H+2)))
pygame.display.set_caption('Tetris')
field = Field(W,H)
pygame.event.set_blocked(pygame.MOUSEMOTION)

#s = Shape((0,0),random.choice(typestrings))
shapes = [new_shape()]
step = 1

while True:
    screen.fill('#20242d')
    #pygame.draw.rect(screen,color_lookup[0],(P,P,W-P,H-P))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: exit()
    if field.mat[2] != [0]*W: exit()

    
    #if not collision(shapes[-1],field.mat):

    if keys[pygame.K_LEFT]:
        pygame.time.delay(10)
        shapes[-1].x -= 1
        if collision(shapes[-1],field.mat):
            shapes[-1].x += 1
    #shapes[-1].x = max(0,shapes[-1].x)
    if keys[pygame.K_RIGHT]:
        pygame.time.delay(10)
        shapes[-1].x += 1
        if collision(shapes[-1],field.mat):
            shapes[-1].x -= 1
        #shapes[-1].x = max(W-1,shapes[-1].x)
    
    if keys[pygame.K_UP]:
        pygame.time.delay(10)
        #shapes[-1].rotate(shapes[-1].mat)
        #shapes[-1].chamber(field)
        shapes[-1].rotate()
        if collision(shapes[-1],field.mat):
            for _ in range(3):
                shapes[-1].rotate()

    if keys[pygame.K_DOWN]:
        pygame.time.delay(10)
        shapes[-1].y += 1
        if collision(shapes[-1],field.mat):
                shapes[-1].y -= 1

    if keys[pygame.K_SPACE]:
        pygame.time.delay(10)
        shapes[-1].hard_drop(field)

    z = 0
    b = 0
    for r in shapes[-1].mat:
        if r[-1] == 0:
            z += 1

    if z == len(r):
        b = 1
    
    shapes[-1].x = max(0,min(W-len(shapes[-1].mat[0]),shapes[-1].x))
    
    #shapes[-1].hard_drop(field,True)'''
    
    ghost = copy(shapes[-1])
    for r in range(len(ghost.mat)):
        for c in range(len(ghost.mat[0])):
            if ghost.mat[r][c]: ghost.mat[r][c] = 8
    
    while not collision(ghost,field.mat):# or ghost.y+len(ghost.mat) < H-1:
        ghost.y += 1    
    ghost.y -= 1

    #print(shapes[-1].x)

    pygame.time.delay(50)
    
    if step % 2 == 0:
        for s in shapes:
            s.drop(field)    
    
    field.clear()
    
    draw(field.mat,(P,P),screen,P)
    draw(ghost.mat,(P+P*ghost.x,P+P*ghost.y),screen,P,True)

    for s in shapes:
        if s.enabled:
            draw(s.mat,(P+P*s.x,P+P*s.y),screen,P,True)
    
    #print(s.enabled)
    if not shapes[-1].enabled:
        shapes.pop()
        shapes.append(new_shape())

    pygame.draw.rect(screen,'#20242d',(0,0,P*(W+2),P*3))
    pygame.display.update()
    step += 1