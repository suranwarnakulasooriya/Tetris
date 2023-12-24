# Tetris
A Python version of Tetris ran in the terminal using curses.

## Dependencies
Curses is the only dependency. To install it, do:
```
pip install curses
```

## Configuration
`tetris_tui.py` can be configured in the following lines:
```
12 W,H = 10,20 # playfield dimensions
13 target_fps = 30 # target frames per second
14 max_grace = 4 # number of grace moves per piece
15 projection = True # whether the ghost piece appears
16 fall_speed = 6 # number of frames between every shape drop
17 ui_color = True # whether the pieces have color or not
18 block_character = '█' # pick from █ , # , ∎ , ■ or others
```
Make sure that `high.txt` is in the same directory as the python file.

## Controls
|Key|Action|
|---|------|
|q|exit|
|p|pause|
|r|restart|
|left|move left|
|right|move right|
|up|rotate|
|down|soft drop|
|space|hard drop|
|h|hold/swap|

![tetris](https://user-images.githubusercontent.com/68828123/184267959-a6196e0d-2ec2-4fbe-832e-e63159c56bd7.gif)
