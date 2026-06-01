# Revised S&P-Style Review v4: FastMatMul

**Paper:** *FastMatMul: Efficient Verifiable Matrix Multiplication via Linear Error-Correcting Codes*  
**Reviewed material:** revised `FastMatMul/main.tex`, `Contents/*.tex`, `Tables/*.tex`, bibliography, build log, and compiled `FastMatMul/main.pdf`  
**Venue assumption:** IEEE Symposium on Security and Privacy style review  
**Review form note:** S&P의 정확한 HotCRP 양식은 공개 양식만으로 확정하기 어렵기 때문에, 점수가 포함된 S&P/HotCRP 스타일 양식으로 작성했다.

## Recommendation

**Overall recommendation: Borderline Reject as submitted.**

This is the cleanest and most honest version so far. The paper now clearly frames FastMatMul as a **matrix-checking layer** that is conditional on certified encoded inputs and a selected `CodeCom` backend. It defines the code-commitment backend more carefully, states the soundness-critical ordering assumptions, separates interactive and Fiat-Shamir soundness, clarifies that the main experiments use `t=128` while strict `delta=1/2` 128-bit proximity soundness needs `t=130`, and explicitly says the artifact does not independently implement or measure `CodeCom.Verify`.

That honesty is valuable, but it also makes the remaining S&P blocker sharper: as submitted, this is not yet an end-to-end verifiable matrix multiplication system, and the central `O(k)` result is conditional on a backend that is not concretely instantiated or measured. I would not accept this version at S&P, but I now see it as a plausible workshop/early-round systems-crypto paper and a credible foundation for a stronger S&P submission.

## Scores

| Category | Score | Meaning |
|---|---:|---|
| Overall merit | 2.5 / 5 | Borderline reject; promising conditional result |
| Reviewer confidence | 4 / 5 | High |
| Novelty | 3 / 5 | Interesting protocol restructuring, conditional on backend |
| Technical soundness | 3.5 / 5 | Conditional theorem is much clearer |
| Significance | 3 / 5 | Potentially useful if backend is realized |
| Evaluation | 2 / 5 | Better scoped, still incomplete |
| Presentation | 4 / 5 | Much clearer and more candid |
| S&P fit | 3 / 5 | Good topic, but needs end-to-end evidence |
| Artifact readiness | 1.5 / 5 | Artifact limitations are acknowledged but not solved |

## Summary

FastMatMul checks committed matrix multiplication using a structured Freivalds reduction and code-based proximity testing. The prover computes `x = rA`, `y = xB`, and `z = rC` outside the SNARK, commits to their encodings, and proves sampled encoded-coordinate consistency. If a global relation is false, code distance should cause a random sampled coordinate to detect the inconsistency.

The revised paper now formalizes the missing full-codeword binding assumption via a `CodeCom` backend. The theorem proves soundness relative to certified input commitments, the codeword-binding error of `CodeCom`, the position-binding error of the opening layer, and the SNARK soundness error. The evaluation is explicitly described as measuring the multiplication-checking layer under a conditional linear-time backend model.

This is a much cleaner framing. But for S&P, the paper still needs a concrete backend instantiation and an evaluation that includes it.

## Strengths

**The model is now honest.** The paper no longer overclaims a complete end-to-end system. It says the theorem and asymptotic claim are conditional on the chosen code-commitment backend.

**The `CodeCom` definition is clearer.** The backend now has a position-opening verifier, completeness, and global codeword-binding game. The statement that every accepting opening must match `Enc(v)_j` is the right property.

**The soundness proof is better structured.** The proof explicitly lists timing invariants, samples `I` as an ordered tuple with replacement, and clarifies that without-replacement sampling can only help.

**Concrete security discussion improved.** The paper now states that `t=128` gives `2^-126` proximity error for `delta=1/2`, while strict 128-bit proximity soundness needs `t=130`, and aggregate 128-bit budgeting needs still larger slack.

**Evaluation scope is clearer.** The paper now says setup and native multiplication are recorded separately, and that peak memory, repeated-run variance, and independent `CodeCom.Verify` measurements are missing.

**Limitations are explicit.** The conclusion now directly acknowledges non-end-to-end input commitments, unisolated `CodeComV`, large proof sizes, missing memory/variance logging, no ZK proof, and narrow baselines.

## Major Weaknesses

### W1. The central backend is still not instantiated

The paper's main `O(tk)` claim depends on a linear-time `CodeCom` backend with `E_cc(k)=O(k)`. The paper now admits that the artifact does not independently implement or measure `CodeComV`. This is the right admission, but it means the main performance claim is conditional.

For S&P, the authors need to instantiate one backend end to end. Listing possible choices such as Brakedown/Orion-style code commitments, in-circuit encoder checks, or commitment-to-codeword linking is not enough. These options have different security assumptions and different concrete costs.

### W2. The evaluated system is only the checking layer

The abstract and conclusion now say the implementation evaluates the multiplication-checking layer. That is accurate, but it weakens the empirical claim. The measured `7.5x` and `15.1x` constraint reductions do not include an independently implemented code-commitment verifier. Thus the evaluation does not yet demonstrate the complete protocol promised by the formal construction.

This is probably the single most important issue to fix before S&P submission.

### W3. The exact code distance remains backend-specific and unspecified

The paper gives symbolic soundness in terms of `delta`, and the evaluation uses `rho=1/2`, `n=2k`, and `t=128`. But it still does not give the proven relative distance of the exact code/backend used in the main experiments.

The paper should pick a code and backend, state the proven `delta`, and set `t` from that value. A theorem parameterized by `delta` is fine, but the evaluation must use a concrete `delta`.

### W4. Concrete 128-bit measurements are still not in the main table

The paper is candid that `t=128` is a scaling benchmark rather than strict 128-bit proximity soundness for `delta=1/2`. That is acceptable as a caveat, but a security submission should report the main numbers at the claimed security level, or at least provide a rescaled `t=130` and aggregate-budget table.

The difference between 128 and 130 samples is small, so this should be easy to address.

### W5. Evaluation methodology remains incomplete

The paper still lacks several S&P-level evaluation details:

- hardware, RAM, OS, compiler flags, Rust version, curve, hash, and backend libraries;
- peak resident memory for all variants;
- setup/key sizes, not only example setup times;
- repeated-run variance;
- random seeds and matrix distributions;
- artifact URL and exact reproduction commands;
- per-component constraint breakdowns.

The current paper acknowledges several of these omissions. That helps credibility but does not replace the measurements.

### W6. Baselines remain too narrow

The only implemented baseline is an optimized Freivalds SNARK. Since the paper positions itself against code-based proof systems, sumcheck/GKR approaches, and committed matrix multiplication protocols, the evaluation should include at least one stronger baseline:

- generic Brakedown/Orion-style proof of the Freivalds relation;
- sumcheck/GKR matrix multiplication verification;
- zkMatrix or another committed-matrix multiplication system;
- a realistic zkML matrix layer.

Without this, the result is promising but hard to calibrate against the state of the art.

### W7. Proof size limits deployment

The proof-size breakdown is useful, but the evaluated backends still produce proofs up to roughly 48 MB for one `4096 x 4096` multiplication. The paper should discuss target deployment regimes where this is acceptable and compare proof sizes with committed-matrix alternatives.

### W8. Formatting and venue readiness remain unresolved

The compiled PDF is 14 pages, with references beginning on page 14. The paper is still in ACM CCS format with placeholder DOI/ISBN and ACM metadata warnings. This is not an S&P-ready PDF.

## Detailed Comments

1. **Instantiate `CodeCom`.** Choose one backend and give algorithms, proof contents, verifier relation, assumptions, and binding proof.

2. **Measure `CodeComV`.** Include its constraints, proving time, verification time, and proof-size contribution separately.

3. **Use concrete `delta`.** State the exact code construction and relative distance used in experiments.

4. **Report strict-security numbers.** Add `t=130` for the `delta=1/2` proximity target, and ideally an aggregate 128-bit budget table.

5. **Add a component table.** Break constraints into fold checks, openings/Merkle paths, `CodeCom`, linking, and SNARK overhead.

6. **Add system details.** Report hardware, RAM, software stack, curve, hash, field modulus, and compiler settings.

7. **Add memory and variance.** Peak RSS and repeated-run statistics are important for the Freivalds OOM claim.

8. **Report key/setup sizes.** Setup times are mentioned, but key sizes and full setup tables are still missing.

9. **Add stronger baselines.** At least one code-based SNARK or sumcheck/GKR comparison would substantially improve the paper.

10. **Make artifact instructions explicit.** Include exact commands and expected outputs.

11. **Clarify end-to-end versus layer-only claims everywhere.** The paper mostly does this now; keep the title/abstract/conclusion consistently aligned.

12. **Convert to S&P format.** Fix the 14-page ACM-format issue before submission.

## Questions for Authors

1. Which concrete `CodeCom` backend do you intend as the primary instantiation?

2. What is the proven `delta` for that backend?

3. How large is `sigma_v`, and is it inside the SNARK witness or auxiliary proof data?

4. What is the measured `CodeComV` constraint count?

5. How would Table 1 change for `t=130` or for aggregate 128-bit soundness?

6. What machine and memory limit caused Freivalds to fail at `k=4096`?

7. How large are the proving/verifying keys for each backend?

8. Can the authors compare proof size and prover time with zkMatrix or a sumcheck/GKR implementation?

9. What application can tolerate 24-48 MB proofs per multiplication?

10. Will an anonymized artifact with reproduction scripts be available?

## Required Changes Before S&P Submission

1. Provide and evaluate a concrete `CodeCom` backend.
2. Report main numbers at strict concrete security parameters.
3. State the exact code distance and code construction.
4. Add component-level constraints, memory, setup/key sizes, and variance.
5. Add stronger baselines.
6. Package an anonymized artifact.
7. Convert to S&P format and fix page/layout issues.

## Confidential Comments to PC

The paper has improved substantially in intellectual honesty. It now makes clear that the theorem is conditional and the implementation measures only the checking layer. That makes the current result easier to trust but also less complete. I would not accept it at S&P in this form, because the central efficient backend is not instantiated or measured.

If the authors implement one `CodeCom` backend and provide concrete 128-bit end-to-end measurements, this could become a serious applied-crypto submission.

## Final Verdict

**Best revision so far, but still not S&P-ready.** The model and proof are now much cleaner; the missing piece is an end-to-end backend instantiation and a complete systems evaluation.
