import torch
import GPUtil

print(torch.cuda.is_available())

print(GPUtil.getAvailable())
