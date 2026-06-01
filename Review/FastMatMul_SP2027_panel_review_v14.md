# FastMatMul S&P 2027 Panel Review v14

Template used: `SP2027_review_template_and_sample.md`  
Review date: 2026-05-29  
Manuscript: `FastMatMul/main.tex`, latest `FastMatMul/main.pdf`  
Venue facts checked against official IEEE S&P 2027 CFP/submission instructions:

- Official CFP: https://sp2027.ieee-security.org/cfpapers.html
- Submission/page/anonymity/ethics instructions: https://sp2027.ieee-security.org/cfpapers.html

Note: the supplied template is written for agentic-system papers. This paper is a cryptographic/verifiable-computation paper, so R2 is interpreted as a ML/VC threat-model and application-scope critic while preserving the template structure.

---

## 1. Agent 0 Evidence Cartographer and S&P Fit Report

### Claimed Contributions

- A code-based matrix-multiplication checking layer for verifiable computation.
- A reduction from matrix multiplication to sampled proximity checks over row-wise encoded matrix commitments.
- A black-box sampled-opening backend interface connecting Groth16 witness values to authenticated Merkle leaf handles.
- A soundness theorem relative to certified encoded input commitments and the sampled-opening backend.
- A Rust implementation compared against a direct Freivalds-in-SNARK baseline.
- A GPT-2 checking-layer case study over certified roots.

### Evidence Map

| Claim | Evidence in manuscript | Assessment |
|---|---|---|
| In-circuit work is `O(tk + E_msg)` | Construction Sec. 4, complexity table, evaluation scaling | Mostly supported for the checking layer |
| Soundness bound holds | Theorem 5.1, proof sketch in main body, detailed proof in Appendix A | Main theorem is clear, but concrete backend details are mostly appendix-only |
| Sampled columns are not serialized | Evaluation Sec. 6, Appendix C byte accounting | Supported; now consistently scoped as online proof bytes |
| `147 KB` online proof at `k=4096` | Fig. 2/Table 4 and Appendix C | Measured, but excludes key/CRS and raw input certification |
| GPT-2 speedup | Fig. 3/Table 5 | A useful case study, not an end-to-end verifiable ML result |
| End-to-end deployment remains beneficial | Deployment-bound discussion | Conditional; raw input certification is not implemented or measured |

### Closest Works

- Classical Freivalds checking.
- Code-based proof systems such as Brakedown and Orion.
- SNARK systems including Groth16, Pinocchio, Hyrax, Sonic, Marlin, Spartan.
- Verifiable ML systems such as SafetyNets, Mystique, zkCNN, vCNN, zkML.
- Dedicated matrix-verification and matrix-VC protocols.

### Novelty Delta

The strongest novelty is the checking-layer decomposition: use Freivalds plus codeword proximity sampling, while keeping large sampled matrix columns private as SNARK witnesses linked to compact authenticated handles. The paper is more convincing than earlier drafts because it now explicitly separates certified input roots, sampled openings, online proof bytes, and raw-input certification. The novelty is still bounded by the backend assumption: the main paper does not fully instantiate the sampled-opening backend inside the 13-page body.

### S&P Fit

The topic fits S&P under applied cryptography, verification, and secure systems. The paper has plausible practical relevance through SNARK-heavy verifiable computation and ML inference. The main concern is not venue fit but evidence completeness: S&P has no conditional acceptance, and core backend/key-size evidence remains incomplete.

### Policy, Format, Ethics, and Artifact Risks

- Format: compliant. Latest PDF is 16 pages. Main text, conclusion, and references finish by page 12; appendices begin page 13.
- Template: `\documentclass[conference,compsoc]{IEEEtran}` is correct.
- Ethics: adequate for this work; no human subjects, live systems, or vulnerability disclosure.
- GenAI: LLM-use disclosure is present.
- Anonymity: title page and PDF metadata look anonymous. However `FastMatMul/main.fls` contains `PWD /Users/kyeongtae/FastMatMul/Paper`. Build artifacts and `.DS_Store` should not be included in an anonymous artifact repository.

### Main Reviewer Attack Points

- The concrete sampled-opening/CP-link backend is central to the proof-size claim but is mostly in Appendix B, which reviewers are not required to read.
- Key/CRS/generator sizes are explicitly excluded and not reported.
- Raw input certification is outside scope; this is honestly disclosed, but it limits end-to-end VC and ML claims.
- The artifact tree still contains stale `Protocols/` drafts and build artifacts that can confuse reviewers or break anonymity.

### Missing Evidence Likely Fatal at S&P

Not necessarily fatal if the authors frame the work strictly as a checking layer. Potentially fatal if the paper is read as a complete verifiable-computation or verifiable-ML system:

- No measured raw-input certification pipeline.
- No serialized proving/verifying-key or CRS/generator sizes.
- No main-body theorem statement for the concrete batched backend used in the implementation.

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

The submission proposes a modular matrix-multiplication checking protocol that reduces the SNARK relation from Freivalds-style quadratic work to sampled linear work, assuming certified encoded input commitments and a sampled-opening backend. The formal structure is now much clearer: the theorem is explicitly relative to certified roots, message binding, sampled linking, Merkle position binding, and SNARK soundness. However, the most implementation-specific part of the security story, namely the batched CP-link/QA-NIZK backend that supports the reported online proof sizes, is largely moved to the appendix. Since S&P reviewers need the main submission to stand on its own, this is a serious weakness.

### Strengths

- The main theorem is now scoped honestly as statement soundness over certified encoded commitments.
- The ordering of `cm_A,cm_B,cm_C`, `r`, intermediate commitments, and `I` is clear.
- The proof separates Freivalds error, proximity error, SNARK soundness, opening binding, and backend consistency.
- The notation has improved: the protocol now uses aggregate auxiliary proof `sigma_I` instead of per-link serialized proofs in the main flow.

### Weaknesses

1. The concrete backend theorem is appendix-only. The main 13-page body relies on a black-box sampled-opening backend, but the evaluation depends on a specific batched CP-link backend and a 128-byte proof component.
2. The main theorem does not instantiate `epsilon_link` in the body. Appendix B gives `epsilon_ped + epsilon_QA + Q/|F|`, but the main security section only says Appendix B gives the concrete backend.
3. QA-NIZK is not sufficiently introduced in the main body. The paper assumes soundness and CRS structure without a compact construction or citation in the main line of the argument.
4. The paper does not prove argument-of-knowledge or zero knowledge, which is acceptable, but the VC/security framing must avoid implying those properties.
5. Key/CRS/generator material is explicitly outside online proof size; that is correct, but it is a nontrivial cryptographic cost left unquantified.

### Detailed Comments

- Definition 4.1 is a backend contract, not a concrete primitive. This is fine, but then the main body should not let readers infer that the evaluated backend is fully specified there.
- Theorem 5.1 is acceptable as a compositional theorem, but the main body should include one sentence such as: "For the artifact backend, `epsilon_link = epsilon_ped + epsilon_QA + Q/|F|` under Appendix B's assumptions."
- Appendix B now defines `T_I` and the batching equation. This fixes the earlier undefined-batch-tag issue, but relying on Appendix B is risky because reviewers need not read appendices.
- The non-interactive proof discussion correctly mentions random-oracle loss, but the backend batching also uses Fiat-Shamir. The paper should ensure these random-oracle uses are jointly domain-separated and included in the final loss accounting.

### Questions for Authors

- What exact QA-NIZK construction is used for the linear batch relation, and under which assumption?
- Are handle generators seed-derived or serialized? If seed-derived, what is the generator derivation model?
- Does `epsilon_FS(q_H)` include both protocol Fiat-Shamir and CP-link batching Fiat-Shamir queries?
- Can the main theorem instantiate the artifact backend without sending the reader to Appendix B?

### Comparison With Recent Work

The paper positions itself well against Freivalds-in-SNARK and code-based committed-oracle systems. The relation to Brakedown/Orion is now more precise: this is not a new global code-commitment primitive, but a sampled checking layer over certified roots. The matrix-VC comparison remains necessarily qualitative because assumptions differ.

### Ethics, Disclosure, and Artifact Concerns

No direct ethical issue. The proof and backend details should be included in an anonymized artifact because the formal claim relies on them.

### Final Recommendation

Weak Reject. The formal core is plausible and close, but the concrete backend used for the headline proof-size result is not sufficiently self-contained in the main submission.

### What Would Change My Score

A compact main-body statement of the artifact backend theorem, its assumptions, and `epsilon_link` instantiation would likely move this review to Borderline or Weak Accept.

---

## 3. R2 Agentic AI Security and ML Threat-Model Critic Review

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

This is not an agentic-AI security paper; it is a verifiable-computation paper with a verifiable-ML motivation. The ML-facing claim is now appropriately narrowed to a GPT-2 checking-layer case study over certified roots. That scoping is much better than claiming an end-to-end verifiable inference system. However, the practical ML relevance still depends on an unimplemented upstream certification pipeline for model weights, activations, and outputs. The paper gives a deployment-bound argument, but no measured pipeline. For S&P, this is acceptable only if the paper consistently presents the result as a cryptographic checking layer, not as a complete zkML system.

### Strengths

- The paper no longer overclaims end-to-end zkML.
- The GPT-2 section clearly says costs are over certified roots.
- The verifier/prover tradeoff is explicit: faster proving and smaller circuits, but slower verification in the GPT-2 row.
- The evaluation includes a realistic neural-network-shaped aggregation of 36 matrix multiplications.

### Weaknesses

1. The ML motivation remains stronger than the measured end-to-end evidence.
2. Static weight roots and per-request activation/output roots are discussed, but no concrete upstream interface is implemented.
3. The result does not address non-matrix operations, quantization, batching behavior, or model-pipeline integration.
4. The paper's practical relevance depends on amortization assumptions that are only bounded analytically.

### Detailed Comments

- Abstract and Introduction now correctly say "checking layer" and "certified commitments." This should remain unchanged.
- The GPT-2 row is best treated as a case study, not as a benchmark of a full verifiable inference system.
- The deployment-bound margins are useful, but they do not substitute for a measured root-certification instantiation.
- If the authors want ML reviewers to care, they should state which deployment class benefits most: static model weights with many repeated proofs, not arbitrary one-off inference.

### Questions for Authors

- Which roots in the GPT-2 case are static and amortizable, and which are per request?
- What is the expected certification path for activation/output roots?
- Does the checker compose with existing zkML systems, or does it require a separate committed-codeword pipeline?

### Comparison With Recent Work

The paper should avoid being judged directly against full zkML systems. Its contribution is narrower: a faster multiplication-checking component that could be plugged into a larger committed-codeword VC stack.

### Ethics, Disclosure, and Artifact Concerns

No human-subjects or live-system issue. The LLM-use disclosure is adequate as editorial assistance.

### Final Recommendation

Borderline. The ML/application story is honest enough, but the paper should not lean harder on GPT-2 than the evidence supports.

### What Would Change My Score

A concrete certification interface for activations/outputs, even analytically specified with a measured microbenchmark, would improve the application case.

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

The paper is careful to separate upstream input-root certification from the online multiplication checker. That separation makes the system boundary understandable, but it also exposes the main deployment gap. A real deployment must produce certified roots, manage setup/key/CRS material, and decide how to amortize static and dynamic roots. The paper measures the online checker and reports useful speedups over a Freivalds SNARK baseline, but it leaves several production costs as assumptions. This is not fatal for a modular cryptographic paper, but it weakens the systems claim and makes the paper less complete for S&P.

### Strengths

- The two-layer deployment model is explicit.
- The paper gives online proof sizes and separates raw sampled columns from serialized proof material.
- Verification overhead is now reported more honestly; GPT-2 verification is only `1.39x` slower rather than an unbounded surprise.
- Hardware and core experimental parameters are present.

### Weaknesses

1. Raw input certification is unimplemented and unmeasured.
2. Serialized proving/verifying-key and CRS/generator sizes are not reported.
3. The paper excludes native multiplication and certification costs from the checking-layer comparison; this is legitimate but must remain prominent.
4. Artifact hygiene is not ready: build artifacts, `.DS_Store`, and stale `Protocols/` files remain in the tree.
5. The artifact anonymity risk is concrete: `main.fls` contains a local user path.

### Detailed Comments

- Table 3 is helpful because it explicitly separates certified input roots and online checking. This should stay in the main body.
- Appendix C says setup/key sizes are not reported. This is a major limitation for systems readers because CRS/key material can dominate deployment storage.
- The `Protocols/` folder contains old draft protocol files that are not included by `main.tex`. If submitted as artifact, they will confuse reviewers about which protocol is actually evaluated.
- The artifact should include a clean build/reproduction script and omit transient LaTeX artifacts.

### Questions for Authors

- What files are actually part of the intended anonymous artifact?
- Are proving/verifying keys generated per matrix size, per circuit, or reusable across dimensions?
- How large is the Groth16 proving key for `k=4096` and for the GPT-2 circuit?
- Is the CP-link generator material seed-derived, universal, or serialized?

### Comparison With Recent Work

The paper is strongest when compared with a direct Freivalds-in-SNARK checker. Comparisons to full VC/zkML deployments should remain qualitative unless input certification and setup/key material are included.

### Ethics, Disclosure, and Artifact Concerns

The artifact needs anonymization. Remove `.fls`, `.fdb_latexmk`, `.log`, `.aux`, `.blg`, `.out`, `.DS_Store`, and stale protocol drafts unless they are explicitly marked as non-submission material.

### Final Recommendation

Weak Reject. The system boundary is now honest, but the deployment evidence remains incomplete.

### What Would Change My Score

Reporting key/CRS sizes and cleaning the artifact would likely move this to Borderline or Weak Accept from a systems perspective.

---

## 5. R4 Empirical Rigor, Reproducibility, and Artifact Auditor Review

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

The evaluation provides meaningful scaling evidence for the online checking layer. The primary plots show the expected linear versus quadratic constraint growth, and the Freivalds baseline is a reasonable same-stack baseline for the specific relation. The paper also reports a GPT-2 case study and clearer proof-size accounting. However, reproducibility and empirical completeness are not yet S&P-strong. The paper omits variance, peak memory, key/CRS sizes, strict-parameter measured rows, and raw input certification. It also does not measure Freivalds at `k=8192`, where the extrapolated advantage would be most visible.

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
6. Artifact contents are not clean or anonymized in the current tree.

### Detailed Comments

- The `k=4096` result is the strongest empirical row: `30.3x` fewer constraints and `7.24x` faster proving than Freivalds.
- The proof-size claim is now phrased as online proof bytes excluding key/CRS, which is correct.
- The GPT-2 proof is `3,355,428 B`, substantially larger than single-matrix rows; the paper reports it, but the reader would benefit from a short explanation of what dominates this size.
- Appendix C's measurement coverage table is useful, but some of its most important limitations should be summarized in the main body.

### Questions for Authors

- How many times was each benchmark run?
- Were there failed or out-of-memory runs?
- What are the proving-key and verifying-key sizes for each reported row?
- Can the artifact reproduce every figure/table from one command?
- Are random seeds, parameter files, and CSV outputs included anonymously?

### Comparison With Recent Work

The evaluation is fair against Freivalds-in-SNARK for the online checker. It does not establish superiority over full code-based VC systems or dedicated matrix-VC protocols under their native assumptions, and the paper mostly avoids claiming that.

### Ethics, Disclosure, and Artifact Concerns

No direct ethics issue. Artifact readiness is the main concern.

### Final Recommendation

Weak Reject. The evaluation supports the central trend but leaves too many deployment and reproducibility costs unmeasured for an S&P accept.

### What Would Change My Score

Adding key/CRS sizes, repeated-run statistics, peak memory, and a clean anonymized artifact would likely move this review to Borderline or Weak Accept.

---

## 6. PC Discussion

### Anchor 1: Novelty Delta and S&P-Level Significance

Lead: R1.

The panel agrees that the checking-layer decomposition is meaningful and relevant to S&P. The novelty is not a new SNARK or new code-commitment system, but a useful composition for matrix multiplication over certified encoded roots. R2 notes that the ML application should remain secondary. R3 and R4 agree that the contribution is strongest when scoped as a modular cryptographic checker.

Score changes: none.

### Anchor 2: Baseline Fairness and Empirical Adequacy

Lead: R4.

The Freivalds-in-SNARK baseline is fair for the main checking-layer claim. The evidence is weaker for broader VC or zkML claims because input certification and key/CRS sizes are excluded. The panel agrees that the paper is honest about this exclusion, but honesty does not fully replace measurement.

Score changes: none.

### Anchor 3: Necessity and Sufficiency of Cryptographic Machinery

Lead: R1.

The panel agrees that the sampled-opening backend is necessary for the claimed online proof-size behavior. However, the concrete backend theorem being in Appendix B is a problem under the S&P rule that appendices are optional for reviewers. R1 would be more positive if the main body contained the concrete `epsilon_link` instantiation and QA-NIZK assumptions.

Score changes: R1 remains Weak Reject rather than Borderline.

### Anchor 4: Deployment, Runtime Boundary, and Operational Realism

Lead: R3.

The system boundary is now clear: certified roots are preconditions and raw input certification is upstream. The panel views this as acceptable only if the paper does not imply end-to-end VC. Key/CRS sizes and artifact hygiene remain operational gaps.

Score changes: none.

### Anchor 5: External Validity, Reproducibility, Artifacts, Ethics, and Disclosure

Lead: R4.

The paper includes ethics and LLM-use disclosures and has no obvious REC issue. Artifact readiness is still weak because build products leak a local path and stale protocol drafts remain. Theoretical proof artifacts are encouraged by S&P, and this paper would benefit from a clean proof/artifact bundle.

Score changes: none.

---

## 7. PC Chair Meta-Review

### Final Decision

Reject / high Borderline in current form.

This is close enough that a compact pre-submission revision could materially improve it, but under S&P's no-conditional-accept posture the current submission still has central evidence and self-containment gaps.

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
- The paper now states its certified-root assumption honestly.
- Evaluation shows strong scaling against a fair direct Freivalds-in-SNARK baseline.
- Page format, anonymity in the PDF, ethics, and LLM disclosure are acceptable.

### Key Rejection Arguments

- The concrete backend that enables the online proof-size claim is mostly appendix-only.
- Key/CRS/generator sizes are not measured.
- Raw input certification is not implemented or measured.
- Artifact tree is not anonymization-clean and contains stale draft protocol files.
- Strict-parameter results and reproducibility statistics are not measured.

### Public Meta-Review Concerns If Accepted

If accepted, the public meta-review would need to state that the result is a checking-layer protocol over certified encoded roots, not an end-to-end raw-input VC or zkML system. It would also need to disclose that online proof sizes exclude key/CRS/generator material and raw input certification.

### Conditional Uplift Conditions

S&P 2027 has no conditional acceptance. The following would have needed to be in the submitted paper:

- A main-body statement of the concrete batched backend theorem and assumptions.
- Explicit `epsilon_link = epsilon_ped + epsilon_QA + Q/|F|` in the security section.
- Serialized key/CRS/generator sizes for at least `k=1024`, `k=4096`, and GPT-2.
- Clean anonymized artifact with stale drafts and local-path build files removed.
- Repeated-run/variance and peak-memory reporting.

### Rebuttal Advice

The rebuttal should not promise new experiments. It should point reviewers to exact main-body statements for the certified-root scope, online-proof-size convention, and backend assumptions. If key/CRS data exists in the artifact, cite exact anonymous files and numbers. If not, acknowledge the limitation and avoid reframing the result as end-to-end.

### Final Recommendation

Weak Reject for S&P as currently submitted. The paper is technically much closer than earlier drafts, but the remaining issues affect core claims rather than presentation polish.

### Most Important Changes Before Submission

1. Move the concrete backend theorem summary and `epsilon_link` instantiation from Appendix B into the main body.
2. Add key/CRS/generator size accounting or make every proof-size claim explicitly "online proof bytes excluding key/CRS."
3. Clean the artifact repository for anonymity and remove stale draft protocol files.

### Desk-Reject, REC, Artifact, Anonymity, or Policy Risks

- Desk reject for page limit: no current risk.
- REC/ethics: no current risk.
- PDF anonymity: no current risk found.
- Artifact anonymity: current risk due to `main.fls` local path and `.DS_Store`/build artifacts.
- Artifact confusion: current risk due to stale `Protocols/` files.

---

## 8. Short Action List for Authors

1. Put the CP-link/backend theorem summary in the main body, not only Appendix B.
2. In Theorem 5.1 or immediately after it, instantiate `epsilon_link` for the artifact backend.
3. Add a one-paragraph QA-NIZK/CRS/generator model in the main body.
4. Report key/CRS/generator byte sizes for representative rows, or state in every headline proof-size sentence that the number is online-only.
5. Keep all end-to-end VC and zkML language scoped to certified roots.
6. Add variance/repeated-run counts and peak memory if available.
7. Remove `.fls`, `.fdb_latexmk`, `.log`, `.aux`, `.blg`, `.out`, `.DS_Store`, and stale `Protocols/` drafts from the anonymous artifact.
8. Keep the current page discipline: the format is finally in good shape.
