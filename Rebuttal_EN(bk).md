We thank all reviewers for their constructive feedback. Below, we address the main concerns and summarize the revisions.

## Positioning and Comparison with Prior Work

We do not claim novelty for code-based proximity testing itself, as used in Ligero, Brakedown, Blaze, and Orion. LAMP's contribution is a protocol construction that exploits matrix multiplication and linear codes to replace quadratic in-circuit computation with sampling-based proximity checks. Although specialized to matrix multiplication rather than a general-purpose IOP or proof system, LAMP targets a fundamental primitive in many applications, including verifiable AI, where repeated large-scale matrix operations can account for substantial proving cost.

The manuscript does not sufficiently compare LAMP with prior matrix-multiplication proof techniques. zkMatrix expresses matrix multiplication as inner-product relations and adapts Bulletproofs techniques to achieve `O(k^2)` prover complexity and `O(\log k)` verifier complexity and proof size. DualMatrix, a follow-up by the authors of zkMatrix, improves prover complexity to `O(K+k)`, where `K` is the number of non-zero entries. For dense matrices, `K=\Theta(k^2)`, so the complexity remains `O(k^2)`. zkMaP uses KZG commitments to achieve constant-size proofs and verifier time without an arithmetic circuit, while requiring `O(k^2)` prover-side computation.

LAMP also requires `O(k^2)` operations to compute `(x,y,z)` and the matrix commitments, but reduces circuit complexity to `O(k)` constraints, which is, to the best of our knowledge, state of the art. In our Groth16 implementation, proving cost is `O(k\log k)`, while proof size and verifier complexity are `O(\log k)`.

We also attempted direct experimental comparisons, but found no public zkMatrix implementation, and the zkMaP GitHub link had expired. We therefore used the public DualMatrix implementation as the closest reproducible baseline and compared it with the revised LAMP protocol, which includes an independent challenge `s` for `\hat{B}`. In the revision, we will add DualMatrix to Related Work and update Section 7 with experimental results, including an asymptotic comparison table of LAMP, zkMatrix, DualMatrix, and zkMaP.

## Using the Original Matrices Inside the Circuit

In standard LAMP, all row-wise encoded columns are fixed before the challenge using Pedersen and Merkle commitments, while the commit-carrying SNARK commits only to the `O(k)` values corresponding to sampled columns used in the online relation. If the original matrices are also used in the same circuit, the commit-carrying SNARK can instead commit to all `O(k^2)` matrix entries, allowing the application computation and LAMP checks to use the same witness variables. The matrix-multiplication check still requires only `O(k)` constraints, while separate Merkle openings and CP-Link can be avoided. Ensuring that the commitment represents the model weights intended by the verifier is a separate application-level problem outside the scope of this work.

## Validity of the Committed Matrix Encodings

Reviewers C and D noted that the encoding consistency guarantees for `(\hat{A},\hat{B},\hat{C})` and `(x,y,z)` were unclear. Re-examining this issue revealed the need to strengthen the original proximity test.

LAMP applies EncCheck to `(x,y,z)` and uses random folding to test the proximity of `(\hat{A},\hat{B},\hat{C})`. For `A` and `C`, any non-zero malformed component induces a non-zero degree-bounded polynomial in random challenge `r`, which evaluates to zero only with negligible probability. In contrast, if a malformed component `D` of `B` satisfies `AD=0`, then `xD=rAD=0` for every `r`, so the original test cannot detect it. Therefore, after committing to the matrices, we introduce an independent uniform challenge `s` alongside `r` and add a proximity test on `s\hat{B}`. The encodings of `(x,y,z)` are verified as before using the Barycentric Reed-Solomon Consistency Check in Appendix D.

A proximity test guarantees that a committed word is `\delta`-close to a valid codeword, so a few modified symbols may still pass within the allowed distance. This is not a soundness failure. Within the unique-decoding radius, the corresponding codeword is unique, while claiming a different matrix requires modifying positions on the scale of the Reed-Solomon minimum distance. Such changes are detected with high probability by the sampling-based checks.

In the revision, we will incorporate this proximity test and update the soundness analysis and related proofs.

## Additional Revisions

We will also:

* correct numerical inconsistencies and typos between the Abstract and main text;
* add setup cost and proof size to Section 7, and clarify that Groth16 has constant-size proofs regardless of constraint count;
* clarify that "Linear Verification" refers to the linear circuit complexity of the matrix-multiplication relation, not prover time;
* strengthen the relevant proofs, including the Fiat-Shamir transformation;
* measure and report LAMP's memory usage in Section 7; and
* clarify the trade-offs related to the GPT-2 experiments.
