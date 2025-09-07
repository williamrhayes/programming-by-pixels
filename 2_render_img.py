from rpi_ws281x import Adafruit_NeoPixel, Color
from PIL import Image
import numpy as np
import argparse

parser = argparse.ArgumentParser(
    prog="RednerBanners",
    description="Apply a 32x8 image to the pixel matrix",
)
parser.add_argument("-img", "--image",type=str, help="The file name of the image you want to display", default="img/poker.png")
parser.add_argument("-br", "--brightness", type=int, help="The brightness of the display, 0 is darkest and 255 is brightest.", default=25)
args = parser.parse_args()

# Assistance from NeoPixel library strandtest example by Tony DiCola (tony@tonydicola.com)
# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels (32 x 8 = 256).
LED_PIN        = 18       # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800_000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = args.brightness       # Set to 0 for darkest and 255 for brightest
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

# Define our Pixel data structure   
class Pixel():
    def __init__(self, color=[0,0,0], is_enabled=False):
        self.color = color
        self.r, self.g, self.b = color
        self.is_enabled = is_enabled

    def toggle(self):
        self.is_enabled = not self.is_enabled

# Extract the color value from each pixel in the image
def put_img_to_strip(img_data, size=(32,8), strip=strip, x_offset=0, y_offset=0):
    state = np.zeros_like(size[0]*size[1], shape=size, dtype=Pixel)
    strip = strip
    for x, _ in enumerate(state):
        for y, _ in enumerate(state[x]):
            try:
                r, g, b, a = img_data.getpixel((x,y))
                if a > 0:  
                    state[x][y] = Pixel(color=[r,g,b], is_enabled=True)
                else:
                    state[x][y] = Pixel()
            except:
                state[x][y] = Pixel()
    # Shift the location of the image on the pixel board up or down
    state = np.flip(state, axis=1)
    state = np.roll(state, x_offset, axis=0)
    state = np.roll(state, y_offset, axis=1)
    
    return state

# Transform the board state matrix so that it directly
# maps onto the LED baord
def transform_board_state(state):
    # The board alternates indices, to make it match
    # the matrix we need to flip every other column
    # before outputting it to the board
    transformed_state = []
    for i, col in enumerate(state):
        if i%2:
            col = np.flip(col)
        transformed_state.append(col)
    transformed_state = np.array(transformed_state)
        
    return np.flip(transformed_state).ravel()


# Load in our image and convert it to RGBA
img_to_load = args.image
img_data = Image.open(img_to_load).convert("RGBA")

state = put_img_to_strip(img_data)
pixel_grid = transform_board_state(state)
for i, pixel in enumerate(pixel_grid):
    r, g, b = pixel.color
    strip.setPixelColor(i, Color(r,g,b))

strip.show()
