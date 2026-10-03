from pathlib import Path
import subprocess,sys,json,hashlib,platform
root=Path.cwd();out=root/'recorded-v2';out.mkdir(exist_ok=True)
subprocess.run(['duct','--clobber','--fail-time','0','-p',str(out/'duct_'),sys.executable,'benchmark/run_matrix.py'],check=True)
with (out/'analysis.txt').open('w') as f: subprocess.run([sys.executable,'benchmark/analyze.py',str(out/'results')],stdout=f,check=True)
meta={p.parent.name:json.loads(p.read_text())['hashes'] for p in sorted((out/'results').glob('*/metadata.json'))}
(out/'numerical-hashes.json').write_text(json.dumps(meta,indent=2)+'\n')
(out/'host-cpu.txt').write_text(subprocess.check_output(['lscpu'],text=True))
(out/'environment.json').write_text(json.dumps({'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'source_commit':'5f8229787001a946e4e020b68805661272577428','inputs_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('pixi.toml'),Path('pixi.lock'),*sorted(Path('benchmark').glob('*'))] if p.is_file()}},indent=2)+'\n')
print('Recorded matrix; numerical hashes: recorded-v2/numerical-hashes.json')
