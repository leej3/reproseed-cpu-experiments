import subprocess,json,pathlib
p=pathlib.Path('.')
original=json.loads(subprocess.check_output(['git','show','benchmark-recorded:recorded/numerical-hashes.json'],text=True))
current=json.loads((p/'recorded/numerical-hashes.json').read_text())
assert original==current, 'DataLad rerun changed numerical outputs'
historical={q.parent.name:json.loads(q.read_text())['hashes'] for q in (p/'results/20261003T182617Z').glob('*/metadata.json')}
assert current==historical, 'Pixi environment changed historical numerical outputs'
summary={'recorded_commit':subprocess.check_output(['git','rev-parse','benchmark-recorded'],text=True).strip(),'rerun_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'configurations':len(current),'arrays_per_configuration':len(next(iter(current.values()))),'rerun_hashes_equal':True,'historical_hashes_equal':True}
(p/'provenance-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
