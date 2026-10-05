AI draft - not reviewed by John

## October 5 update: expanded native benchmarks

Read the [condensed report](REPORT.txt) for findings still relevant after
[ReproNim/reproseed#9](https://github.com/ReproNim/reproseed/pull/9) adopted
caller-value preservation and the latest review of
[ReproNim/reproseed#11](https://github.com/ReproNim/reproseed/pull/11).
The October 4 expansion adds 192 native process runs, PyTorch coverage,
and measured AVX2/COMPATIBLE/STRICT performance tradeoffs across three hosts.
See [detailed results](followup-summary.json), [host records](host-results/),
and [provenance](followup-provenance.json). Synthetic raw arrays, checksums, and the combined dataset history bundle
are uploaded to a draft release, pending explicit approval for public release.
They are not yet publicly downloadable. The published metadata and hashes
remain available here.
Archive paths are relative to each host's dataset root; use that host's
`commands.json` to select executed configurations. Extract archives into
separate host directories, not over a Git-annex checkout's symlinks.

The measurements pin earlier code; they do not test current #9. The report
supersedes the historical recommendations below. In particular, current #9
already preserves caller values, including empty values, and intentionally
keeps NumPy lists verbatim. No change to either PR is included here.
The old COMPATIBLE patch and proposed-code directory are historical evaluated
artifacts, not a recommendation to apply them unchanged to current #9.
`followup-provenance.json` records the investigation's original local-only
scope; publication was subsequently authorized on October 5.

---

## Historical October 3 investigation (pinned old PR revisions)

# CPU reproducibility experiments for reproseed PR 9

These experiments support [ReproNim/reproseed#9](https://github.com/ReproNim/reproseed/pull/9)
and [the proposed preservation of explicit MKL CNR settings and NumPy exclusions](https://github.com/ReproNim/reproseed/pull/11).
The scripts, locked Pixi environment, DataLad executions, runtime diagnostics,
and output arrays are preserved here. Upstream revision: `5f8229787001a946e4e020b68805661272577428`.

## Main findings

1. **Preserve MKL STRICT.** On Typhon, direct `AVX2,STRICT` made all four tested
   double-precision GEMMs identical across 1/2/4 threads. The original PR drops
   STRICT and three shapes vary with thread count. Preserving the explicit value
   restores the direct results. For `(m,k,n)=(8,8193,8)`, the PR's 1-vs-2-thread
   comparison differs in 62/64 elements, maximum absolute error `1.652011860642233e-13`.
2. **Merge NumPy exclusions.** Starting with `NPY_DISABLE_CPU_FEATURES=X86_V3`, the
   candidate retains it and adds the PR's exclusions. All five NumPy outputs match
   explicitly supplying the combined list. On Typhon, original PR versus candidate
   differs in 39,313 float32 exp values, 11,739 log values, and 14,227 sin values
   out of 100,003 each. Maximum absolute differences are 0.001953125,
   4.76837158203125e-7, and 5.960464477539063e-8 respectively. The original PR had
   removed X86_V3; the recorded feature map verifies its preservation by the fix.
3. **The default profile helps, but MKL differs across vendors in this matrix.**
   At each fixed thread count, all ten PR-controlled arrays agree between the two
   Intel hosts. Against Unity AMD, the six NumPy/OpenBLAS arrays agree, but all four
   MKL products differ. On AMD, MKL's CNR query reports AUTO (2) for the PR's AVX2
   request, whereas Typhon reports AVX2 (10). Explicit COMPATIBLE preserved by the
   candidate yields agreement of all ten arrays across all three hosts at each
   fixed thread count. This is an observed result for these versions and inputs,
   not a claim of arbitrary workload equivalence.
4. **Separate CNR enablement from branch selection.** On Typhon, explicitly setting
   AVX512 versus AVX2 (standard CNR enabled in both cases) changes all four MKL
   products. NumPy and OpenBLAS outputs in that controlled comparison are identical.
   This supports a branch-selection effect without attributing every difference
   in an uncontrolled native-vs-wrapper comparison solely to AVX512 instructions.

## Hosts and recorded executions

Each host ran 14 configurations x 3 thread counts x 2 fresh processes = 84 runs,
with 10 output arrays per run. All 42 repeat pairs per host were bitwise identical.
Input byte hashes match in every cross-host comparison.

| Host | CPU | ISA | DataLad execution | Git branch |
|---|---|---|---|---|
| Typhon | Intel Xeon Silver 4309Y | AVX512 | `c3fa2559a942cebce693fd6f9608ee77558855ab` | `master` |
| Smaug | Intel Xeon E5-2623 v3 | AVX2 | rerun `686cd602c70c3ba19bc79633e2ec44cd4706c88b` | `smaug-results` |
| Unity cpu053 | AMD EPYC 7763 | AVX2 | rerun `e37bd9e1163d1e59c4f3f86e333c22979621d4fd` | `unity-results` |

Unity ran via Slurm job 65197091 with 4 CPUs and 4 GiB; its script and log are on
`unity-results` under `scheduler/`. Both reruns execute the Typhon DataLad run,
not a separately rewritten benchmark. No numerical work ran on Unity's login node.

## Inspect and reproduce

```sh
git clone https://github.com/leej3/reproseed-cpu-experiments.git
cd reproseed-cpu-experiments
pixi install --locked
# Re-execute the recorded finalized benchmark; outputs are under recorded-v2/.
pixi run --locked datalad rerun c3fa2559a942cebce693fd6f9608ee77558855ab
# Or record a new execution with the same declared inputs and outputs:
pixi run --locked benchmark-v2
```

Use a supported Linux x86-64 host. CPU availability affects the results and is
recorded. Environment variables are set before library import. Each run fixes
OMP/MKL/OpenBLAS threads to 1, 2, or 4 and sets both dynamic-thread controls FALSE.
MKL is 2025.2.0, NumPy 2.4.2, Python 3.13.5; complete packages/builds are in pixi.lock.
No GPU, PyTorch, or oneDNN numerical tests are included.

DataLad records command, inputs and outputs; Pixi supplies the environment.
Keep the recorded code/lock revision when reproducing. `PROVENANCE.md` describes
the earlier v1 workflow; the finalized v2 command above supersedes it.

### Retrieve arrays

Each host branch has `recorded-v2/` with diagnostics, raw-array SHA256 hashes,
full NPZ arrays, and `results/comparisons.json` (bitwise equality, differing counts,
maximum absolute and relative differences). Archives are hosted in the
[cpu-matrix-v2 release](https://github.com/leej3/reproseed-cpu-experiments/releases/tag/cpu-matrix-v2).
DataLad's archive remote maps individual annexed arrays to these assets:

```sh
pixi run git annex enableremote datalad-archives
pixi run datalad get recorded-v2/results/strict-t1-r1/outputs.npz
# For another host, use a separate clone with --branch smaug-results or unity-results.
```

`cross-host-inputs/` contains the exact metadata collected from each host's Git
history, including the source commit. `summarize.py` verifies identical inputs
and computes `cross-host-summary.json`. No tolerance threshold is used for
bitwise comparisons; small numerical differences are not asserted to have
scientific significance. Published archives contain the final v2 arrays; older
v1 results remain historical metadata and are not all available from the release.

## Review scope and references

Proposed changes: retain explicit MKL CNR (warn on unverified/out-of-profile
settings); merge NumPy exclusions without duplicate growth; describe the profile
as configuring supported libraries; document MKL vendor/thread requirements and
oneDNN's build dependency. The candidate script is `benchmark/candidate-reproseed.sh`.
The shell patch passed ShellCheck and all 21 Bats tests on Linux.

- [Intel CNR conditions](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-2/reproducibility-conditions.html)
- [Intel branch semantics](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-2/specifying-code-branches.html)
- [CNR diagnostic API](https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2025-2/mkl-cbwr-get.html)
- [NumPy runtime controls](https://numpy.org/doc/stable/reference/simd/build-options.html#runtime-dispatch)
- [oneDNN build/runtime controls](https://uxlfoundation.github.io/oneDNN/dev_guide_cpu_dispatcher_control.html)

The early harness corrections and initial historical runs are documented in Git
history. Current claims use finalized v2 recorded runs and reruns. This dataset
provides execution provenance and retrievable evidence; it does not establish
all STAMPED properties or universal numerical equivalence.
