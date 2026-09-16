# LAMP

**LAMP: Linear-Constraint Proofs for Matrix Multiplication via Proximity
Testing**

LAMP is a cryptography research artifact for checking large matrix
multiplication claims in verifiable computation. This repository contains the
paper source, compiled paper, experimental result files, references, and review
notes for the FastMatMul paper.

The main paper studies how to reduce the in-circuit cost of verifying a
`k x k` matrix product compared with direct matrix multiplication and a
Freivalds-style SNARK baseline.

## Repository Layout

```text
.
+-- Paper/
|   +-- main.tex                  # Main paper entry point
|   +-- main.pdf                  # Compiled paper
|   +-- Contents/                 # Paper sections
|   +-- Styles/                   # LaTeX packages, macros, bibliography
+-- Experiment/
|   +-- Rebuttal/                 # Official revision data and accounting
|   +-- Previous/                 # Superseded measurements
+-- Implementation/               # Go/gnark implementation and harness
+-- NEXT_WORK_PLAN.md             # Current remaining-work checklist
+-- Rebuttal.md                   # Submitted text rebuttal
+-- S&P review.txt                # Original reviews and interactive asks
+-- archive/post-rebuttal-plans/  # Historical plans and evidence snapshots
+-- AGENTS.md                     # Local writing/workflow instructions
```

`NEXT_WORK_PLAN.md` is the only active planning document. Historical
post-rebuttal plans are retained under `archive/post-rebuttal-plans/` and should
not be interpreted as the current task status.

## Paper

The paper source is in `Paper/main.tex`, with section files under
`Paper/Contents/`.

To rebuild the paper from the `Paper/` directory:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

The generated PDF is available at:

```text
Paper/main.pdf
```

## Experimental Data

The benchmark CSV files under `Experiment/Rebuttal/` record the measurements
used in the evaluation section.  `FINAL_ACCOUNTING.md` states their protocol
version and evidence boundary.

The available data files are:

- `Experiment/Rebuttal/lamp_benchmark_results.csv`
- `Experiment/Rebuttal/lamp_batch_benchmark_results.csv`
- `Experiment/Rebuttal/lamp_gpt2_benchmark_results.csv`
- `Experiment/Rebuttal/freivalds_benchmark_results.csv`
- `Experiment/Rebuttal/dualmatrix_benchmark_results.csv`
- `Experiment/Rebuttal/dualmatrix_gpt2_benchmark_results.csv`
- `Experiment/Rebuttal/final_protocol_accounting.csv`

See `Paper/Contents/evaluation.tex` and
`Experiment/Rebuttal/FINAL_ACCOUNTING.md` for the reported measurements and
caveats.

## Artifact Scope

This repository contains the paper, implementation, benchmark outputs,
accounting notes, and review material.  The preserved server timings are
pre-binding point snapshots; final-circuit compile rows and a final serializer
smoke test are recorded separately.

## Notes

- The paper is written in English and uses standard cryptographic notation.
- The LaTeX build target is pdfLaTeX with BibTeX.
- The paper distinguishes recorded byte subtotals from final all-inclusive
  prover-to-verifier communication.  CRS, proving/verifying keys, and generator
  material are setup data rather than per-proof communication.
