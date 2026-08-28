We thank all reviewers for their careful and constructive feedback.

POSITIONING AND COMPARISON

The manuscript does not sufficiently compare LAMP with prior matrix-multiplication proofs. LAMP checks matrix-multiplication statements over committed row-wise encodings; it is not a general-purpose IOP or end-to-end zkML system. We do not claim novelty for ECC or code-based proximity testing, used in Ligero, Brakedown, Blaze, and Orion. Our contribution is the matrix-specific reduction from quadratic in-circuit computation to sampled consistency checks.

Freivalds-in-Groth16 isolates this reduction under matched experimental conditions, but is not a state-of-the-art baseline. zkMatrix reports O(k^2) prover work and O(log k) proof size and verifier complexity. DualMatrix, its publicly implemented follow-up, reports O(K+k) field operations plus O(k) group operations/pairings, where K=nnz(A)+nnz(B)+nnz(C)=Theta(k^2) for dense inputs, and O(log k) proof size and verifier complexity. zkMaP reports O(k^2) prover work, 320-byte proofs, a constant pairing count, and O(k) verifier-side field work. At fixed code rate, LAMP uses O(k^2) field work for intermediate vectors and O(k^2) group work to commit encoded columns, but reduces the in-circuit relation to O(tk+E_code) constraints. Its Groth16 proving work is O(k log k), with O(log k) proof size and verifier complexity.

We could not locate a public zkMatrix implementation, and the zkMaP artifact was unavailable. We therefore used the public DualMatrix implementation as the closest reproducible reference and completed a comparison with the revised LAMP protocol, including the independent challenge s for B. Section 7 will report the methodology, conditions, and results, together with an asymptotic comparison to zkMatrix, DualMatrix, and zkMaP.

USING THE ORIGINAL MATRICES INSIDE THE CIRCUIT

In standard LAMP, rt_ABC fixes Merkle commitments to all row-wise encoded columns before the challenges, whereas the commit-carrying SNARK commits only the O(tk) values from sampled columns used in the online relation. If the original matrices are already witnesses in the same circuit, a commit-carrying SNARK can instead commit to all O(k^2) matrix entries and use the same witness variables in the application computation and LAMP checks. The matrix-multiplication check remains O(tk+E_code) constraints, and separate Merkle-opening and CP-Link layers can be avoided. Establishing that this commitment represents the verifier-intended model weights remains a separate application-level question.

VALIDITY OF THE COMMITTED MATRIX ENCODINGS

Reviewers C and D are correct that the current theorem assumes validity of the committed row-wise encodings rather than proving it. Structurally, LAMP applies EncCheck to x, y, and z, while random folding tests the proximity of hat(A), hat(B), and hat(C). For A and C, a nonzero malformed component yields a nonzero degree-bounded polynomial in random r, which vanishes only with negligible probability. The B fold is different: if a malformed component is D with AD=0, then xD=v(r)AD=0 for every r, so the existing check cannot detect it.

We will therefore sample an independent uniform challenge s for B alongside the existing Freivalds challenge r, after rt_ABC is fixed. Before the query set and code-check points are sampled, the prover commits to the encoding of b_s=sB together with those of x, y, and z. EncCheck verifies b_s, and sampled fold equations link it to hat(B) fixed by rt_ABC. The revised theorem will give the proximity radius, extraction argument, and full soundness bound; within the unique-decoding radius, a close word still determines one decoded row.

This test adds one O(k^2) native vector-matrix product, one encoding/commitment, and O(tk+E_code) circuit constraints. Total prover work remains O(k^2), while the circuit remains linear in k for fixed t and code rate.

SECURITY SCOPE AND SETUP

We will restrict the formal theorem to the public-coin interactive protocol and leave a formal ROM analysis of the implemented multi-round Fiat-Shamir transform to future work. We will also document Groth16's per-circuit setup and QALink's configuration-dependent CRS and their deployment costs.

MEASUREMENTS AND PRESENTATION

We will correct the inconsistent values to 0.06 s, 8.43x, and 1.77x. “Linear” refers to the main constraint count, not total prover time. We will report the GPT-2 result as a trade-off: 1.77x faster proving, but 6.52 s versus 0.49 s verification and 3.34 MB versus 196 B proofs. The 196 B value is not a typo: Groth16 proof size is constant in circuit size, whereas LAMP additionally serializes sampled Merkle openings and CP-Link proofs. We will clarify encoding-time accounting, add repetitions, variance, and memory where available, correct the listed notation and typographical issues, and include the full proof of Theorem 6.2 in the appendix.
