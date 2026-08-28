We thank the reviewers for their careful and constructive feedback.

COMPARISON WITH PRIOR WORK

We agree that the manuscript does not sufficiently compare LAMP with prior matrix-multiplication proofs. Freivalds-in-Groth16 was intended to isolate the benefit of moving matrix-vector products out of the circuit under matched conditions, but it is not a state-of-the-art baseline.

zkMatrix has O(k^2) prover work and O(log k) proof size and verifier complexity. DualMatrix, its publicly implemented follow-up, uses O(K+k) field operations and O(k) group operations/pairings, where K is the total number of nonzero entries; for dense matrices, K=Theta(k^2). zkMaP has O(k^2) prover work and produces 320-byte proofs verified with two pairings.

LAMP's total prover work is also O(k^2), including the field work for its intermediate vectors and the group work for encoded-column commitments. Its advantage is instead in the circuit: the matrix-multiplication relation uses O(tk+E_code) constraints, giving O(k log k) Groth16 proving work and O(log k) proof size and verifier complexity. We do not claim that ECC or code-based proximity testing is new; our contribution is this matrix-specific reduction. Although specialized, matrix multiplication is a recurring proving bottleneck in verifiable AI.

We could not locate a public zkMatrix implementation, and the zkMaP artifact was unavailable. We therefore used the public DualMatrix implementation as the closest reproducible reference and completed a comparison with the revised LAMP protocol, including the independent challenge s for B. Section 7 will report the methodology, conditions, and results, together with an asymptotic comparison table covering LAMP, zkMatrix, DualMatrix, and zkMaP.

USING THE ORIGINAL MATRICES INSIDE THE CIRCUIT

Reviewer B asks what happens when the original matrices are used elsewhere in the circuit. In standard LAMP, rt_ABC fixes Merkle commitments to all encoded columns, while the commit-carrying SNARK commits only the O(tk) sampled values used by the online relation.

If the matrices are already circuit witnesses, the commit-carrying SNARK can instead commit to all O(k^2) matrix entries and reuse the same variables in both the application and LAMP checks. This makes the witness-commitment cost quadratic, but the matrix-multiplication check remains O(tk+E_code) constraints; separate Merkle-opening and CP-Link layers can then be avoided. Whether this commitment corresponds to the intended model weights remains an application-level question.

VALIDITY OF THE COMMITTED MATRIX ENCODINGS

Reviewers C and D are correct that the current theorem assumes validity of the committed row-wise encodings without proving it. The existing folds give the required proximity guarantee for A and C by the standard polynomial argument. The B fold is different because its coefficient vector is x=rA: if a malformed component D satisfies AD=0, then xD=rAD=0 for every r, so the check cannot detect it.

We will therefore sample an independent uniform challenge s for B at the same time as r, after rt_ABC is fixed. Before the query set and code-check points are sampled, the prover commits to the encoding of sB together with those of x, y, and z. Appendix D's Barycentric Reed–Solomon Consistency Check verifies this encoding, and sampled fold equations link it to hat(B) fixed by rt_ABC. The revised theorem will give the proximity radius, extraction argument, and full soundness bound. Within the unique-decoding radius, a close word still determines one decoded row, so a few modified symbols are not themselves a soundness failure.

The additional test requires one O(k^2) native vector-matrix product, one encoding/commitment, and O(tk+E_code) circuit constraints. Thus, total prover work remains O(k^2), and the circuit remains linear in k for fixed t and code rate.

OTHER REVISIONS

We will correct the inconsistent values to 0.06 s, 8.43x, and 1.77x, and clarify that "linear" refers to the main constraint count rather than total prover time. We will describe the GPT-2 result as a trade-off: proving is 1.77x faster, while verification increases from 0.49 s to 6.52 s and proof size from 196 B to 3.34 MB. The 196 B value is not a typo: a Groth16 proof is constant-size, whereas LAMP also includes sampled Merkle openings and CP-Link proofs.

We will include the full proof of the revised theorem. The formal result will cover the public-coin interactive protocol; a formal ROM analysis of the multi-round Fiat–Shamir transform is left to future work. Section 7 will explain Groth16's per-circuit setup and QALink's configuration-dependent CRS, and report repetition counts, memory use, and encoding-time accounting. We will correct the listed typographical issues as well.
