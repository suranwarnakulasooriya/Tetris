# Tetris
A Python version of Tetris.

## Dependencies
Pygame is the only dependency for this project. To install it, do:
```
pip install pygame
```

## Configuration
There are six parameters that are reasonable to configure. They can be changed in the following lines:
```
07 P = 70 # cell size in pixels
08 input_delay = 10 # delay on keyboard input in milliseconds
09 delay = 50 # constant delay in milliseconds
10 max_grace = 4 # number of grace moves per piece
11 projection = True # whether the ghost piece appears
12 fall_speed = 4 # number of frames between every shape drop
```
Make sure that `high.txt` and `font.ttf` are in the same directory as `tetris.py`.

## Controls
The game is played entirely with the keyboard. Press Q to toggle pause, ESC to exit, and R to restart on game over. use the left and right arrows to move the current shape left or right. Use the up arrow to rotate the shape 90 degrees counterclockwise. Press the down arrow to soft drop and the space bar to hard drop. Press H to swap the current piece.

![tetris](https://user-images.githubusercontent.com/68828123/184267959-a6196e0d-2ec2-4fbe-832e-e63159c56bd7.gif)
