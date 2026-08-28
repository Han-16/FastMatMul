리뷰어 여러분의 세심하고 건설적인 피드백에 감사드립니다. 아래에서는 주요 우려 사항에 답변하고, 이에 따른 수정 사항을 요약합니다.

## 기존 연구와의 비교

모든 리뷰어가 지적하신 바와 같이, 현재 원고에서는 LAMP와 기존 matrix multiplication proof 기법 간의 비교가 충분하지 않았습니다. 수정본에서는 zkMatrix, DualMatrix, zkMaP과의 개념적·실험적 비교를 강화하겠습니다.

zkMatrix는 matrix multiplication을 inner-product relations로 표현하여 `O(k^2)`의 prover complexity와 `O(\log k)`의 verifier complexity 및 proof size를 달성합니다. zkMatrix의 저자들이 후속 연구로 제안한 DualMatrix는 prover complexity를 O(K+k)로 개선하며, 여기서 K는 non-zero entries의 개수를 의미합니다. Dense matrices에서는 K=\Theta(k^2)이므로 여전히 O(k^2)입니다. 
LAMP 역시 `(x,y,z)`를 계산하는 데 `O(k^2)`의 field operations가 필요하지만, circuit complexity를 `O(k)` constraints로 줄이며, 이는 저희가 아는 한 현재 state of the art입니다. 저희의 Groth16 기반 구현에서는 proving cost가 `O(k\log k)`이고, proof size와 verifier complexity는 `O(\log k)`입니다.

저희는 기존 연구들과의 직접적인 실험 비교도 시도하였습니다. 그러나 zkMatrix의 공개 구현체는 찾을 수 없었으며, zkMaP의 GitHub 링크는 만료된 상태였습니다. 두 연구의 저자들에게 코드 이용 가능 여부를 문의하였으나 아직 답변을 받지 못해, 현 시점에서는 직접적인 실험 비교가 어렵습니다. 따라서 공개된 DualMatrix 구현체와 실험적으로 비교하였으며, 독립적인 uniform challenge `s`를 추가한 수정 프로토콜을 기준으로 LAMP의 성능을 다시 측정하였습니다. 수정본에서는 Related Work에 DualMatrix를 추가하고 Section 7을 이에 맞게 업데이트하겠습니다.

## Circuit 내부에서 Original Matrices를 사용하는 경우

Reviewer B께서는 matrices가 circuit 내부의 다른 computations에서도 사용되는 경우에 대해 질문해 주셨습니다. Matrix multiplication verification만 필요한 경우, LAMP는 sampled columns에 대해서만 commitment를 생성합니다. 반면 matrices가 이미 circuit 내부에서 사용되고 있다면, commit-carrying SNARK를 이용하여 전체 matrices에 commitment하면서 동일한 LAMP checks를 적용할 수 있습니다.

이 경우 commit-carrying SNARK의 commitment cost는 `O(k)`에서 `O(k^2)`로 증가하지만, matrix multiplication relation 자체를 검증하는 데 필요한 constraints는 여전히 `O(k)`입니다. 또한 별도의 Merkle proofs와 CP-Link가 필요하지 않으므로, Groth16만으로 constant-size proof와 verifier complexity를 제공할 수 있습니다. 반면 zkMaP과 같이 circuit 외부에서 검증을 수행하는 방식은, 검증된 matrices와 circuit 내부에서 사용되는 matrices를 연결하기 위한 추가 mechanism이 필요합니다.

## Committed Matrix Encodings의 Validity

Reviewers C와 D께서는 `(\hat A,\hat B,\hat C)`와 `(x,y,z)`의 encoding consistency가 명확하지 않다고 지적하셨습니다. 이 문제를 다시 검토한 결과, 기존 proximity test를 강화할 필요가 있음을 확인하였습니다.
구조적으로, LAMP는 `(x,y,z)`에 대해서는 encoding check를 수행하고, `(\hat A,\hat B,\hat C)`에 대해서는 random folding을 통해 proximity를 검증합니다.
기존 프로토콜은 `(r\hat A),(x\hat B),(r\hat C)`와 `\mathrm{Enc}(x),\mathrm{Enc}(y),\mathrm{Enc}(z)` 사이의 consistency를 확인합니다. Uniform한 `r`은 `\hat A`와 `\hat C`에 필요한 proximity guarantee를 제공하지만, `x=rA`는 반드시 uniform하지 않으므로 `\hat B`에 대해서는 동일한 guarantee를 제공하지 않습니다. 이를 해결하기 위해 독립적인 uniform challenge `s`를 도입하고, `s\hat B`에 대한 추가 proximity test를 수행합니다. `(x,y,z)`의 encodings는 기존과 동일하게 Appendix D의 Barycentric Reed–Solomon Consistency Check를 통해 검증합니다.

Proximity test는 committed word가 valid codeword에 대해 `\delta`-close함을 보장합니다. 따라서 일부 symbols만 변경된 word는 허용된 거리 안에 있는 경우 여전히 test를 통과할 수 있습니다. 그러나 이는 soundness failure가 아닙니다. Unique-decoding radius 내에서는 해당 word가 하나의 codeword에 유일하게 대응되며, 다른 matrix를 주장하기 위해서는 Reed–Solomon minimum distance에 해당하는 규모의 변경이 필요합니다. 이러한 변경은 sampled checks에 의해 높은 확률로 검출됩니다.

수정본에서는 이 추가 test를 반영하고, 이에 따른 soundness analysis와 proofs를 업데이트하겠습니다.

## LAMP의 Novelty와 Scope

저희는 ECC나 code-based proximity testing 자체의 novelty를 주장하지 않습니다. Reviewer D가 지적한 바와 같이 Ligero, Brakedown, Orion 등에서도 관련 기법이 사용되었습니다.

LAMP의 기여는 matrix multiplication의 구조를 활용하여 quadratic in-circuit computation을 sampled consistency checks로 대체하는 protocol construction에 있습니다. 이를 통해 constraints를 `O(k^2)`에서 `O(k)`로 줄입니다. LAMP는 matrix multiplication에 특화되어 있지만, matrix multiplication은 verifiable AI를 비롯한 다양한 응용에서 핵심적인 primitive이며, 특히 대규모 matrix operations가 반복되는 경우 proof-generation cost의 상당 부분을 차지할 수 있습니다.

## 추가 반영 사항
이외에도 수정본에서는 다음 사항들을 추가로 반영하겠습니다. Abstract와 main text 사이의 일부 수치상의 불일치를 수정하고, Section 7에 setup cost와 proof size에 대한 내용을 추가하겠습니다.






