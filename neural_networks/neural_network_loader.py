import torch as t
import torchvision.datasets as datasets 
import torchvision.transforms as transforms

from network import Network

transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,)),])
mnist_trainset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = t.utils.data.DataLoader(mnist_trainset, batch_size=10, shuffle=True)
mnist_testset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
test_loader = t.utils.data.DataLoader(mnist_testset, batch_size=10, shuffle=True)
    
model = t.load('./models/network_0.pth')
input_data = t.rand(1, 28, 28)
output = model.forward_details(input_data)

print(input_data)
print(model.layer_outputs)