# FastMatMul S&P 2027 Panel Review v15

Review date: 2026-05-29  
Manuscript: `FastMatMul/main.tex`, latest `FastMatMul/main.pdf`  
Template basis: `SP2027_review_template_and_sample.md`, with user-specific exclusions applied.

Official venue references:

- IEEE S&P 2027 CFP: https://sp2027.ieee-security.org/cfpapers.html
- IEEE S&P 2027 submission instructions: https://sp2027.ieee-security.org/cfpapers.html

---

## 1. Agent 0 Evidence Cartographer and S&P Fit Report

### Claimed Contributions

- A code-based matrix-multiplication checking layer for verifiable computation.
- A reduction from matrix multiplication to sampled proximity checks over row-wise encoded matrix commitments.
- A sampled-opening backend interface that links Groth16 witness values to authenticated Merkle leaf handles.
- A soundness theorem relative to certified encoded input commitments and the sampled-opening backend.
- A Rust implementation compared with a direct Freivalds-in-SNARK baseline.
- A GPT-2 checking-layer case study over certified roots.

### Evidence Map

| Claim | Evidence in manuscript | Assessment |
|---|---|---|
| In-circuit work is `O(tk + E_msg)` | Construction Sec. 4, complexity table, evaluation scaling | Mostly supported for the online checking layer |
| Soundness bound holds | Theorem 5.1, main proof sketch, Appendix A proof | Plausible, but concrete backend instantiation is not self-contained in main body |
| Sampled matrix columns are not serialized | Evaluation Sec. 6 and Appendix C accounting | Supported; proof-size claims are now scoped as online proof bytes |
| `147 KB` online proof at `k=4096` | Sec. 6 and Appendix C | Measured, but excludes key/CRS/generator material and raw input certification |
| GPT-2 speedup | Fig. 3/Table 5 | Useful case study, not an end-to-end verifiable ML result |
| End-to-end deployment remains beneficial | Deployment-bound discussion | Conditional; raw input certification is not measured |

### Novelty Delta

The strongest novelty is the checking-layer decomposition: combine Freivalds with codeword proximity sampling, while keeping large sampled matrix columns private as SNARK witnesses linked to compact authenticated handles. The submission is now clearer because it separates certified input roots, sampled openings, online proof bytes, and raw-input certification. The novelty is still partially bounded by the sampled-opening backend assumption.

### S&P Fit

The topic fits S&P under applied cryptography, verification, and secure systems. Theoretical relevance to practice is plausible because matrix multiplication is a bottleneck in SNARK-based verifiable computation and verifiable ML. The main issue is evidence completeness, not venue fit.

### Format and Policy Check

- Latest `main.pdf` is 16 pages.
- Main text, conclusion, and references finish by page 12; appendices begin page 13.
- The page budget is therefore compliant with the S&P 2027 13-page main-text rule plus references/appendices.
- `\documentclass[conference,compsoc]{IEEEtran}` is correct.
- Anonymous title page is correct.
- Ethics and LLM-use sections are present and adequate.

### Main Reviewer Attack Points

- The concrete CP-link/backend theorem is central to the proof-size claim but is mostly in Appendix B.
- `epsilon_link` is not instantiated in the main security theorem body.
- Key/CRS/generator sizes are excluded from online proof-size claims and not reported.
- Raw input certification is explicitly outside scope, limiting end-to-end VC and ML claims.
- Strict `t=133` security rows are extrapolated, not measured.

---

## 2. R1 Formal, Cryptographic, and Protocol Soundness Hawk Review

Score: Weak Reject  
Confidence: 4

### Sub-scores

| Criterion | Score |
|---|---|
| Significance | Medium-High |
| Novelty | Medium |
| Correctness | Medium |
| Evidence quality | Medium-Low |
| Presentation | Medium |
| S&P fit | Medium-High |

### 100-Word Author-Framing Summary

The paper proposes a modular matrix-multiplication checking protocol that reduces the SNARK relation from Freivalds-style quadratic work to sampled linear work, assuming certified encoded input commitments and a sampled-opening backend. The formal scope is now much clearer: the theorem is explicitly relative to certified roots, message binding, sampled linking, Merkle position binding, and SNARK soundness. However, the most implementation-specific part of the security story, namely the batched CP-link/QA-NIZK backend supporting the reported online proof sizes, remains mostly in the appendix. For S&P, this weakens the self-contained correctness argument.

### Strengths

- The theorem is now honestly scoped as statement soundness over certified encoded commitments.
- The challenge ordering is clear: input roots before `r`, intermediate commitments before `I`.
- The proof separates Freivalds error, proximity error, SNARK soundness, opening binding, and backend consistency.
- The protocol now uses aggregate auxiliary proof `sigma_I`, resolving the earlier per-link/proof-size mismatch.

### Weaknesses

1. The concrete backend theorem is not in the main body. The main 13-page submission relies on a black-box sampled-opening backend, while the evaluation depends on a specific batched CP-link backend.
2. The main security theorem does not instantiate `epsilon_link`; Appendix B gives the relevant `epsilon_ped + epsilon_QA + Q/|F|` style bound.
3. QA-NIZK is not sufficiently introduced in the main text. The construction assumes a sound proof for the linear batch relation, but the main body does not define its statement, CRS model, or proof-size basis.
4. Fiat-Shamir appears both in the main protocol and in the backend batching. The paper should explicitly state whether the final `epsilon_FS(q_H)` covers both random-oracle uses.
5. The result is not an argument of knowledge or zero knowledge. The paper says this, but the abstract and introduction should continue avoiding any stronger VC implication.

### Detailed Comments

- Definition 4.1 is a backend contract, not a concrete primitive. This is acceptable only if the paper consistently frames the backend as an assumption.
- Theorem 5.1 would be stronger if followed by a main-body corollary for the evaluated backend.
- Appendix B now defines `T_I` and the batching equation, which fixes a prior transcript ambiguity. The issue is placement, not content.
- The sampled-opening backend is the main non-standard component. Keeping its core theorem only in the appendix makes the submitted paper weaker.

### Questions for Authors

- What exact QA-NIZK construction is used for the linear batch relation?
- Are handle generators seed-derived, universal, or serialized?
- Does the Fiat-Shamir loss account for both protocol challenge derivation and backend batch challenge derivation?
- Can the paper state the evaluated backend theorem in the main body in 5-6 lines?

### Comparison With Recent Work

The comparison to Freivalds-in-SNARK is clear and relevant. The relationship to Brakedown/Orion is now better scoped: the paper does not claim a new global code-commitment primitive, but a checking layer over certified roots. The comparison to dedicated matrix-VC work remains qualitative, which is acceptable given differing assumptions.

### Ethics and Disclosure Concerns

No direct concern.

### Final Recommendation

Weak Reject. The formal idea is plausible and close, but the main submission still hides a central backend assumption behind appendix-level detail.

### What Would Change My Score

A compact main-body statement of the concrete backend theorem, assumptions, and `epsilon_link` instantiation would likely move this to Borderline or Weak Accept.

---

## 3. R2 ML/VC Threat-Model and Application-Scope Critic Review

Score: Borderline  
Confidence: 3

### Sub-scores

| Criterion | Score |
|---|---|
| Significance | Medium |
| Novelty | Medium |
| Correctness | Medium |
| Evidence quality | Medium-Low |
| Presentation | Medium |
| S&P fit | Medium |

### 100-Word Author-Framing Summary

This is a verifiable-computation paper with a verifiable-ML motivation. The ML-facing claim is now appropriately narrowed to a GPT-2 checking-layer case study over certified roots. That scoping is much better than claiming an end-to-end verifiable inference system. However, the practical ML relevance still depends on an upstream certification pipeline for model weights, activations, and outputs. The paper gives a deployment-bound argument, but no measured pipeline. For S&P, this is acceptable only if the paper consistently presents the result as a cryptographic checking layer, not as a complete zkML or raw-input verifiable-computation system.

### Strengths

- The paper no longer overclaims end-to-end zkML.
- The GPT-2 section clearly says costs are over certified roots.
- The verifier/prover tradeoff is explicit.
- The evaluation includes a neural-network-shaped aggregation of 36 matrix multiplications.

### Weaknesses

1. The ML motivation remains stronger than the measured end-to-end evidence.
2. Static weight roots and per-request activation/output roots are discussed, but no concrete upstream interface is implemented.
3. The result does not address non-matrix operations, quantization, batching behavior, or model-pipeline integration.
4. Deployment benefit depends on amortization assumptions that are only bounded analytically.

### Detailed Comments

- Abstract and Introduction correctly use “checking layer” and “certified commitments.” This should not be weakened.
- The GPT-2 row should remain framed as a case study, not a full verifiable inference benchmark.
- The deployment-bound margins are useful but do not replace a measured root-certification instantiation.
- The most plausible deployment is repeated use of static certified roots with amortization.

### Questions for Authors

- Which GPT-2 roots are static and amortizable, and which are per request?
- What is the expected certification path for activation/output roots?
- Does the checker compose with existing zkML systems, or does it require a separate committed-codeword pipeline?

### Comparison With Recent Work

The paper should avoid direct claims against full zkML systems. Its contribution is narrower: a faster multiplication-checking component that may fit into a larger committed-codeword VC stack.

### Ethics and Disclosure Concerns

No direct concern. The LLM-use disclosure is adequate.

### Final Recommendation

Borderline. The application story is now honest enough, but the paper should not lean harder on GPT-2 than the evidence supports.

### What Would Change My Score

A concrete certification interface for activations/outputs, even with a small measured component or precise analytical contract, would improve the score.

---

## 4. R3 Systems Threat-Model and Deployment Realism Skeptic Review

Score: Weak Reject  
Confidence: 4

### Sub-scores

| Criterion | Score |
|---|---|
| Significance | Medium |
| Novelty | Medium |
| Correctness | Medium |
| Evidence quality | Medium-Low |
| Presentation | Medium |
| S&P fit | Medium |

### 100-Word Author-Framing Summary

The paper now gives a clear system boundary: certified input roots are preconditions, and the online multiplication checker proves only the relation among those roots. That makes the contribution easier to evaluate, but it also exposes the main deployment gap. A real deployment must produce certified roots, manage setup/key/CRS material, and decide how to amortize static and dynamic roots. The paper measures the online checker and reports useful speedups over Freivalds-in-SNARK, but several production costs remain outside the comparison. This is acceptable for a modular cryptographic paper only if the claims stay tightly scoped.

### Strengths

- The two-layer deployment model is explicit.
- The paper separates raw sampled columns from serialized online proof material.
- Verification overhead is reported clearly in the GPT-2 row.
- Hardware and core experimental parameters are present.

### Weaknesses

1. Raw input certification is unimplemented and unmeasured.
2. Serialized proving/verifying-key and CRS/generator sizes are not reported.
3. The comparison excludes native multiplication and certification costs; this is legitimate but must remain prominent.
4. The proof-size claim is online-only and should never be shortened to “proof size” without qualification.

### Detailed Comments

- Table 3 is useful because it separates certified input roots from online checking.
- Appendix C says setup/key sizes are not reported. This is a major limitation for systems readers.
- The single most important systems clarification is whether setup/key material scales with `k`, with circuit size, or with the backend parameters.
- The paper’s deployment story is strongest for repeated checks over amortized certified roots.

### Questions for Authors

- Are proving/verifying keys generated per matrix size, per circuit, or reusable across dimensions?
- How large is the Groth16 proving key for `k=4096` and for the GPT-2 circuit?
- Is CP-link generator material seed-derived, universal, or serialized?
- What amortization regime is required for the GPT-2 case study to remain favorable?

### Comparison With Recent Work

The paper is strongest against a direct Freivalds-in-SNARK checker. Comparisons to full VC/zkML deployments should remain qualitative unless input certification and setup/key material are included.

### Ethics and Disclosure Concerns

No direct concern.

### Final Recommendation

Weak Reject. The boundary is honest, but deployment evidence remains incomplete.

### What Would Change My Score

Reporting key/CRS sizes and adding one concrete certification-interface option would likely move this to Borderline.

---

## 5. R4 Empirical Rigor and Evidence Auditor Review

Score: Weak Reject  
Confidence: 4

### Sub-scores

| Criterion | Score |
|---|---|
| Significance | Medium |
| Novelty | Medium |
| Correctness | Medium |
| Evidence quality | Medium-Low |
| Presentation | Medium |
| S&P fit | Medium |

### 100-Word Author-Framing Summary

The evaluation provides meaningful scaling evidence for the online checking layer. The primary plots show the expected linear versus quadratic constraint growth, and the Freivalds baseline is a reasonable same-stack baseline for the specific relation. The paper also reports a GPT-2 case study and clearer proof-size accounting. However, empirical completeness is not yet S&P-strong. The paper omits variance, peak memory, key/CRS sizes, strict-parameter measured rows, and raw input certification. It also does not measure Freivalds at `k=8192`, where the extrapolated advantage would be most visible.

### Strengths

- Same-stack Freivalds baseline is appropriate for the checking-layer claim.
- Main matrix benchmark reports constraints and proving time across several `k`.
- GPT-2 case study reports constraints, setup, prove, verify, and proof bytes.
- Appendix C explicitly distinguishes measured and unmeasured costs.

### Weaknesses

1. No variance, confidence intervals, or repeated-run statistics.
2. No peak memory reporting.
3. No serialized key/CRS size reporting.
4. Strict `t=133` rows are extrapolated, not measured.
5. Freivalds is not measured at `k=8192`, so the largest comparison lacks a baseline point.

### Detailed Comments

- The `k=4096` result is the strongest empirical row: `30.3x` fewer constraints and `7.24x` faster proving than Freivalds.
- The proof-size claim is now correctly phrased as online proof bytes excluding key/CRS.
- The GPT-2 proof is `3,355,428 B`, substantially larger than single-matrix rows. The paper reports this, but should briefly explain what dominates that size.
- Appendix C’s measurement coverage table is useful, but the most important exclusions should remain visible in the main body.

### Questions for Authors

- How many times was each benchmark run?
- Were there failed or out-of-memory runs?
- What are the proving-key and verifying-key sizes for each reported row?
- Why is Freivalds not measured at `k=8192`?
- How sensitive are results to `t=133` when measured rather than extrapolated?

### Comparison With Recent Work

The evaluation is fair against Freivalds-in-SNARK for the online checker. It does not establish superiority over full code-based VC systems or dedicated matrix-VC protocols under their native assumptions, and the paper mostly avoids claiming that.

### Ethics and Disclosure Concerns

No direct concern.

### Final Recommendation

Weak Reject. The evaluation supports the central trend but leaves too many deployment and measurement costs unreported for a strong S&P accept.

### What Would Change My Score

Adding key/CRS sizes, repeated-run statistics, peak memory, and measured strict-parameter rows would likely move this to Borderline or Weak Accept.

---

## 6. PC Discussion

### Anchor 1: Novelty Delta and S&P-Level Significance

Lead: R1.

The panel agrees that the checking-layer decomposition is meaningful and relevant to S&P. The novelty is not a new SNARK or new code-commitment system, but a useful composition for matrix multiplication over certified encoded roots. R2 notes that the ML application should remain secondary. R3 and R4 agree that the contribution is strongest when scoped as a modular cryptographic checker.

Score changes: none.

### Anchor 2: Baseline Fairness and Empirical Adequacy

Lead: R4.

The Freivalds-in-SNARK baseline is fair for the main checking-layer claim. The evidence is weaker for broader VC or zkML claims because input certification and key/CRS sizes are excluded. The panel agrees that the paper is honest about these exclusions, but disclosure does not fully replace measurement.

Score changes: none.

### Anchor 3: Necessity and Sufficiency of Cryptographic Machinery

Lead: R1.

The panel agrees that the sampled-opening backend is necessary for the claimed online proof-size behavior. However, the concrete backend theorem being in Appendix B is a problem under the S&P rule that appendices are optional for reviewers. R1 would be more positive if the main body contained the concrete `epsilon_link` instantiation and QA-NIZK assumptions.

Score changes: R1 remains Weak Reject rather than Borderline.

### Anchor 4: Deployment and Operational Realism

Lead: R3.

The system boundary is clear: certified roots are preconditions and raw input certification is upstream. The panel views this as acceptable only if the paper does not imply end-to-end VC. Key/CRS sizes remain an operational gap.

Score changes: none.

### Anchor 5: External Validity, Measurement Completeness, Ethics, and Disclosure

Lead: R4.

The evidence supports the online-checking trend but does not fully cover deployment costs or statistical stability. No severe ethics issue is apparent.

Score changes: none.

---

## 7. PC Chair Meta-Review

### Final Decision

Reject / high Borderline in current form.

The paper is technically close, and its current framing is substantially more defensible than earlier versions. However, under S&P’s no-conditional-accept posture, the main submission still has central self-containment and measurement gaps.

### Vote Distribution

| Reviewer | Score | Confidence |
|---|---:|---:|
| R1 | Weak Reject | 4 |
| R2 | Borderline | 3 |
| R3 | Weak Reject | 4 |
| R4 | Weak Reject | 4 |

### Key Acceptance Arguments

- Clear S&P relevance in applied cryptography and verifiable computation.
- The checking-layer idea is technically plausible and useful.
- The certified-root assumption is now explicit.
- Evaluation shows strong scaling against a fair direct Freivalds-in-SNARK baseline.
- Page format, ethics, and LLM-use disclosure are acceptable.

### Key Rejection Arguments

- The concrete backend enabling the online proof-size claim is mostly appendix-only.
- Key/CRS/generator sizes are not measured.
- Raw input certification is not implemented or measured.
- Strict-parameter results are extrapolated.
- Empirical stability is not reported.

### Public Meta-Review Concerns If Accepted

If accepted, the public meta-review would need to state that the result is a checking-layer protocol over certified encoded roots, not an end-to-end raw-input VC or zkML system. It would also need to disclose that online proof sizes exclude key/CRS/generator material and raw input certification.

### Conditional Uplift Conditions

S&P 2027 has no conditional acceptance. The following would have needed to be in the submitted paper:

- A main-body statement of the concrete batched backend theorem and assumptions.
- Explicit `epsilon_link = epsilon_ped + epsilon_QA + Q/|F|` in the security section.
- Serialized key/CRS/generator sizes for representative rows.
- Repeated-run statistics, peak memory, and measured strict-parameter rows.

### Rebuttal Advice

The rebuttal should not promise new experiments. It should point reviewers to exact main-body statements for the certified-root scope, online-proof-size convention, backend assumptions, and measured evidence. If key/CRS data already exists in the paper, cite the exact table and numbers.

### Final Recommendation

Weak Reject for S&P as currently submitted. The paper is close enough that a small but targeted pre-submission revision could change the outcome.

### Most Important Changes Before Submission

1. Move the concrete backend theorem summary and `epsilon_link` instantiation from Appendix B into the main body.
2. Add key/CRS/generator size accounting, or keep every proof-size claim explicitly “online proof bytes excluding key/CRS.”
3. Add measured strict-parameter rows or clearly demote them to extrapolation.

### Desk-Reject, REC, Anonymity, or Policy Risks

- Desk reject for page limit: no current risk.
- REC/ethics: no current risk.
- Paper anonymity: no current risk found in the manuscript.
- Policy: no current issue beyond ensuring all central assumptions remain in the main body.

---

## 8. Short Action List for Authors

1. Put the CP-link/backend theorem summary in the main body, not only Appendix B.
2. In Theorem 5.1 or immediately after it, instantiate `epsilon_link` for the evaluated backend.
3. Add a one-paragraph QA-NIZK/CRS/generator model in the main body.
4. Report key/CRS/generator byte sizes for representative rows, or state in every headline proof-size sentence that the number is online-only.
5. Keep all end-to-end VC and zkML language scoped to certified roots.
6. Add variance/repeated-run counts and peak memory if available.
7. Keep the current page discipline: the format is in good shape.
