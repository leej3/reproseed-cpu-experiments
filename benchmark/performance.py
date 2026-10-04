"""Native warmed compute timing. No imports/startup/input generation inside timing."""
import argparse,ctypes as C,hashlib,json,os,pathlib,statistics,sys,time
import numpy as np
from threadpoolctl import threadpool_info
p=argparse.ArgumentParser();p.add_argument('out');p.add_argument('--torch',action='store_true');p.add_argument('--save-arrays',action='store_true');args=p.parse_args()
out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
digest=lambda x:hashlib.sha256(x.tobytes()).hexdigest()
rng=np.random.Generator(np.random.PCG64(20261004)); inputs={};outputs={};measurements={}
def bench(name,fn,input_arrays):
 inputs[name]=[digest(a) for a in input_arrays]
 for _ in range(3): result=fn()
 start=time.perf_counter();result=fn();dt=time.perf_counter()-start
 count=max(1,min(10000,int(.08/max(dt,1e-9))))
 samples=[];hashes=[]
 for _ in range(7):
  start=time.perf_counter()
  for _ in range(count): result=fn()
  samples.append((time.perf_counter()-start)/count)
  arr=result.detach().numpy() if hasattr(result,'detach') else result
  hashes.append(digest(arr))
 outputs[name]=arr.copy()
 med=statistics.median(samples)
 measurements[name]={'seconds':samples,'iterations_per_sample':count,'median_seconds':med,'min_seconds':min(samples),'max_seconds':max(samples),'relative_mad':statistics.median(abs(x-med) for x in samples)/med,'output_hashes':hashes,'repeat_identical':len(set(hashes))==1}
meta={'environment':{k:v for k,v in os.environ.items() if k.startswith(('MKL_','OMP_','OPENBLAS_','NPY_','REPROSEED','ATEN_','ONEDNN_','DNNL_'))},'affinity':sorted(os.sched_getaffinity(0)),'loadavg':os.getloadavg(),'numpy':np.__version__}
if args.torch:
 import torch
 torch.set_num_threads(int(os.environ['OMP_NUM_THREADS']));torch.set_num_interop_threads(1)
 meta.update(torch_version=torch.__version__,torch_build=torch.__config__.show(),aten_cpu_capability=torch.backends.cpu.get_cpu_capability(),mkldnn_available=torch.backends.mkldnn.is_available(),mkldnn_enabled=torch.backends.mkldnn.enabled)
 with torch.inference_mode():
  a=rng.standard_normal((1024,1024)).astype('float32');b=rng.standard_normal((1024,1024)).astype('float32');ta=torch.from_numpy(a);tb=torch.from_numpy(b)
  bench('torch_mm1024',lambda:ta@tb,[a,b])
  x=rng.uniform(.01,10,1000003).astype('float32');tx=torch.from_numpy(x)
  bench('torch_exp32',lambda:torch.exp(tx),[x])
  x=rng.standard_normal((4,32,64,64)).astype('float32');w=rng.standard_normal((64,32,3,3)).astype('float32');tx=torch.from_numpy(x);tw=torch.from_numpy(w)
  bench('torch_conv2d',lambda:torch.nn.functional.conv2d(tx,tw,padding=1),[x,w])
  x=rng.standard_normal((1,8,32,32,32)).astype('float32');w=rng.standard_normal((16,8,3,3,3)).astype('float32');tx=torch.from_numpy(x);tw=torch.from_numpy(w)
  bench('torch_conv3d',lambda:torch.nn.functional.conv3d(tx,tw,padding=1),[x,w])
else:
 mkl=C.CDLL(str(pathlib.Path(sys.prefix)/'lib/libmkl_rt.so.2'))
 mkl.MKL_CBWR_Get.argtypes=[C.c_int];mkl.MKL_CBWR_Get.restype=C.c_int
 meta['mkl_cbwr_raw']=mkl.MKL_CBWR_Get(-1)
 ver=C.create_string_buffer(512);mkl.MKL_Get_Version_String(ver,C.c_int(512));meta['mkl_version']=ver.value.decode()
 mkl.cblas_dgemm.argtypes=[C.c_int]*6+[C.c_double,C.c_void_p,C.c_int,C.c_void_p,C.c_int,C.c_double,C.c_void_p,C.c_int]
 for m,k,n in [(1024,1024,1024),(256,4096,256),(8,8193,8)]:
  a=rng.standard_normal((m,k));b=rng.standard_normal((k,n));c=np.empty((m,n))
  def gemm():
   mkl.cblas_dgemm(101,111,111,m,n,k,1.,a.ctypes.data,k,b.ctypes.data,n,0.,c.ctypes.data,n);return c
  bench(f'mkl_{m}_{k}_{n}',gemm,[a,b])
 a=rng.standard_normal((1024,1024));b=rng.standard_normal((1024,1024));c=np.empty((1024,1024))
 bench('openblas1024',lambda:np.matmul(a,b,out=c),[a,b])
 x=rng.uniform(.01,10,1000003).astype('float32');y=np.empty_like(x)
 bench('numpy_exp32',lambda:np.exp(x,out=y),[x])
meta['threadpools']=threadpool_info();meta['inputs']=inputs;meta['measurements']=measurements
(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
if args.save_arrays:np.savez(out/'outputs.npz',**outputs)
print(json.dumps({'out':str(out),'medians':{k:v['median_seconds'] for k,v in measurements.items()}}))
