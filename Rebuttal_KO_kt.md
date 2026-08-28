세심하고 건설적인 피드백을 주신 리뷰어분들께 감사드립니다.

기존 연구와의 비교

현재 원고에서 LAMP와 기존 matrix-multiplication proof의 비교가 충분하지 않았다는 점에 동의합니다. Freivalds-in-Groth16은 동일한 조건에서 matrix-vector product를 circuit 밖으로 옮기는 효과를 확인하기 위한 비교 대상이었지만, state-of-the-art baseline은 아닙니다.

zkMatrix의 prover work는 O(k^2)이고 proof size와 verifier complexity는 O(log k)입니다. 공개 구현이 있는 후속 연구 DualMatrix는 O(K+k) field operations와 O(k) group operations/pairings를 사용합니다. 여기서 K는 nonzero entries의 총수이며 dense matrices에서는 K=Theta(k^2)입니다. zkMaP의 prover work는 O(k^2)이고, 320-byte proof를 두 번의 pairing으로 검증합니다.

LAMP의 전체 prover work 역시 intermediate vectors를 위한 field work와 encoded-column commitments를 위한 group work를 포함하여 O(k^2)입니다. LAMP의 이점은 circuit에 있습니다. Matrix-multiplication relation은 O(tk+E_code) constraints를 사용하고, 이에 따른 Groth16 proving work는 O(k log k), proof size와 verifier complexity는 O(log k)입니다. 저희는 ECC나 code-based proximity testing 자체가 새롭다고 주장하지 않으며, 기여는 이를 활용한 matrix-specific reduction입니다. 특화된 프로토콜이지만 matrix multiplication은 verifiable AI에서 반복적으로 나타나는 proving bottleneck입니다.

zkMatrix의 공개 구현은 찾을 수 없었고 zkMaP artifact도 사용할 수 없었습니다. 따라서 공개된 DualMatrix 구현을 가장 가까운 재현 가능한 대상으로 사용하여, B에 대한 독립 challenge s를 포함한 수정 LAMP 프로토콜과의 비교를 완료했습니다. Section 7에는 실험 방법, 조건 및 결과와 함께 LAMP, zkMatrix, DualMatrix 및 zkMaP의 asymptotic comparison table을 제시하겠습니다.

Circuit 내부에서 원본 행렬을 사용하는 경우

Reviewer B는 원본 행렬이 circuit의 다른 부분에서도 사용되는 경우를 질문했습니다. 표준 LAMP에서 rt_ABC는 모든 encoded columns의 Merkle commitments를 고정하지만, commit-carrying SNARK는 online relation에 사용되는 O(tk) sampled values만 commit합니다.

원본 행렬이 이미 circuit witnesses라면 commit-carrying SNARK가 O(k^2)개의 전체 matrix entries에 commit하고 application computation과 LAMP checks에서 동일한 variables를 사용할 수 있습니다. Witness-commitment cost는 quadratic이 되지만 matrix-multiplication check는 O(tk+E_code) constraints를 유지하며, 별도의 Merkle-opening과 CP-Link layers는 피할 수 있습니다. 이 commitment가 의도한 model weights에 대응하는지는 별도의 application-level 문제입니다.

Committed matrix encodings의 유효성

Reviewer C와 D의 지적대로 현재 theorem은 committed row-wise encodings의 유효성을 증명하지 않고 가정합니다. 기존 fold는 표준 polynomial argument에 의해 A와 C에 필요한 proximity guarantee를 제공합니다. 반면 B fold의 coefficient vector는 x=rA입니다. Malformed component D가 AD=0을 만족하면 모든 r에 대해 xD=rAD=0이므로 기존 검사로는 이를 탐지할 수 없습니다.

따라서 rt_ABC가 고정된 뒤 r과 동시에 B를 위한 독립적인 uniform challenge s를 추출하겠습니다. Query set과 code-check points가 추출되기 전에 prover는 sB의 encoding을 x, y, z의 encodings와 함께 commit합니다. Appendix D의 Barycentric Reed–Solomon Consistency Check는 이 encoding을 검사하고, sampled fold equations는 이를 rt_ABC에 고정된 hat(B)와 연결합니다. 수정된 theorem에는 proximity radius, extraction argument 및 전체 soundness bound를 명시하겠습니다. Unique-decoding radius 안에서는 close word도 하나의 decoded row를 결정하므로 일부 symbols의 변경 자체는 soundness failure가 아닙니다.

추가 검사는 하나의 O(k^2) native vector-matrix product, 한 번의 encoding/commitment 및 O(tk+E_code) circuit constraints를 요구합니다. 따라서 전체 prover work는 O(k^2)을 유지하고 fixed t와 code rate에서 circuit은 k에 대해 선형입니다.

그 밖의 수정 사항

불일치한 값은 0.06 s, 8.43x, 1.77x로 수정하고, "linear"이 전체 prover time이 아니라 핵심 constraint count를 뜻한다는 점을 명확히 하겠습니다. GPT-2 결과는 trade-off로 설명하겠습니다. Proving은 1.77x 빨라지지만 verification은 0.49 s에서 6.52 s로, proof size는 196 B에서 3.34 MB로 증가합니다. 196 B는 오타가 아닙니다. Groth16 proof는 constant-size인 반면 LAMP에는 sampled Merkle openings와 CP-Link proofs가 포함됩니다.

수정된 theorem의 full proof를 포함하겠습니다. Formal result는 public-coin interactive protocol을 대상으로 하며, multi-round Fiat–Shamir transform의 정식 ROM analysis는 future work로 남기겠습니다. Section 7에는 Groth16의 per-circuit setup, QALink의 configuration-dependent CRS, repetition counts, memory use 및 encoding-time accounting을 설명하겠습니다. 지적된 오탈자도 함께 수정하겠습니다.
