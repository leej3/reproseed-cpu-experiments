# reproseed PR 9: Typhon numerical investigation

Recommendation: preserve explicit MKL_CBWR settings. The PR removes STRICT and
introduces thread-count-dependent output in the tested GEMM workloads. The isolated
candidate restores the direct STRICT results. This is a demonstrated bitwise
reproducibility regression, not a demonstrated scientific-significance error.

## Recorded experiment

- Host: Typhon, Intel Xeon Silver 4309Y, Linux x86_64 with AVX512/FMA.
- Source: source/ detached at 5f8229787001a946e4e020b68805661272577428; unchanged.
- Python 3.13.5; NumPy 2.4.2; MKL 2025.2.0; bundled OpenBLAS 0.3.31.dev.
- Complete installed versions: requirements.lock. CPU evidence: host-cpu.txt.
- Final authoritative run: results/20261003T182617Z; logs/final_*.
- 9 configurations x 3 thread counts (1/2/4) x 2 fresh processes = 54 successful runs.
- MKL_DYNAMIC=FALSE, OMP_DYNAMIC=FALSE; MKL, OpenMP and OpenBLAS counts explicitly set.
- Seeded PCG64 inputs; input byte hashes verified equal in every comparison.
- Four double-precision GEMMs: (m,k,n) = (257,513,193), (8,8193,8),
  (129,2049,65), (513,513,513). NumPy exp/log and OpenBLAS GEMM also recorded.
- Every one of the 27 within-configuration repeat pairs was bitwise identical.

## Findings

Direct AVX2,STRICT: all four MKL outputs identical across 1/2/4 threads.
PR with AVX2,STRICT preset: the environment becomes AVX2 and three GEMM shapes
vary across thread counts. For (8,8193,8), 1 versus 2 threads differs in 62/64
elements, maximum absolute difference 1.652011860642233e-13.

MKL_CBWR_Get(MKL_CBWR_ALL) confirms 65546 (= AVX2 10 | STRICT 65536) directly,
10 under the PR, and 65546 under candidate-reproseed.sh. The candidate preserves
any nonempty explicit MKL_CBWR. All four candidate MKL outputs match the direct
STRICT outputs at each thread count and across thread counts. Other PR controls
remain active; OpenBLAS reports Haswell under both PR and candidate.

COMPATIBLE is also replaced: diagnostic 3 becomes 10. The candidate preserves 3
and matches direct COMPATIBLE MKL outputs at each thread count. COMPATIBLE does
not promise independence of thread count; this is not an AMD hardware test.

Native versus PR at one thread: NumPy exp differs in 4530/100003 values and log
in 115/100003; OpenBLAS switches from SkylakeX to Haswell and GEMM differs.
These show the controls change paths/results on this host. They do not by
themselves establish agreement across different physical CPUs.

## Reproduce

From /home/leej3/reproseed:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.lock
duct --fail-time 0 -p logs/reproduction_ .venv/bin/python run.py
# Substitute the RESULTS directory printed by run.py:
.venv/bin/python analyze.py results/20261003T182617Z
```

run.py creates timestamped result directories; do not reuse a duct output prefix.
The probe records environment, CPU-feature map, threadpool/backend versions,
CNR settings, input hashes, output hashes and full arrays. Comparisons report
bitwise equality, differing element counts, maximum absolute and relative errors.
Maximum relative error uses max(abs(a),abs(b),tiny) as the denominator.
The retained seeded generator and pinned NumPy regenerate inputs; input arrays
are not separately saved. Source and experiment checksums are in evidence.sha256.

## Scope and remaining work

No PyTorch/oneDNN runs, AMD runs, CPU masking, or cross-machine comparisons yet.
The tested candidate addresses MKL only, not NumPy exclusion merging. Preserving
explicit settings permits intentional deviations from the default profile.
No PR changes, commits, or external comments were made.

Earlier run 20261003T182408Z failed due to the harness calling a lowercase MKL
symbol rather than the C ABI symbol MKL_CBWR_Get. The intermediate run
20261003T182449Z completed computations but queried option 0 (invalid), returning
-2. Its numerical results are exploratory; use the final corrected run for claims.
The final query uses -1, MKL_CBWR_ALL from the matching installed headers.
Failed/intermediate scripts and logs remain for audit; these were harness errors.
An initially installed yanked NumPy 2.4.0 was replaced before numerical testing.

## Primary references

- PR code: https://github.com/ReproNim/reproseed/blob/5f8229787001a946e4e020b68805661272577428/reproseed.sh#L74
- Intel CNR conditions (STRICT includes GEMM; standard CNR requires fixed threading): https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-2/reproducibility-conditions.html
- Branch semantics and STRICT syntax: https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2025-2/specifying-code-branches.html
- CNR diagnostic API: https://www.intel.com/content/www/us/en/docs/onemkl/developer-reference-c/2025-2/mkl-cbwr-get.html
- Installed matching constants/ABI: .venv/include/mkl_types.h and mkl_service.h.

Suggested review focus: preserve explicitly configured MKL CNR and add regression
coverage. This request is supported by an actual counterexample and a tested fix;
broader backend caveats should remain separate from this demonstrated issue.
