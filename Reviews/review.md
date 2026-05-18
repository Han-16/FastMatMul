# Review: FastMatMul — Efficient Verifiable Matrix Multiplication via Linear Error-Correcting Codes

**Venue target:** 보안/암호학 학회 (CCS, NDSS, USENIX Security 등 상위권)  
**Reviewer confidence:** 4/5 (해당 분야에 대한 충분한 이해를 갖추고 있음)

---

## 1. 논문 요약

본 논문은 SNARK 기반 검증 가능한 행렬 곱셈(verifiable matrix multiplication)의 회로 크기를 기존 Freivalds 방식의 O(k²)에서 O(tk)로 줄이는 프로토콜 FastMatMul을 제안한다. 핵심 아이디어는 행렬의 각 행을 선형 오류 정정 부호(linear error-correcting code)로 인코딩한 뒤, Merkle 트리로 커밋하고, 랜덤 샘플링된 소수의 열(column) 위치에서 fold 연산과 Merkle 경로 검증만으로 일관성을 확인하는 것이다. 비싼 O(k³) 행렬 곱셈은 SNARK 외부에서 수행하고, SNARK 회로 내에서는 O(tk) 크기의 경량 검증만 수행한다. Rust 구현체를 통해 k=1,024에서 Freivalds 대비 7.5배 제약 조건(constraint) 감소, 23.9배 증명 시간 단축을 보고하며, Freivalds가 메모리 부족으로 실패하는 k=2,048 이상에서도 동작함을 보인다.

---

## 2. 강점 (Strengths)

### S1. 명확하고 깔끔한 핵심 아이디어

"SNARK 회로 내에서 계산(compute)하는 대신 검사(check)한다"는 패러다임 전환이 직관적이고 설득력 있다. Freivalds의 랜덤화 검증과 오류 정정 부호의 proximity testing을 결합하는 방식이 자연스럽고, relation reduction chain (R_orig → R_Freivalds → R_SNARK)으로의 분해가 깔끔하게 구조화되어 있다. 이 아이디어 자체는 기존 code-based proof system(Ligero, Brakedown)의 철학을 행렬 곱셈이라는 구조적 문제에 맞춤 적용한 것으로, 기술적으로 타당하다.

### S2. 체계적인 보안 분석

soundness 증명이 commitment binding, algebraic evasion, proximity evasion의 세 가지 직교적 failure mode로 분해되어 있어 따라가기 쉽고, 각 항의 바운드가 명확하다. 구체적 파라미터(λ=128) 아래에서의 수치적 soundness error 계산도 포함되어 있어 실용적이다.

### S3. 실험적 검증의 포함

Rust 구현체를 통해 이론적 주장을 실험으로 뒷받침하고 있으며, 두 가지 SNARK 백엔드(Ped, KZG)와 두 가지 부호 설정(linear-time encodable, constant-rate)에 대한 비교를 제공한다. constraint count가 k에 대해 선형적으로 증가하는 것과 Freivalds 대비 proving time 이점이 실험적으로 확인된다.

### S4. 논문 작성 품질

전반적으로 논문이 잘 구조화되어 있고, 표기법이 일관적이며, Technical Overview 섹션이 formal construction에 앞서 직관을 효과적으로 전달한다. 프로토콜 figure와 notation table도 유용하다.

---

## 3. 약점 (Weaknesses)

### W1. (Major) 기술적 참신성(novelty)의 한계

이 논문의 가장 큰 약점은 핵심 구성 요소들이 모두 기존에 잘 알려진 기법이라는 점이다. Freivalds' algorithm, linear code의 linearity를 이용한 fold, Merkle commitment, proximity testing — 이 모든 것은 Ligero, Brakedown, FRI 등에서 이미 사용된 아이디어다. 논문 스스로 Related Work에서 Bennett et al. [2023]이 coding theory를 행렬 곱셈 검증에 적용한 이론적 연결을 이미 탐구했다고 언급하고 있다. 본 논문의 기여는 이러한 기존 기법들을 행렬 곱셈이라는 특정 문제에 조합한 "engineering contribution"에 가깝다. 상위 학회에서는 이 수준의 참신성이 충분한지 의문이 제기될 수 있다.

**제안:** Bennett et al.과의 차별점을 더 명확히 기술하고, 단순 조합 이상의 기술적 통찰이 있다면 그것을 부각시킬 필요가 있다. 예를 들어, encoding constraint를 SNARK 내부에서 처리하는 구체적 방법론이나, 구조적 challenge vector (Vandermonde)와 code linearity의 상호작용에서 발생하는 미묘한 기술적 이슈가 있다면 그것을 강조해야 한다.

### W2. (Major) 불완전한 실험 평가

실험 평가에 여러 중요한 누락이 있다:

1. **Sumcheck 기반 방식과의 비교 부재.** 논문이 주요 경쟁자로 다루는 것은 "direct Freivalds SNARK baseline"뿐이다. 그러나 Related Work에서 언급하는 SafetyNets, zkCNN의 sumcheck 방식이나 zkMatrix, DualMatrix, zkVC 등의 최신 전용 프로토콜과의 실험적 비교가 전혀 없다. 특히 zkVC는 12배 prover speedup을 주장하며 Transformer inference에 대한 적용까지 보여주고 있어, 이들과의 직접 비교 없이는 FastMatMul의 실질적 우위를 판단하기 어렵다.

2. **End-to-end ML inference 평가 부재.** 논문은 동기를 "verifiable ML inference"와 Transformer에 두고 있으나, 실제 신경망 추론에 대한 실험은 없다. 단일 행렬 곱셈에 대한 마이크로벤치마크만으로는 실제 multi-layer 추론에서의 이점을 판단하기 어렵다.

3. **Proof size와 verification time의 열위.** FastMatMul(Ped)의 proof size가 1.70~48.79 MB에 달하고, verification time이 0.06~1.38초인 반면, Freivalds baseline은 168 bytes / 0.001초이다. 이는 수백~수만 배의 차이로, "succinct argument"라는 SNARK의 핵심 특성을 상당 부분 상실한 것이다. 논문에서 이를 future work로 언급하고 있으나, 현재 상태에서는 verifier 측 비용이 매우 크며, 이는 스마트 컨트랙트 기반 검증 등 실용적 시나리오에서 큰 제약이 된다.

4. **하드웨어 환경 미기재.** 실험에 사용된 CPU, RAM, OS 등의 하드웨어 사양이 논문에 명시되어 있지 않다.

### W3. (Major) Encoding constraint로 인한 O(k²) 회귀 문제

논문의 핵심 주장은 "O(tk) 회로 크기"이지만, Section 4.3에서 스스로 인정하듯 일반적인 constant-rate 코드를 사용하면 encoding constraint가 O(k²)를 기여한다. 이 경우 전체 회로 크기가 O(tk + k²)가 되어, 점근적으로 Freivalds의 O(k²)와 동일하다. O(tk)를 달성하려면 linear-time encodable code(예: expander-based code)가 필요한데, 이러한 코드의 실질적 구현 복잡도와 상수 인자(constant factor)에 대한 구체적 논의가 부족하다. Table 2에서 encoding constraint 수치를 보여주지만, 이것이 전체 회로에 미치는 영향을 명확히 정량화하지 않고 있다.

**제안:** linear-time encodable code 사용 시와 일반 코드 사용 시의 전체 회로 크기를 명확히 분리하여 제시하고, 각각의 trade-off를 정량적으로 비교해야 한다.

### W4. (Minor) Knowledge soundness 증명의 부재

Remark 3에서 knowledge soundness(argument of knowledge)를 주장하면서 "full formal proof는 full version으로 미룬다"고 하고 있다. 보안 학회 제출에서 핵심 보안 속성의 증명을 생략하는 것은 바람직하지 않다. 특히 rewinding을 통한 행렬 추출 과정에서 Vandermonde 시스템의 invertibility와 SNARK extractor의 상호작용에 대한 세부 사항이 자명하지 않을 수 있다.

### W5. (Minor) 비직사각형 행렬 및 배치 처리 미지원

현재 프로토콜은 k×k 정방행렬만 다루고 있다. 실제 Transformer에서는 다양한 차원의 비정방 행렬 곱셈(예: (batch, seq_len, d_model) × (d_model, d_ff))이 발생한다. 비정방 행렬로의 확장이 자명하다면 간략히라도 언급이 필요하고, 비자명하다면 논의가 필요하다. 또한 batched verification(여러 행렬 곱을 한 번에 검증)에 대한 논의가 future work에 한 줄로만 언급되어 있어, 실용적 관점에서 아쉽다.

### W6. (Minor) Fiat-Shamir 변환의 보안 논의 불충분

Fiat-Shamir 변환 시 grinding attack에 대한 논의가 포함되어 있으나, 최근 연구에서 제기된 Fiat-Shamir의 round-by-round soundness 문제나, concrete security loss에 대한 더 깊은 분석이 필요하다. 특히 본 프로토콜은 3-round이므로, 각 라운드 간의 Fiat-Shamir 적용에서의 soundness degradation을 보다 엄밀하게 다뤄야 한다.

---

## 4. 세부 코멘트 (Minor Comments)

- **Abstract:** "7.5× constraint reduction at k=1,024 and up to 23.9× proving-time speedup" — 이 수치는 Freivalds baseline 대비이므로, 더 강력한 baseline(sumcheck 기반 등)과의 비교가 아님을 명확히 해야 한다.
- **Section 3.5 (Freivalds):** structured challenge vector r = (1, r, r², ..., r^{k-1})을 사용할 때 soundness bound가 (k-1)/|F|로 약해지는데, 이것이 보안에 미치는 영향을 Section 5에서만이 아닌 처음 소개 시점에서도 간략히 언급하면 좋겠다.
- **Figure 1:** 프로토콜 도식은 명확하나, 어떤 단계가 SNARK 내부이고 어떤 단계가 외부인지를 시각적으로 더 명확히 구분하면 좋겠다.
- **Section 6.4 (Verification time):** verification time이 O(tk)로 증가한다고 하는데, 이는 public input이 O(tk) 크기이기 때문이다. 이 점이 "succinct" verification이라는 SNARK의 정의와 어떻게 양립하는지 논의가 필요하다.
- **Bibliography:** CCS '25에 제출한다면, 2026년으로 표기된 DualMatrix [Cong et al., 2026]의 출판 연도를 확인해야 한다.
- **Appendix A:** Reed-Solomon codeword의 확률적 검증에 대한 부록이 본문과의 연결이 불명확하다. 본 프로토콜에서 이 기법이 구체적으로 어디에 사용되는지 명시해야 한다.

---

## 5. 질문 (Questions for Authors)

1. Linear-time encodable code를 사용한 실험(Table 1)에서, 구체적으로 어떤 expander-based code 구현을 사용했는가? Brakedown의 코드를 그대로 가져왔는가, 아니면 별도 구현인가?
2. Encoding constraint가 O(k²)인 일반 코드를 사용할 때, 실질적으로 Freivalds 대비 이점이 있는 k의 범위는 어디까지인가?
3. Proof size를 KB 단위로 줄이기 위해 KZG를 commitment layer에 적용하는 것이 future work라고 했는데, 이 경우 trusted setup 외에 추가적인 기술적 장벽이 있는가?
4. 비정방 행렬 A ∈ F^{m×k}, B ∈ F^{k×n}에 대한 확장이 자명한가? 그렇다면 회로 크기는 어떻게 되는가?
5. 여러 행렬 곱을 체인으로 검증할 때(예: multi-layer inference), 중간 커밋먼트를 재사용할 수 있는가?

---

## 6. 종합 평가 (Overall Assessment)

### 점수: Weak Accept (조건부 수락)

본 논문은 잘 쓰여진 논문으로, 실용적인 문제(SNARK 내 행렬 곱셈 비용)에 대한 깔끔한 해결책을 제시한다. 프로토콜 설계가 깔끔하고, 보안 분석이 체계적이며, 실험이 이론적 주장을 뒷받침한다.

그러나 다음의 우려가 있다:

- **기술적 참신성이 제한적이다.** 핵심 기법들(Freivalds + linear code + proximity testing + Merkle)이 모두 기존에 잘 알려진 것이며, 이들의 조합이 상위 학회의 novelty 기준을 충족하는지 의문이다.
- **실험 비교가 불충분하다.** 가장 약한 baseline(direct Freivalds SNARK)만 비교하고 있으며, sumcheck 기반 방식이나 최신 전용 프로토콜(zkMatrix, zkVC 등)과의 비교가 없다.
- **Proof size/verification time의 열위가 심각하다.** 현재 상태에서는 proof가 수십 MB에 달하여, 많은 실용적 시나리오에서 배포가 어렵다.

### 학회 수준 평가

- **S&P, CCS, USENIX Security (1티어):** 현재 상태로는 accept 가능성이 낮다. Novelty 부족과 불완전한 비교 실험이 주요 약점이다.
- **NDSS, ESORICS, ACSAC (1.5~2티어):** 위의 약점들을 보완한다면(특히 W1, W2) 경쟁력이 있다. 특히 zkVC, DualMatrix 등과의 실험적 비교를 추가하고, end-to-end ML inference 시나리오에서의 평가를 포함한다면 충분히 가능성이 있다.
- **ACNS, CT-RSA, FC 등 (2티어 암호학):** 현재 상태에서도 accept 가능성이 높다. 깔끔한 구성과 체계적인 분석이 이 수준의 학회에서 좋은 평가를 받을 수 있다.

### 주요 개선 권고사항 (수락을 위한 필수 조건)

1. **최신 경쟁 프로토콜과의 실험적 비교를 추가하라** — 최소한 sumcheck 기반 방식(SafetyNets/zkCNN) 또는 zkVC와의 proving time, constraint count 비교가 필요하다.
2. **Proof size 문제에 대한 구체적 해결 방안을 제시하라** — 현재의 수십 MB proof size는 치명적 약점이다. KZG commitment layer 적용의 프로토타입이라도 포함하면 논문의 가치가 크게 올라간다.
3. **End-to-end 적용 사례를 최소 하나 포함하라** — 단일 행렬 곱이 아닌, 2~3 layer Transformer의 attention 또는 FFN에 FastMatMul을 적용한 결과를 보여주면 motivation과의 일관성이 확보된다.
4. **Knowledge soundness 증명을 appendix에라도 포함하라.**
5. **하드웨어 환경 및 재현 가능성 정보를 명시하라.**

---

*Review Date: 2026-05-18*
