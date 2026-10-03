from pathlib import Path
p=Path('probe.py'); s=p.read_text().replace('MKL_CBWR_Get(0)','MKL_CBWR_Get(-1)');p.write_text(s)
s=Path('source/reproseed.sh').read_text(); needle='    eval "_cur=\\${$_var:-}"\n';assert needle in s
s=s.replace(needle,needle+'    # Experimental narrow fix: preserve explicitly configured MKL CNR.\n    if [ "$_var" = "MKL_CBWR" ] && [ -n "$_cur" ]; then\n        continue\n    fi\n')
p=Path('candidate-reproseed.sh');p.write_text(s);p.chmod(0o755)
p=Path('run.py');s=p.read_text().replace("('native',{},False)","('strict_fixed',{'MKL_CBWR':'AVX2,STRICT'},'fixed'),('compatible_fixed',{'MKL_CBWR':'COMPATIBLE'},'fixed'),('native',{},False)")
s=s.replace("str(root/'source/reproseed.sh')","str(root/('candidate-reproseed.sh' if wrapped == 'fixed' else 'source/reproseed.sh'))")
p.write_text(s)
p=Path('analyze.py');s=p.read_text().replace("['native','pr','strict','strict_pr','compatible','compatible_pr','avx2']","['native','pr','strict','strict_pr','compatible','compatible_pr','avx2','strict_fixed','compatible_fixed']").replace("[('native','pr'),","[('strict','strict_fixed'),('compatible','compatible_fixed'),('native','pr'),")
p.write_text(s)
