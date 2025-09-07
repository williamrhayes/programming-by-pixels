import time
import argparse
import colorsys
from rpi_ws281x import Adafruit_NeoPixel, Color
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from network import Network

parser = argparse.ArgumentParser(
    prog="NeuralNetwork",
    description="View the inner architecture of a neural network evaluated on the MNIST dataset.",
)
parser.add_argument("-n", "--network", type=int, help="The network architecture to use during evaluation.", default=0)
parser.add_argument("-img", "--image", type=int, help="Whether to display the original image during evaluation. If not 1, we don't show", default=0)
parser.add_argument("-s", "--speed", type=int, help="Speed (ms) between evaluations.", default=1_000)


args = parser.parse_args()

# LED strip configuration:
LED_COUNT      = 256       # Number of LED pixels.
LED_PIN        = 18       # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800_000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 1        # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0        # set to '1' for GPIOs 13, 19, 41, 45 or 53

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

# Clear the LED strip before beginning the game
for i in range(strip.numPixels()): strip.setPixelColor(i, Color(0,0,0))
strip.show()

# Load in our model
model = torch.load(f"./models/network_{args.network}.pth")

# Load in our evaluation images
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,)),])
mnist_testset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
test_loader = torch.utils.data.DataLoader(mnist_testset, batch_size=10, shuffle=True)

# A board is a matrix of cells   
class Pixel():
    def __init__(self, color=[0,0,0]):
        self.color = color

# Transform the board state matrix so that it directly
# maps onto the LED baord
def transform_board_state(state):
    # The board alternates indices, to make it match
    # the matrix we need to flip every other column
    # before outputting it to the board
    transformed_state = []
    for row, col in enumerate(state):
        if row % 2:
            col = np.flip(col)
        transformed_state.append(col)
    transformed_state = np.array(transformed_state)
        
    return np.flip(transformed_state).ravel()

def visualize_network_architecture(layer_outputs, size=(32,8)):
    state = np.zeros_like(size[0]*size[1], shape=size, dtype=Pixel)
    for y, layer in enumerate(layer_outputs[:-1]):
        layer_data = layer[0]
        start_idx = (size[0] - len(layer_data)) // 2
        state[start_idx:start_idx + len(layer_data), y] = layer_data[:32].detach().numpy()
        
    final_output, = layer_outputs[-1]
    start_idx = (size[0] - 10) // 2
    state[start_idx:start_idx + len(final_output), -1] = final_output.detach().numpy()
        
    return state

# Map the color to the value / weight of the neuron
# upon evaluation
def map_color(value, min_value, max_value):
    normalized_value = (value - min_value) / (max_value - min_value)
    hue = 0.33 * normalized_value
    rgb = colorsys.hsv_to_rgb(hue,1,1)
    scaled_rgb = [int(val*255) for val in rgb]
    return scaled_rgb

print("evaluating...")
with torch.no_grad():
    for data in test_loader:
        x, y = data
        for i, sample_x in enumerate(x):
            # Apply our model to the input dataset
            output = model.forward_details(sample_x)
            # Visualize our network parameters on the LED matrix
            final_predictions = model.layer_outputs[-1][0].detach().numpy()
            predicted_val = np.argmax(final_predictions)
            pre_transformed_state = visualize_network_architecture(model.layer_outputs)
            transformed_state = transform_board_state(pre_transformed_state)
            print(f"True Label: {y[i]}")
            print(f"Model Predicts: {predicted_val}")
    
            for i, val in enumerate(transformed_state):
                if val == 0:
                    strip.setPixelColor(i, Color(0,0,0))
                else:
                    r, g, b = map_color(val, min_value=min(transformed_state), max_value=max(transformed_state))
                    strip.setPixelColor(i, Color(r,g,b))
            
            strip.show()
            
            # Visualize our input image on the computer
            if args.image == 1:
                plt.imshow(sample_x.view(28, 28))
                plt.show()
                
            time.sleep(args.speed / 1_000)
