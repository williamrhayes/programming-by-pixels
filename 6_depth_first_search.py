import numpy as np
import random
import time
from rpi_ws281x import *
import colorsys
import argparse
from collections import deque, Counter

parser = argparse.ArgumentParser(
    prog="DepthFirstSearch",
    description="Apply the DFS algorithm 32x8 to the pixel matrix",
)
parser.add_argument("-s", "--speed", type=int, help="The speed (ms) of the DFS when searching the pixel grid", default=0)
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
strip.show()

# A cell is an individual component of my 32x8 matrix
class Cell():
    
    def __init__(self):
        self.is_active = True
        self.visited = False
        self.is_goal = False
        self.color = (255, 255, 255)
        
    def __repr__(self):
        return f"{int(self.is_active)}"
        
    # Flip the state of the cell between states
    # of dead and alive
    def flip(self):
        self.is_active = not self.is_active
        
    # If the cell is alive return the cell's color
    # otherwise return no color for the LED board
    def get_color(self):
        if self.is_active:
            return self.color
        return (0,0,0)
    
        
        
# A board is a matrix of cells   
class Board():
    
    def __init__(self, size=(32,8), strip=strip):
        self.size = size
        self.state = np.zeros_like(size[0]*size[1], shape=size, dtype=Cell)
        self.strip = strip
        for x, _ in enumerate(self.state):
            for y, _ in enumerate(self.state[x]):
                self.state[x][y] = Cell()
        
    # Collect the neighbors for a given index (i=(x,y))
    # provided by ChatGPT
    def get_neighbor_positions(self, x, y):
        
        # Get the row and column indices of the given index
        row_index, col_index = x, y
        neighbor_indices = [
                            #(row_index - 1, col_index - 1), # Top-left
                            (row_index - 1, col_index),     # Top
                            #(row_index - 1, col_index + 1), # Top-right
                            (row_index, col_index - 1),     # Left
                            (row_index, col_index + 1),     # Right
                            #(row_index + 1, col_index - 1), # Bottom-left
                            (row_index + 1, col_index),     # Bottom
                            #(row_index + 1, col_index + 1), # Bottom-right
                            ]
        
        # Get whether the neighbors are open
        open_neighbor_positions = [(row, col) for row, col in neighbor_indices if 0 <= row < self.size[0] and 0 <= col < self.size[1] and (self.state[row][col].is_active == False or self.state[row][col].is_goal)]
        
        # Return the total number of living neighbors for a given cell
        return open_neighbor_positions
    
    # Checks if the next space to search is a valid one
    def is_valid(self, x, y):
        return 0 <= x < self.size[0] and 0 <= y < self.size[1] and self.state[x][y].is_active
     
    def carve_passage(self, x, y):
        """ Recursive function that carves a path to help generate a maze """
        self.state[x][y].is_active = False
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny) and self.state[nx][ny].is_active:
                mx, my = (x + nx) // 2, (y + ny) // 2
                self.state[mx][my].is_active = False
                self.carve_passage(nx, ny)
    
    # Generate a maze for our DFS algo to traverse
    def generate_maze(self):
        """ Generate maze starting from (start_x, start_y) """
        self.carve_passage(0,0)
        
        ### HACKY SOLUTION - Randomize edge states to complete the maze
        for i in range(self.size[0]):
            self.state[i, -1].is_active = bool(np.random.choice([0,1], p=[0.3, 0.7]))
        for j in range(self.size[1]):
            self.state[-1, j].is_active = bool(np.random.choice([0,1], p=[0.3, 0.7]))

        # Ensure end point (bottom-right corner) is a path
        self.state[self.size[0] - 1][self.size[1] - 1].is_active = False
        self.state[self.size[0] - 2][self.size[1] - 1].is_active = False
        
        # Turn any cell that has no neighbors into a wall
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                num_neighbors = len(self.get_neighbor_positions(x, y))
                if num_neighbors == 0:
                    self.state[x][y].is_active = True
        
        # Update the LEDs to reflect this state
        self.light()
        
    # Apply the Depth First Search Algorithm to solve this problem
    def depth_first_search(self, start_x=0, start_y=0, goal_x=31, goal_y=7, wait_ms=25):
        #(255, 155, 0)
        # Initialize the goal marker
        self.state[goal_x][goal_y].__dict__.update(
            {'is_active': True, 'color': (0, 255, 0), 'is_goal': True,}
        )
        # Set the attributes of the starting point
        self.state[start_x][start_y].__dict__.update(
            {'is_active': True, 'color': (255, 0, 0), 'visited': True}
        )
        self.light()
        
        # Start the DFS algo
        current_pos = (start_x, start_y)
        stack = []
        visited = {current_pos}
        while current_pos[0] != goal_x or current_pos[1] != goal_y:
            x, y = current_pos
            # Choose the next point to explore from your list of neighbors
            neighbors = self.get_neighbor_positions(x, y)
            for neighbor in neighbors: stack.append(neighbor)
            next_pos = stack.pop()
            self.state[next_pos[0]][next_pos[1]].__dict__.update(
                {'is_active': True, 'color': (255, 0, 0), 'visited': True}
            )
            # Move away from the current state / display it as visited
            self.state[current_pos[0]][current_pos[1]].__dict__.update(
                {'is_active': True, 'color': (255, 155, 0), 'visited': True}
            )
            # Display these changes on the LED matrix
            current_pos_index = self.get_transformed_index(current_pos[0], current_pos[1])
            self.strip.setPixelColor(current_pos_index, Color(255, 155, 0))
            next_pos_index = self.get_transformed_index(next_pos[0], next_pos[1])
            self.strip.setPixelColor(next_pos_index, Color(255, 0, 0))
            self.strip.show()
            time.sleep(wait_ms / 1000)
            
            # Set the current position to this next position
            current_pos = next_pos
    
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
    
    # Get the pixel corresponding to the x / y position listed
    def get_transformed_index(self, x, y):
        if x % 2:
            y = self.size[1] - 1 - y
        return x * self.size[1] + y
    # Get the X / Y position given a list of coordinates
    def get_original_coordinates(self, i):
        x = i // self.size[1]
        y = i % self.size[1]
        if x % 2:
            y = self.size[1] - 1 - y
        return x, y
        
    
    # Translate this matrix of cells onto the LED board
    def light(self, wait_ms=100):
        cells = self.transform_board_state()
        for i, cell in enumerate(cells):
            if cell.is_active:
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
    while True:
        b = Board()
        b.generate_maze()
        # Select a random start and end position
        active_indices = [i for i, cell in enumerate(b.transform_board_state()) if not cell.is_active]
        start_x, start_y = b.get_original_coordinates(int(np.random.choice(active_indices)))
        goal_x, goal_y = b.get_original_coordinates(np.random.choice(active_indices))
        # Apply the DFS algo
        b.depth_first_search(start_x=start_x, start_y=start_y, goal_x=goal_x, goal_y=goal_y, wait_ms=args.speed)
