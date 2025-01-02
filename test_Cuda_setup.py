import torch

print(torch.version.cuda)  # Should match the installed CUDA version
print(torch.backends.cudnn.version())  # Should correspond to cuDNN version

print("CUDA Available:", torch.cuda.is_available())
print("CUDA Device Count:", torch.cuda.device_count())
print("CUDA Device Name:", torch.cuda.get_device_name(0))

a = torch.rand(10000, 10000).to("cuda")
b = torch.matmul(a, a)
print(b)
