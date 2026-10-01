#!/usr/bin/env python3
"""Validate the received EPYC runs and generate paper tables; no experiments run."""

import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
TABLES = BASE.parents[1] / "Paper" / "Tables"
HEAD = "b34d2287c30730a3990d92630185a0a792a2897f"
SOURCE = "79ba76054e42800de44600c750a8438947f60ce9d8793e6777f3c3e120d6670c"
SCHEMES = ("lamp", "independent_zkmatrix_optimized_bn254")
DATASETS = {
    "square": "lamp-three-results-10reps-k7-k11-20260930T233536Z",
    "batch": "lamp-batch-results-10reps-k7-q1-q10-20261001T032827Z",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats(values):
    require(all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in values),
            "Invalid measurement")
    return {"mean": statistics.mean(values), "sample_sd": statistics.stdev(values)}


def collect():
    groups = defaultdict(list)
    inputs = {}
    for workload, dirname in DATASETS.items():
        directory = BASE / dirname / workload
        manifest_path = directory / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        inputs[str(manifest_path.relative_to(BASE.parents[1]))] = digest(manifest_path)
        require(manifest["completion_status"] == "complete" and manifest["run_state"] == "finished",
                f"Incomplete {workload} run")
        require(manifest["source"]["head"] == HEAD and manifest["source"]["source_tree_sha256"] == SOURCE,
                "Unexpected measurement source")
        expected_commands = 55 if workload == "square" else 110
        require(len(manifest["commands"]) == manifest["expected_command_count"] == expected_commands,
                "Unexpected command grid")
        require(manifest["processor"] == "AMD EPYC 7B13" and manifest["cpu_count"] == 32
                and manifest["go"] == "go version go1.26.2 linux/amd64", "Unexpected machine")
        for command in manifest["commands"]:
            require(command["status"] == "completed" and command["exit_status"] == 0,
                    "Failed measurement command")
            raw = directory / Path(command["stdout"]).parent.name / "lamp_comparison.jsonl"
            inputs[str(raw.relative_to(BASE.parents[1]))] = digest(raw)
            rows = [json.loads(line) for line in raw.read_text().splitlines() if line.strip()]
            require(len(rows) == command["expected_verified_record_count"] == command["verified_record_count"],
                    "Raw record count differs from manifest")
            for row in rows:
                scheme = row["scheme"]
                require(scheme in SCHEMES and row["verification_succeeded"] is True
                        and row["protocol_path"] == workload, "Wrong scheme, path, or verification")
                require(row["source"]["head"] == HEAD and row["source"]["source_tree_sha256"] == SOURCE,
                        "Raw record source mismatch")
                require(row["run"]["binary_sha256"] == command["binary_sha256"], "Binary mismatch")
                cfg, host, dims = row["experiment_config"], row["host"], row["dimensions"]
                require(cfg["threads"] == 32 and cfg["repetitions"] == 10,
                        "Unexpected thread or repetition setting")
                require(host["processor"] == "AMD EPYC 7B13" and host["cpu_count"] == 32
                        and int(host["runtime_num_cpu"]) == int(host["gomaxprocs"]) == 32
                        and host["go"] == "go version go1.26.2 linux/amd64"
                        and host["os"].startswith("Linux-") and host["memory_bytes"] >= 240 * 2**30,
                        "Unexpected execution environment")
                if scheme == "lamp":
                    n = dims["K"]
                    require(dims["N"] == 2 * n and row["query_count"] == cfg["queries"] == 309
                            and cfg["rho"] == "1/2", "LAMP parameters differ from Section 7")
                    require(row["statement_bytes"] == 64, "Unexpected LAMP statement accounting")
                    require(math.isclose(row["timings_seconds"]["prove"],
                                         row["timings_seconds"]["full_online_prove"], rel_tol=1e-12),
                            "LAMP uses a different timing boundary")
                else:
                    n = dims["n"]
                    require(dims["m"] == dims["inner"] == n and row["run"]["curve"] == "BN254"
                            and row["variant"] == "independent_zkmatrix_optimized_bn254_accelerated",
                            "Unexpected zkMatrix construction or dimensions")
                q = row.get("batch_q", 1)
                require(row["statement_bytes"] == (64 if scheme == "lamp" else 112 * q),
                        "Unexpected statement size")
                t = row["timings_seconds"]
                require(math.isclose(t["prove"], t["matrix_commit"] + t["precommitted_online_prove"],
                                     rel_tol=1e-12), "Commitments missing from proving time")
                groups[(workload, n, q, scheme)].append(row)

    expected = {(workload, n, q, scheme)
                for workload, sizes, batches in (("square", (128, 256, 512, 1024, 2048), (1,)),
                                                ("batch", (128,), range(1, 11)))
                for n in sizes for q in batches for scheme in SCHEMES}
    require(set(groups) == expected, "Incomplete or unexpected comparison grid")
    summaries = {}
    for key, rows in groups.items():
        require(len(rows) == 10, f"Expected ten repetitions: {key}")
        summaries[key] = {"repetitions": 10,
                          "prove_seconds": stats([r["timings_seconds"]["prove"] for r in rows]),
                          "verify_ms": stats([1000 * r["timings_seconds"]["verify"] for r in rows]),
                          "proof_bytes": stats([r["compressed_payload_bytes"] for r in rows]),
                          "statement_bytes": stats([r["statement_bytes"] for r in rows])}

    # Independent recomputation must agree with the received server aggregates.
    for workload, dirname in DATASETS.items():
        summary_path = BASE / dirname / workload / "summary.json"
        inputs[str(summary_path.relative_to(BASE.parents[1]))] = digest(summary_path)
        saved = json.loads(summary_path.read_text())
        require(len(saved) == (10 if workload == "square" else 20), "Unexpected server summary")
        for group in saved:
            key = group["key"]
            dims = json.loads(key[3])
            n = dims["K"] if key[0] == "lamp" else dims["n"]
            actual = summaries[(workload, n, key[4], key[0])]
            require(group["n"] == 10, "Unexpected server repetition count")
            for field, remote, scale in (("prove_seconds", "prove_seconds", 1),
                                         ("verify_ms", "verify_seconds", 1000),
                                         ("proof_bytes", "compressed_payload_bytes", 1),
                                         ("statement_bytes", "statement_bytes", 1)):
                for statistic in ("mean", "sample_sd"):
                    require(math.isclose(actual[field][statistic], scale * group[remote][statistic],
                                         rel_tol=1e-12, abs_tol=1e-10), "Server aggregate differs from raw data")
    return summaries, inputs


def time_cell(metric, places):
    return rf"\({metric['mean']:.{places}f}\pm{metric['sample_sd']:.{places}f}\)"


def bytes_cell(metric):
    n = metric["mean"]
    return (f"{n:,.0f}" if n == int(n) else f"{n:,.1f}").replace(",", "{,}")


def main():
    summaries, inputs = collect()
    header = "% Generated from ten verified EPYC repetitions by Benchmark/epyc/generate_comparison_tables.py.\n"
    square = []
    for n in (128, 256, 512, 1024, 2048):
        for scheme, label in ((SCHEMES[0], r"\(\protocol\)"), (SCHEMES[1], "zkMatrix")):
            m = summaries[("square", n, 1, scheme)]
            square.append(" & ".join((str(n), label, time_cell(m["prove_seconds"], 3),
                                      time_cell(m["verify_ms"], 2), bytes_cell(m["proof_bytes"]),
                                      bytes_cell(m["statement_bytes"]))) + r" \\")
        if n != 2048:
            square.append(r"\midrule")
    batch = []
    for q in range(1, 11):
        pair = [summaries[("batch", 128, q, scheme)] for scheme in SCHEMES]
        cells = [str(q)]
        for metric, places in (("prove_seconds", 3), ("verify_ms", 2)):
            cells.extend(time_cell(m[metric], places) for m in pair)
        for metric in ("proof_bytes", "statement_bytes"):
            cells.extend(bytes_cell(m[metric]) for m in pair)
        batch.append(" & ".join(cells) + r" \\")
    TABLES.mkdir(exist_ok=True)
    (TABLES / "zkMatrix_epyc_square_rows.tex").write_text(
        header + r"\newcommand{\epycSquareRows}{%" + "\n" + "\n".join(square) + "\n}\n")
    (TABLES / "zkMatrix_epyc_batch_rows.tex").write_text(
        header + r"\newcommand{\epycBatchRows}{%" + "\n" + "\n".join(batch) + "\n}\n")
    output = {"source_commit": HEAD, "source_tree_sha256": SOURCE,
              "verified_record_count": 300, "input_files_sha256": inputs,
              "groups": [{"workload": k[0], "dimension": k[1], "batch_q": k[2], "scheme": k[3], **m}
                         for k, m in sorted(summaries.items())]}
    (BASE / "paper_comparison_measurements.json").write_text(json.dumps(output, indent=2) + "\n")
    print("Verified 300 records in 30 conditions against source, commands, host, parameters, and server aggregates.")
    print("Generated two EPYC comparison tables and paper_comparison_measurements.json; no experiments run.")


if __name__ == "__main__":
    main()
