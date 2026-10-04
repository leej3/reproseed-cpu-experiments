import os,torch
print('torch',torch.__version__,'ATen',torch.backends.cpu.get_cpu_capability(),flush=True)
torch.set_num_threads(1)
with torch.inference_mode():
 a=torch.ones((1024,1024));b=a.clone();c=a@b
 with torch.backends.mkldnn.verbose(torch.backends.mkldnn.VERBOSE_ON):
  x=torch.ones((4,32,64,64));w=torch.ones((64,32,3,3));torch.nn.functional.conv2d(x,w,padding=1)
  x=torch.ones((1,8,32,32,32));w=torch.ones((16,8,3,3,3));torch.nn.functional.conv3d(x,w,padding=1)
