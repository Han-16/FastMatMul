# S&P-Style Review: FastMatMul

**Paper:** *FastMatMul: Efficient Verifiable Matrix Multiplication via Linear Error-Correcting Codes*  
**Reviewed material:** `FastMatMul/main.tex`, included `Contents/*.tex`, `Protocols/*.tex`, `Tables/*.tex`, bibliography, and the current compiled `FastMatMul/main.pdf`  
**Venue assumption:** IEEE Symposium on Security and Privacy style review  
**Review form note:** S&P의 정확한 HotCRP 리뷰 양식은 공개 문서만으로는 확정하기 어렵기 때문에, 점수가 포함된 S&P/HotCRP 스타일 양식으로 작성했다.

## Recommendation

**Overall recommendation: Reject / Weak Reject as submitted.**

이 논문은 Freivalds randomized check와 linear error-correcting code의 proximity sampling을 결합해 matrix multiplication SNARK circuit을 `O(k^2)`에서 `O(tk)`로 줄이려는 흥미로운 아이디어를 담고 있다. 큰 방향은 충분히 연구 가치가 있고, large matrix multiplication이 verifiable ML 및 proof-carrying data pipeline에서 중요한 병목이라는 문제 설정도 설득력 있다.

하지만 현재 원고는 S&P 제출 품질에는 아직 못 미친다. 가장 큰 문제는 **SNARK relation이 실제로 어떤 commitment-codeword consistency를 증명하는지 불명확하고, 그에 따라 soundness proof와 complexity claim이 서로 맞지 않는다**는 점이다. 또한 concrete security parameter, query count `t`, code rate/distance, backend details, hardware, setup time, memory, and state-of-the-art comparisons가 부족해 평가 결과를 S&P 수준으로 신뢰하기 어렵다.

## Scores

| Category | Score | Meaning |
|---|---:|---|
| Overall merit | 2 / 5 | Weak reject; interesting idea but not submission-ready |
| Reviewer confidence | 4 / 5 | High, based on full TeX read-through |
| Novelty | 3 / 5 | Plausible combination, but positioning against code-based IOP/SNARK work is thin |
| Technical soundness | 2 / 5 | Core proof path has important specification gaps |
| Significance | 3 / 5 | Potentially useful for large matrix verification |
| Evaluation | 2 / 5 | Promising numbers, but too under-specified |
| Presentation | 3 / 5 | Generally readable, but repetitive and imprecise at key points |
| S&P fit | 3 / 5 | Applied cryptography/proof-system topic fits, but security rigor must improve |
| Artifact readiness | 1 / 5 | No reproducibility or artifact instructions in the paper |

## Summary

FastMatMul targets verifiable matrix multiplication for committed matrices `A`, `B`, and `C`. Instead of arithmetizing the full product or even the full Freivalds vector-matrix products inside a SNARK, the prover computes intermediate vectors `x = rA`, `y = xB`, and `z = rC` outside the circuit, commits to encoded forms of these vectors, and proves only local consistency checks at `t` randomly sampled codeword positions. The intended soundness argument is that any incorrect vector relation induces disagreement between two codewords on at least a `delta` fraction of coordinates, so random sampling catches cheating except with probability about `(1-delta)^t`.

The claimed benefit is substantial: under a linear-time encodable code, the circuit size is claimed to be `O(tk)`, and the experiments report up to `15.1x` fewer constraints and `2.95x` faster proving than a Freivalds SNARK baseline at `k = 2048`.

I like the high-level idea. However, the current formalization does not yet pin down the exact relation being proven, especially the global versus local validity of committed intermediate codewords. The security theorem also omits the SNARK soundness error and treats the certified input-commitment layer as an external assumption whose cost and interface are not fully specified. As written, I would not recommend submitting this version to S&P.

## Strengths

**The problem is important.** Matrix multiplication is a real bottleneck in verifiable computation and zkML. A practical way to avoid `O(k^2)` in-circuit Freivalds checks would be valuable.

**The main technical direction is intuitive and potentially elegant.** Using code linearity to compare sampled encoded coordinates of `rA`, `xB`, and `rC` is a clean way to turn vector-matrix computation into local checks.

**The paper is mostly readable.** The introduction, technical overview, and relation chain make the intended protocol easy to understand at a high level.

**The evaluation shows a plausible asymptotic trend.** The reported constraint counts roughly double when `k` doubles for FastMatMul, while Freivalds grows by about `4x`, which is consistent with the claimed `O(k)` versus `O(k^2)` behavior.

**The paper is honest in one important respect.** It explicitly states that the main theorem is relative to certified encoded input commitments, and that full knowledge soundness requires composition with an extractable input-commitment interface.

## Major Weaknesses

### W1. The SNARK relation and encoding-validity claim are not well specified

The central formal issue is around the constraints `Enc(x)=enc_x`, `Enc(y)=enc_y`, and `Enc(z)=enc_z` in the SNARK relation. The witness definition only includes the intermediate vectors and the opened coordinates at queried positions. It does not include the full committed vector codewords, nor enough information to recompute the Merkle root of a full `Enc(v)` inside the SNARK.

This creates a fork:

1. If the SNARK proves **global** validity of `cm_x`, `cm_y`, and `cm_z` as commitments to full codewords `Enc(x)`, `Enc(y)`, and `Enc(z)`, then the witness and circuit must include enough data to bind the entire Merkle root to the encoded vector. That cost is not captured by the claimed `O(tk + t log n + E_C(k))`.
2. If the SNARK proves only **local** validity at sampled coordinates, then the relation should say so explicitly, and the soundness proof should be rewritten around local coordinate checks rather than globally committed codewords.

This is not merely presentation. The distance-based argument depends on exactly what is bound before the query set `I` is sampled. The current text alternates between a global codeword-validity interpretation and a sampled-coordinate opening interpretation.

### W2. The security theorem omits essential error terms and assumptions

The stated soundness error is

`epsilon_bind + (k-1)/|F| + 4(1-delta)^t`.

This bound should also include at least the SNARK soundness or knowledge-soundness error. The protocol's verifier ultimately accepts when `SNARK.V` accepts, so an unsound SNARK immediately breaks the composed protocol.

For the non-interactive version, the proof should include random-oracle query factors for both challenges, clear domain separation, and a transcript definition. The current Fiat-Shamir text sets `r = Hash(cm_A, cm_B, cm_C)` and `I = Hash(cm_x, cm_y, cm_z)`, but `I` should be bound to the full transcript, including public parameters, input commitments, `r`, vector commitments, and domain tags. The current grinding discussion only handles `I`, not the possibility of grinding over statement commitments in the non-interactive setting.

The theorem also compresses all Merkle binding failures into one `epsilon_bind`; a clean reduction should state whether this is per-root, per-opening, or already union-bounded over all commitments and openings.

### W3. The committed-input model is too strong for the headline claim

The construction assumes certified public roots `cm_A`, `cm_B`, and `cm_C` that already bind to row-wise encodings of valid matrices. This is a legitimate model, but it weakens the headline claim "verifiable matrix multiplication" unless the paper specifies:

- how these certified commitments are produced;
- how a verifier or downstream application learns or opens the raw output `C`;
- whether the cost of certifying `A`, `B`, and `C` is amortized, external, or part of the end-to-end protocol;
- whether the security goal is statement soundness, argument of knowledge, or a committed-output proof.

Without this interface, a major part of the verification problem is delegated to an unspecified layer. S&P reviewers will likely ask whether the `O(tk)` improvement survives in a complete end-to-end system.

### W4. Concrete security parameters are missing from the evaluation

The evaluation does not state the actual code family parameters: `n`, rate `rho`, relative distance `delta`, number of sampled indices `t`, hash security level, or whether the table uses the `t` required for 128-bit soundness.

This matters a lot. For a rate-1/2 Reed-Solomon-like distance, 128-bit proximity soundness typically suggests around 128 samples, before union-bound slack. If the implementation uses a much smaller `t`, then the reported constraints and proof sizes are not directly comparable to a 128-bit Freivalds/SNARK baseline. If it does use large `t`, the paper should show how the reported constraint counts arise.

The text repeatedly calls `t` a small security-parameter-dependent constant, but a security paper needs concrete parameters, not just asymptotic reassurance.

### W5. The evaluation is not S&P-grade yet

The reported performance numbers are promising, but the evaluation section is too thin for a top security venue. It lacks:

- hardware specification, RAM, OS, compiler flags, backend libraries, and curve/hash choices;
- whether proving time includes native matrix multiplication, encoding, Merkle construction, CRS/setup, and commitment/linking;
- setup time and CRS size for Groth16/KZG variants;
- memory usage and explanation of the Freivalds out-of-memory point;
- variance, number of runs, random seeds, and matrix distributions;
- artifact or reproduction commands;
- comparison to relevant state-of-the-art protocols such as zkMatrix, zkVC, generic Brakedown/Orion-style proving of the Freivalds circuit, or sumcheck/GKR-based matrix multiplication verification.

The baseline against only an optimized Freivalds SNARK is useful but insufficient to justify S&P-level significance.

### W6. The `O(k)` circuit claim relies on an underdeveloped code-validity story

The paper says linear-time encodable expander-based codes make the encoding-validity term `O(k)`. But "linear-time encodable" is not automatically the same as "cheap to prove inside a SNARK that a Merkle root commits to the full encoding." The paper needs to define the exact code used, its encoder circuit, how commitment consistency is checked, and why the in-circuit constraints match the table.

For dense general codes, the paper acknowledges an `O(k^2)` encoding-validity term, but the relationship between Table 1, Table 2, and the actual implementation remains hard to audit.

### W7. Zero-knowledge discussion is too hand-wavy

The paper says zero-knowledge can be obtained by replacing Merkle commitments with hiding commitments and using a ZK-SNARK. This is plausible as a future direction, but the current paragraph is too broad. Hiding commitments, masked intermediate vectors, opening consistency, and sampled-coordinate leakage all need a real construction and proof. The paper should avoid implying that ZK follows "without structural changes" unless it actually provides the construction.

### W8. Related work positioning is incomplete

The paper cites the right broad areas, but it does not yet sharply position the contribution against:

- generic code-based IOP/SNARK techniques;
- matrix multiplication verification via coding theory;
- polynomial commitment based committed matrix multiplication;
- sumcheck/GKR approaches used in verifiable ML systems;
- recent zkML systems where matrix products are embedded in larger pipelines.

The novelty may be real, but currently reads as a plausible composition of known ingredients rather than a clearly differentiated S&P contribution.

## Detailed Comments

1. **Add an explicit composed security theorem.** It should include SNARK soundness, Merkle binding, Fiat-Shamir random-oracle query bounds, and the certified-input commitment assumption.

2. **Choose one encoding-validity model.** Either prove full committed codeword validity and pay for it, or define the relation as local coordinate encoding checks and prove soundness accordingly.

3. **Define the concrete code.** Give `rho`, `delta`, `n`, encoder circuit, code construction, and the exact formula for `t` used in experiments.

4. **Bind Fiat-Shamir to the full transcript.** Use domain-separated hashes such as `r = H("challenge-r", pp, cm_A, cm_B, cm_C)` and `I = H("query-I", pp, cm_A, cm_B, cm_C, r, cm_x, cm_y, cm_z)`.

5. **Clarify what is in the proof.** The paper alternates between "SNARK proof only," "six roots plus SNARK proof," and proof sizes of tens of MB due to linking/opening material. State the exact proof object for each backend.

6. **Report proof sizes in the main table.** Proof size is central because the Merkle/CPLink variants reach roughly 49 MB at `k=4096`.

7. **Separate setup, commitment, native arithmetic, and SNARK proving time.** The text mentions CPLink commitment time dominates at one point; this should be a full breakdown for every backend.

8. **Add memory numbers.** "Freivalds exhausts memory" is not meaningful without machine RAM, measured peak RSS, and whether the failure is due to witness generation, constraint synthesis, proving key size, or prover execution.

9. **Do not overclaim succinct verification.** In the evaluated Merkle/CPLink setting, verification and proof size scale with opened column material. The paper should distinguish core SNARK verification from total protocol verification.

10. **Add limitations.** The protocol is best for large square or near-square products under certified committed inputs, with large proof sizes in the evaluated Merkle setting and no current ZK proof. This should be stated explicitly.

11. **Fix venue/template artifacts.** The current LaTeX is ACM CCS-style with placeholder DOI/ISBN and missing ACM CCS/keyword metadata. For S&P, the paper needs the IEEE/S&P template and submission-specific formatting.

12. **Address compile/layout warnings.** The current build log contains many overfull boxes and required metadata warnings. These are not technical blockers, but they signal draft-level polish.

## Questions for Authors

1. What exact code parameters (`n`, `rho`, `delta`) and query count `t` were used for Table 1?

2. Do the reported constraint counts correspond to 128-bit soundness? If yes, how large is `t`, and how are the constraints distributed across fold checks, Merkle checks, encoding checks, and linking?

3. Does the SNARK prove that `cm_x`, `cm_y`, and `cm_z` commit to the full codewords `Enc(x)`, `Enc(y)`, and `Enc(z)`, or only that sampled openings match locally computed coordinates?

4. How are the certified input commitments to `A`, `B`, and `C` generated and verified in an end-to-end application?

5. Are native matrix multiplication, encoding, Merkle tree construction, KZG/CPLink commitment, and setup included in the reported proving times?

6. What hardware and memory limits were used, and what exactly failed for Freivalds at `k = 4096`?

7. Can you compare against at least one state-of-the-art committed matrix multiplication protocol and one generic code-based SNARK baseline?

8. Is the implementation or artifact available with scripts to reproduce the tables?

## Required Changes Before S&P Submission

1. Rewrite the SNARK relation so the commitment/codeword validity semantics are unambiguous.
2. Add a full composed security theorem with SNARK soundness and Fiat-Shamir terms.
3. Specify exact concrete parameters and tie all benchmark rows to a concrete security level.
4. Explain and account for the certified input-commitment layer.
5. Add a detailed evaluation methodology section with hardware, software, setup, memory, proof size, and timing breakdowns.
6. Add stronger baselines beyond Freivalds.
7. Add artifact/reproducibility instructions.
8. Tone down or fully formalize the zero-knowledge extension.
9. Convert to the S&P template and polish layout/metadata.

## Confidential Comments to PC

The paper contains a promising applied-cryptography idea, but I would not accept the current version. My main concern is not that the high-level sampling argument is obviously wrong; rather, the formal relation does not make precise whether intermediate commitments are globally valid codewords or merely locally checked at sampled coordinates. That ambiguity propagates into both the soundness theorem and the `O(k)` circuit claim.

If the authors can cleanly define a local-check relation, prove it in the random-oracle and SNARK-composition setting, and provide concrete 128-bit parameters with reproducible evaluation, this could become a serious submission. As written, it is closer to a promising workshop paper or an early S&P draft than a competitive S&P paper.

## Final Verdict

**Not ready for S&P submission in its current form.** The core idea is worth developing, but the paper needs a more precise relation, a composed security proof, concrete parameterization, and a much stronger evaluation before it can plausibly survive S&P review.
