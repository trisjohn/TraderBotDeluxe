
# 1. Design Model (input, output size, forward pass)
# 2. Construct loss and optimizer
# 3. Training Loop
#   a. forward pass: compute prediction
#   b. backward pass: gradients
#   c. update weights

import torch

x = torch.rand(2,2)
print(x)