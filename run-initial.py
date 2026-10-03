import os,pathlib,subprocess,sys,json,datetime
root=pathlib.Path(__file__).resolve().parent
run=root/'results'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run.mkdir(parents=True)
base={k:v for k,v in os.environ.items() if not k.startswith(('MKL_','OMP_','OPENBLAS_','NPY_','REPROSEED','ATEN_','ONEDNN_','DNNL_'))}
base.update(REPROSEED='1',MKL_DYNAMIC='FALSE',OMP_DYNAMIC='FALSE',MKL_INTERFACE_LAYER='LP64',LD_LIBRARY_PATH=str(root/'.venv/lib'))
cases=[('native',{},False),('pr',{},True),('strict',{'MKL_CBWR':'AVX2,STRICT'},False),('strict_pr',{'MKL_CBWR':'AVX2,STRICT'},True),('compatible',{'MKL_CBWR':'COMPATIBLE'},False),('compatible_pr',{'MKL_CBWR':'COMPATIBLE'},True),('avx2',{'MKL_CBWR':'AVX2'},False)]
for name,extra,wrapped in cases:
 for threads in [1,2,4]:
  for repeat in [1,2]:
   dest=run/f'{name}-t{threads}-r{repeat}';dest.mkdir()
   env=dict(base,OMP_NUM_THREADS=str(threads),MKL_NUM_THREADS=str(threads),OPENBLAS_NUM_THREADS=str(threads),**extra)
   cmd=[sys.executable,str(root/'probe.py'),str(dest)]
   if wrapped:cmd=[str(root/'source/reproseed.sh')]+cmd
   p=subprocess.run(cmd,env=env,capture_output=True,text=True)
   (dest/'stdout.txt').write_text(p.stdout);(dest/'stderr.txt').write_text(p.stderr)
   (dest/'command.json').write_text(json.dumps({'command':cmd,'exit':p.returncode},indent=2))
   print(dest.name,p.returncode,flush=True)
   if p.returncode:raise SystemExit(p.stderr)
print('RESULTS='+str(run))
