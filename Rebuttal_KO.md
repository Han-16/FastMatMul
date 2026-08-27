리뷰어 여러분의 세심하고 건설적인 피드백에 감사드립니다. 아래에서는 주요 우려 사항에 답변하고 수정본에서 보완할 내용을 설명드립니다.

## Comparison with Prior Work
모든 리뷰어가 지적한 바와 같이, 기존 원고에서는 prior matrix multiplication proof 기법들과의 비교가 충분하지 않았습니다. 수정본에서는 zkMatrix, DualMatrix, zkMaP과의 개념적·실험적 비교를 보완하겠습니다.
zkMatrix는 matrix multiplication을 inner-product relations로 표현하여 (O(k^2)) prover complexity와 (O(\log k)) verifier complexity 및 proof size를 달성합니다. 후속 연구인 DualMatrix는 prover complexity를 (O(K+k))로 개선하지만, dense matrices에서는 여전히 (O(k^2))입니다. zkMaP은 KZG commitments를 이용해 arithmetic circuit 없이 constant-size proof와 verifier time을 달성하지만, prover-side computation은 (O(k^2))입니다.
LAMP 역시 (x,y,z) 계산에 (O(k^2)) field operations가 필요하지만, circuit constraints를 (O(k))로 줄이며, 이는 저희가 아는 한 state-of-the-art 수준입니다. Groth16 기반 구현의 proving cost는 (O(k\log k)), proof size와 verifier complexity는 (O(\log k))입니다.
zkMatrix의 공개 구현체를 찾을 수 없었고 zkMaP의 GitHub 링크도 만료되어, 저자들에게 코드를 요청했으나 아직 답변을 받지 못했습니다. 따라서 공개된 DualMatrix 구현체와 비교하였고, 추가된 uniform challenge (s) 기반 proximity test를 반영하여 LAMP의 실험을 다시 측정하였습니다.
수정본에서는 DualMatrix를 Related Work에 추가하고, Section 7의 실험 결과와 asymptotic comparison을 갱신하겠습니다.

## Using the Original Matrices Inside the Circuit
Reviewer B께서 matrices가 circuit의 다른 computations에도 사용되는 경우를 질문하셨습니다. Matrix multiplication verification만 필요한 경우 LAMP는 sampled columns만 commit하면 됩니다. 반면 matrices가 이미 circuit 내부에서 사용된다면 commit-carrying SNARK만을 이용해 전체 matrices를 commit하고 동일한 LAMP checks를 수행할 수 있습니다.
이 경우 commitment cost는 (O(k))에서 (O(k^2))로 증가하지만, matrix multiplication relation 자체는 여전히 (O(k)) constraints로 검증됩니다. 또한 별도의 Merkle proof와 CP-Link가 필요하지 않아 Groth16만으로 constant-size proof와 verifier complexity를 얻을 수 있습니다.반면 zkMaP처럼 circuit 외부에서 검증하는 방식은 matrices를 circuit 내부 사용과 연결하기 위한 추가 mechanism이 필요합니다.

## Validity of the Committed Matrix Encodings
Reviewer C와 D께서 ((\hat A,\hat B,\hat C))와 ((x,y,z))의 encoding consistency가 어떻게 보장되는지 명확하지 않다고 지적하셨으며, 이를 재검토하면서 기존 proximity test를 보완할 필요가 있음을 확인했습니다.
기존에는 x, y, z를 계산하고, (r\hat A), (x\hat B), (r\hat C)와 Enc(x), Enc(y), Enc(z)의 consistency를 확인하였습니다. Uniform (r)은 (\hat A,\hat C)에 대한 proximity guarantee를 제공하지만, (x=rA)는 일반적으로 uniform하지 않아 (\hat B)에 동일한 보장을 제공하지 못합니다.  따라서 수정된 프로토콜에서는 독립적인 uniform challenge (s)를 추가해 (s\hat B)에 대한 proximity test를 수행합니다. (x,y,z)의 encodings은 기존과 같이 Appendix D의 Barycentric Reed–Solomon Consistency Check로 검증합니다.
Proximity test는 committed word가 valid codeword에 (\delta)-close함을 보장합니다. 따라서 일부 symbols가 변경된 (\hat A*)도 허용 거리 내라면 통과할 수 있습니다. 그러나 이는 soundness failure가 아니고, unique-decoding radius 내에서는 하나의 codeword에 uniquely bound되며, 다른 (A')를 주장하려면 Reed–Solomon codeword의 minimum distance 수준의 차이가 필요하므로 sampled checks에서 높은 확률로 검출됩니다.
수정본에서는 (\hat B)에 대한 추가 proximity test와 이에 따른 soundness 분석 및 증명을 반영하겠습니다.

## Novelty and Scope of LAMP
저희는 ECC나 code-based proximity testing 자체의 novelty를 주장하지 않습니다. Reviewer D가 지적한 바와 같이 Ligero, Brakedown, Orion 등에서도 관련 기법이 사용되었습니다.
LAMP의 기여는 matrix multiplication의 구조를 활용해 in-circuit computation을 sampled consistency checks로 대체하여 constraints를 (O(k^2))에서 (O(k))로 줄이는 protocol construction입니다.  LAMP는 matrix multiplication에 특화되어 있지만, 이는 verifiable AI를 포함한 다양한 applications의 핵심 primitive이며 대규모 반복 연산은 proof generation의 주요 bottleneck이 될 수 있습니다. 따라서 이를 효율화하는 것은 전체 proving cost를 실질적으로 줄일 수 있습니다.



