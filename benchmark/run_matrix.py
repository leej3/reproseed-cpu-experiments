import os,pathlib,subprocess,sys,json,datetime
root=pathlib.Path(__file__).resolve().parent
run=root.parent/'recorded'/'results';run.mkdir(parents=True,exist_ok=True)
base={k:v for k,v in os.environ.items() if not k.startswith(('MKL_','OMP_','OPENBLAS_','NPY_','REPROSEED','ATEN_','ONEDNN_','DNNL_'))}
base.update(REPROSEED='1',MKL_DYNAMIC='FALSE',OMP_DYNAMIC='FALSE',MKL_INTERFACE_LAYER='LP64',LD_LIBRARY_PATH=str(pathlib.Path(sys.prefix)/'lib'))
cases=[('strict_fixed',{'MKL_CBWR':'AVX2,STRICT'},'fixed'),('compatible_fixed',{'MKL_CBWR':'COMPATIBLE'},'fixed'),('native',{},False),('pr',{},True),('strict',{'MKL_CBWR':'AVX2,STRICT'},False),('strict_pr',{'MKL_CBWR':'AVX2,STRICT'},True),('compatible',{'MKL_CBWR':'COMPATIBLE'},False),('compatible_pr',{'MKL_CBWR':'COMPATIBLE'},True),('avx2',{'MKL_CBWR':'AVX2'},False)]
for name,extra,wrapped in cases:
 for threads in [1,2,4]:
  for repeat in [1,2]:
   dest=run/f'{name}-t{threads}-r{repeat}';dest.mkdir(exist_ok=True)
   env=dict(base,OMP_NUM_THREADS=str(threads),MKL_NUM_THREADS=str(threads),OPENBLAS_NUM_THREADS=str(threads),**extra)
   cmd=[sys.executable,str(root/'probe.py'),str(dest)]
   if wrapped:cmd=[str(root/('candidate-reproseed.sh' if wrapped == 'fixed' else 'upstream-reproseed.sh'))]+cmd
   p=subprocess.run(cmd,env=env,capture_output=True,text=True)
   (dest/'stdout.txt').write_text(p.stdout);(dest/'stderr.txt').write_text(p.stderr)
   (dest/'command.json').write_text(json.dumps({'command':cmd,'exit':p.returncode},indent=2))
   print(dest.name,p.returncode,flush=True)
   if p.returncode:raise SystemExit(p.stderr)
print('RESULTS='+str(run))
