We thank all reviewers for their careful and constructive feedback. Below, we address the main concerns and summarize the revisions.

## Comparison with Prior Work

As all reviewers noted, the manuscript does not sufficiently compare LAMP with prior matrix multiplication proof techniques. We will strengthen comparisons with zkMatrix, DualMatrix, and zkMaP.

zkMatrix expresses matrix multiplication as inner-product relations, achieving `O(k^2)` prover complexity and `O(\log k)` verifier complexity and proof size. DualMatrix, a follow-up work by the authors of zkMatrix, improves prover complexity to `O(K+k)`, where `K` is the number of non-zero entries; for dense matrices, `K=\Theta(k^2)`, so it remains `O(k^2)`. zkMaP uses KZG commitments to achieve constant-size proofs and verifier time without an arithmetic circuit, while requiring `O(k^2)` prover-side computation.

LAMP also requires `O(k^2)` field operations to compute `(x,y,z)`, but reduces circuit complexity to `O(k)` constraints, which is, to the best of our knowledge, state-of-the-art. In our Groth16 implementation, proving costs `O(k\log k)`, while proof size and verifier complexity are `O(\log k)`.

We attempted direct experimental comparisons, but found no public zkMatrix implementation and the zkMaP GitHub link had expired. We contacted both author groups but have not received responses. We therefore compare against the public DualMatrix implementation and re-evaluated LAMP with the revised protocol using a uniform challenge `s`. We will add DualMatrix to Related Work and update Section 7 accordingly.

## Using the Original Matrices Inside the Circuit

Reviewer B asked about cases where the matrices are also used in other circuit computations. If only matrix multiplication verification is needed, LAMP commits only to sampled columns in the commit-carrying SNARK. If the matrices are already used in the circuit, we can use only a commit-carrying SNARK to commit to the full matrices while applying the same LAMP checks.

This raises the commitment cost of the commit-carrying SNARK from `O(k)` to `O(k^2)`, while the matrix multiplication relation still requires only `O(k)` constraints. Merkle proofs and CP-Link are unnecessary, allowing Groth16 alone to provide constant-size proofs and constant verifier complexity. In contrast, approaches such as zkMaP that verify outside the circuit require an additional mechanism to link the verified matrices to their use within the circuit.

## Validity of the Committed Matrix Encodings

Reviewers C and D noted that the encoding consistency of `(\hat{A},\hat{B},\hat{C})` and `(x,y,z)` was unclear. Re-examining this issue showed that the original proximity test must be strengthened.

LAMP performs encoding checks on `(x,y,z)` and verifies proximity of `(\hat{A},\hat{B},\hat{C})` through random folding. The original protocol checks consistency between `(r\hat{A}),(x\hat{B}),(r\hat{C})` and `\mathrm{Enc}(x),\mathrm{Enc}(y),\mathrm{Enc}(z)`. Uniform `r` guarantees proximity for `\hat{A}` and `\hat{C}`, but `x=rA` is not necessarily uniform, so the same does not hold for `\hat{B}`. We therefore add an independent uniform challenge `s` and a proximity test on `s\hat{B}`. The encodings of `(x,y,z)` are verified as before using the Barycentric Reed–Solomon Consistency Check in Appendix D.

A proximity test guarantees that a committed word is `\delta`-close to a valid codeword, so a few modified symbols may still pass within the allowed distance. This is not a soundness failure: within the unique-decoding radius, the word corresponds uniquely to one codeword, while claiming another matrix requires changes on the scale of the Reed–Solomon minimum distance, which sampled checks detect with high probability.

We will incorporate this test and update the soundness analysis and proofs.

## Novelty and Scope of LAMP

We do not claim novelty for ECC or code-based proximity testing itself. As Reviewer D noted, related techniques have also been used in prior works such as Ligero, Brakedown, and Orion.

LAMP's contribution is a protocol construction that exploits matrix multiplication structure to replace quadratic in-circuit computation with sampled consistency checks, reducing constraints from `O(k^2)` to `O(k)`. Although specialized to matrix multiplication, LAMP targets a fundamental primitive in applications such as verifiable AI, where large-scale matrix operations can dominate proof-generation cost.

## Additional Revisions

We will also:

* correct numerical inconsistencies and typos between the Abstract and main text;
* add setup cost and proof size to Section 7, noting that Groth16 has constant-size proofs regardless of constraint count;
* clarify that "Linear Verification" refers to the linear circuit complexity of the matrix multiplication relation, not the prover time;
* strengthen the relevant proofs;
* measure and report LAMP's memory usage in Section 7;
* discuss different-dimension matrix multiplication, such as in GPT-2, and its trade-offs as future work; and
* clarify that our guarantee is knowledge of `A,B,C` satisfying `AB=C`; proving that they are the correct model weights is outside our scope.
