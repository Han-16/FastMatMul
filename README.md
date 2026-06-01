# FastMatMul

**FastMatMul: A Code-Based Matrix-Multiplication Checking Layer for Verifiable
Computation**

FastMatMul is a cryptography research artifact for checking large matrix
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
|   +-- Protocols/                # Protocol descriptions
|   +-- Styles/                   # LaTeX packages, macros, bibliography
|   +-- Tables/                   # Evaluation tables
+-- Experiment/
|   +-- freivalds_benchmark_results.csv
|   +-- meow_benchmark_results.csv
|   +-- freivalds_gpt2_benchmark_results.csv
|   +-- meow_gpt2_benchmark_results.csv
|   +-- system_info.json
+-- Reference/                    # Related-work PDFs
+-- Review/                       # Internal review notes
+-- AGENTS.md                     # Local writing/workflow instructions
```

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

The benchmark CSV files under `Experiment/` record the measurements used in the
evaluation section.

The available data files are:

- `Experiment/freivalds_benchmark_results.csv`
- `Experiment/meow_benchmark_results.csv`
- `Experiment/freivalds_gpt2_benchmark_results.csv`
- `Experiment/meow_gpt2_benchmark_results.csv`
- `Experiment/system_info.json`

See `Paper/Contents/evaluation.tex` and the CSV files in `Experiment/` for the
reported measurements and caveats.

## Artifact Scope

This repository snapshot contains the paper source, compiled paper, benchmark
tables, benchmark CSV outputs, reference material, and review notes. It should
be read as a paper-and-measurement artifact, not as an implementation
repository.

## Notes

- The paper is written in English and uses standard cryptographic notation.
- The LaTeX build target is pdfLaTeX with BibTeX.
- The benchmark byte counts in the paper are online proof bytes and exclude
  raw input certification, proving/verifying keys, CRS material, and generator
  material unless explicitly stated otherwise.
