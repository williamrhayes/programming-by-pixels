import torch.nn as nn

class Network(nn.Module):
    def __init__(self, *args, input_size=28*28, final_output_size=10):
        super(Network, self).__init__()
        
        # Validate that at least two layers are specified
        if len(args) < 2:
            raise ValueError("At least two layer sizes must be specified (input and output).")
        
        # Create a list to hold the layers
        layers = []
        
        # Iterate over the args to create linear layers
        for output_size in args:
            layers.append(nn.Linear(input_size, output_size))
            input_size = output_size  # Update the input size for the next layer

        # Apply the last layer (fixed ouptut size)
        layers.append(nn.Linear(input_size, final_output_size))
        
        layers.append(nn.ReLU())

        # Combine all layers into a Sequential module
        self.network = nn.Sequential(*layers)
    
    def forward(self, img):
        # Convert and flatten the input image
        x = img.view(-1, 28 * 28)
        # Pass through the Sequential model
        x = self.network(x)
        return x
    
    # Method similar to forward, but returns the values
    # of the neurons in each individual layer as output
    def forward_details(self, img):
        x = img.view(-1, 28 * 28)
        self.layer_outputs = []  # Clear previous outputs
        # Pass through each layer manually to collect outputs
        for layer in self.network:
            x = layer(x)
            self.layer_outputs.append(x)  # Save the output at this step
        return x