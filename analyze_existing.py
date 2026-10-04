import itertools,json,pathlib
root=pathlib.Path('cross-host-inputs')
hosts={h:json.loads((root/f'{h}.json').read_text())['records'] for h in ['typhon','smaug','unity']}
result={}
for case in ['native','pr','compatible_fixed','strict_fixed']:
 pairs=[]
 for (ha,ta),(hb,tb) in itertools.combinations(itertools.product(hosts,[1,2,4]),2):
  a=hosts[ha][f'{case}-t{ta}-r1']; b=hosts[hb][f'{case}-t{tb}-r1']
  assert a['input_hashes']==b['input_hashes']
  pairs.append({'a':[ha,ta],'b':[hb,tb],'differing_arrays':[k for k in a['hashes'] if a['hashes'][k]!=b['hashes'][k]]})
 result[case]=pairs
out=pathlib.Path('followup-results');out.mkdir(exist_ok=True)
(out/'existing-cross-thread-host.json').write_text(json.dumps(result,indent=2)+'\n')
for case,pairs in result.items():
 print(case,'of',len(pairs),'host/thread pairs; all arrays identical in',sum(not p['differing_arrays'] for p in pairs))
 for h in hosts:
  print(h,sorted({k for p in pairs if p['a'][0]==p['b'][0]==h for k in p['differing_arrays']}))
