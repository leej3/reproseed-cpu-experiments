# Recorded benchmark workflow

Run from `/home/leej3/reproseed` on Typhon. Pixi 0.81.0 was installed locally at
`.tools/pixi`; no system software or shell configuration was changed.

```sh
.tools/pixi install --locked
.tools/pixi run --locked benchmark
.tools/pixi run --locked reproduce
```

The `benchmark` task executes:

```sh
datalad run -m numerical-matrix --explicit \
  -i pixi.toml -i pixi.lock -i benchmark -i execute_recorded.py \
  -o recorded python execute_recorded.py
```

The `reproduce` task executes `datalad rerun benchmark-recorded` through Pixi.
The stable local tag `benchmark-recorded` identifies the verified original run:
`d6235f1a062554fae05208dcb7b388a10acb14f3`.
The verified rerun is `374553c44943f309967aa2e7a882d59cdbcd97f5`.
Alternatively, use the immutable recorded commit directly:

```sh
.tools/pixi run --locked datalad rerun d6235f1a062554fae05208dcb7b388a10acb14f3
```

Keep the dataset clean and the recorded lock/code revision checked out when
reproducing. DataLad records the command and input/output paths; Pixi resolves the
software environment. DataLad rerun alone does not provision the Pixi environment.

## Evidence

- `benchmark/`: tracked snapshots of the exact upstream script, candidate, probe,
  matrix runner, and analyzer. Upstream revision is
  `5f8229787001a946e4e020b68805661272577428`.
- `pixi.toml`, `pixi.lock`: project-local DataLad, git-annex, duct, Python and
  numerical dependencies. Uses conda-forge Python 3.13.5, with PyPI NumPy 2.4.2
  and MKL 2025.2.0 plus explicitly pinned original runtime dependencies.
- `recorded/`: declared DataLad output, containing raw arrays, metadata, command
  records, CPU details, comparisons, and duct logs. Arrays are in git-annex.
- `recorded/numerical-hashes.json`: SHA256 of raw numerical array bytes.
- `provenance-verification.json`: verified original/rerun commits and comparisons.
- `verify_provenance.py`: checks rerun and historical numerical hashes.

All 54 configurations x 7 arrays = 378 hashes match between the recorded run,
DataLad rerun, and the historical final run. Logs/timing and NPZ packaging may
change on rerun; numerical equality is checked on raw array bytes.

The older timestamped results were saved as historical evidence, not retroactively
represented as DataLad runs. Their original `.venv` remains untouched and ignored.
The live `source/` checkout is also ignored and unchanged; it had an editor swap
file when provenance was added. The recorded benchmark uses tracked snapshots.

This dataset now supports traceable execution and rerun; it does not itself prove
all STAMPED properties, cross-host equality, or availability of annex content from
another machine. No remote publication or backup was configured. All commits and
the run tag are local to Typhon. The original PR was not modified.

References:
- https://docs.datalad.org/en/stable/generated/man/datalad-run.html
- https://docs.datalad.org/en/stable/generated/man/datalad-rerun.html
- https://pixi.prefix.dev/latest/workspace/lockfile/
