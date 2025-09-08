This python code is designed to allow a Raspberry Pi to control a [WS2812B Individually addressable LED matrix](https://www.amazon.com/BTF-LIGHTING-Individual-Addressable-Flexible-Controllers/dp/B088BTXHRG).
More details can be found on my blog [Programming by Pixels](https://dimmin.com/blog/post/15/), https://dimmin.com/blog/post/15/

# Visualization Examples
## Image Banners
Users can render banners with the same dimensions (<img width="32" height="8" alt="poker" src="https://github.com/user-attachments/assets/0c24526a-33b6-4914-ac53-97ded113db92" />) across their matrix
https://github.com/user-attachments/assets/a67e59f7-d6ca-4201-83b0-aaa9855efaa0

## Sending Messages
Users can pass arguments to their raspberry pi and render messages across their 32 x 8 LED matrix using the command
```bash
sudo python3 4_send_message.py -m "DIMMiN says hello!" -rgb 230 35 75 -s 20
```
https://github.com/user-attachments/assets/eefb193d-1e15-4916-a32a-69994f48bbcb

## Conway's Game of Life
[Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) can be simulated, using each LED to represent a cell:
https://github.com/user-attachments/assets/749e79f2-8329-4b20-a1c1-474197ae94c3

# Depth First Search (DFS)
Depth First Search can be deployed to visualize solving a maze:
https://github.com/user-attachments/assets/8d5d6a1f-4a95-4238-8ba6-62dbc4b105dc

# Neural Network Inference
The inference on the MNIST dataset can be visualized on different neural network architectures:
https://github.com/user-attachments/assets/ce83c92e-6526-4b19-ac69-eab45aa8e404
