# Tetris
A Python version of Tetris.

## Dependencies
Pygame and curses are the only dependencies for this project. To install them, do:
```
pip install pygame # for tetris.py
pip install curses # for tetris_tui.py
```

## Pygame Configuration
There are six parameters that are reasonable to configure in `tetris.py`. They can be changed in the following lines:
```
08 P = 30 # cell size in pixels
09 target_fps = 30
10 max_grace = 4 # number of grace moves per piece
11 projection = True # whether the ghost piece appears
12 fall_speed = 6 # number of frames between every shape drop
```
Make sure that `high.txt` and `font.ttf` are in the same directory as `tetris.py`. `font.ttf` is only used by `tetris.py`.

## TUI Configuration
`tetris_tui.py` can be configured in the following lines:
```
17 W = 10; H = 20 # playfield dimensions
18 target_fps = 30
19 max_grace = 4 # number of grace moves per piece
20 projection = True # whether the ghost piece appears
21 fall_speed = 6 # number of frames between every shape drop
22 ui_color = True # whether the pieces have color or not
23 block_character = '#' # pick from █ , # , ∎ , ■ or others
```

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
