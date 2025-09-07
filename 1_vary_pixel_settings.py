from rpi_ws281x import Adafruit_NeoPixel, Color
import argparse

# Parse the CLI for arguments about our pixel
parser = argparse.ArgumentParser(
    prog="PixelPosition",
    description="Learn about the pixel matrix and alter individual pixel states",
)

parser.add_argument("-n", "--pixelnum", type=int, help="The pixel number to activate.", default=0)
parser.add_argument("-br", "--brightness", type=int, help="The brightness of the display, 0 is darkest and 255 is brightest.", default=25)
parser.add_argument("-rgb", type=int, help="The r, g, and b value of the activated pixel.", nargs=3, default=[255,255,255])
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

# Set the first pixel to high brightness
pixel_num = args.pixelnum
r,g,b = args.rgb
strip.setPixelColor(pixel_num, Color(r,g,b))
strip.show()
