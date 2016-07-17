#!/usr/bin/python
# Filename: Tetris.py

# by Cliff Dong

import random
import sys
import time
import termios
import threading

# globle parameter
STAGE_WIDTH = 10
STAGE_HEIGHT = 20
SCREEN_POS = [9, 10]
NEXT_DISP_POS_X = SCREEN_POS[0] + STAGE_WIDTH + 4
NEXT_DISP_POS_Y = SCREEN_POS[1] + 2

START_POS_X = STAGE_WIDTH/2 - 1
START_POS_Y = 0

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

# Tetromino
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
CELL_PATTERN = '[]'

# Key
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
K_Q = 113
K_MINUS = 45
K_PLUS = 61

# RLock
mylock = threading.RLock()

def gen_tetri_type():
    return random.randint(0, 6)

def gen_tetri_orient():
    return random.randint(0, 3)

def prt_cell(bcolor, fcolor, axx, axy, pattern):
    print "\33[%d;%dH\33[%s;%sm%s\33[0m" % (axy, axx, BCOLOR[bcolor], \
            FCOLOR[fcolor], pattern)

def clean_cell(caxx, caxy):
    prt_cell('black', 'black', caxx, caxy, '  ')

def usage():
    print 'Usage: Tetris\n\
Options:\n \
  -h, --help            show this help message\n\
Operating Instructions:\n \
  KEY             ACTION\n \
  w/i     --      ROTATE\n \
  s/k     --      DOWN\n \
  a/j     --      LEFT\n \
  d/l     --      RIGHT\n \
  SPACE   --      DROP\n \
  +       --      LEVEL UP\n \
  -       --      LEVEL DOWN\n \
  q/ESC   --      QUIT\n\n \
  Enjoy :)\n\n'

class Tetris:
    def __init__(self):
        self.stage = []
        self.orient = 0
        self.type = 0
        self.pos_x = 0
        self.pos_y = 0
        self.next_orient = 0
        self.next_type = 0
        self.next_pos_x = 0
        self.next_pos_y = 0
        self.score = 0
        self.level = 1
        self.delay = 1
        
        self.prepare_stage()
        
    def prepare_stage(self):
        self.prt_border()
        self.init_stage(STAGE_WIDTH,STAGE_HEIGHT)
        self.set_next()
        self.set_current()
        self.set_next()
        self.prt_statusbar()

    def init_stage(self, width, height):
        single_line = []
        for count in range(0, width):
            single_line.append(0)
        for count in range(0, height):
            self.stage.append(single_line[:])

    def prt_border(self):
        # clean screen
        print "\33[2J\33[0m"
        # top
        for count in range(SCREEN_POS[0]*2, (SCREEN_POS[0]+STAGE_WIDTH+2)*2):
            prt_cell('cyan', 'white',count ,SCREEN_POS[1], '-')
        # bottom
        for count in range(SCREEN_POS[0]*2, (SCREEN_POS[0]+STAGE_WIDTH+2)*2):
            prt_cell('cyan', 'white',count ,SCREEN_POS[1]+STAGE_HEIGHT+1, '-')
        # left
        for count in range(SCREEN_POS[1], SCREEN_POS[1]+STAGE_HEIGHT+2):
            prt_cell('cyan', 'white',SCREEN_POS[0]*2 ,count , '||') 
        # right
        for count in range(SCREEN_POS[1], SCREEN_POS[1]+STAGE_HEIGHT+2):
            prt_cell('cyan', 'white',(SCREEN_POS[0]+STAGE_WIDTH+1)*2 ,count , '||')

    def prt_statusbar(self):
        status_bar_x = NEXT_DISP_POS_X
        status_bar_y = NEXT_DISP_POS_Y + 5
        # clean previous StatusBar
        for sby in range(SCREEN_POS[1], SCREEN_POS[1]+STAGE_HEIGHT+2):
            for sbx in range(status_bar_x, status_bar_x+6):
                clean_cell(sbx*2, sby)
        # now print it
        self.prt_next()
        prt_cell('black', 'cyan', status_bar_x*2, status_bar_y, 'Score')
        prt_cell('black', 'white', status_bar_x*2, status_bar_y+1, self.score)
        prt_cell('black', 'cyan', status_bar_x*2, status_bar_y+3, 'Level')
        prt_cell('black', 'white', status_bar_x*2, status_bar_y+4, self.level)

    def prt_stage(self):
        for county in range(0, STAGE_HEIGHT):
            for countx in range(0, STAGE_WIDTH):
                if self.stage[county][countx] > 0:
                    prt_cell('white', 'black', (countx+SCREEN_POS[0]+1)*2, \
                            county+SCREEN_POS[1]+1, '[]')
                else:
                    clean_cell((countx+SCREEN_POS[0]+1)*2, county+SCREEN_POS[1]+1)

    def clean_stage(self):
        for county in range(SCREEN_POS[1]+1, SCREEN_POS[1]+STAGE_HEIGHT+1):
            for countx in range(SCREEN_POS[0]+1, SCREEN_POS[0]+STAGE_WIDTH+1):
                clean_cell(countx*2, county)

    def purge_line(self):
        blank_line = []
        for count in range(0, STAGE_WIDTH):
            blank_line.append(0)
        linecount = STAGE_HEIGHT - 1 
        countsum = 0 
        while linecount >= 0:
            if self.stage[linecount].count(1) == STAGE_WIDTH:
                # found a full line, we move the upper lines down
                countsum += 1
                upperline = linecount
                while  upperline > 0:
                    self.stage[upperline] = self.stage[upperline-1][:]
                    upperline -= 1
                self.stage[0] = blank_line[:]
            else:
                linecount -= 1
        return countsum

    def update_score(self, lines):
        if lines > 0:
            self.score += 2 ** lines - 1
            time.sleep(0.5)
            self.prt_stage()
            self.prt_statusbar()

    def level_up(self):
        mylock.acquire()
        if self.level >= 10:
            mylock.release()
            return
        else:
            self.level += 1
            self.delay = 1 - ((self.level-1) * 0.1)
            self.prt_statusbar()
            mylock.release()

    def level_down(self):
        mylock.acquire()
        if self.level <= 1:
            mylock.release()
            return
        else:
            self.level -= 1
            self.delay = 1 - ((self.level-1) * 0.1)
            self.prt_statusbar()
            mylock.release()

    def prt_next(self):
        # This is only used when print the next Tetri
        next = TETRIS[self.next_type][self.next_orient]
        for blkj in range(0,len(next)):
            for blki in range(0,len(next[0])):
                if next[blkj][blki] == 1:
                    prt_cell('cyan', 'white', (blki+self.next_pos_x)*2, \
                            blkj+self.next_pos_y, CELL_PATTERN)

    def del_from_stage(self):
        self.block = TETRIS[self.type][self.orient]
        for blkj in range(0,len(self.block)):
            for blki in range(0,len(self.block[0])):
                if self.block[blkj][blki] == 1:
                    self.stage[self.pos_y+blkj][self.pos_x+blki] -= 1

    def add_to_stage(self):
        self.block = TETRIS[self.type][self.orient]
        for blkj in range(0,len(self.block)):
            for blki in range(0,len(self.block[0])):
                if self.block[blkj][blki] == 1:
                    self.stage[self.pos_y+blkj][self.pos_x+blki] += 1

    def rotate(self):
        mylock.acquire()
        # rotate this Tetris
        if self.move_test(0, 0, 1) == 1:
            self.del_from_stage()
            self.orient = (self.orient + 1) % 4
            self.add_to_stage()
            self.prt_stage()
        mylock.release()

    def set_current(self):
        self.pos_x = START_POS_X
        self.pos_y = START_POS_Y
        self.type = self.next_type
        self.orient = self.next_orient
        self.add_to_stage()
        self.prt_stage()
        # if Game Over
        self.block = TETRIS[self.type][self.orient]
        for blkj in range(0,len(self.block)):
            for blki in range(0,len(self.block[0])):
                if self.block[blkj][blki] == 1:
                    if self.stage[self.pos_y+blkj][self.pos_x+blki] > 1:
                        #if keylistener_thread.isAlive():
                        #    keylistener_thread.stop()
                        return 0
        return 1

    def set_next(self):
        self.next_pos_x = NEXT_DISP_POS_X
        self.next_pos_y = NEXT_DISP_POS_Y
        self.next_orient = gen_tetri_orient()
        self.next_type = gen_tetri_type()

    def move_left(self):
        mylock.acquire()
        if self.move_test(-1, 0) == 1:
            self.del_from_stage()
            self.pos_x -= 1 
            self.add_to_stage()
            self.prt_stage()
        mylock.release()

    def move_right(self):
        mylock.acquire()
        if self.move_test(1, 0) == 1:
            self.del_from_stage()
            self.pos_x += 1
            self.add_to_stage()
            self.prt_stage()
        mylock.release()

    def move_down(self):
        mylock.acquire()
        if self.move_test(0, 1) == 1:
            self.del_from_stage()
            self.pos_y += 1
            self.add_to_stage()
            self.prt_stage()
        else:
            # the Current one has landed
            # check if there is a line needs to be purged, and update score
            self.update_score(self.purge_line())
            # Start Next one and generate a new next
            time.sleep(0.1)
            if self.set_current() == 0:
                # Game Over
                mylock.release()
                return 0
            self.set_next()
            self.prt_statusbar()
        mylock.release()
        return 1

    def move_test(self,offsetX, offsetY, isRotate = 0):
        self.del_from_stage()
        self.orient = (self.orient + isRotate) % 4
        self.pos_x += offsetX
        self.pos_y += offsetY
        tblock = TETRIS[self.type][self.orient]
        # test border
        for blkj in range(0,len(tblock)):
            for blki in range(0,len(tblock[0])):
                if tblock[blkj][blki] == 1:
                    if self.pos_x+blki < 0 or self.pos_x+blki > STAGE_WIDTH-1 \
                            or self.pos_y+blkj > STAGE_HEIGHT-1:
                                self.pos_x -= offsetX
                                self.pos_y -= offsetY
                                self.orient = (self.orient - isRotate) % 4
                                self.add_to_stage()
                                return 0 
        # then test overlap
        self.add_to_stage()
        for blkj in range(0,len(tblock)):
            for blki in range(0,len(tblock[0])):
                if tblock[blkj][blki] == 1:
                    if self.stage[self.pos_y+blkj][self.pos_x+blki] > 1:
                        self.del_from_stage()
                        self.pos_x -= offsetX
                        self.pos_y -= offsetY
                        self.orient = (self.orient - isRotate) % 4
                        self.add_to_stage()
                        return 0
        self.del_from_stage()
        self.pos_x -= offsetX
        self.pos_y -= offsetY
        self.orient = (self.orient - isRotate) % 4
        self.add_to_stage()
        return 1

    def drop(self):
        mylock.acquire()
        downlines = 1
        while True:
            if self.move_test(0,downlines) == 1:
                downlines += 1
            else:
                break
        self.del_from_stage()
        self.pos_y += (downlines -1)
        self.add_to_stage()
        self.prt_stage()
        # the Current one has landed
        # check if there is a line needs to be purged, and update score
        self.update_score(self.purge_line())
        # Start Next one and generate a new next
        time.sleep(0.1)
        if self.set_current() == 0:
            # Game Over
            mylock.release()
            return 0
        self.set_next()
        self.prt_statusbar()
        mylock.release()
        return 1

class KeyListener(threading.Thread):
    def __init__(self, tetris):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.tetris = tetris
        self.exit_game = 0
        self.game_over = 0

    def run(self):
        old_attrs = termios.tcgetattr(sys.stdin.fileno())
        new_attrs = old_attrs[:]
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, new_attrs)
        try:
            inputstr = list()
            while not self.thread_stop:
                keych = sys.stdin.read(1)
                if not keych or keych == chr(4):
                    break
                key = ord(keych)
                if key == K_A or key == K_J:
                    self.tetris.move_left()
                elif key == K_D or key == K_L:
                    self.tetris.move_right()
                elif key == K_W or key == K_I:
                    self.tetris.rotate()
                elif key == K_S or key == K_K:
                    if self.tetris.move_down() == 0:
                        self.game_over = 1
                        self.exit_game = 1
                        break
                elif key == K_SPACE:
                    if self.tetris.drop() == 0:
                        self.game_over = 1
                        self.exit_game = 1
                        break
                elif key == K_MINUS:
                    self.tetris.level_down()
                elif key == K_PLUS:
                    self.tetris.level_up()
                elif key == K_Q or key == K_ESC:
                    self.exit_game = 1
                    break
        finally:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_attrs)

    def stop(self):
        self.thread_stop = True

class Game(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.tetris = Tetris()
        self.keylistener_thread = KeyListener(self.tetris)

    def end_game(self, outstr):
        # set cursor postion 
        print "\33[%d;%dH\33[0m" % (SCREEN_POS[1]+STAGE_HEIGHT+4, 1)
        print outstr
        if self.keylistener_thread.isAlive():
            print 'Press q to exit.'
            self.keylistener_thread.join()
        # resume cursor display
        print '\33[?25h'
        sys.exit(0)

    def run(self):
        self.keylistener_thread.start()
        while self.keylistener_thread.exit_game == 0:
            time.sleep(self.tetris.delay)
            if self.tetris.move_down() == 0:
                self.keylistener_thread.game_over = 1
                break

        if self.keylistener_thread.game_over == 1:
            self.end_game('Game Over!')
        else:
            self.end_game('Quit Game')

    def stop(self):
        self.thread_stop = True

# main start from here
if len(sys.argv) == 2:
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        usage()
        sys.exit(0)

# hide cursor
print '\33[?25l'

game = Game()
game.start()