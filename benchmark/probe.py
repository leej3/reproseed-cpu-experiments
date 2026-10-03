import ctypes as C, hashlib, json, os, pathlib, sys
import numpy as np
from threadpoolctl import threadpool_info
out=pathlib.Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True)
def digest(a): return hashlib.sha256(a.tobytes()).hexdigest()
info={'numpy':np.__version__, 'environment':{k:v for k,v in os.environ.items() if k.startswith(('MKL_','OMP_','OPENBLAS_','NPY_','REPROSEED'))},'cpu_features':np._core._multiarray_umath.__cpu_features__}
rng=np.random.Generator(np.random.PCG64(20261003))
a=rng.standard_normal((257,513)); b=rng.standard_normal((513,193)); x=rng.uniform(.01,10,100003)
info['input_hashes']={k:digest(v) for k,v in [('a',a),('b',b),('x',x)]}
outputs={'numpy_exp':np.exp(x),'numpy_log':np.log(x),'numpy_exp32':np.exp(x.astype(np.float32)), 'numpy_log32':np.log(x.astype(np.float32)), 'numpy_sin32':np.sin(x.astype(np.float32)),'openblas_gemm':a@b}
mkl=C.CDLL(str(pathlib.Path(sys.prefix)/'lib/libmkl_rt.so.2'))
mkl.MKL_CBWR_Get.argtypes=[C.c_int]; mkl.MKL_CBWR_Get.restype=C.c_int
info['mkl_cbwr_raw']=mkl.MKL_CBWR_Get(-1)
info['mkl_auto_branch']=mkl.MKL_CBWR_Get_Auto_Branch()
ver=C.create_string_buffer(512); mkl.MKL_Get_Version_String(ver,C.c_int(512));info['mkl_version']=ver.value.decode()
mkl.cblas_dgemm.argtypes=[C.c_int]*6+[C.c_double,C.c_void_p,C.c_int,C.c_void_p,C.c_int,C.c_double,C.c_void_p,C.c_int]
for m,k,n in [(257,513,193),(8,8193,8),(129,2049,65),(513,513,513)]:
 aa=rng.standard_normal((m,k));bb=rng.standard_normal((k,n));cc=np.zeros((m,n))
 info['input_hashes'][f'mkl_{m}_{k}_{n}']=digest(aa)+':'+digest(bb)
 mkl.cblas_dgemm(101,111,111,m,n,k,1.,aa.ctypes.data,k,bb.ctypes.data,n,0.,cc.ctypes.data,n)
 outputs[f'mkl_{m}_{k}_{n}']=cc
info['threadpools']=threadpool_info();info['hashes']={k:digest(v) for k,v in outputs.items()}
np.savez(out/'outputs.npz',**outputs);(out/'metadata.json').write_text(json.dumps(info,indent=2))
print(json.dumps({'directory':str(out),'cbwr':info['mkl_cbwr_raw'],'hashes':info['hashes']}))
