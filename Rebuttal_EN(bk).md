We thank all reviewers for their constructive feedback. Below, we address the main concerns and revisions.

## Positioning and Comparison with Prior Work

We do not claim novelty for code-based proximity testing itself, as used in Ligero, Brakedown, Blaze, and Orion. LAMP contributes a protocol construction that exploits matrix multiplication structure and linear codes to replace quadratic in-circuit computation with sampling-based proximity checks. Although specialized to matrix multiplication, LAMP targets a fundamental primitive in applications such as verifiable AI, where large matrix operations can dominate proving cost.

The manuscript does not sufficiently compare LAMP with prior matrix-multiplication proofs. zkMatrix expresses matrix multiplication as inner-product relations and adapts Bulletproofs to achieve `O(k^2)` prover complexity and `O(\log k)` verifier complexity and proof size. DualMatrix improves prover complexity to `O(K+k)`, where `K` is the number of non-zero entries; for dense matrices, `K=\Theta(k^2)`, so it remains `O(k^2)`. zkMaP uses KZG commitments to achieve constant-size proofs and verifier time without an arithmetic circuit, while requiring `O(k^2)` prover-side computation.

LAMP also requires `O(k^2)` operations to compute `(x,y,z)` and matrix commitments, but reduces circuit complexity to `O(k)` constraints, which is, to the best of our knowledge, state of the art. In our Groth16 implementation, proving cost is `O(k\log k)`, while proof size and verifier complexity are `O(\log k)`.

For direct comparison, we found no public zkMatrix implementation, and the zkMaP GitHub link had expired. We therefore used public DualMatrix as the closest reproducible baseline and compared it with revised LAMP, including an independent challenge `s` for `\hat{B}`. We will add DualMatrix to Related Work and update Section 7 with experimental results and an asymptotic comparison.

## Using the Original Matrices Inside the Circuit

In standard LAMP, row-wise encoded columns are fixed before the challenge using Pedersen and Merkle commitments, while the commit-carrying SNARK commits only to the `O(k)` values for sampled columns. If the original matrices are also used in the same circuit, it can instead commit to all `O(k^2)` matrix entries, allowing application computation and LAMP checks to share witness variables. The matrix-multiplication check still requires only `O(k)` constraints, while separate Merkle openings and CP-Link can be avoided. Ensuring that the commitment represents verifier-intended model weights is an application-level problem outside our scope.

## Validity of the Committed Matrix Encodings

Reviewers C and D noted that the encoding-consistency guarantees for `(\hat{A},\hat{B},\hat{C})` and `(x,y,z)` were unclear. Re-examining this issue showed that the original proximity test must be strengthened.

LAMP applies EncCheck to `(x,y,z)` and uses random folding to test the proximity of `(\hat{A},\hat{B},\hat{C})`. For `A` and `C`, any non-zero malformed component induces a non-zero degree-bounded polynomial in random challenge `r`, which evaluates to zero only with negligible probability. In contrast, if a malformed component `D` of `B` satisfies `AD=0`, then `xD=rAD=0` for every `r`, so the original test cannot detect it. We therefore introduce, after committing to the matrices, an independent uniform challenge `s` alongside `r` and add a proximity test on `s\hat{B}`. The encodings of `(x,y,z)` are verified as before using the Barycentric Reed-Solomon Consistency Check in Appendix D.

A proximity test guarantees that a committed word is `\delta`-close to a valid codeword, so a few modified symbols may still pass within the allowed distance. This is not a soundness failure: within the unique-decoding radius, the corresponding codeword is unique, while claiming a different matrix requires modifying positions on the scale of the Reed-Solomon minimum distance. Such changes are detected with high probability by sampling-based checks. We will incorporate this ㅁadditional proximity test and update the soundness analysis and proofs.

## Additional Revisions

We will also:

* correct numerical inconsistencies and typos between the Abstract and main text;
* clarify that Freivalds' Groth16 proof size is `196B`, since Groth16 proof size is independent of constraint count, and report Groth16/QALink setup time and proof size in Section 7;
* clarify that "Linear Verification" refers to linear circuit complexity of the matrix-multiplication relation, not prover time;
* strengthen the related proofs, while leaving a formal ROM proof for the multi-round Fiat-Shamir transformation to future work;
* clarify that encoding time is included in commit time, and report encoding time, LAMP's memory usage, and repetition counts in Section 7; and
* clarify the GPT-2 experimental trade-offs.
