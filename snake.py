#!/usr/bin/python
# -*- encoding: utf-8 -*-

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


# Raspberry Pi pin configuration
RST = 25
DC = 24
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Initialize library.
disp.begin()

# Create blank image for drawing.
image = Image.new('1', (disp.width, disp.height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Load default font.
font = ImageFont.load_default()
temp = None

# Align middle
def align_middle(x1, x2, l):
    lc = 6
    return (x2-x1-l*lc)/2 + x1

# Configurations of this game
# You may check the preference below and alter the values if you want
display_interval = 0.05                # Refresh display every 0.05 second => FPS = 20
size = 2                               # Size of a snake, 2 means one point occupies four pixels (2x2)
# Initialize the boundary of the gaming area
area = (0, 0, disp.width*2/3/size-1, (disp.height-2)/size-1)    # Gameing area in points with size
boundary = (0, 0, (area[2]+1)*size+1, (area[3]+1)*size+1)       # Gameing boundary
boundary_cross = True                  # snake is able to cross the boundary 
# Block setting
block_mode = False                     # Do not create blocks
# Initialize a snake
snake = []                             # snake
snake0 = (area[2]/2, area[3]/2)        # snake's head (first pixel)
snake1 = snake0                        # snake's tail (last pixel)
l = 4                                  # snake's length = 4
interval_max = 1
interval_min = 0.05
interval = interval_max                # move the snake every 1 second
direction = (1, 0)                     # direction = Right
food = snake0                          # normal food
food_score = 1                         # each food worth 1 score
sfood = ()                             # initialize a empty special food
sfood_lifetime = 10                    # special food exists for 10 seconds
sfood_count = 0                        # to count the time of the special food
sfood_interval = 0.25                  # refresh the special food every 0.25 second
sfood_time = 30                        # Possible to generate a special food every 30 seconds
sfood_score = 5                        # each special food worth 5 scores
blocks = []                            # blocks for blocking the snake
scores = [0, 10, 50, 100, 150, 250, 350, 550, 750, 950, 1200]
levels = [0, 1,  2,  3,   4,   5,   6,   7,   8,   9,   10]
score = 0
level = 0

# Create a block
def block_create():
    p = (random.randint(0, area[2])/4+1, random.randint(0, area[3]+1)/4)
    for x in range(random.randint(0, area[2]-p[0]+1), area[2]-p[0]+1, 1):
        for y in range(random.randint(0, area[3]-p[1]+1), area[3]-p[1]+1, 1):
            for i in range(len(snake)):
                if snake[i][0] >= x and snake[i][0] <= p[0]+x and snake[i][1] >= y and snake[i][1] <= p[1]+y:
                    if snake[i][1]+1 > y:
                        y = snake[i][1]+1
                    break
            if y + p[1] > area[3]:
                break
            else:
                return (x, y, p[0]+x, p[1]+y)
    return block_create()

# Check if the point is in the blocks
def block_check(point):
    x = point[0]
    y = point[1]
    for block in blocks:
        if  x >= block[0] and x <= block[2] and y >= block[1] and y <= block[3]:
            return True
    return False

# Initialize a new block
def block_init():
    # Create a new block
    block = block_create()
    # Add block to blocks and draw the block
    blocks.append(block)
    draw.rectangle((block[0]*size+1, block[1]*size+1, (block[2]+1)*size, (block[3]+1)*size), outline=255, fill=255)
    # Renew food if it is in the new block
    if food[0] >= block[0] and food[0] <= block[2] and food[1] >= block[1] and food[1] <= block[3]:
        gen_food()
    # Remove special food if it is in the new block
    global sfood, sfood_count
    if sfood != ():
        if sfood[0] >= block[0] and sfood[0] <= block[2] and sfood[1] >= block[1] and sfood[1] <= block[3]:
            draw.rectangle((sfood[0]*size+1, sfood[1]*size+1, (sfood[0]+1)*size, (sfood[1]+1)*size), outline=0, fill=0)
            sfood = ()
            sfood_count = 0

# Initialize a game panel
def game_init():
    # Clear display.
    disp.clear()
    draw.rectangle(boundary, outline=255, fill=0)
    draw.text((align_middle(boundary[2]+4, disp.width - 1, len('Score')), 0),             'Score', font=font, fill=255)
    draw.text((align_middle(boundary[2]+4, disp.width - 1, len('Score')), disp.height/2), 'Level', font=font, fill=255)
    snake_init()

# Draw an initial a snake
def snake_init():
    global snake1
    for i in range(l):
        snake1 = (snake0[0]-i, snake0[1])
        draw.rectangle((snake1[0]*size+1, snake1[1]*size+1, (snake1[0]+1)*size, (snake1[1]+1)*size), outline=255, fill=255)
        snake.append(snake1)
    draw.text((align_middle(boundary[2]+4, disp.width - 1, len(str(score))), disp.height/4),   str(score), font=font, fill=255)
    draw.text((align_middle(boundary[2]+4, disp.width - 1, len(str(level))), disp.height/4*3), str(level), font=font, fill=255)
    gen_food()

def draw_notification(msg):
    draw.rectangle((boundary[2]/2-32, boundary[3]/2-8, boundary[2]/2+32, boundary[3]/2+8), outline=255, fill=0)
    draw.text((align_middle(boundary[2]/2-32, boundary[2]/2+32, len(msg)), boundary[3]/2-6), msg, font=font, fill=255)

# Draw a notification box when game is over
def game_over():
    draw_notification('GAME OVER')
    my_snake._stopevent.set()
    my_sfood._stopevent.set()

# Draw a notification box when game is paused
def game_paused(paused):
    global temp, image, draw
    if paused:
        my_sfood.pause()
        my_snake.pause()
        temp = image.copy()
        # Display paused notification
        draw_notification('PAUSED')
    else:
        image = temp
        draw = ImageDraw.Draw(image)
        my_sfood.resume()
        my_snake.resume()

# Draw a notification box when game is paused
interval_ori = None
def game_speeded(speeded):
    global interval_ori, interval
    if speeded:
        interval_ori = interval
        interval = interval_min
    else:
        interval = interval_ori

# Draw a notification box when game is exited
def game_exited():
        draw_notification('GOOD BYE!')

# Check the boundary with the new pixel / head to prevent it run out of the game panel
def boundary_check(point):
    x = point[0]
    y = point[1]
    if x == -1:
        if boundary_cross == True:
            x = area[2]
        else:
            game_over()
    elif x == area[2]+1:
        if boundary_cross == True:
            x = 0
        else:
            game_over()
    elif y == -1:
        if boundary_cross == True:
            y = area[3]
        else:
            game_over()
    elif y == area[3]+1:
        if boundary_cross == True:
            y = 0
        else:
            game_over()
    for block in blocks:
        if  x >= block[0] and x <= block[2] and y >= block[1] and y <= block[3]:
            game_over()
    return (x, y)

# Check if the snake is eating itself
def snake_selfcheck():
    for i in range(1, len(snake), 1):  
        if snake0 == snake[i]:    # Game over
            game_over()

import random
# Generate a food
def gen_food():
    global food
    while food in snake or block_check(food):
        x = random.randint(area[0], area[2])
        y = random.randint(area[1], area[3])
        food = (x, y)
    draw.rectangle((food[0]*size+1, food[1]*size+1, (food[0]+1)*size, (food[1]+1)*size), outline=255, fill=255)

def gen_sfood():
    global sfood
    if random.randint(0, int(sfood_time/sfood_interval)) == 0:
        while sfood == () or sfood in snake or sfood == food or block_check(sfood):
            x = random.randint(area[0], area[2])
            y = random.randint(area[1], area[3])
            sfood = (x, y)

# Update score and level
def update_info():
    # Clear the part of score
    draw.rectangle((boundary[2]+4, disp.height/4, disp.width-1, disp.height/2), outline=0, fill=0)
    draw.text((align_middle(boundary[2]+4, disp.width - 1, len(str(score))), disp.height/4),   str(score), font=font, fill=255)
    # Update Level
    global level
    for i in range(10, 0, -1):
        if score >= scores[i] and levels[i] > level:
            if block_mode:
                block_init()
            level = levels[i]
            global interval, interval_ori
            if speeded:
                interval_ori -= (interval_max-interval_min)/10
                if interval_ori <= 0:
                    interval_ori = interval_min
            else:
                interval -= (interval_max-interval_min)/10
                if interval <= 0:
                    interval = interval_min
            draw.rectangle((boundary[2]+4, disp.height*3/4, disp.width-1, disp.height-1), outline=0, fill=0)
            draw.text((align_middle(boundary[2]+4, disp.width - 1, len(str(level))), disp.height*3/4),   str(level), font=font, fill=255)
            break

# Refresh a frame
def snake_refresh():
    global food, sfood, snake, snake0, snake1, l, score
    # Renew snake0 / head
    snake0 = (snake0[0]+direction[0], snake0[1]+direction[1])    # Renew the first pixel / head
    snake0 = boundary_check(snake0)                  # Check if snake0 is in the boundary and renew it
    draw.rectangle((snake0[0]*size+1, snake0[1]*size+1, (snake0[0]+1)*size, (snake0[1]+1)*size), outline=255, fill=255)
    snake.insert(0, snake0)                          # inset the first pixel / point in p
    snake_selfcheck()
    if snake0 == sfood:
        score += sfood_score
        update_info()
        sfood = ()    # Remove special food
    if snake0 == food:
        score += food_score
        l = l+1
        update_info()
        gen_food()
    else:
        draw.rectangle((snake1[0]*size+1, snake1[1]*size+1, (snake1[0]+1)*size, (snake1[1]+1)*size), outline=0, fill=0)
        snake1 = snake[l-1]           # Renew the last pixel / snake1
        del snake[l]                  # Remove the last pixel in snake

import threading
# Special food
class Sfood(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
        self._flag = threading.Event()
        self._flag.set()
    def run(self):
        my_outline = 0
        while not self._stopevent.isSet():
            self._stopevent.wait(sfood_interval)
            self._flag.wait()
            global sfood
            if sfood == ():
                gen_sfood()
            if sfood != ():
                global sfood_count
                sfood_count += 1
                if my_outline == 0:
                    my_outline = 255
                else:
                    my_outline = 0
                draw.rectangle((sfood[0]*size+1, sfood[1]*size+1, (sfood[0]+1)*size, (sfood[1]+1)*size), outline=my_outline, fill=my_outline)
                # Remove sfood if it is timeout
                if sfood_interval*sfood_count > sfood_lifetime:
                    draw.rectangle((sfood[0]*size+1, sfood[1]*size+1, (sfood[0]+1)*size, (sfood[1]+1)*size), outline=0, fill=0)
                    sfood = ()
                    sfood_count = 0
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def pause(self):
        self._flag.clear()
    def resume(self):
        self._flag.set()

# Refresh a snake
class Snake(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
        self._flag = threading.Event()
        self._flag.set()
    def run(self):
        while not self._stopevent.isSet():
            self._stopevent.wait(interval)
            self._flag.wait()
            snake_refresh()
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def pause(self):
        self._flag.clear()
    def resume(self):
        self._flag.set()

# Display image
class Game(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
    def run(self):
        while not self._stopevent.isSet():
            self._stopevent.wait(display_interval)
            disp.image(image)
            disp.display()
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)

# Read pressed key from keyboard
# Refered from: http://code.activestate.com/recipes/572182-how-to-implement-kbhit-on-linux/
import sys, termios, atexit
from select import select

# save the terminal settings
fd = sys.stdin.fileno()
new_term = termios.tcgetattr(fd)
old_term = termios.tcgetattr(fd)

# new terminal setting unbuffered
new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)

# Switch to normal terminal
def set_normal_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)

# Switch to unbuffered terminal
def set_curses_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

def getch():
    return sys.stdin.read(1)

def kbhit():
    dr = select([sys.stdin], [], [], 0)
    return dr <> []

def game_set_diffculity(a, b, c, d, e, f, g, h):
    global boundary_cross, block_mode, l, interval, interval_max
    global sfood_lifetime, sfood_time, food_score, sfood_score
    boundary_cross = a
    block_mode = b
    l = c
    interval_max = d
    interval = interval_max
    sfood_lifetime = e
    sfood_time = f
    food_score = g
    sfood_score = h

import os, time
if __name__ == '__main__':
    atexit.register(set_normal_term)
    set_curses_term()
    diffculity = '0'
    try:
        diffculity = sys.argv[1]
    except:
        pass
    if diffculity == '2':
        game_set_diffculity(False, True, 8, 0.5, 5, 120, 1, 5)
    elif diffculity == '1':
        game_set_diffculity(True, True, 6, 0.8, 8, 60, 3, 10)
    else:
        game_set_diffculity(True, False, 4, 1, 10, 30, 5, 20)
    game_init()
    my_snake = Snake()
    my_sfood = Sfood()
    my_game = Game()
    my_snake.start()
    my_sfood.start()
    my_game.start()
    paused = False
    speeded = False
    if diffculity == '2':
        block_init()
    print "------------How to play------------"
    print "Control: Press 'w', 'a', 's', 'd'"
    print "Speed up/remove effect: Press 'q'"
    print "Exit game: Press 'x'"
    while True:
        if kbhit():
            ch = getch()
            # Identify next direction
            if (ch == 'w' or ch == 'W') and snake[0][1] - snake[1][1] != 1:
                direction = (0, -1)
            elif (ch == 'a' or ch == 'A') and snake[0][0] - snake[1][0] != 1:
                direction = (-1, 0)
            elif (ch == 's' or ch == 'S') and snake[0][1] - snake[1][1] != -1:
                direction = (0, 1)
            elif (ch == 'd' or ch == 'D') and snake[0][0] - snake[1][0] != -1:
                direction = (1, 0)
            if ch == 'x':    # Exit the game
                if paused:
                    game_paused(False)
                game_exited()
                time.sleep(0.05)
                my_game.join()
                quit()
            elif ch == 'p':    # Pause or resume the game
                paused = not paused
                game_paused(paused)
            if ch == 'q':
                speeded = not speeded
                game_speeded(speeded)
