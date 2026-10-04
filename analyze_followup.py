import itertools,json,pathlib,statistics
root=pathlib.Path('host-results'); data={};timings=[];repeats=[];comparisons=[]
for host in ['typhon','smaug','unity']:
 for mode in ['performance','torch']:
  path=root/host/'followup-results'/mode
  if not (path/'commands.json').exists():continue
  commands=json.loads((path/'commands.json').read_text())
  # A DataLad rerun can retain original-host outputs for skipped configurations.
  # Only entries actually executed in this host's command manifest are evidence.
  for command in commands:
   case,t,b=command['case'],command['threads'],command['block']
   name=f'{case}-t{t}-b{b}'
   meta=json.loads((path/name/'metadata.json').read_text())
   assert meta['affinity']==command['cpu_affinity'], (host,name)
   data[host,mode,case,t,b]=meta
  for case,t in sorted({(c['case'],c['threads']) for c in commands}):
   ds=[data[host,mode,case,t,b] for b in range(3)]
   assert all(d['inputs']==ds[0]['inputs'] for d in ds)
   for workload in ds[0]['measurements']:
    runs=[d['measurements'][workload] for d in ds]
    medians=[r['median_seconds'] for r in runs];med=statistics.median(medians)
    base=statistics.median(data[host,mode,'pr9',t,b]['measurements'][workload]['median_seconds'] for b in range(3))
    native=statistics.median(data[host,mode,'native',t,b]['measurements'][workload]['median_seconds'] for b in range(3))
    timings.append(dict(host=host,mode=mode,case=case,threads=t,workload=workload,median_seconds=med,ratio_pr9=med/base,ratio_native=med/native,process_medians=medians,process_spread=(max(medians)-min(medians))/med,max_sample_relative_mad=max(r['relative_mad'] for r in runs)))
    hashes={h for r in runs for h in r['output_hashes']}
    repeats.append(dict(host=host,mode=mode,case=case,threads=t,workload=workload,all_21_identical=len(hashes)==1))
for mode in ['performance','torch']:
 for case in ['native','pr9','compatible','avx2_explicit','strict_avx2']:
  keys=[k for k in data if k[1]==mode and k[2]==case and k[4]==0]
  for ka,kb in itertools.combinations(keys,2):
   a,b=data[ka],data[kb];assert a['inputs']==b['inputs'],(ka,kb)
   comparisons.append(dict(mode=mode,case=case,a=[ka[0],ka[3]],b=[kb[0],kb[3]],different=[w for w in a['measurements'] if a['measurements'][w]['output_hashes'][0]!=b['measurements'][w]['output_hashes'][0]]))
equivalence=[]
for (host,mode,case,t,b),a in data.items():
 if case!='pr9':continue
 other=data[host,mode,'avx2_explicit',t,b]
 assert a['inputs']==other['inputs']
 different=[w for w in a['measurements'] if a['measurements'][w]['output_hashes'][0]!=other['measurements'][w]['output_hashes'][0]]
 assert not different,(host,mode,t,b,different)
 equivalence.append(dict(host=host,mode=mode,threads=t,block=b,all_equal=True))
result=dict(timings=timings,repeat_consistency=repeats,comparisons=comparisons,pr9_equals_explicit_avx2=equivalence)
pathlib.Path('followup-summary.json').write_text(json.dumps(result,indent=2)+'\n')
for h in ['typhon','smaug','unity']:
 print('\nHOST',h)
 for t in [1,4]:
  for r in timings:
   if r['host']==h and r['threads']==t and r['case']=='compatible':
    print(t,r['workload'],f"{r['ratio_pr9']:.2f}x PR9",f"{r['ratio_native']:.2f}x native",f"spread {r['process_spread']:.1%}")
print('Nonrepeatable:',[r for r in repeats if not r['all_21_identical']])
for c in comparisons:
 if c['case'] in ['compatible','pr9','strict_avx2'] and c['a'][1]==c['b'][1] and c['a'][0]!=c['b'][0]:print(c)
