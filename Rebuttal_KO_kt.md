세심하고 건설적인 피드백을 주신 모든 리뷰어께 감사드립니다.

기존 연구 대비 위치와 비교

현재 원고는 LAMP와 기존 matrix-multiplication proof를 충분히 비교하지 않았습니다. LAMP는 committed row-wise encodings에 대한 matrix-multiplication statement를 검사하며, 범용 IOP나 end-to-end zkML system은 아닙니다. 저희는 Ligero, Brakedown, Blaze, Orion 등에서 사용된 ECC나 code-based proximity testing 자체의 novelty를 주장하지 않습니다. 저희의 기여는 quadratic in-circuit computation을 sampled consistency checks로 전환하는 matrix-specific reduction입니다. 특화된 프로토콜이지만 matrix multiplication은 verifiable AI에서 반복적으로 나타나는 proving bottleneck입니다.

Freivalds-in-Groth16은 동일한 실험 조건에서 이 reduction의 효과를 분리하지만 state-of-the-art baseline은 아닙니다. zkMatrix는 O(k^2) prover work와 O(log k) proof size 및 verifier complexity를 보고합니다. 공개 구현이 있는 후속 연구 DualMatrix는 O(K+k) field operations와 O(k) group operations/pairings를 보고하며, K=nnz(A)+nnz(B)+nnz(C)=Theta(k^2)인 dense inputs에서는 여전히 quadratic입니다. Proof size와 verifier complexity는 O(log k)입니다. zkMaP은 O(k^2) prover work, 320-byte proofs, constant pairing count 및 O(k) verifier-side field work를 보고합니다. Fixed code rate에서 LAMP는 intermediate vectors에 O(k^2) field work, encoded-column commitments에 O(k^2) group work를 사용하지만 in-circuit relation은 O(tk+E_code) constraints로 줄입니다. Groth16 proving work는 O(k log k)이고 proof size와 verifier complexity는 O(log k)입니다.

zkMatrix의 공개 구현은 찾을 수 없었고 zkMaP artifact도 사용할 수 없었습니다. 따라서 공개된 DualMatrix 구현을 가장 가까운 재현 가능한 대상으로 사용하여, B에 대한 독립 challenge s를 포함한 수정 LAMP 프로토콜과의 비교를 완료했습니다. Section 7에는 실험 방법, 조건 및 결과를 보고하고, zkMatrix, DualMatrix 및 zkMaP과의 asymptotic comparison도 함께 제시하겠습니다.

Circuit 내부에서 원본 행렬을 사용하는 경우

표준 LAMP에서 rt_ABC는 challenge 전에 모든 row-wise encoded columns의 Merkle commitments를 고정하지만, commit-carrying SNARK는 online relation에 사용되는 sampled columns의 O(tk) values만 commit합니다. 원본 행렬이 이미 같은 circuit의 witnesses라면 commit-carrying SNARK가 O(k^2)개의 전체 matrix entries에 commit하고, application computation과 LAMP checks가 동일한 witness variables를 사용할 수 있습니다. Matrix-multiplication check는 O(tk+E_code) constraints를 유지하며 별도의 Merkle-opening과 CP-Link layers는 피할 수 있습니다. 해당 commitment가 verifier가 의도한 model weights를 나타낸다는 보장은 별도의 application-level 문제입니다.

Committed matrix encodings의 유효성

Reviewer C와 D의 지적대로 현재 정리는 committed row-wise encodings의 유효성을 증명하지 않고 가정합니다. 구조적으로 LAMP는 x, y, z에 EncCheck를 적용하고, random folding으로 hat(A), hat(B), hat(C)의 proximity를 검사합니다. A와 C에서는 nonzero malformed component가 random r에 관한 nonzero degree-bounded polynomial을 만들기 때문에 negligible한 확률로만 0이 됩니다. 반면 B에서 malformed component D가 AD=0을 만족하면 모든 r에 대해 xD=rAD=0이므로 기존 검사로는 이를 탐지할 수 없습니다.

따라서 rt_ABC가 고정된 뒤 기존 Freivalds challenge r과 동시에 B를 위한 독립적인 uniform challenge s를 추출하겠습니다. Query set과 code-check points가 추출되기 전에 prover는 b_s=sB의 encoding을 x, y, z의 encodings와 함께 commit합니다. Appendix D의 Barycentric Reed–Solomon Consistency Check(EncCheck)는 b_s를 검사하고 sampled fold equations는 이를 rt_ABC에 고정된 hat(B)와 연결합니다. 수정된 theorem에는 proximity radius, extraction argument 및 전체 soundness bound를 명시하겠습니다. Unique-decoding radius 안의 close word는 여전히 하나의 decoded row를 결정합니다.

이 검사는 하나의 O(k^2) native vector-matrix product, 한 번의 encoding/commitment 및 O(tk+E_code) circuit constraints를 추가합니다. 전체 prover work는 O(k^2)을 유지하고, fixed t와 code rate에서 circuit은 k에 대해 선형입니다.

보안 범위와 setup

Formal theorem은 public-coin interactive protocol로 한정하고, 구현된 multi-round Fiat-Shamir transform의 정식 ROM 분석은 future work로 남기겠습니다. Groth16의 per-circuit setup과 QALink의 configuration-dependent CRS 및 배포 비용도 설명하겠습니다.

측정값과 서술 수정

불일치한 값은 0.06 s, 8.43x, 1.77x로 수정하겠습니다. “Linear”은 전체 prover time이 아니라 핵심 constraint count를 의미합니다. GPT-2 결과는 proving이 1.77x 빨라지는 대신 verification이 0.49 s에서 6.52 s로, proof가 196 B에서 3.34 MB로 증가하는 trade-off로 보고하겠습니다. 196 B는 오타가 아닙니다. Groth16 proof size는 circuit size와 무관하게 constant인 반면, LAMP는 sampled Merkle openings와 CP-Link proofs도 직렬화합니다. Encoding-time accounting, 반복 측정, 분산, memory를 보완하고 열거된 표기·오탈자를 수정하며 Theorem 6.2의 full proof를 appendix에 포함하겠습니다.
