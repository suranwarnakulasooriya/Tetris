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
08 P = 30 # cell size in pixels
09 target_fps = 30
10 max_grace = 4 # number of grace moves per piece
11 projection = True # whether the ghost piece appears
12 fall_speed = 4 # number of frames between every shape drop
```
Make sure that `high.txt` and `font.ttf` are in the same directory as `tetris.py`.

## Controls
|Key|Action|
|---|------|
|q|pause|
|esc|exit|
|r|restart|
|left|move left|
|right|move right|
|up|rotate|
|down|soft drop|
|space|hard drop|
|h|hold/swap|

![tetris](https://user-images.githubusercontent.com/68828123/184267959-a6196e0d-2ec2-4fbe-832e-e63159c56bd7.gif)
