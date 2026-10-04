import itertools,json,os,pathlib,random,subprocess,sys
root=pathlib.Path.cwd();torch='--torch' in sys.argv
out=root/'followup-results'/('torch' if torch else 'performance');out.mkdir(parents=True,exist_ok=True)
# Use distinct physical cores on one socket where topology permits, respecting allocation.
allowed=os.sched_getaffinity(0);cores={}
for cpu in sorted(allowed):
 p=pathlib.Path(f'/sys/devices/system/cpu/cpu{cpu}/topology')
 key=((p/'physical_package_id').read_text().strip(),(p/'core_id').read_text().strip())
 cores.setdefault(key,cpu)
chosen=list(cores.values())[:4]
if len(chosen)<4:raise RuntimeError(f'Need 4 allocated physical cores; have {chosen}')
cpuinfo=pathlib.Path('/proc/cpuinfo').read_text()
cases=[('native',None,None),('pr9','upstream-reproseed.sh',None),('compatible','compatible-default.sh',None),('avx2_explicit','compatible-default.sh','AVX2'),('strict_avx2','compatible-default.sh','AVX2,STRICT')]
if 'GenuineIntel' in cpuinfo and 'avx512f' in cpuinfo:cases.append(('strict_avx512','candidate-reproseed.sh','AVX512,STRICT'))
base={k:v for k,v in os.environ.items() if not k.startswith(('MKL_','OMP_','OPENBLAS_','NPY_','REPROSEED','ATEN_','ONEDNN_','DNNL_','KMP_'))}
base.update(MKL_DYNAMIC='FALSE',OMP_DYNAMIC='FALSE',MKL_INTERFACE_LAYER='LP64',OMP_PROC_BIND='close',OMP_PLACES='cores')
(out/'host-cpu.txt').write_text(subprocess.check_output(['lscpu'],text=True));records=[]
for block in range(3):
 combos=list(itertools.product(cases,[1,4]));random.Random(20261004+block).shuffle(combos)
 for (name,wrapper,cbwr),threads in combos:
  env=base|{k:str(threads) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']}
  if cbwr:env['MKL_CBWR']=cbwr
  dest=out/f'{name}-t{threads}-b{block}'
  cmd=[sys.executable,str(root/'benchmark/performance.py'),str(dest)]
  if torch:cmd.append('--torch')
  if block==0:cmd.append('--save-arrays')
  if wrapper:cmd=[str(root/'benchmark'/wrapper)]+cmd
  cmd=['taskset','-c',','.join(map(str,chosen[:threads]))]+cmd
  records.append({'command':cmd,'case':name,'threads':threads,'block':block,'cpu_affinity':chosen[:threads]})
  with dest.with_suffix('.stdout').open('w') as stdout,dest.with_suffix('.stderr').open('w') as stderr:
   subprocess.run(cmd,env=env,stdout=stdout,stderr=stderr,check=True)
  print(name,threads,block,flush=True)
(out/'commands.json').write_text(json.dumps(records,indent=2)+'\n')
