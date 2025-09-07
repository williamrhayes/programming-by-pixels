from rpi_ws281x import Adafruit_NeoPixel, Color
from PIL import Image, ImageOps, ImageFont, ImageDraw
import numpy as np
import time
import argparse

parser = argparse.ArgumentParser(
    prog="RenderMessage",
    description="Render a message onto the pixel matrix",
)

parser.add_argument("-m", "--messages", nargs="+", type=str, help="The message to send to the pixel matrix", default="the quick brown fox jumped over the lazy dog")
parser.add_argument("-br", "--brightness", type=int, help="The brightness of the display", default=25)
parser.add_argument("-s", "--speed", type=int, help="The speed (ms) of the message scroll per iteration", default=20)
parser.add_argument("-rgb", type=int, help="The r, g, and b value of the displayed message", nargs=3, default=[255,255,255])
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
    def __init__(self, color=[0,0,0]):
        self.color = color

def put_img_to_strip(img_array, size=(32,8), strip=strip, current_pos=0, x_offset=0, y_offset=0):
    state = np.zeros_like(size[0]*size[1], shape=size, dtype=Pixel)
    for x, _ in enumerate(state):
        for y, _ in enumerate(state[x]):
            try:
                r, g, b, a = img_array[x,y]
                if a > 0:  
                    state[x][y] = Pixel(color=[r,g,b])
                else:
                    state[x][y] = Pixel()
            except:
                state[x][y] = Pixel()
    # Shift the location of the image on the pixel board so that
    # It can be read from left to right
    state = np.rot90(state, 2, axes=(1,0))
    
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

def display_message(msg_text, fontsize=8, color=[255,255,255]):
    font = ImageFont.truetype('PixelOperator8.ttf', fontsize) #load the font
    size = np.array(font.getsize(msg_text))  #calc the size of text in pixels
    message = Image.new('1', tuple(size), 1)  #create a b/w image
    draw = ImageDraw.Draw(message)
    draw.text((0, 0), msg_text, font=font) #render the text to the bitmap
    message = message.convert("RGBA")
    # Split the image into individual bands
    r, g, b, a = message.split()

    # Invert the RGB channels
    r = ImageOps.invert(r)
    g = ImageOps.invert(g)
    b = ImageOps.invert(b)
    
    # Convert channels to NumPy arrays
    r_array = np.array(r)
    g_array = np.array(g)
    b_array = np.array(b)

    # Identify pixels where r, g, and b are 255
    mask = (r_array == 255) & (g_array == 255) & (b_array == 255)

    # Set g and b to 0 where the condition is met
    input_r, input_g, input_b = color
    r_array[mask] = input_r
    g_array[mask] = input_g
    b_array[mask] = input_b

    # Convert arrays back to Image objects
    r = Image.fromarray(r_array)
    g = Image.fromarray(g_array)
    b = Image.fromarray(b_array)
    
    # Merge the channels back together
    message = Image.merge("RGBA", (r, g, b, a))
    return message

def render_message(msg_text, color=args.rgb, wait_ms=args.speed):
    img = display_message(msg_text=msg_text, color=color)
    # Transform the image to read correctly on the pixel grid
    img_array = np.rot90(np.array(img))
    # Add padding of zeros with shape 32x8x4 to the original array
    padding = ((33, 0), (0, 0), (0, 0))
    img_array = np.pad(img_array, padding, mode='constant', constant_values=0)

    params = {
        "current_pos":0,
        "x_offset": 0,
        "y_offset": 0
    }
    current_pos = -1
    while current_pos > -img_array.shape[0]:
        state = put_img_to_strip(img_array[current_pos:, :, :], **params)
        transformed_board = transform_board_state(state)
        for i, pixel in enumerate(transformed_board):
            r, g, b = pixel.color
            strip.setPixelColor(i, Color(r,g,b))
        time.sleep(wait_ms/1_000.0)
        strip.show()
        current_pos-=1
    
if __name__ == "__main__":
    all_messages=args.messages
    for msg_text in all_messages:
        print("Processing Message...")
        render_message(msg_text)
        print("Message Complete.")
