# Tetris
A Python version of Tetris that runs in the terminal using curses.

## Dependencies
Curses is the only dependency. To install it, do:
```
pip install curses
```

## Configuration
The dimensions of the playfield, frame rate, number of grace moves, and block character can be changed in the following lines:
```
12 W,H = 10,20 # playfield dimensions
13 target_fps = 30 # target frames per second
14 max_grace = 4 # number of grace moves per piece
15 block_character = '█' # pick from █ , # , ∎ , ■ or others
```
Make sure that `high.txt` is in the same directory as `tetris.py`.

## Controls
|Key|Action|
|---|------|
|q|exit|
|p|pause|
|r|restart (also works on pause)|
|c|toggle colors|
|g|toggle ghost piece|
|left|move left|
|right|move right|
|up|rotate|
|down|soft drop|
|space|hard drop|
|h|hold/swap|
