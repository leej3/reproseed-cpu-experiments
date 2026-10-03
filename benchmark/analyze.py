import pathlib,json,sys,numpy as np
root=pathlib.Path(sys.argv[1]); rows=[]
def compare(a,b):
 ma=json.loads((root/a/'metadata.json').read_text());mb=json.loads((root/b/'metadata.json').read_text());assert ma['input_hashes']==mb['input_hashes']
 aa=np.load(root/a/'outputs.npz');bb=np.load(root/b/'outputs.npz')
 stats={}
 for k in aa.files:
  x,y=aa[k],bb[k];d=np.abs(x-y)
  stats[k]={'equal':bool(x.tobytes()==y.tobytes()),'different_elements':int(np.count_nonzero(x!=y)),'max_abs':float(d.max()),'max_rel':float(np.max(d/np.maximum(np.maximum(np.abs(x),np.abs(y)),np.finfo(float).tiny)))}
 rows.append({'a':a,'b':b,'stats':stats})
for name in ['native','pr','strict','strict_pr','compatible','compatible_pr','avx2','strict_fixed','compatible_fixed','numpy_existing','numpy_expected','numpy_pr','numpy_fixed','avx512']:
 for t in [1,2,4]:compare(f'{name}-t{t}-r1',f'{name}-t{t}-r2')
 for t in [2,4]:compare(f'{name}-t1-r1',f'{name}-t{t}-r1')
for a,b in [('numpy_expected','numpy_fixed'),('numpy_existing','numpy_pr'),('numpy_pr','numpy_fixed'),('avx512','avx2'),('strict','strict_fixed'),('compatible','compatible_fixed'),('native','pr'),('strict','strict_pr'),('compatible','compatible_pr'),('avx2','strict_pr')]:
 for t in [1,2,4]:compare(f'{a}-t{t}-r1',f'{b}-t{t}-r1')
(root/'comparisons.json').write_text(json.dumps(rows,indent=2))
for row in rows:
 diffs={k:v for k,v in row['stats'].items() if not v['equal']}
 if diffs: print(row['a'],row['b'],json.dumps(diffs))
for name in ['native','pr','strict','strict_pr','compatible','compatible_pr','avx2','strict_fixed','compatible_fixed','numpy_existing','numpy_expected','numpy_pr','numpy_fixed','avx512']:
 m=json.loads((root/f'{name}-t1-r1/metadata.json').read_text()); print(name,'cbwr',m['mkl_cbwr_raw'],'pools',[(p.get('internal_api'),p.get('architecture'),p.get('version'),p.get('num_threads')) for p in m['threadpools']])
