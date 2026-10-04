import os,pathlib,subprocess,sys
out=pathlib.Path('followup-results/dispatch');out.mkdir(parents=True,exist_ok=True)
base={k:v for k,v in os.environ.items() if not k.startswith(('MKL_','OMP_','OPENBLAS_','NPY_','REPROSEED','ATEN_','ONEDNN_','DNNL_'))}
base.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',MKL_DYNAMIC='FALSE',OMP_DYNAMIC='FALSE',MKL_VERBOSE='1')
for case,wrapper in [('native',None),('pr9','upstream-reproseed.sh'),('compatible','compatible-default.sh')]:
 cmd=[sys.executable,'benchmark/dispatch.py']
 if wrapper:cmd=['benchmark/'+wrapper]+cmd
 with (out/(case+'.log')).open('w') as f:subprocess.run(cmd,env=base,stdout=f,stderr=subprocess.STDOUT,check=True)
