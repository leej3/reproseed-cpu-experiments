from pathlib import Path
import hashlib
root=Path.cwd(); b=root/'benchmark'; b.mkdir(exist_ok=True)
for src,dst in [('probe.py','probe.py'),('analyze.py','analyze.py'),('candidate-reproseed.sh','candidate-reproseed.sh'),('source/reproseed.sh','upstream-reproseed.sh')]:
 p=b/dst;p.write_bytes((root/src).read_bytes());p.chmod(0o755 if dst.endswith('.sh') else 0o644)
s=(root/'run.py').read_text().replace("root=pathlib.Path(__file__).resolve().parent","root=pathlib.Path(__file__).resolve().parent")
s=s.replace("run=root/'results'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run.mkdir(parents=True)","run=root.parent/'recorded'/'results';run.mkdir(parents=True,exist_ok=True)")
s=s.replace("str(root/'.venv/lib')","str(pathlib.Path(sys.prefix)/'lib')").replace("'source/reproseed.sh'","'upstream-reproseed.sh'").replace('dest.mkdir()','dest.mkdir(exist_ok=True)')
(b/'run_matrix.py').write_text(s)
(root/'.gitignore').write_text((root/'.gitignore').read_text()+'\n.venv/\n.tools/\nsource/\n*.swp\n' if (root/'.gitignore').exists() else '.pixi/\n.venv/\n.tools/\nsource/\n*.swp\n')
(root/'.gitattributes').write_text('* annex.largefiles=(largerthan=1mb)\n*.npz annex.largefiles=anything\n')
