We thank all reviewers for their careful and constructive feedback. Below, we address the main concerns and summarize the corresponding revisions.

## Positioning and Comparison with Prior Work

We do not claim novelty for code-based proximity testing itself, as used in prior works such as Ligero, Brakedown, Blaze, and Orion. LAMP's contribution is a protocol construction that exploits the structure of matrix multiplication and linear codes to replace quadratic in-circuit computation with sampling-based proximity checks. Although LAMP is specialized to matrix multiplication rather than being a general-purpose IOP or proof system, matrix multiplication is a fundamental primitive in many applications, including verifiable AI, where repeated large-scale matrix operations can account for a substantial portion of proving cost.

The current manuscript does not sufficiently compare LAMP with prior matrix-multiplication proof techniques. zkMatrix expresses matrix multiplication as inner-product relations and adapts techniques from Bulletproofs to achieve `O(k^2)` prover complexity and `O(\log k)` verifier complexity and proof size. DualMatrix, a follow-up work by the authors of zkMatrix, improves prover complexity to `O(K+k)`, where `K` is the number of non-zero entries. For dense matrices, `K=\Theta(k^2)`, so the complexity remains `O(k^2)`. zkMaP uses KZG commitments to achieve constant-size proofs and constant verifier time without an arithmetic circuit, while requiring `O(k^2)` prover-side computation.

LAMP also requires `O(k^2)` operations to compute `(x,y,z)` and the matrix commitments, but reduces the circuit complexity to `O(k)` constraints, which is, to the best of our knowledge, state-of-the-art. In our Groth16 implementation, SNARK proving costs `O(k\log k)`, while proof size and verifier complexity are `O(\log k)`.

We also attempted direct experimental comparisons. However, we could not find a public zkMatrix implementation, and the zkMaP GitHub link had expired. We therefore used the publicly available DualMatrix implementation as the closest reproducible baseline and completed a comparison against the revised LAMP protocol, which includes an independent challenge `s` for `\hat{B}`. In the revision, we will add DualMatrix to Related Work and update Section 7 accordingly.

## Using the Original Matrices Inside the Circuit

In standard LAMP, all row-wise encoded columns are fixed before the challenge using Pedersen and Merkle commitments, while the commit-carrying SNARK commits only to the `O(k)` values of the sampled columns used in the online relation. If the original matrices are also used in the same circuit, the commit-carrying SNARK can instead commit to all `O(k^2)` matrix entries, allowing the application computation and the LAMP checks to use the same witness variables. In this setting, the matrix-multiplication check still requires only `O(k)` constraints, while separate Merkle openings and CP-Link can be avoided. Ensuring that the commitment represents the model weights intended by the verifier is a separate application-level problem and is outside the scope of this work.

## Validity of the Committed Matrix Encodings

Reviewers C and D noted that it was unclear how the encoding consistency of `(\hat{A},\hat{B},\hat{C})` and `(x,y,z)` is guaranteed. Re-examining this issue revealed the need to strengthen the original proximity test.

Structurally, LAMP applies EncCheck to `(x,y,z)` and uses random folding to test the proximity of `(\hat{A},\hat{B},\hat{C})`. For `A` and `C`, any non-zero malformed component induces a non-zero degree-bounded polynomial in the random challenge `r`, which evaluates to zero only with negligible probability. In contrast, for `B`, if a malformed component `D` satisfies `AD=0`, then `xD=v(r)AD=0` for every `r`, so the original test cannot detect it. We therefore introduce an independent uniform random challenge `s` and add a proximity test on `s\hat{B}`. The encodings of `(x,y,z)` are verified as before using the Barycentric Reed-Solomon Consistency Check in Appendix D.

The proximity test guarantees that a committed word is `\delta`-close to a valid codeword, so a word with a few modified symbols may still pass if it remains within the allowed distance. This does not constitute a soundness failure. Within the unique-decoding radius, the corresponding codeword is uniquely determined, while claiming a different matrix requires modifying positions on the scale of the Reed-Solomon minimum distance. Such changes are detected with high probability by the sampling-based checks.

We will incorporate this additional test and update the corresponding soundness analysis and proofs.

## Additional Revisions

We will also make the following revisions:

* correct numerical inconsistencies and typos between the Abstract and the main text;
* add discussion of setup and proof size to Section 7.



