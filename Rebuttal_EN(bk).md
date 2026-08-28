We thank all reviewers for their careful and constructive feedback. Below, we address the main concerns and summarize the corresponding revisions.

## Comparison with Prior Work

As all reviewers noted, the current manuscript does not sufficiently compare LAMP with prior matrix multiplication proof techniques. We will strengthen the conceptual and experimental comparisons with zkMatrix, DualMatrix, and zkMaP.

zkMatrix expresses matrix multiplication as inner-product relations, achieving O(k^2) prover complexity and O(\log k) verifier complexity and proof size. DualMatrix, a follow-up work by the authors of zkMatrix, improves the prover complexity to O(K+k), where K denotes the number of non-zero entries. For dense matrices, K=\Theta(k^2), so the complexity remains O(k^2).

LAMP also requires `O(k^2)` field operations to compute `(x,y,z)`, but reduces circuit complexity to `O(k)` constraints, which is, to the best of our knowledge, state of the art. In our Groth16-based implementation, proving costs `O(k\log k)`, while proof size and verifier complexity are `O(\log k)`.

We also attempted direct experimental comparisons with prior work. However, we could not find a public implementation of zkMatrix, and the zkMaP GitHub link had expired. We contacted the authors of both works to ask about code availability but have not yet received a response, making direct experimental comparison difficult at this time. We therefore performed an experimental comparison with the publicly available DualMatrix implementation and re-evaluated LAMP using the revised protocol with the additional independent uniform challenge `s`. In the revision, we will add DualMatrix to Related Work and update Section 7 accordingly.

## Using the Original Matrices Inside the Circuit

Reviewer B asked about cases where the matrices are also used in other circuit computations. If only matrix multiplication verification is needed, LAMP commits only to sampled columns. If the matrices are already used inside the circuit, we can use only a commit-carrying SNARK to commit to the full matrices while applying the same LAMP checks.

This increases the commitment cost of the commit-carrying SNARK from `O(k)` to `O(k^2)`, while the matrix multiplication relation still requires only `O(k)` constraints. Separate Merkle proofs and CP-Link are also unnecessary, allowing Groth16 alone to provide constant-size proofs and constant verifier complexity. In contrast, approaches such as zkMaP that verify outside the circuit require an additional mechanism to link the verified matrices to their in-circuit use.

## Validity of the Committed Matrix Encodings

Reviewers C and D noted that the encoding consistency of `(\hat A,\hat B,\hat C)` and `(x,y,z)` was unclear. Re-examining this issue revealed the need to strengthen the original proximity test.

Structurally, LAMP performs encoding checks on `(x,y,z)`, while verifying the proximity of `(\hat A,\hat B,\hat C)` through random folding. The original protocol checks consistency between `(r\hat A),(x\hat B),(r\hat C)` and `\mathrm{Enc}(x),\mathrm{Enc}(y),\mathrm{Enc}(z)`. A uniform `r` provides the required proximity guarantee for `\hat A` and `\hat C`. However, `x=rA` is not necessarily uniform, so the same guarantee does not hold for `\hat B`. We therefore introduce an independent uniform challenge `s` and an additional proximity test on `s\hat B`. The encodings of `(x,y,z)` are verified as before using the Barycentric Reed–Solomon Consistency Check in Appendix D.

The proximity test guarantees that a committed word is `\delta`-close to a valid codeword. Thus, a word with a few modified symbols may still pass if it remains within the allowed distance. This is not a soundness failure. Within the unique-decoding radius, the word is uniquely associated with one codeword; claiming a different matrix requires changes on the scale of the Reed–Solomon minimum distance, which sampled checks detect with high probability.

We will incorporate this test and update the corresponding soundness analysis and proofs.

## Novelty and Scope of LAMP

We do not claim novelty for ECC or code-based proximity testing themselves. As Reviewer D noted, related techniques have been used in Ligero, Brakedown, and Orion.

LAMP's contribution is a protocol construction that exploits matrix multiplication structure to replace quadratic in-circuit computation with sampled consistency checks, reducing constraints from `O(k^2)` to `O(k)`. Although specialized to matrix multiplication, LAMP targets a fundamental primitive in many applications, including verifiable AI, where repeated large-scale matrix operations can account for a substantial portion of proof-generation cost.


## Additional Revisions
In addition to the revisions discussed above, we will correct the minor numerical inconsistencies between the Abstract and the main text. We will also expand Section 7 to include a discussion of the setup cost and proof size.



