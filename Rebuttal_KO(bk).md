모든 리뷰어분들의 세심하고 건설적인 피드백에 감사드립니다. 아래에서는 주요 우려 사항에 답변하고 수정 사항을 요약합니다.

## 기존 연구 대비 위치와 비교

저희는 Ligero, Brakedown, Blaze, Orion 등에서 사용된 code-based proximity testing 자체의 novelty를 주장하지 않습니다. LAMP의 기여는 matrix multiplication의 구조와 linear code를 활용하여 quadratic in-circuit computation을 sampling-based proximity checks로 대체하는 protocol construction에 있습니다. LAMP는 general-purpose IOP나 proof system이 아니라 matrix multiplication에 특화된 기법이지만, matrix multiplication은 verifiable AI를 비롯한 다양한 응용의 핵심 primitive이며, 반복되는 대규모 matrix operations는 proving cost의 상당 부분을 차지할 수 있습니다.

현재 원고는 LAMP와 기존 matrix-multiplication proof 기법들을 충분히 비교하지 않았습니다. zkMatrix는 matrix multiplication을 inner-product relations로 표현하고 Bulletproofs 기법을 변형하여 `O(k^2)` prover complexity와 `O(\log k)` verifier complexity 및 proof size를 달성합니다. zkMatrix 저자들의 후속 연구인 DualMatrix는 prover complexity를 `O(K+k)`로 개선하며, `K`는 non-zero entries의 개수입니다. Dense matrices에서는 `K=\Theta(k^2)`이므로 여전히 `O(k^2)`입니다. zkMaP은 KZG commitments를 사용해 arithmetic circuit 없이 constant-size proofs와 constant verifier time을 달성하지만, prover 측에서 `O(k^2)` computation을 요구합니다.

LAMP 역시 `(x,y,z)`와 matrix commitments 계산에 `O(k^2)` operations가 필요하지만, circuit complexity를 `O(k)` constraints로 줄이며, 이는 저희가 아는 한 state-of-the-art입니다. Groth16 구현에서는 proving cost가 `O(k\log k)`이고, proof size와 verifier complexity는 `O(\log k)`입니다.

직접적인 experimental comparison도 시도하였으나, zkMatrix의 공개 구현체를 찾을 수 없었고 zkMaP의 GitHub 링크도 만료되어 있었습니다. 따라서 공개된 DualMatrix 구현체를 가장 가까운 reproducible baseline으로 사용하여, `\hat{B}`에 대한 독립 challenge `s`를 포함한 수정 LAMP protocol과의 비교를 완료하였습니다. 수정본에서는 Related Work에 DualMatrix를 추가하고, Section 7에 experimental results와 LAMP, zkMatrix, DualMatrix, zkMaP의 asymptotic comparison table을 추가하겠습니다.

## Circuit 내부에서 Original Matrices를 사용하는 경우

표준 LAMP에서는 challenge 이전에 모든 row-wise encoded columns를 Pedersen 및 Merkle commitments로 고정하고, commit-carrying SNARK는 online relation의 sampled columns에 해당하는 `O(k)` values만 commit합니다. Original matrices도 동일한 circuit에서 사용된다면, commit-carrying SNARK가 전체 `O(k^2)` matrix entries에 commit하여 application computation과 LAMP checks가 동일한 witness variables를 사용할 수 있습니다. 이 경우 matrix-multiplication check는 여전히 `O(k)` constraints만 필요하며, 별도의 Merkle openings와 CP-Link를 피할 수 있습니다. 해당 commitment가 verifier가 의도한 model weights를 나타내는지 보장하는 것은 별도의 application-level 문제로, 본 논문의 scope 밖입니다.

## Committed Matrix Encodings의 Validity

Reviewers C와 D께서는 `(\hat{A},\hat{B},\hat{C})`와 `(x,y,z)`의 encoding consistency 보장이 명확하지 않다고 지적하셨습니다. 이를 재검토한 결과, 기존 proximity test를 강화할 필요가 있음을 확인하였습니다.

LAMP는 `(x,y,z)`에 EncCheck를 적용하고, random folding으로 `(\hat{A},\hat{B},\hat{C})`의 proximity를 검사합니다. `A`와 `C`의 경우, non-zero malformed component는 random challenge `r`에 대한 non-zero degree-bounded polynomial을 유도하므로 negligible probability로만 0이 됩니다. 반면 `B`의 malformed component `D`가 `AD=0`을 만족하면 모든 `r`에 대해 `xD=rAD=0`이므로 기존 test로는 탐지할 수 없습니다. 따라서 행렬을 commit한 후 `r`과 동시에 독립적인 uniform random challenge `s`를 도입하고 `s\hat{B}`에 대한 proximity test를 추가합니다. `(x,y,z)`의 encodings는 기존과 동일하게 Appendix D의 Barycentric Reed-Solomon Consistency Check로 검증합니다.

Proximity test는 committed word가 valid codeword에 `\delta`-close함을 보장하므로, 허용 거리 내에서는 일부 symbols가 변경되어도 통과할 수 있습니다. 그러나 이는 soundness failure가 아닙니다. Unique-decoding radius 내에서는 대응 codeword가 유일하며, 다른 matrix를 주장하려면 Reed-Solomon minimum distance 규모의 positions를 변경해야 합니다. 이러한 변경은 sampling-based checks가 높은 확률로 탐지합니다.

수정본에서는 이 추가된 proximity test를 반영하고 soundness analysis와 관련 proofs를 업데이트하겠습니다.

## 추가 수정 사항

수정본에서는 다음 사항들도 반영하겠습니다.

* Abstract와 본문의 수치 불일치 및 오탈자를 수정하겠습니다.
* Section 7에 setup cost와 proof size를 추가하고, Groth16의 proof size가 constraint 수와 무관하게 constant-size임을 명시하겠습니다.
* "Linear Verification"이 prover time이 아니라 matrix multiplication relation의 linear circuit complexity를 의미함을 명확히 하겠습니다.
* Fiat-Shamir를 포함한 관련 proofs를 보강하겠습니다.
* LAMP의 memory usage를 측정하여 Section 7에 보고하겠습니다.
* GPT-2 실험 관련 trade-offs를 명확히 하겠습니다.
