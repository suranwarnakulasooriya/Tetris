from tetris import *

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((P*(W+2),P*(H+2)))
pygame.display.set_caption('Tetris')
font = pygame.font.Font(f'{dir}/font.ttf',P//2)
pygame.event.set_blocked(pygame.MOUSEMOTION) # block mouse movement

rs = font.render('press R to restart',True,color_lookup[8])
rrs = rs.get_rect()
rrs.topleft = (P,P//2)

while True:
    #screen.fill('#20242d')
    screen.fill(color_lookup[9])
    shape = shapes[-1] # currently active shape

    # exit scenarios
    for event in pygame.event.get():
        if event.type == pygame.QUIT: close(highscore)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: close(highscore)
    
    if field.mat[2] != [0]*W: # game ends when top visible has a block
        gameover = True

    # react to input
    if keys[pygame.K_q] and not gameover: # pause
        pygame.time.delay(input_delay)
        paused = not paused

    if keys[pygame.K_r] and gameover: # restart
        gameover = False
        field.reset()
        shapes = [new_shape()]
        score = 0

    if not paused and not gameover:
        if keys[pygame.K_LEFT]: # move left
            pygame.time.delay(input_delay)
            shape.x -= 1
            if collision(shape,field.mat):
                shapes[-1].x += 1

        elif keys[pygame.K_RIGHT]: # move right
            pygame.time.delay(input_delay)
            shape.x += 1
            if collision(shape,field.mat):
                shape.x -= 1
        
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
            y = shape.y
            pygame.time.delay(input_delay)
            shape.hard_drop(field)
            score += 2*(shape.y-y)

        step += 1   
        if step % fall_speed == 0: # shape drops every fall_speed frames
            for s in shapes:
                s.drop(field)    
    
        shape.x = max(0,min(W-len(shape.mat[0]),shapes[-1].x)) # adjust x position of shape
        highscore = max(highscore,score)
    
    score = field.clear(score) # clear filled rows and increase score
    draw(field.mat,(P,P),screen,P) # draw field

    # project shape
    if projection:
        ghost = copy(shape)
        for r in range(len(ghost.mat)):
            for c in range(len(ghost.mat[0])):
                if ghost.mat[r][c]: ghost.mat[r][c] = 8
        while not collision(ghost,field.mat):
            ghost.y += 1    
        ghost.y -= 1
        draw(ghost.mat,(P+P*ghost.x,P+P*ghost.y),screen,P,True)

    for s in shapes: # draw current hape
        if s.enabled:
            draw(s.mat,(P+P*s.x,P+P*s.y),screen,P,True)

    if not shape.enabled: # generate a new shape if the current one is disabled
        shapes.pop()
        shapes.append(new_shape())

    pygame.draw.rect(screen,color_lookup[9],(0,0,P*(W+2),P*3)) # hud background

    # render score and highscore
    sc = font.render(f'score:{score:06}',True,color_lookup[8])
    rsc = sc.get_rect()
    rsc.topleft = (P,P//2)
    if not gameover: screen.blit(sc,rsc)
    hs = font.render(f'high :{highscore:06}',True,color_lookup[8])
    rhs = hs.get_rect()
    rhs.topleft = (P,P+P//2)
    screen.blit(hs,rhs)

    if gameover: screen.blit(rs,rrs) # render restard prompt if needed
    
    pygame.time.delay(delay)
    pygame.display.update()