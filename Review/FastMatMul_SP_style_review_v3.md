# Revised S&P-Style Review v3: FastMatMul

**Paper:** *FastMatMul: Efficient Verifiable Matrix Multiplication via Linear Error-Correcting Codes*  
**Reviewed material:** revised `FastMatMul/main.tex`, `Contents/*.tex`, `Tables/*.tex`, bibliography, build log, and compiled `FastMatMul/main.pdf`  
**Venue assumption:** IEEE Symposium on Security and Privacy style review  
**Review form note:** S&P의 정확한 HotCRP 양식은 공개 양식만으로 확정하기 어렵기 때문에, 점수가 포함된 S&P/HotCRP 스타일 양식으로 작성했다.

## Recommendation

**Overall recommendation: Borderline Reject / Weak Reject as submitted.**

This revision is materially stronger than the previous one. It now defines a `CodeCom` backend abstraction, separates interactive and Fiat-Shamir soundness, adds a concrete parameter table, acknowledges that `t=128` is slightly below the strict `t=130` needed for a conservative `delta=1/2` 128-bit proximity target, gives more timing-scope detail, adds proof-object and CPLink proof-size breakdown tables, and includes an explicit limitations paragraph. These changes make the paper more honest and easier to review.

I still would not submit this exact version to S&P. The remaining blocker is that the main result still relies on a **linear-time code-commitment backend** whose concrete construction, proof, and measured constraint contribution are not sufficiently specified. The evaluation is also still incomplete for a top security venue: hardware/RAM, peak memory, variance, artifact instructions, stronger baselines, and per-component constraint breakdowns are missing. Finally, the current build is still ACM CCS-style and compiles to 14 pages, with references beginning on page 14.

## Scores

| Category | Score | Meaning |
|---|---:|---|
| Overall merit | 2.5 / 5 | Borderline reject; promising but not yet S&P-ready |
| Reviewer confidence | 4 / 5 | High |
| Novelty | 3 / 5 | Interesting protocol composition; novelty depends on backend realization |
| Technical soundness | 3 / 5 | Improved theorem and model, but backend abstraction remains central |
| Significance | 3 / 5 | Potentially useful for large verifiable linear algebra |
| Evaluation | 2 / 5 | Better scoped, still under-documented |
| Presentation | 3.5 / 5 | Clearer and more transparent than before |
| S&P fit | 3 / 5 | Good applied-crypto topic, but needs stronger evidence |
| Artifact readiness | 1.5 / 5 | Artifact is mentioned but not packaged/reproducible in the paper |

## Summary

FastMatMul verifies committed matrix multiplication by combining a structured Freivalds check with proximity testing over linear error-correcting codes. The prover computes `x = rA`, `y = xB`, and `z = rC` outside the SNARK, commits to encoded versions of these vectors, and proves sampled coordinate consistency inside a SNARK. If a global relation is false, code distance should imply that sampled coordinates catch the inconsistency.

The current revision formalizes the missing global codeword-validity condition as a `CodeCom` backend. This backend is required to bind an intermediate commitment `cm_v` to the full codeword `Enc(v)` and has verifier cost `E_cc(k)`. The headline `O(tk)` circuit claim holds only when this backend is linear-time.

The paper is now much more careful about its assumptions. However, the `CodeCom` backend is still not concretely instantiated enough to justify the headline performance claim as an end-to-end system contribution.

## Strengths

**The proof model is clearer.** The paper now defines a code-commitment backend and uses a single error term `epsilon_cc` for codeword-binding failure. This is a cleaner way to state the missing assumption.

**The soundness statement is more complete.** It now separates interactive soundness from Fiat-Shamir soundness and adds an explicit `epsilon_FS(q_H)` term.

**The concrete parameter discussion improved.** The paper now states `rho=1/2`, `n=2k`, and `t=128` for the main experiments, and it honestly notes that strict 128-bit proximity soundness under `delta=1/2` would require `t=130`.

**Evaluation scope is more transparent.** The paper now says proving time excludes setup, gives example setup-time ranges, and admits that peak memory and repeated-run variance are not logged.

**Proof-size transparency improved.** The new CPLink proof-size breakdown and proof-object table make it much clearer why proofs reach roughly 48 MB.

**The limitations paragraph is useful.** It explicitly acknowledges relative input commitments, large proof sizes, lack of ZK, missing memory/variance logging, and narrow baselines.

## Major Weaknesses

### W1. The central `CodeCom` backend remains under-instantiated

The paper now defines the right abstraction, but it still does not provide a concrete construction with enough detail for S&P. The text says the backend can be instantiated by Brakedown/Orion-style code commitments, an in-circuit encoder check tied to the root, or a commitment-to-codeword linking proof. These are very different systems with different proof sizes, setup assumptions, verifier costs, and soundness proofs.

The main theorem and the main table depend on an efficient backend with `E_cc(k)=O(k)`. To support the headline claim, the paper should choose one backend and specify:

- exact algorithms for commit, open, prove codeword binding, and verify;
- how `cm_v` is tied to the full codeword rather than sampled positions;
- what `sigma_v` contains;
- whether `sigma_v` is inside the SNARK witness, outside as auxiliary data, or both;
- the exact constraint and proof-size contribution of `CodeCom.Verify`;
- the backend's binding proof and assumptions.

Right now, the paper proves a conditional theorem over a powerful abstraction and then evaluates as if the abstraction were already realized.

### W2. The main experiments do not meet the stated strict 128-bit proximity target

The evaluation uses `t=128`. The security section correctly says that for a conservative `delta=1/2` calculation, `t=130` is needed so that `4(1-delta)^t <= 2^-128`.

This is not a fatal gap because the difference is only about 1.6% in `t`-linear terms, but the paper should either:

- rerun or rescale the main table for `t=130`; or
- state the reported table is for an approximately 126-bit proximity term before the strict slack; or
- specify an actual code distance `delta > 1/2` if available.

As written, the abstract advertises 128-bit-style soundness, while the main measurements use parameters that the paper itself says are slightly short under the conservative calculation.

### W3. The exact code distance `delta` is still unspecified

The parameter table says the exact `delta` is a property of the selected backend. But the soundness and query complexity are functions of `delta`, and the main experiments use a concrete `t`.

For a security paper, the selected code family and its distance must be explicit. "Expander-based code as in Brakedown" is not enough; the paper should state the actual expansion/distance parameters or cite and instantiate a concrete code with a proven relative distance.

### W4. Evaluation still lacks enough methodology detail

The revision improves timing-scope clarity, but the paper still lacks:

- hardware, RAM, OS, compiler flags, Rust version, backend libraries, curve, hash, and field modulus;
- peak memory for all variants;
- repeated-run variance;
- random seeds and matrix distributions;
- CRS/proving-key sizes;
- artifact URL and exact reproduction commands;
- per-component constraint breakdowns.

The paper now admits some of these limitations, which is good, but S&P generally expects the data itself, not only an acknowledgement that it is missing.

### W5. The "Freivalds exhausts memory" claim is still weakly evidenced

The paper now phrases this more carefully as an observed out-of-memory outcome in the benchmark environment, and the table notes that peak memory was not logged. That is an improvement, but it also weakens the strength of the claim.

For S&P, the paper should include peak RSS and the failure point: constraint generation, witness generation, setup/key generation, or proving. Without this, the `k=4096` comparison is anecdotal.

### W6. Baselines remain too narrow

The only implemented baseline is an optimized Freivalds SNARK. The related-work section discusses zkMatrix, zkVC, Brakedown, Orion, and sumcheck/GKR approaches, but the evaluation does not compare against them.

At minimum, I would expect one generic code-based SNARK baseline for the Freivalds relation and one sumcheck/GKR or committed-matrix baseline. Otherwise the paper risks being seen as showing that FastMatMul beats a deliberately direct SNARK encoding, not that it advances the state of the art.

### W7. Proof size is still a serious deployment limitation

The CPLink breakdown is helpful, but the evaluated proof sizes still reach roughly 48 MB for a single `4096 x 4096` multiplication. The final "practical recommendation" now says applications must tolerate backend-dependent opening/linking material, which is more honest. But the paper should discuss application regimes where this proof size is acceptable and regimes where it is not.

### W8. Formatting remains not submission-ready

The current build log reports `main.pdf` as 14 pages and references begin on page 14. The paper is still in ACM CCS format with placeholder DOI/ISBN and ACM metadata warnings. For an S&P submission, this must be converted to the correct IEEE/S&P template and page-budget assumptions.

## Detailed Comments

1. **Instantiate one `CodeCom` backend.** Pick the backend used in Table 1 and describe it fully. Avoid listing several possible backends without implementing one.

2. **Rerun or rescale for strict parameters.** Use `t=130` for the main `delta=1/2` security target, or clearly label the current `t=128` table as slightly below the strict 128-bit bound.

3. **State the actual `delta`.** The paper needs a concrete code construction and relative distance, not only a symbolic theorem.

4. **Add a component constraint table.** Break constraints into fold, Merkle/opening, CodeCom, linking, and SNARK overhead.

5. **Add hardware and memory.** Include machine specs, peak RSS, and failure location for Freivalds.

6. **Add setup/key-size tables.** Since Groth16/KZG are used, setup time and proving/verifying key sizes matter.

7. **Add variance.** Report median/mean over several runs for feasible sizes and single-run status only where unavoidable.

8. **Add artifact instructions.** Include exact commands, expected CSVs, plotting scripts, and expected output hashes or table values.

9. **Move proof size into the main comparison.** The proof-size breakdown is useful, but proof size should be visible in the main table.

10. **Strengthen baselines.** Add at least one code-based SNARK or sumcheck/GKR baseline.

11. **Clarify native arithmetic inclusion.** The paper says native matrix multiplication is recorded separately, but the final performance claims should specify whether the speedups include or exclude it.

12. **Fix venue format.** Convert from ACM CCS to S&P/IEEE style and resolve metadata/layout warnings.

## Questions for Authors

1. Which concrete `CodeCom` backend is implemented in Table 1?

2. What is the proven `delta` for the exact code used in the experiments?

3. Are the reported `O(k)` constraints for `CodeCom.Verify` measured separately anywhere?

4. Why not report the main table for `t=130` if that is the strict 128-bit conservative target?

5. What are the hardware specs and available RAM for the reported out-of-memory result?

6. What are the setup time, proving-key size, and verifying-key size for each backend?

7. Can the authors provide peak memory and per-component timing/constraint breakdowns?

8. How do proof sizes compare to zkMatrix or sumcheck/GKR alternatives for similar dimensions?

9. Is there an anonymized artifact ready for S&P review?

10. In what target application is a 24-48 MB proof per matrix multiplication acceptable?

## Required Changes Before S&P Submission

1. Fully specify and instantiate the `CodeCom` backend used in the experiments.
2. Use strict concrete security parameters in the main table or clearly label the current security level.
3. Provide the actual code distance and code construction.
4. Add component-level constraints, timing, proof size, setup, key size, and memory tables.
5. Add stronger baselines.
6. Package an anonymized artifact with reproduction instructions.
7. Convert to the S&P template and fix the page/layout issues.

## Confidential Comments to PC

This paper is moving in the right direction. The authors have addressed several reviewer-style criticisms by making the theorem conditional on a code-commitment backend and by adding limitations. I no longer view the proof story as obviously confused. However, the central efficient backend is still not sufficiently real in the paper. The evaluation is also not yet at the level expected for S&P.

I would encourage another revision, but I would not accept this version. If the authors instantiate `CodeCom`, provide concrete `delta/t` parameters, and strengthen the artifact/evaluation, this could become a plausible applied-cryptography submission.

## Final Verdict

**Closer, but still not S&P-ready.** The paper now has a cleaner model and more honest evaluation scope, but the main result remains conditional on an under-specified linear-time code-commitment backend and an incomplete systems evaluation.
