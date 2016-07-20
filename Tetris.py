#!/usr/bin/python
# Filename: Tetris.py

# by Cliff Dong

import sys
import time
import termios
import threading
from Utils import *
from Config import *

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
  p       --      PAUSE/RESUME\n \
  +       --      LEVEL UP\n \
  -       --      LEVEL DOWN\n \
  q/ESC   --      QUIT\n\n'

class Tetris:
    """Tetris Game"""
    def __init__(self, width, height, scr_pos, pattern):
        self.stage_width = width
        self.stage_height = height
        self.scr_pos_x = scr_pos[0]
        self.scr_pos_y = scr_pos[1]
        self.pattern = pattern
        self.next_disp_pos_x = self.scr_pos_x + self.stage_width + 4
        self.next_disp_pos_y = self.scr_pos_y + 2

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
        self.interval = 1
        self.pause = 0
        self.lock = threading.RLock()
        
        self.__prepare_stage()
        
    def __prepare_stage(self):
        self.__prt_border()
        self.__init_stage(self.stage_width,self.stage_height)
        self.__set_next()
        self.__set_current()
        self.__set_next()
        self.__prt_statusbar()

    def __init_stage(self, width, height):
        single_line = []
        for count in range(0, width):
            single_line.append(0)
        for count in range(0, height):
            self.stage.append(single_line[:])

    def __prt_border(self):
        # clean screen
        print "\33[2J\33[0m"
        # top
        for count in range(self.scr_pos_x*2, (self.scr_pos_x+self.stage_width+2)*2):
            prt_cell('cyan', 'white',count ,self.scr_pos_y, '=')
        # bottom
        for count in range(self.scr_pos_x*2, (self.scr_pos_x+self.stage_width+2)*2):
            prt_cell('cyan', 'white',count ,self.scr_pos_y+self.stage_height+1, '=')
        # left
        for count in range(self.scr_pos_y, self.scr_pos_y+self.stage_height+2):
            prt_cell('cyan', 'white',self.scr_pos_x*2 ,count , '||')
        # right
        for count in range(self.scr_pos_y, self.scr_pos_y+self.stage_height+2):
            prt_cell('cyan', 'white',(self.scr_pos_x+self.stage_width+1)*2 ,count , '||')

    def __prt_statusbar(self):
        info_x = self.next_disp_pos_x
        info_y = self.next_disp_pos_y + 5
        status_bar_x = self.scr_pos_x + self.stage_width + 2
        status_bar_y = self.scr_pos_y

        # clean previous StatusBar
        for sby in range(status_bar_y, status_bar_y + self.stage_height + 2):
            for sbx in range(status_bar_x, status_bar_x + 11):
                clean_cell(sbx * 2, sby)
        # now print it
        self.__prt_next()
        prt_cell('black', 'cyan', info_x * 2, info_y, 'Score')
        prt_cell('black', 'white', info_x * 2, info_y + 1, \
                 self.score)
        prt_cell('black', 'cyan', info_x * 2, info_y + 3, 'Level')
        prt_cell('black', 'white', info_x * 2, info_y + 4, \
                 self.level)

        if self.pause == 1:
            prt_cell('black', 'cyan', info_x * 2, info_y + 6, \
                     'PAUSED!         ')
        else:
            prt_cell('black', 'cyan', info_x * 2, info_y + 6, \
                     'Press P to pause')

    def __prt_stage(self):
        for county in range(0, self.stage_height):
            for countx in range(0, self.stage_width):
                if self.stage[county][countx] > 0:
                    prt_cell('white', 'black', (countx+self.scr_pos_x+1)*2, \
                            county+self.scr_pos_y+1, self.pattern)
                else:
                    clean_cell((countx+self.scr_pos_x+1)*2, county+self.scr_pos_y+1)

    def __clean_stage(self):
        for county in range(self.scr_pos_y+1, self.scr_pos_y+self.stage_height+1):
            for countx in range(self.scr_pos_x+1, self.scr_pos_x+self.stage_width+1):
                clean_cell(countx*2, county)

    def __purge_line(self):
        blank_line = []
        for count in range(0, self.stage_width):
            blank_line.append(0)
        linecount = self.stage_height - 1
        countsum = 0 
        while linecount >= 0:
            if self.stage[linecount].count(1) == self.stage_width:
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

    def __update_score(self, lines):
        if lines > 0:
            self.score += 2 ** lines - 1
            time.sleep(0.5)
            self.__prt_stage()
            self.__prt_statusbar()

    def __prt_next(self):
        # This is only used when print the next Tetri
        next = TETRIS[self.next_type][self.next_orient]
        for y in range(0,len(next)):
            for x in range(0,len(next[0])):
                if next[y][x] == 1:
                    prt_cell('cyan', 'white', (x + self.next_pos_x) * 2, \
                             y + self.next_pos_y, self.pattern)

    def __del_from_stage(self):
        tetri = TETRIS[self.type][self.orient]
        for y in range(0,len(tetri)):
            for x in range(0,len(tetri[0])):
                if tetri[y][x] == 1:
                    self.stage[self.pos_y + y][self.pos_x + x] -= 1

    def __add_to_stage(self):
        tetri = TETRIS[self.type][self.orient]
        for y in range(0,len(tetri)):
            for x in range(0,len(tetri[0])):
                if tetri[y][x] == 1:
                    self.stage[self.pos_y + y][self.pos_x + x] += 1

    def __set_current(self):
        self.pos_x = self.stage_width/2 - 1
        self.pos_y = 0
        self.type = self.next_type
        self.orient = self.next_orient
        self.__add_to_stage()
        self.__prt_stage()
        # if Game Over
        tetri = TETRIS[self.type][self.orient]
        for y in range(0,len(tetri)):
            for x in range(0,len(tetri[0])):
                if tetri[y][x] == 1:
                    if self.stage[self.pos_y + y][self.pos_x + x] > 1:
                        return 0
        return 1

    def __set_next(self):
        self.next_pos_x = self.next_disp_pos_x
        self.next_pos_y = self.next_disp_pos_y
        self.next_orient = gen_tetri_orient()
        self.next_type = gen_tetri_type()

    def __move_test(self, offset_x, offset_y, is_rotate = 0):
        self.__del_from_stage()
        self.orient = (self.orient + is_rotate) % 4
        self.pos_x += offset_x
        self.pos_y += offset_y
        tetri = TETRIS[self.type][self.orient]
        # test border
        for y in range(0,len(tetri)):
            for x in range(0,len(tetri[0])):
                if tetri[y][x] == 1:
                    if self.pos_x + x < 0 or self.pos_x + x > self.stage_width-1 \
                            or self.pos_y + y > self.stage_height-1:
                                self.pos_x -= offset_x
                                self.pos_y -= offset_y
                                self.orient = (self.orient - is_rotate) % 4
                                self.__add_to_stage()
                                return 0
        # then test overlap
        self.__add_to_stage()
        for y in range(0,len(tetri)):
            for x in range(0,len(tetri[0])):
                if tetri[y][x] == 1:
                    if self.stage[self.pos_y + y][self.pos_x + x] > 1:
                        self.__del_from_stage()
                        self.pos_x -= offset_x
                        self.pos_y -= offset_y
                        self.orient = (self.orient - is_rotate) % 4
                        self.__add_to_stage()
                        return 0
        self.__del_from_stage()
        self.pos_x -= offset_x
        self.pos_y -= offset_y
        self.orient = (self.orient - is_rotate) % 4
        self.__add_to_stage()
        return 1

    def get_interval(self):
        """Get sleep interval, which determine the tetrmino auto move down speed"""
        return self.interval

    def level_up(self):
        """Increase the game difficulty level"""
        guard = LockGuard(self.lock)
        if self.level >= 10:
            return
        else:
            self.level += 1
            self.interval = 1 - ((self.level-1) * 0.1)
            self.__prt_statusbar()

    def level_down(self):
        """Decrease the game difficulty level"""
        guard = LockGuard(self.lock)
        if self.level <= 1:
            return
        else:
            self.level -= 1
            self.interval = 1 - ((self.level-1) * 0.1)
            self.__prt_statusbar()

    def do_pause(self, pause):
        """Pause/Resume the game"""
        self.pause = pause
        self.__prt_statusbar()

    def rotate(self):
        """Rotate tetrmino"""
        guard = LockGuard(self.lock)
        # rotate this Tetris
        if self.__move_test(0, 0, 1) == 1:
            self.__del_from_stage()
            self.orient = (self.orient + 1) % 4
            self.__add_to_stage()
            self.__prt_stage()

    def move_left(self):
        """Move tetrmino left"""
        guard = LockGuard(self.lock)
        if self.__move_test(-1, 0) == 1:
            self.__del_from_stage()
            self.pos_x -= 1
            self.__add_to_stage()
            self.__prt_stage()

    def move_right(self):
        """Move tetrmino right"""
        guard = LockGuard(self.lock)
        if self.__move_test(1, 0) == 1:
            self.__del_from_stage()
            self.pos_x += 1
            self.__add_to_stage()
            self.__prt_stage()

    def move_down(self):
        """Move tetrmino down"""
        guard = LockGuard(self.lock)
        if self.__move_test(0, 1) == 1:
            self.__del_from_stage()
            self.pos_y += 1
            self.__add_to_stage()
            self.__prt_stage()
        else:
            # the Current one has landed
            # check if there is a line needs to be purged, and update score
            self.__update_score(self.__purge_line())
            # Start Next one and generate a new next
            time.sleep(0.1)
            if self.__set_current() == 0:
                # Game Over
                return 0
            self.__set_next()
            self.__prt_statusbar()
        return 1

    def drop(self):
        """Drop tetrmino"""
        guard = LockGuard(self.lock)
        downlines = 1
        while True:
            if self.__move_test(0,downlines) == 1:
                downlines += 1
            else:
                break
        self.__del_from_stage()
        self.pos_y += (downlines -1)
        self.__add_to_stage()
        self.__prt_stage()
        # the Current one has landed
        # check if there is a line needs to be purged, and update score
        self.__update_score(self.__purge_line())
        # Start Next one and generate a new next
        time.sleep(0.1)
        if self.__set_current() == 0:
            # Game Over
            return 0
        self.__set_next()
        self.__prt_statusbar()
        return 1

class KeyListener(threading.Thread):
    def __init__(self, tetris):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.tetris = tetris
        self.pause = 0
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
                if self.pause == 0:
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

                if key == K_MINUS:
                    self.tetris.level_down()
                elif key == K_PLUS:
                    self.tetris.level_up()
                elif key == K_P:
                    self.pause = (self.pause + 1) % 2
                    self.tetris.do_pause(self.pause)
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
        self.tetris = Tetris(STAGE_WIDTH, STAGE_HEIGHT, SCREEN_POS, CELL_PATTERN)
        self.keylistener_thread = KeyListener(self.tetris)

    def __start_game(self):
        hide_cursor()
        self.keylistener_thread.start()

    def __end_game(self, outstr):
        set_cursor_pos(self.tetris.scr_pos_y + self.tetris.stage_height + 4, 1)
        print outstr
        if self.keylistener_thread.isAlive():
            print 'Press q to exit.'
            self.keylistener_thread.stop()
            self.keylistener_thread.join()
        resume_cursor()
        sys.exit(0)

    def run(self):
        self.__start_game()
        while self.keylistener_thread.exit_game == 0:
            time.sleep(self.tetris.get_interval())
            if self.keylistener_thread.pause == 0:
                if self.tetris.move_down() == 0:
                    self.keylistener_thread.game_over = 1
                    break

        if self.keylistener_thread.game_over == 1:
            self.__end_game('Game Over!')
        else:
            self.__end_game('Quit Game')

    def stop(self):
        self.thread_stop = True

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            usage()
            sys.exit(0)
        else:
            print 'Bad option!'
            usage()
            sys.exit(1)

    game = Game()
    game.start()

if __name__ == '__main__':
    main()