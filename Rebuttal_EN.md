# IEEE S&P 2027 Text Rebuttal — Working Draft

We thank all reviewers for their careful and constructive feedback. Below, we address the main concerns and summarize the corresponding revisions.

## Comparison with Prior Work

As all reviewers noted, the current manuscript does not sufficiently compare LAMP with prior matrix multiplication proof techniques. We will strengthen the conceptual and experimental comparisons with zkMatrix, DualMatrix, and zkMaP.

zkMatrix expresses matrix multiplication as inner-product relations, achieving `O(k^2)` prover complexity and `O(\log k)` verifier complexity and proof size. DualMatrix improves the prover complexity to `O(K+k)`, but this remains `O(k^2)` for dense matrices. zkMaP uses KZG commitments to achieve constant-size proofs and verifier time without an arithmetic circuit, while still requiring `O(k^2)` prover-side computation.

LAMP also requires `O(k^2)` field operations to compute `(x,y,z)`, but reduces the circuit complexity to `O(k)` constraints, which is state of the art to the best of our knowledge. In our Groth16-based implementation, proving costs `O(k\log k)`, while proof size and verifier complexity are `O(\log k)`.

We could not find a public implementation of zkMatrix, and the zkMaP GitHub link has expired. We contacted the authors but have not yet received a response. We therefore compare experimentally with the public DualMatrix implementation and re-evaluated LAMP using the revised protocol with an additional independent uniform challenge `s`. We will add DualMatrix to Related Work and update Section 7 accordingly.

## Using the Original Matrices Inside the Circuit

Reviewer B asked about cases where the matrices are also used in other circuit computations. If only matrix multiplication verification is needed, LAMP commits only to sampled columns. If the matrices are already used inside the circuit, a commit-carrying SNARK alone can commit to the full matrices while applying the same LAMP checks.

This increases the commitment cost from `O(k)` to `O(k^2)`, but the matrix multiplication relation itself still requires only `O(k)` constraints. Moreover, separate Merkle proofs and CP-Link are unnecessary, allowing Groth16 alone to provide constant-size proofs and verifier complexity. In contrast, approaches such as zkMaP that perform verification outside the circuit require an additional mechanism to link the verified matrices to their in-circuit use.

## Validity of the Committed Matrix Encodings

Reviewers C and D noted that the encoding consistency of `(\hat A,\hat B,\hat C)` and `(x,y,z)` was unclear. Re-examining this issue revealed that the original proximity test must be strengthened.

The original protocol checks consistency between `(r\hat A),(x\hat B),(r\hat C)` and `\mathrm{Enc}(x),\mathrm{Enc}(y),\mathrm{Enc}(z)`. While uniform `r` provides the required proximity guarantee for `\hat A` and `\hat C`, `x=rA` is not necessarily uniform and therefore does not provide the same guarantee for `\hat B`. We address this by introducing an independent uniform challenge `s` and an additional proximity test on `s\hat B`. The encodings of `(x,y,z)` are still verified using the Barycentric Reed–Solomon Consistency Check in Appendix D.

The proximity test guarantees that a committed word is `\delta`-close to a valid codeword. Thus, a word with a few modified symbols may still pass if it remains within the allowed distance. This is not a soundness failure: within the unique-decoding radius, the word is uniquely associated with a single codeword, whereas claiming a different matrix requires modifications on the scale of the Reed–Solomon minimum distance, which the sampled checks detect with high probability.

We will incorporate this additional test and update the corresponding soundness analysis and proofs.

## Novelty and Scope of LAMP

We do not claim novelty for ECC or code-based proximity testing themselves. As Reviewer D noted, related techniques have been used in Ligero, Brakedown, and Orion.

LAMP's contribution is a protocol construction that exploits the structure of matrix multiplication to replace quadratic in-circuit computation with sampled consistency checks, reducing the number of constraints from `O(k^2)` to `O(k)`. Although LAMP is specialized to matrix multiplication, matrix multiplication is a core primitive in many applications, including verifiable AI, where repeated large matrix operations can account for a substantial portion of proof-generation cost.
