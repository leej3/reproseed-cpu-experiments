import json,pathlib
hosts={h:json.loads(pathlib.Path(f'cross-host-inputs/{h}.json').read_text()) for h in ['typhon','smaug','unity']}
comparisons=[]
for other in ['smaug','unity']:
 for case,a in hosts['typhon']['records'].items():
  b=hosts[other]['records'][case]
  assert a['input_hashes']==b['input_hashes'], (other,case,'different inputs')
  comparisons.append({'reference':'typhon','other':other,'case':case,'differing_arrays':[k for k in a['hashes'] if a['hashes'][k]!=b['hashes'][k]]})
summary={'source_commits':{h:d['commit'] for h,d in hosts.items()},'input_hashes_equal':True,'comparisons':comparisons}
pathlib.Path('cross-host-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified identical input hashes for every cross-host comparison.')
