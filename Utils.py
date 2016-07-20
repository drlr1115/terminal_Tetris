#!/usr/bin/python
# Filename: Utils.py

# by Cliff Dong

import random

# Tetromino definition
# * * * *
TETRI0 = (((1,1,1,1),(0,0,0,0)), ((1,0),(1,0),(1,0),(1,0)), \
        ((1,1,1,1),(0,0,0,0)), ((1,0),(1,0),(1,0),(1,0)))
# * *
# * *
TETRI1 = (((1,1),(1,1)), ((1,1),(1,1)), \
        ((1,1),(1,1)), ((1,1),(1,1)))
#   *
# * * *
TETRI2 = (((0,1,0),(1,1,1)), ((1,0),(1,1),(1,0)), \
        ((1,1,1),(0,1,0)), ((0,1),(1,1),(0,1)))
# *
# * * *
TETRI3 = (((1,0,0),(1,1,1)), ((1,1),(1,0),(1,0)), \
        ((1,1,1),(0,0,1)), ((0,1),(0,1),(1,1)))
# * * *
# *
TETRI4 = (((1,1,1),(1,0,0)), ((1,1),(0,1),(0,1)), \
        ((0,0,1),(1,1,1)), ((1,0),(1,0),(1,1)))
# * *
#   * *
TETRI5 = (((1,1,0),(0,1,1)), ((0,1),(1,1),(1,0)), \
        ((1,1,0),(0,1,1)), ((0,1),(1,1),(1,0)))
#   * *
# * *
TETRI6 = (((0,1,1),(1,1,0)), ((1,0),(1,1),(0,1)), \
        ((0,1,1),(1,1,0)), ((1,0),(1,1),(0,1)))

TETRIS = (TETRI0, TETRI1, TETRI2, TETRI3, TETRI4, TETRI5, TETRI6)


# Key mapping
K_W = 119
K_A = 97
K_S = 115
K_D = 100
K_I = 105
K_J = 106
K_K = 107
K_L = 108
K_ESC = 27
K_SPACE = 32
K_P = 112
K_Q = 113
K_MINUS = 45
K_PLUS = 61


# Color
BCOLOR = {  'black'      : 40,
    'red'        : 41,
        'green'      : 42,
            'yellow'     : 43,
            'blue'       : 44,
            'purple'     : 45,
            'cyan'       : 46,
            'white'      : 47,
            }
FCOLOR = {  'black'      : 30,
    'red'        : 31,
        'green'      : 32,
            'yellow'     : 33,
            'blue'       : 34,
            'purple'     : 35,
            'cyan'       : 36,
            'white'      : 37,
            }


def gen_tetri_type():
    return random.randint(0, 6)

def gen_tetri_orient():
    return random.randint(0, 3)

def prt_cell(bcolor, fcolor, axx, axy, pattern):
    print "\33[%d;%dH\33[%s;%sm%s\33[0m" % (axy, axx, BCOLOR[bcolor], \
            FCOLOR[fcolor], pattern)

def clean_cell(caxx, caxy):
    prt_cell('black', 'black', caxx, caxy, '  ')

def hide_cursor():
    print '\33[?25l'

def set_cursor_pos(x, y):
    print "\33[%d;%dH\33[0m" % (x, y)

def resume_cursor():
    print '\33[?25h'


class LockGuard():
    """An auto-release Lock Guard, only support threading.RLock currently"""
    def __init__(self, lock):
        self.lock = lock
        self.lock.acquire()
    def __del__(self):
        self.lock.release()
