# Revised S&P-Style Review: FastMatMul

**Paper:** *FastMatMul: Efficient Verifiable Matrix Multiplication via Linear Error-Correcting Codes*  
**Reviewed material:** revised `FastMatMul/main.tex`, included `Contents/*.tex`, `Tables/*.tex`, bibliography, build log, and compiled `FastMatMul/main.pdf`  
**Venue assumption:** IEEE Symposium on Security and Privacy style review  
**Review form note:** S&P의 정확한 HotCRP 양식은 공개 양식만으로 확정하기 어렵기 때문에, 점수가 포함된 S&P/HotCRP 스타일 양식으로 작성했다.

## Recommendation

**Overall recommendation: Weak Reject / Borderline Reject as submitted.**

The revision is clearly stronger than the earlier draft. The paper now acknowledges that the circuit size is really
`O(tk + t log n + E_C(k))`, adds SNARK and certificate error terms to the soundness statement, binds Fiat-Shamir challenges to a fuller transcript, and tones down the zero-knowledge paragraph. These are meaningful improvements.

However, I still would not submit this exact version to S&P. The main blocker has shifted rather than disappeared: the paper now relies on an **encoding-certified commitment interface** whose verifier supposedly proves that an intermediate root binds to the full encoded vector, with cost `E_C(k)=O(k)` for the main experiments. This interface is not concretely specified or instantiated enough to support the headline claims. The evaluation numbers are also almost unchanged and still omit concrete security parameters, hardware, memory, setup costs, and stronger baselines.

## Scores

| Category | Score | Meaning |
|---|---:|---|
| Overall merit | 2 / 5 | Weak reject; promising but still under-specified |
| Reviewer confidence | 4 / 5 | High |
| Novelty | 3 / 5 | Interesting composition, but now depends on an abstract certified-commitment layer |
| Technical soundness | 3 / 5 | Improved proof shape; key abstraction remains uninstantiated |
| Significance | 3 / 5 | Potentially useful for large verifiable linear algebra |
| Evaluation | 2 / 5 | Same promising trend, still too under-specified |
| Presentation | 3 / 5 | Clearer and more honest, but still draft-like for S&P |
| S&P fit | 3 / 5 | Good topic fit, not yet enough rigor/evidence |
| Artifact readiness | 1 / 5 | No artifact or reproducibility guidance |

## Summary

FastMatMul verifies committed matrix multiplication by combining a structured Freivalds check with proximity testing over linear error-correcting codes. The prover computes `x = rA`, `y = xB`, and `z = rC` outside the SNARK, commits to encoded versions of these vectors, and proves sampled coordinate consistency inside a SNARK. If a global relation is false, code distance should imply that a random coordinate detects the inconsistency with probability at least `delta`.

The revision adds a certified encoded-vector commitment layer: each intermediate commitment `cm_v` comes with a certificate `sigma_v` proving that all openings correspond to the full codeword `Enc(v)`. This is intended to fix the earlier ambiguity between local openings and global codeword validity.

This is the right direction, but the new abstraction is doing a lot of work. Without a concrete `Cert`/`EncCert.Verify` construction, constraints, proof object, and benchmark linkage, the paper is not yet convincing as an S&P submission.

## Strengths

**The revision addresses several serious proof-structure issues.** The soundness theorem now includes `epsilon_SNARK`, `epsilon_cert`, and a union-bounded Merkle binding error. This is a substantial improvement over the earlier statement.

**The cost claim is more honest.** The abstract and contribution list now state `O(tk + t log n + E_C(k))` and only specialize to `O(tk)` under a linear-time certified encoding layer.

**The Fiat-Shamir treatment is better.** The query hash now includes public parameters, input roots, `r`, and vector roots with domain separation. This is closer to what a real non-interactive protocol needs.

**The core idea remains attractive.** If the certified commitment layer can be instantiated with low overhead, the fold-check approach is a clean way to reduce in-circuit vector-matrix work.

**The PDF now compiles to 13 pages.** The build log shows `main.pdf` is 13 pages. There are still ACM-template issues, but the paper is at least less obviously over-length than the previous 12-page ACM draft with weaker content.

## Major Weaknesses

### W1. The new certified-encoding interface is too abstract

The paper introduces `EncCert.Verify(cm_v, v, sigma_v)` and assumes it guarantees that all accepting openings under `cm_v` are coordinates of the full codeword `Enc(v)`. This is exactly the property the protocol needs, but it is not a standard primitive as stated, and the paper does not give a concrete construction.

The abstraction hides the hardest part of the original issue. To make the main claim credible, the paper must specify:

- algorithms `Cert`, `EncCert.Verify`, opening, and extraction/binding games;
- whether `sigma_v` is a SNARK witness, auxiliary proof data, or both;
- how `cm_v` is bound to the entire codeword rather than only sampled coordinates;
- why the verifier cost is `E_C(k)=O(k)` for expander-based codes;
- how this layer interacts with Merkle roots, KZG, and CPLink variants.

As written, the paper effectively says: "Assume a certificate that proves the committed vector is the full encoding, cheaply." That may be a useful modularization, but S&P reviewers will want the module instantiated and evaluated.

### W2. The evaluation does not substantiate `E_C(k)=O(k)`

The main performance table is now described as using a "linear-time certified encoding configuration," but the table does not show the actual certificate-verifier constraints or explain how they were generated. The numbers appear to be inherited from the previous version, while the formal protocol now includes a stronger certificate layer.

This is a serious evidence gap. If `EncCert.Verify` is new protocol machinery, the evaluation should break out constraints and time for:

- fold checks;
- Merkle path checks;
- encoding-certificate verification;
- CPLink/KZG/linking;
- native matrix arithmetic and commitment generation.

Without this decomposition, the reader cannot tell whether the reported linear growth actually includes the newly formalized certificate checks.

### W3. Concrete security parameters are still missing

The paper still does not state the actual experimental values of `n`, `rho`, `delta`, and `t`. It gives the formula
`t = ceil(128 / log2(1/(1-delta)))`, but the evaluation never says which `delta` the expander code achieves or which `t` was used in Table 1.

This is central. Constraint counts and proof sizes depend linearly on `t`. A top-tier security paper needs to state whether the benchmark corresponds to 128-bit soundness, what union-bound slack is included, and how large the random-oracle/Fiat-Shamir loss is.

### W4. The committed-input model remains underspecified

The theorem is still relative to certified public input commitments to `A`, `B`, and `C`. This is acceptable as a model, but the paper claims a verifiable matrix multiplication protocol and does not provide an end-to-end interface for producing or verifying those input commitments.

Important questions remain:

- Who certifies that `cm_A`, `cm_B`, and `cm_C` are row-wise encodings?
- Is the certification cost amortized or paid per multiplication?
- How does a verifier learn the raw output `C` if needed?
- Does the argument prove knowledge of `A`, `B`, and `C`, or only statement soundness relative to external commitments?

The paper does acknowledge this as a relative statement, but for S&P this boundary should be part of the system design, not just a theorem caveat.

### W5. The experimental methodology is still not S&P-grade

The evaluation still lacks basic reproducibility details:

- hardware, RAM, OS, compiler, Rust flags, backend libraries, curve, hash, and field;
- number of runs and variance;
- random matrix distribution and seeds;
- setup time and CRS/key sizes;
- peak memory for every backend;
- exact cause of Freivalds out-of-memory at `k=4096`;
- artifact repository and reproduction scripts.

The reported trends are plausible, but S&P reviewers will not treat the numbers as strong evidence without this context.

### W6. Baselines are still too narrow

The only concrete baseline is an optimized Freivalds SNARK. That is useful, but not enough for the claims made in related work and evaluation. The paper should compare against at least one of:

- a generic Brakedown/Orion-style proving of the Freivalds relation;
- sumcheck/GKR matrix multiplication verification;
- zkMatrix or another committed matrix multiplication protocol;
- a recent zkML system's matrix layer implementation;
- an algebraic vector-commitment implementation if KZG is discussed as a future proof-size optimization.

Without stronger baselines, the paper may be seen as optimizing against a strawman.

### W7. Proof size remains a major practical issue

The evaluated proof sizes are 1.70 MB to 48.79 MB, and verification grows with linked column material. This is now acknowledged more clearly, but it is still not reflected in the main table or the recommendation. For many S&P-relevant deployments, a 48 MB proof for one matrix multiplication is not "manageable verifier work" without a careful application model.

### W8. The security proof still needs tighter formalization

The proof is much improved, but still informal in several places:

- `Bad_cert` is defined via the existence of an accepting opening, but the protocol only opens sampled coordinates; the game should quantify over adversarially chosen openings more precisely.
- `sigma_v` is generated before the query in the figure, but is only a SNARK witness later; the timing and binding of certificates should be formalized.
- The theorem for the interactive protocol omits the Fiat-Shamir loss, while the non-interactive protocol is the likely deployed version.
- The union-bound parameter paragraph gives roughly 126 bits after the factor `4`; if the target is 128-bit proximity soundness after the union bound, `t` should include the extra two bits.

None of these look fatal, but they would draw reviewer scrutiny.

## Detailed Comments

1. **Define the certified-encoding primitive formally.** Add a definition with algorithms, correctness, binding/extractability, and concrete instantiations.

2. **Instantiate `EncCert.Verify`.** A construction based on expander-code encoder circuits, Merkle linking, or a SNARKed encoding proof must be described rather than abstracted away.

3. **Add a constraint breakdown table.** Report constraints for fold, Merkle paths, certificate verification, and linking separately for each `k`.

4. **State concrete code parameters.** For every benchmark table, include `n`, `rho`, `delta`, `t`, field, curve, hash, and claimed soundness.

5. **Clarify proof objects per backend.** The paper mentions roots, SNARK proof, auxiliary openings, linking material, and certificates. Give exact proof contents and sizes for Merkle, KZG, and CPLink.

6. **Move proof size into the main comparison table.** It is too important to leave only in prose.

7. **Report memory and setup.** The "Freivalds exhausts memory" claim needs peak RSS and failure location. Groth16/KZG variants need setup time and key size.

8. **Strengthen related work comparisons.** The distinction from zkMatrix, zkVC, Bennett et al., Brakedown, Orion, and sumcheck/GKR should be sharper and experimentally supported where possible.

9. **Add limitations.** The paper should explicitly list relative input commitments, large proof sizes, lack of ZK proof, and dependence on a certified-encoding layer.

10. **Use the correct venue template.** The current paper is still in ACM CCS format with placeholder DOI/ISBN and ACM metadata warnings. S&P submission should use the IEEE/S&P format.

11. **Fix build polish.** The current log still has many overfull boxes and metadata warnings. These are secondary, but visible.

## Questions for Authors

1. What concrete construction implements `EncCert.Verify`, and is it part of the reported circuit?

2. What are `n`, `rho`, `delta`, and `t` in Table 1?

3. Do the reported results correspond to 128-bit soundness after the `4(1-delta)^t` union bound and Fiat-Shamir loss?

4. Are the certificate constraints included in the 53k to 1.67M constraint counts?

5. What is the exact proof object for each backend, including roots, openings, link proofs, certificates, and SNARK proofs?

6. What hardware, RAM, curve, hash, and Rust/SNARK libraries were used?

7. Are native matrix multiplication, encoding, Merkle construction, KZG/CPLink commitment, and setup included in proving time?

8. How are certified input commitments generated in an end-to-end application?

9. Can the authors provide a comparison to a code-based SNARK or sumcheck/GKR baseline?

10. Is an artifact available?

## Required Changes Before S&P Submission

1. Give a concrete certified-encoding commitment construction and proof.
2. Tie all benchmark numbers to concrete 128-bit parameters.
3. Add constraint/time/proof-size/memory breakdowns.
4. Add stronger baselines beyond Freivalds.
5. Specify the committed-input interface end to end.
6. Add artifact and reproducibility instructions.
7. Add an explicit limitations section.
8. Convert to the S&P template and polish compile/layout warnings.

## Confidential Comments to PC

This revision moves in the right direction. The authors noticed the key issue with global codeword validity and introduced an abstraction meant to fix it. But the abstraction is now the central unproven component of the paper. If instantiated efficiently, the work could become interesting; if not, the main `O(k)` claim may not hold.

I would not accept this version. I would encourage resubmission after the certified-encoding layer is specified and the evaluation is redone with concrete security parameters and stronger baselines.

## Final Verdict

**Improved, but still not ready for S&P.** The proof story is closer, and the claims are more careful, but the paper now depends on an under-specified certified-encoding commitment primitive. The next revision should make that primitive real, measured, and end-to-end.
