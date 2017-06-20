Game: Snake for Raspberry Pi with 12864/SSD1306 in Python

### Demo
<img src="https://github.com/xswxm/Play-Snake-on-12864-SSD1306/blob/master/demo.JPG?raw=true" 
alt="Demo" width="480" height="360" border="10" />

### Setting Up
Configure your 128464 by following this tutorial: https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black/usage?view=all


Edit the script. Replace the pins with yours
```python
# Ports used for fthe Display. You may have to change them to yours
RST = 25
DC = 24
```
More configuration. Change the values if you want
```python
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
```

### How to Use
```sh
# Run directly with diffculity = 0
sudo python snake.py
# Run directly with diffculity = 1
sudo python snake.py 1
# Run directly with diffculity = 2
sudo python snake.py 2
```
### How to Play
Control: Press 'w', 'a', 's', 'd'
Speed up/remove effect: Press 'q'
Exit game: Press 'x'

License
----
MIT
