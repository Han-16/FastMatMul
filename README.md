# LAMP

**LAMP: Linear Verification of Matrix Multiplication via Proximity Testing**

This workspace contains the S&P 2027 paper versions, preserved benchmark
measurements, experiment configuration, and review and shepherding records.

## Repositories

- [lysias9049/LAMP](https://github.com/lysias9049/LAMP): this paper workspace,
  manuscript revisions, planning documents, and supporting benchmark records.
- [lysias9049/LAMP-artifact](https://github.com/lysias9049/LAMP-artifact): runnable
  implementations and artifacts. Make implementation changes in that repository.

Repository URLs recorded in past measurements are historical provenance;
preserve their original commits, source fingerprints, and execution records.

## Repository Layout

```text
.
+-- Paper_original/              # Original S&P revision
+-- Paper/                       # Current manuscript for the EPYC comparison
+-- Benchmark/
|   +-- original/                # Original LAMP benchmark CSV files
|   +-- m1/                      # M1 raw results, manifests, source, table generator
|   +-- epyc/                    # Square and batch 10-repetition results
|       +-- archive/             # Earlier 3-repetition measurements
+-- Experiment/
|   +-- comparison_3reps.json     # Planned EPYC comparison configuration
|   +-- prepare_comparison_3reps.py
+-- Revision/                    # Reviews, rebuttal, shepherd drafts, reference papers
|   +-- archive/                 # Historical reviews/plans and local zkMaP archive
+-- NEXT_WORK_PLAN.md            # Current work plan, in Korean
+-- AGENTS.md                    # Instructions for AI work in this repository
+-- README.md                    # Workspace guide
```

`NEXT_WORK_PLAN.md` records the current work. Files under `Revision/archive/`
are historical snapshots, not current submission status or active instructions.
Shepherd drafts under `Revision/` may also contain status statements from their
original drafting dates.

## Paper Versions

Each paper folder is an independent copy with its own `main.tex`, `main.pdf`,
`Contents/`, `Styles/`, and `Tables/`.

- `Paper_original/` is the original from `Han-16/FastMatMul`, branch
  `snp-revise-v1`, folder `Paper_snp_revise/`, commit
  `930f306d5df1c378089ca181c0770745a930610c`.
- `Paper/` is the current manuscript selected by the user. Its `main.tex`
  includes Section 7 from `Contents/evaluation.tex`. The new EPYC results
  have not yet been incorporated. On 2026-10-01, its compiled `main.pdf`
  was verified to have the same 18-page content as `LAMP-1st-revision.pdf`;
  only PDF timestamps and the document ID differ.

The archival submission PDFs `LAMP.pdf` and `LAMP_diff.pdf`, and duplicate
benchmark CSV files, were removed from the paper folders. `Paper_original/`
therefore preserves the original paper content, rather than every file in the
upstream directory. A new submission diff should be generated against this
original when the revised paper is selected.

To compile a version, run these commands from its paper folder:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Benchmark Data

Measurements are preserved separately from paper sources. Each paper's
`Tables/` directory retains the LaTeX tables required for compilation.

### Original Results

`Benchmark/original/` preserves:

- `lamp_benchmark_results.csv`
- `lamp_batch_benchmark_results.csv`
- `lamp_gpt2_benchmark_results.csv`

These are the existing paper measurements, distinct from the new server
comparison. No implementation or measurement-version classification is
inferred solely from the CSV filenames.

### M1 Comparison

`Benchmark/m1/` preserves raw JSONL results, invocation manifests, the measured
source snapshot, provenance, and aggregate measurements. To validate 280
verified records and regenerate only the M1 paper's two comparison tables:

```bash
python3 Benchmark/m1/generate_tables.py
```

This command does not run experiments. The measured source snapshot is
archived evidence. The original comparison implementation came from
`snp-labs/LAMP`, branch `comparison/zkmatrix-benchmarks`; ongoing implementation
work is maintained in `lysias9049/LAMP-artifact`.

### EPYC Comparison

`Benchmark/epyc/` contains the received server results:

- `lamp-three-results-10reps-k7-k11-20260930T233536Z/`: LAMP and independent
  zkMatrix, square sizes 128–2048, ten repetitions per system and size.
  The separate zkMaP modified-variant measurements are excluded from the
  paper's performance comparison.
- `lamp-batch-results-10reps-k7-q1-q10-20261001T032827Z/`: LAMP and independent
  zkMatrix, batches of 1–10 independent 128×128 products, ten repetitions
  per system and batch size.
- `archive/lamp-results-20260930T062910Z/`: earlier three-repetition square
  and batch measurements, retained as experiment history.

The new runs use the same pinned measurement source, AMD EPYC 7B13 host,
BN254 curve, and 32 threads. LAMP uses code rate 1/2 and 309 queries.
Raw results, configurations, logs, and code snapshots remain together in
each result folder. All file hashes were checked before and after relocation.

Keep raw measurements, manifests, source versions, and host information with
the results. Do not merge M1 and EPYC timings into one aggregate.

## Implementation Source

The runnable implementations are maintained in
[lysias9049/LAMP-artifact](https://github.com/lysias9049/LAMP-artifact).
The zkMaP protocol source formerly under `Implementation/` was checked against
commit `b34d2287c30730a3990d92630185a0a792a2897f`, which was the remote main
at verification under the former `lysias9049/FastMatMul` repository URL.
The eight protocol Go files are byte-identical. The same commit is available
as the artifact repository's main at the repository transition on 2026-10-01.

The local standalone module, CLI, scripts, plans, test logs, and binaries are
preserved in `Revision/archive/zkmap-local-implementation-20261001.tar.gz`.
Its adjacent JSON records upstream provenance and file hashes. All 42 local
files were checked against the archive before removing `Implementation/`.
The source snapshots accompanying benchmark measurements remain preserved.

## Writing and Review

The paper body is in English; planning documents are in Korean. pdfLaTeX with
BibTeX is the build target. See `AGENTS.md` for writing conventions and version
handling. The 2026-09-18 AE review is retained under `Revision/archive/`; its
observations do not establish the current state of the AE submission.
