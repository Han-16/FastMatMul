Dear Shepherd,

Thank you for the committee's feedback and for shepherding our paper, #1646, “LAMP: Linear Verification of Matrix Multiplication via Proximity Testing.” We would like to revise the paper to address Noteworthy Concern 1 regarding the coverage of state-of-the-art performance comparisons beyond DualMatrix.

The interactive-rebuttal revision already includes an asymptotic comparison with zkMatrix, DualMatrix, and zkMaP, and experiments against DualMatrix and a Freivalds-based SNARK baseline. We propose the following additional revisions.

**1. Broaden and qualify the comparison in Section 2 and Table 1.** We will review further relevant work, including *Scalable zkSNARKs for Matrix Computations: A Generic Framework for Verifiable Deep Learning* (Evalyn), for which a public implementation is available. We will clarify the statements proved, commitment interfaces, setup and security assumptions, and which costs are included in the complexity comparisons. This will distinguish LAMP's reduction in circuit constraints from total prover work.

**2. Investigate an additional empirical comparison in Section 7.** We will assess whether Evalyn's public implementation supports a comparable matrix-product workload. Our target is a controlled comparison with explicit accounting for input commitments, proving, verification, and communication. We will first establish the compatibility of the relations, parameters, and measurement boundaries. Where a comparable experiment is feasible, we will add measurements under matched conditions and disclose remaining differences. Otherwise, we will document the specific limitations and discuss published results separately with their experimental conditions, without presenting cross-paper timing ratios as controlled speedups.

**3. Clarify the scope of the performance conclusions.** We will revise the abstract, contributions, evaluation discussion, and conclusion as needed to tie empirical advantages to the evaluated baselines and workloads, and to make the prover-time, verifier-time, and proof-size trade-offs explicit. We will also clarify the distinction between our GPT-2 matrix-product workload and end-to-end inference verification.

We would appreciate your guidance on whether this scope appropriately addresses the concern and whether there is a particular comparison target you would prioritize. We aim to provide a revised manuscript, a diff, and a response letter by October 2, allowing time for feedback before the October 9 near-final approval target. We would then request reconsideration of the concern based on the evidence in the revision.

Best regards,
The authors

References for the proposed additional comparison:

- [Paper](https://eprint.iacr.org/2025/1646)
- [Public implementation](https://github.com/mirandaprivate/evalyn_asiacrypt)
