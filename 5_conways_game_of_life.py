from rpi_ws281x import Adafruit_NeoPixel, Color
from PIL import Image, ImageOps, ImageFont, ImageDraw
import numpy as np
import time
import colorsys
import argparse
from collections import deque, Counter

parser = argparse.ArgumentParser(
    prog="ConwaysGameOfLife",
    description="Apply the Conway's Game of Life algorithm 32x8 to the pixel matrix",
)
parser.add_argument("-s", "--state", type=str, help="The initial state of the board when starting. Includes `random`, `blinker`, `toad`, and `penta-decathlon`. ", default="random")
args = parser.parse_args()

# Assistance from NeoPixel library strandtest example by Tony DiCola (tony@tonydicola.com)
# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels (32 x 8 = 256).
LED_PIN        = 18       # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800_000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 25       # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0        # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with the above configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                          LED_DMA, LED_INVERT, LED_BRIGHTNESS,
                          LED_CHANNEL)
                          
# Intialize the library (must be called once before other functions).
strip.begin()

# Clear the LED strip before executing the new code
for i in range(strip.numPixels()): strip.setPixelColor(i, Color(0,0,0))

# A cell is the individual unit of Conway's
# Game of life
class Cell():
    
    def __init__(self):
        self.is_living = False
        self.map_color_to_int(0)
        # The number of consecutive steps that the cell was alive for
        self.steps_alive = 0
        self.num_living_neighbors = 0
        
    def __repr__(self):
        return f"{int(self.is_living)}"
        
    # Flip the state of the cell between states
    # of dead and alive
    def flip(self):
        self.is_living = not self.is_living
        
    # If the cell is alive return the cell's color
    # otherwise return no color for the LED board
    def get_color(self):
        if self.is_living:
            return self.color
        return (0,0,0)
    
    # Get the number of living neighbors associated with
    # this cell
    def get_num_living_neighbors(self):
        return self.num_living_neighbors
    
    # Map the color to an integer based on any number of things
    # (Total number of living cells,
    #  number of days this individual cell was alive,
    #  total number of neighbors this cell has,
    #  etc.)
    def map_color_to_int(self, integer_value, min_value=0, max_value=256):
        normalized_value = (integer_value - min_value) / (max_value - min_value)
        hue = 0.67 * normalized_value
        rgb = colorsys.hsv_to_rgb(hue,1,1)
        scaled_rgb = [int(val*255) for val in rgb]
        self.color = scaled_rgb
       
# A board is a matrix of cells   
class Board():
    
    def __init__(self, size=(32,8), strip=strip):
        self.size = size
        self.state = np.zeros_like(size[0]*size[1], shape=size, dtype=Cell)
        self.strip = strip
        for x, _ in enumerate(self.state):
            for y, _ in enumerate(self.state[x]):
                self.state[x][y] = Cell()
                
    # Come up with an initial configuration of cells
    def start_life(self, style="random"):
        if style == "random":
            for x, _ in enumerate(self.state):
                for y, _ in enumerate(self.state[x]):
                    # If a 1 is randomly selected
                    if np.random.choice([0,1]):
                        # Strike the life into that cell!
                        self.state[x][y].flip()
        
        if style == "blinker":
            self.state[14][3].flip()
            self.state[15][3].flip()
            self.state[16][3].flip()
            
        if style == "toad":
            self.state[14][3].flip()
            self.state[15][3].flip()
            self.state[16][3].flip()
            self.state[13][4].flip()
            self.state[14][4].flip()
            self.state[15][4].flip()
            
        if style == "penta-decathlon":
            for i in range(8):
                for j in range(3):
                    self.state[i+13][j+2].flip()
    
    # Update the next state based on the following rules:
    # 1) Any live cell with two or three live neighbours survives.
    # 2) Any dead cell with three live neighbours becomes a live cell.
    # 3) All other live cells die in the next generation. Similarly, all other dead cells stay dead.
    def update(self):
        # Count the total number of living cells on the board
        num_living_cells = self.count_living_cells()
        
        # Get the neighbor counts for each cell before updating
        for x, _ in enumerate(self.state):
            for y, _ in enumerate(self.state[x]):
                self.state[x,y].num_living_neighbors = self.count_living_neighbors(x,y)
        
        for x, _ in enumerate(self.state):
            for y, _ in enumerate(self.state[x]):

                # Apply Rule 1
                if ((self.state[x][y].is_living and self.state[x,y].num_living_neighbors == 2) or
                    (self.state[x][y].is_living and self.state[x,y].num_living_neighbors == 3)):
                    self.state[x][y].steps_alive += 1
                
                # Apply Rule 2
                elif (not self.state[x][y].is_living) and (self.state[x,y].num_living_neighbors == 3):
                    self.state[x][y].flip()
                    self.state[x][y].steps_alive += 1
                
                # Apply Rule 3 :(
                elif self.state[x][y].is_living:
                    self.state[x][y].flip()
                    self.state[x][y].steps_alive = 0
                    
                self.state[x][y].map_color_to_int(num_living_cells)
                    
        
    # Collect the neighbors for a given index (i=(x,y))
    # provided by ChatGPT
    def count_living_neighbors(self, x, y):
        
        # Get the row and column indices of the given index
        row_index, col_index = x, y
        
        
        neighbor_indices = [
                            (row_index - 1, col_index - 1), # Top-left
                            (row_index - 1, col_index),     # Top
                            (row_index - 1, col_index + 1), # Top-right
                            (row_index, col_index - 1),     # Left
                            (row_index, col_index + 1),     # Right
                            (row_index + 1, col_index - 1), # Bottom-left
                            (row_index + 1, col_index),     # Bottom
                            (row_index + 1, col_index + 1), # Bottom-right
                            ]
        
        # Get whether the neighbors are living or dead
        neighbors = [self.state[row, col].is_living for row, col in neighbor_indices if 0 <= row < self.size[0] and 0 <= col < self.size[1]]
        
        # Return the total number of living neighbors for a given cell
        return np.sum(neighbors)
    
    # Get the total number of living cells
    def count_living_cells(self):
        num_living = 0
        for x, _ in enumerate(self.state):
            for y, _ in enumerate(self.state[x]):
                if self.state[x][y].is_living:
                    num_living += 1
        return num_living
    
    # Transform the board state matrix so that it directly
    # maps onto the LED baord
    def transform_board_state(self):
        # The board alternates indices, to make it match
        # the matrix we need to flip every other column
        # before outputting it to the board
        transformed_state = []
        for i, col in enumerate(self.state):
            if i%2:
                col = np.flip(col)
            transformed_state.append(col)
        return np.array(transformed_state).ravel()
        
    
    # Translate this matrix of cells onto the LED board
    def light(self, wait_ms=100):
        cells = self.transform_board_state()
        for i, cell in enumerate(cells):
            if cell.is_living:
                r, g, b = cell.color
                self.strip.setPixelColor(i, Color(r,g,b))
            else:
                self.strip.setPixelColor(i, Color(0,0,0))
        time.sleep(wait_ms/1_000.0)
        strip.show()
        
    # Get the integer value that corresponds to this boardstate
    def get_state_int(self):
        flattened_state = b.state.flatten()
        binary_str = ''.join(map(str, flattened_state))
        state_as_int = int(binary_str, 2)
        return state_as_int
        
    
if __name__ == "__main__":      

    b = Board()
    b.start_life(style=args.state)
    b.light()
    time.sleep(1_000/1_000.0)
    
    # Track the history so we can terminate at repeating endstates
    history = deque(maxlen=500)
    history.append(b.get_state_int())

    while True:
        b.update(), b.light()
        history.append(b.get_state_int())
        max_repeated_states = max(Counter(history).values())
        if max_repeated_states == 20:
            b.start_life(style=args.state)
            # Reset the history
            history = deque(maxlen=100)
            history.append(b.get_state_int())

