# IEEE S&P 2027 Post-Rebuttal Action Plan

## 1. 기준과 목표

이 문서는 2026년 8월 28일 text rebuttal 제출 이후부터 9월 3일 수정 원고 제출까지 수행할 작업을 관리한다.

- **제출한 rebuttal:** `Rebuttal_EN.md`, 729 words
- **9월 3일 제출물:** revised paper PDF와 submitted version 대비 diff PDF
- **공식 마감:** 2026년 9월 3일, HotCRP 표시 시각 기준
- **내부 마감:** 2026년 9월 2일 18:00 KST
- **제출 원본:** `origin/snp-2027-제출버전`, `Paper/main-submitted.pdf`
- **수정 작업본:** `main`, `Paper/main.tex`, `Contents/`

### 공식 페이지·양식 제한

- IEEE S&P 2027 일반 연구논문은 **본문(text) 최대 13페이지**와
  **References+Appendix 최대 5페이지**, **전체 최대 18페이지**를 지킨다.
- 13페이지 이후의 본문성 text와 figure는 명확히 Appendix로 표시한다.
- US letter와 `\documentclass[conference,compsoc]{IEEEtran}` 형식을 유지한다.
- 여백, 글꼴, 행간 또는 비정상적인 negative spacing을 조정해 페이지를
  맞추지 않고, 내용의 삭제·축약·재배치로만 제한을 맞춘다.
- 2026-08-28 최초 확장본은 **20페이지**로 본문 및 전체 페이지 제한을
  초과했다. 중복 설명과 전체 protocol figure를 제거하고 상세 증명을
  Appendix로 재배치한 2026-08-29 작업본은 **12페이지**이다. Conclusion과
  References가 9페이지에서 시작하고 Appendix는 10페이지에서 시작하므로,
  현재는 본문 13페이지, References+Appendix 5페이지, 전체 18페이지 제한을
  모두 만족한다.
- 최종 목표는 **본문 13페이지 이하**, **References+Appendix 5페이지 이하**,
  **전체 18페이지 이하**이다. 원 제출본의 본문 11페이지를 반드시 유지할
  필요는 없지만, 핵심 설명을 제외한 중복 확장으로 13페이지를 넘기지 않는다.

`origin/snp-2027-제출버전`과 `Paper/main-submitted.pdf`는 수정하지 않는다. 수정은 현재 `main`의 source에 직접 반영하며, diff만을 위한 중복 `Contents/` 트리는 만들지 않는다.

제출한 rebuttal의 약속을 최종 원고에서 조용히 축소하거나 생략하지 않는다. 약속을 이행할 수 없거나 결과가 달라지면 공동저자 전원이 주장 범위를 다시 결정하고 필요한 경우 HotCRP 후속 설명을 준비한다.

### 서술 원칙

- Rebuttal의 각 우려에는 반드시 답하되, 같은 논거를 Introduction,
  Overview, Construction, Security에서 반복하지 않는다.
- 독립적인 $B$ 검사는 Construction에서 transcript와 검사식만 설명하고,
  기존 $A/C$ 검사와 다른 이유 및 보안 경계는 Security에서 짧게 설명하며,
  완전한 확률 계산은 Appendix에만 둔다.
- 본문에서는 수정의 필요성과 최종 보장만 독자가 이해할 수 있을 정도로
  설명한다. 표준 primitive 정의, bad-event 분해 및 backend 세부식은 핵심
  주장에 직접 필요할 때만 남긴다.
- 페이지 여유가 있더라도 rebuttal 문장을 그대로 확장해 옮기지 않는다.
  추가 실험 결과와 비교표가 들어갈 공간을 우선 확보한다.

## 2. 전체 진행 순서

작업은 다음 세 단계로 진행한다.

1. **실험과 무관한 논문의 작성·수정·개선**
2. **추가 구현·실험**
3. **2단계 결과를 반영한 논문 작성과 최종 제출물 생성**

1단계와 2단계는 병렬로 진행한다. 다만 Construction의 최종 transcript, soundness theorem, 비용식 및 Evaluation 수치는 2단계 결과가 확정된 뒤 3단계에서 동결한다.

## 3. 1단계: 실험과 무관한 논문의 작성·수정·개선

### 3.1 Related Work와 positioning

- Freivalds-in-Groth16 baseline은 state of the art가 아니라 동일 backend에서 matrix--vector products를 circuit 밖으로 옮기는 효과를 분리하는 baseline이라고 설명한다.
- zkMatrix, DualMatrix, zkMaP과 LAMP의 statement, commitment model, prover work, proof size, verifier complexity 및 setup 범위를 비교한다.
- zkMatrix 공개 구현을 찾지 못했고 zkMaP artifact를 사용할 수 없었던 점을 설명한다.
- 공개 구현이 있는 DualMatrix를 가장 가까운 reproducible baseline으로 선택한 이유를 설명한다.
- LAMP가 ECC 또는 proximity testing 자체의 novelty를 주장하지 않고 matrix-specific reduction을 기여로 삼는다는 점을 명확히 한다.
- Ligero, Brakedown, Blaze, Orion 및 zkCNN/zkGPT/zkLLM은 동일한 end-to-end benchmark로 취급하지 않고 statement와 scope 차이를 prose로 설명한다.
- LAMP, zkMatrix, DualMatrix, zkMaP의 asymptotic comparison table 초안을 작성한다. 실험 결과 열은 3단계에서 채운다.

### 3.2 Original matrices를 circuit에서 사용하는 경우

- Standard LAMP에서 $\rt_{ABC}$가 모든 encoded columns의 commitments를 고정하고, commit-carrying SNARK는 online relation에 필요한 sampled values만 commit한다는 점을 명확히 한다.
- Original matrices가 다른 application computation에서도 circuit witnesses로 사용되면 commit-carrying SNARK가 전체 $O(k^2)$ matrix entries에 commit하는 variant를 설명한다.
- Systematic encoding과 full committed-witness projection을 지원하는 backend에서는
  application computation과 LAMP check가 동일 witness variables를 재사용할 수
  있음을 설명한다. Non-systematic encoding의 message-map constraint와 backend
  projection/linking 비용을 생략하지 않는다.
- Witness-commitment cost는 $O(k^2)$이지만 matrix-multiplication check는 $O(tk+E_{\mathsf{code}})$ constraints를 유지한다고 명시한다.
- Commitment가 verifier가 의도한 model weights를 나타내는지 확인하는 문제는 별도의 application-level guarantee로 구분한다.

### 3.3 보안 claim과 setup 범위

- Formal theorem은 public-coin interactive protocol을 대상으로 한다고 명확히 한다.
- Multi-round Fiat--Shamir transform의 정식 ROM proof는 future work로 한정한다.
- Groth16에는 per-circuit setup이 필요하고 QALink CRS는 $t$와 block length 등 configuration에 의존한다고 설명한다.
- Setup이 offline preprocessing인지, 기존 online proving/verification timing에 포함되는지를 명확히 구분한다.
- $\rt_{ABC}$가 verifier가 의도한 model weights를 나타내는지 확인하는 문제는 protocol soundness와 분리한다.

### 3.4 기존 수치와 claim 수정

- `0.06 s`, `8.43x`, `1.77x`, `0.49 s`, `6.52 s`, `196 B`, `3.34 MB`는
  pre-rebuttal protocol의 수치로 분리 보관하고 revised protocol의 결과로
  재사용하지 않는다.
- Abstract, Introduction, Evaluation 및 Conclusion에서는 revised transcript와
  최종 sampling parameter를 사용한 raw log가 준비되기 전까지 직접 성능
  수치를 주장하지 않는다.
- GPT-2를 revised protocol로 재측정한 경우에만 proving 개선과 verification 및
  proof-size overhead를 함께 trade-off로 보고한다.
- Freivalds의 `196 B`를 다시 사용할 경우 Groth16 proof가 constraint 수와
  무관하게 constant-size라는 측정 범위를 함께 설명한다.
- “Linear Verification”과 “linear”은 전체 prover time이 아니라 matrix-multiplication relation의 in-circuit constraint complexity를 의미한다고 설명한다.
- $O(tk)$와 $O(tk+E_{\mathsf{code}})$, $E_{\mathsf{link}}(k)$와 $E_{\mathsf{link}}(k,t)$의 불일치를 바로잡는다.
- 현재 표의 encoding time이 commit time에 포함되는지 또는 누락됐는지 기존 구현과 측정 코드를 통해 확인할 항목으로 표시한다. 확인 전 임의의 수치를 쓰지 않는다.

### 3.5 설명·구조·오탈자 개선

- Introduction에 direct multiplication의 $O(k^3)$, Freivalds의 $O(k^2)$, proximity testing 및 relative code distance에 대한 직관을 추가한다.
- Section 5.3 마지막의 offline-relation 문단을 Section 5.4의 적절한 위치로 이동한다.
- 중복 Brakedown 참고문헌을 하나로 합친다.
- $[n]$과 Pedersen/encoding 식의 index convention을 통일한다.
- 리뷰에 열거된 오탈자를 수정한다.
  - `the LAMPprover`
  - `[26].In particular`
  - `We report the cost of the LAMP`
  - `Let E_Enc(k,n) denote cost ...`
  - `an PPT extractor`
- 실험 결과에 의존하지 않는 표·그림 설명과 section 간 참조를 정리한다.

### 3.6 페이지 예산과 본문·Appendix 재구성

#### 본문에 반드시 유지할 내용

- Introduction에는 문제, 기여, claim 범위와 수정 프로토콜의 핵심만 둔다.
  독립 $B$ 검사의 세부 soundness 설명은 넣지 않고 Security를 참조한다.
- Related Work에는 reviewers가 명시적으로 요청한 matrix-multiplication
  verification 비교 설명과 zkMatrix/DualMatrix/zkMaP/LAMP asymptotic
  comparison table을 유지한다.
- Preliminaries에는 linear/interleaved code, fold, committed-sampled-value
  interface 및 structured Freivalds에 필요한 최소 표기만 유지한다.
- Construction에는 $\rt_{ABC}\rightarrow(r,s)\rightarrow\cm_{XYZB}
  \rightarrow(I,\alpha)$의 commitment/challenge 순서, $\mathbf b=\mathbf sB$,
  sampled fold equations, online/offline binding의 역할 및 complexity를
  유지한다.
- Security에는 valid-codeword input을 가정하지 않는 theorem statement,
  전체 failure bound, $B$에 독립적인 $s$가 필요한 이유와 짧은 proof
  sketch를 유지한다.
- Evaluation에는 실험 환경, 수정 LAMP의 주 비교 결과, DualMatrix 비교,
  setup/측정 범위 및 핵심 trade-off를 유지한다.
- Original matrices를 application circuit에서 함께 사용하는 variant에 대한
  reviewer 답변은 본문에 유지하되 한 문단으로 축약한다.

#### Appendix로 이동할 수 있는 내용

- Structured-fold proximity는 별도 보조정리를 새로 증명하지 않고
  Ben-Sasson et al.의 Reed--Solomon proximity-gap 정리와
  Diamond--Posen의 single-parameter batching 논의를 정확히 인용한다.
- Soundness theorem의 bad-event decomposition, extraction 및 모든 확률 계산을
  포함한 full proof.
- Barycentric Reed--Solomon consistency check의 상세 알고리즘과 증명.
- CP-Link의 blockwise formal statement, backend instantiation 및 세부 검증식.
- 필요한 경우 전체 transcript의 확장 pseudocode, 내부 component breakdown 및
  batch/GPT-2 상세표. 현재 본문은 compact transcript와 online/offline relation
  figures만 유지하며, 중복되는 전체 protocol figure는 삭제한다.

#### 이동보다 삭제·축약해야 할 내용

- Merkle, Pedersen, SNARK 및 CP-SNARK의 표준 알고리즘 목록은 본문에서 짧은
  interface 설명과 인용으로 대체한다. Appendix의 일반적인 SNARK/CP-Link
  security definitions도 핵심 정리에 직접 쓰이지 않는 반복은 삭제한다.
- Technical Overview, Construction, Security Analysis에 반복되는 encoding,
  fold, commitment-linking 및 soundness intuition은 한 번만 상세히 설명한다.
- Construction에는 compact transcript와 online/offline relation figures만
  남기고, 같은 내용을 반복하던 전체 protocol figure는 삭제한다.
- Evaluation의 component/batch/GPT-2 표를 모두 본문에 유지하지 않는다.
  reviewer가 요청한 prior-work 비교와 수정 프로토콜의 주 결과를 우선한다.

#### 페이지 예산

- 본문은 최대 13페이지로 동결하고, 13페이지를 채우기 위한 불필요한 확장은
  하지 않는다.
- 현재 작업본은 총 12페이지이고 Conclusion과 References가 9페이지,
  Appendix가 10페이지에서 시작한다. References+Appendix는 9--12페이지의
  4페이지 안에 들어간다.
- 본문에는 최대 4페이지의 형식상 여유가 있으나, 이는 수정 LAMP 및
  DualMatrix 실험 결과와 필수 비교표를 위한 상한이며 목표 분량이 아니다.
- Appendix 우선순위는 (1) full soundness proof, (2) RS consistency check,
  (3) CP-Link 세부사항, (4) 추가 실험표 순서로 한다.
- 매 주요 통합 후 PDF에서 Section 8/References/Appendix의 실제 시작 페이지를
  기록한다. line count나 source 분량만으로 페이지 제한을 판단하지 않는다.

### 3.7 1단계 완료 조건

- [x] Related Work prose와 asymptotic comparison table 초안이 완성됨
- [x] Original-matrix circuit variant와 비용 설명이 반영됨
- [x] Interactive/Fiat--Shamir/setup claim 범위가 정리됨
- [x] pre-rebuttal 직접 수치를 revised protocol 결과에서 제거하고 재측정
  전까지 claim을 보류함
- [x] Introduction 직관, 문단 위치, 참고문헌, 표기 및 오탈자가 수정됨
- [x] 실험 결과를 기다리는 항목은 2·3단계로 분리했고 근거 없는 새 수치를 추가하지 않음
- [x] 중복 설명을 제거하고 본문 필수 내용과 Appendix 상세 내용을 재배치함
- [x] 현재 작업본이 본문 13페이지, References+Appendix 5페이지, 전체 18페이지 제한을 만족함

## 4. 2단계: 추가 구현·실험

### 4.1 독립 $B$ proximity test 구현

**구현 상태 (2026-08-29): READY.** `Implementation/cmd/lamp`,
`lamp_batch`, `lamp_gpt2`와 각 circuit에 아래 transcript와 complete
intermediate binding을 반영했다. 단일·배치 경로는 소형 end-to-end proof를
성공했고 GPT-2 경로는 전체 Go build와 shape-only circuit compile을
통과했다. 실험 서버에서는 반드시 `scripts/run_revised_suite.sh smoke`를
먼저 실행한다.

- $\rt_{ABC}$가 고정된 뒤, query 이전에 $r$과 함께 독립적인 uniform challenge $\mathbf s$를 생성한다.
- $\mathbf b_s=\mathbf sB$와 $\widehat{\mathbf b}_s=\mathsf{Enc}(\mathbf b_s)$를 구현한다.
- $\mathbf x,\mathbf y,\mathbf z,\mathbf b_s$와 네 encoded view 전체를 하나의
  pre-query commitment $\cm_{XYZB}$에 포함한다.
- Circuit에 $\mathbf b_s$용 `EncCheck`와 sampled $B$-fold equations를 추가한다.
- CP-SNARK의 complete intermediate committed witness를 $\cm_{XYZB}$와
  CP-Link로 연결한다. 입력 행렬 쪽 Merkle opening은 sampled ABC columns에만
  사용한다.
- XYZB를 sampled coordinates에서만 link하는 기존 구조는 사용하지 않는다.
  EncCheck의 전체 word가 query와 code-check points 전에 고정되어야 한다.
- 변경된 circuit와 message layout에 맞춰 Groth16/QALink setup을 다시 생성한다.

### 4.2 회귀·공격 테스트

**로컬 검증 상태 (2026-08-29): VERIFIED.** `go test ./...`가
통과했다. 테스트는 정상 witness, $A=0$에서 $xB$로 감지할 수
없는 $B$ 변조, non-codeword `Enc(sB)`, $r/s$ domain separation, query
uniqueness 및 서로 다른 out-of-domain RS point를 포함한다. 또한
단일·배치 스모크 proof에서 complete intermediate QA-Link가 검증됐다.

- 올바른 $AB=C$ witness가 accept되는지 확인한다.
- $A=0$ 또는 rank-deficient $A$에서도 malformed $B$가 reject되는지 확인한다.
- Commitment 이후 $B$, $\mathbf b_s$ 또는 encoded view를 변경하면 reject되는지 확인한다.
- $\mathbf s$가 $\rt_{ABC}$ 이후, query set $I$ 이전에 transcript에 고정되는지 확인한다.
- $\mathbf x,\mathbf y,\mathbf z,\mathbf b_s$와 complete encoded views가
  $\cm_{XYZB}$ 및 circuit committed witness에 동일하게 연결되는지 확인한다.
- 질의 좌표만 link하고 full EncCheck witness를 사후 선택하는 공격이
  불가능한지 adversarial test로 확인한다.

### 4.3 수정 LAMP 측정

**실행 준비 상태 (2026-08-29): READY; DATA PENDING.** 수정 LAMP와
Freivalds 명령에 3회 반복, deterministic seed, run ID, code commit,
실행 명령, UTC 시작 시각, peak RSS, status를 CSV에 기록하도록
구현했다. 추가 $B$ fold+encoding 시간은 `BProximityTime`으로
분리했다. `run_revised_suite.sh`는 smoke/core/extended profile, raw log,
manifest와 failure exit code를 남긴다. 아래 측정값은 아직 서버에서
생성하지 않았다.

추가 $B$ proximity test 자체는 sampling parameter $t$의 변경을 요구하지
않는다. 수정 protocol의 측정은 Section 7에 보고하는 $t$와 code rate를
그대로 사용하되, $t\le n$과 query uniqueness를 만족해야 한다. 기존 결과는
$B$ 검사가 없는 pre-rebuttal protocol의 측정이므로 revised protocol의
결과로 재사용하지 않고 동일 parameter로 다시 측정한다.

각 raw log/CSV에 다음을 기록한다.

- `k`, `t`, code rate, field/curve, security setting
- code commit hash, 실행 명령, seed, `run_id`
- constraint count, setup/prove/verify time, serialized proof bytes
- $\mathbf sB$, encoding, commitment, Merkle, Groth16, CP-Link component time
- peak RSS, success/OOM/timeout 및 exit status
- $C=AB$ 생성 비용과 setup을 total에 포함했는지 여부

최소 `k=1024`와 대표 대형 지점 하나를 각각 3회 측정한다. `k=128`부터 `k=8192`까지 모든 크기의 우위를 주장하려면 전체 범위를 수정 protocol로 다시 측정한다. 기존 pre-$B$ 결과와 revised 결과를 하나의 최종 protocol 결과처럼 혼합하지 않는다.

### 4.4 DualMatrix 비교 재현성

- 공개 저장소 URL, exact commit, build profile과 실행 명령을 기록한다.
- Curve/security parameters, dense-input 생성 방식, seed, CPU/RAM/thread 수 및 반복 통계를 기록한다.
- LAMP와 DualMatrix의 statement, setup 및 proof contents 차이를 설명한다.
- `k=1024`의 `19.06 s`, `0.15 s`, `88,844 B`를 사용할 경우 raw evidence와 직접 연결한다.
- 기존 데이터가 검증되지 않으면 필요한 지점을 다시 측정하고, 검증되지 않은 직접 수치를 싣지 않는다.

### 4.5 선택적 추가 실험

- 시간과 구현 상태가 허용하면 batch와 GPT-2 workload를 수정 protocol로 재측정한다.
- 이 실험은 $B$ test, 필수 revised LAMP 측정 및 DualMatrix 비교보다 우선하지 않는다.
- 수행하지 못하면 기존 결과의 protocol version과 한계를 논문에서 명확히 표시한다.

### 4.6 2단계 전달물

- 동결된 protocol transcript와 commitment layout
- 최종 constraint 및 asymptotic cost 계산
- 재현 가능한 raw logs/CSV와 실행 명령
- 평균·분산 또는 범위와 repetition count
- setup/online timing 구분 및 encoding-time accounting
- peak memory와 OOM/timeout 설명
- 사용한 code commit hash

## 5. 3단계: 구현·실험 결과를 반영한 논문 작성

### 5.1 Construction 최종 동기화

- **현재 초안 상태:** 논문 source에는 독립 스칼라 (s), 구조화 벡터
  ((1,s,\ldots,s^{k-1})), \(\mathbf b=\mathbf sB\), 네 번째
  `EncCheck`, complete `XYZB` commitment 및 sampled (B)-fold equation을 반영했다.
  구현 transcript와 대조한 뒤에만 최종 확정한다.
- Compact transcript, online/offline relation figures, statement, witness,
  commitment layout, Merkle openings, CP-SNARK relation 및 CP-Link statement를
  실제 구현과 일치시킨다.
- $\mathbf x,\mathbf y,\mathbf z,\mathbf b_s$와 encoded views가 query 이전에 고정되는 binding 순서를 명시한다.
- 추가 검사의 서킷 밖 $O(k^2)$ work와 서킷 안 $O(tk+E_{\mathsf{code}})$ constraints를 실제 구현 경로에 맞게 반영한다.

### 5.2 Soundness theorem과 full proof

- **현재 초안 상태:** valid-codeword input assumption을 제거하고 proximity
  radius \(\tau\), Ben-Sasson et al.의 one-parameter error
  \( (k-1)n/|\mathbb F| \), unique extraction 및 sampled relation error를
  분리한 theorem과 Appendix proof를 작성했다.
- 기존 $A/C$ structured folding argument를 명시한다.
- 독립적인 structured $s$-fold에 의한 $B$ proximity, pre-query binding,
  extraction 및 composition arguments를 작성한다.
- 선택한 code rate, proximity radius $\tau$, sampling parameter $t$와 전체
  soundness bound를 구현·실험 configuration에 일관되게 반영한다.
- Backend failure, code consistency, $A/C$ test, $B$ test, Freivalds 및 sampling error를 구분한다.
- 기존 $t=128$ 데이터는 $B$ 검사가 없는 pre-rebuttal protocol의 결과이므로
  revised protocol의 결과로 재사용하지 않는다. 추가 $B$ 검사를 포함한 동일
  parameter configuration을 다시 측정한다.
- $A=0$, rank-deficient $A$, $C=0$ 및 malformed symbols를 검토한다.
- 수정된 Theorem 6.2의 full proof를 포함하고 공동저자 한 명 이상이 독립 검토한다.

### 5.3 Evaluation 최종 반영

- 수정 LAMP와 DualMatrix의 실험 방법, 조건 및 결과를 Section 7에 추가한다.
- LAMP, zkMatrix, DualMatrix, zkMaP의 asymptotic comparison table을 확정한다.
- 모든 직접 수치를 raw log, 실행 명령, code commit, hardware 및 parameter와 연결한다.
- Setup/prove/verify time, proof size, constraints, repetition count, memory 및 encoding-time accounting을 반영한다.
- GPT-2를 재측정하지 못하면 pre-rebuttal 수치를 revised protocol의 결과로
  싣지 않고 해당 부가 실험을 생략한다.

### 5.4 전체 원고 일관성 검토

- Abstract부터 Conclusion까지 protocol version, 수치, complexity 및 claim scope를 통일한다.
- “completed a comparison with revised LAMP”, “will include the full proof”, “will report”라는 rebuttal 약속이 실제 원고에서 이행됐는지 확인한다.
- 구현, theorem, figure 및 Evaluation이 서로 다른 transcript나 비용을 설명하지 않는지 확인한다.

### 5.5 Build, diff 및 제출

- 하나의 재현 가능한 pdfLaTeX/BibTeX build 절차를 고정한다.
- Unresolved reference/citation, overfull box, 익명성, artifact URL 및 참고문헌을 확인한다.
- PDF에서 본문이 13페이지를 넘지 않고, References+Appendix가 5페이지를
  넘지 않으며, 전체가 18페이지를 넘지 않는지 직접 확인한다. 13페이지 이후의
  모든 본문성 text/figure가 Appendix로 명확히 표시되었는지도 확인한다.
- IEEE `conference,compsoc`, US letter, 기본 margin/font/spacing을 유지하고
  space-scrunching으로 제한을 맞추지 않는다.
- `origin/snp-2027-제출버전`과 `main` source의 diff TeX/PDF를 생성한다.
- Diff 생성물은 submitted/revised source를 덮어쓰지 않는다.
- 설치된 `latexdiff`를 사용해 추가·수정 부분은 노란색 배경으로 표시하고,
  삭제 부분은 별도로 식별 가능하게 표시한다. 하이라이트가 수식·표·그림을
  깨뜨리는 지점만 수동 보정하며 clean revised PDF에는 diff macro를 넣지 않는다.
- Revised PDF와 diff PDF를 HotCRP에 사전 업로드하고 다시 내려받아 확인한다.

## 6. 일정

| 날짜 | 1단계: 논문 수정 | 2단계: 구현·실험 | 3단계: 결과 통합 |
|---|---|---|---|
| **8/28** | Related Work, 기존 수치·오탈자 수정 시작 | protocol transcript와 commitment layout 동결 | 통합 위치와 TODO 표시 |
| **8/29** | Original-matrix/setup/FS 설명, 비교표 초안 | $B$ test 구현과 `k=1024` smoke test | Construction/theorem skeleton 대조 |
| **8/30** | 1단계 수정 완료 및 자체 검토 | `k=1024` 반복 측정, 비용·memory 확인 | $B$ argument와 theorem 1차본 |
| **8/31** | 남은 textual concern 정리 | 대표 대형 지점 및 필수 비교 완료 | full proof와 Sec. 2/4/5/6/7/Appendix 통합·동결 |
| **9/1** | 문장·표기 최종 교정 | raw data와 parameters 동결 | 전체 수치·scope 공동저자 검토 |
| **9/2** | 추가 내용 수정 금지 | 재현성 자료 정리 | clean PDF, diff PDF, HotCRP 사전 업로드 |
| **9/3** | 제출 상태 확인 | 새 실험 수행하지 않음 | 재다운로드·열람 및 최종 제출 검증 |

8월 31일까지 full proof가 검토되지 않으면 unconditional input-validity 주장을 유지하지 말고 공동저자 전원이 theorem 범위와 HotCRP 후속 설명을 결정한다. 부가 실험이 지연되면 먼저 축소하되, rebuttal에서 약속한 수정 LAMP--DualMatrix 결과는 우선 보존한다.

## 7. 역할 분담

| 작업 | 책임 | 승인/검토 |
|---|---|---|
| 1단계 논문 수정, 전체 통합, build/diff/submission | 이경태 | 전체 공동저자 |
| $B$ test 구현, 회귀 테스트, 수정 실험 | 한병규 | Protocol 공동저자 |
| Soundness theorem과 full proof | Protocol/Proof 담당 | 별도 공동저자 1인 이상 |
| 최종 보안·성능 주장 | 전체 공동저자 | 전체 공동저자 |

Proof 작성자가 단독으로 최종 soundness를 승인하지 않는다. 실험 수치를 작성한 사람과 raw evidence를 확인한 사람도 가능하면 분리한다.

## 8. Rebuttal 약속 추적

| 약속 | 단계 | 최종 근거 | 상태 |
|---|---:|---|---|
| Freivalds baseline의 역할과 SOTA가 아님을 명시 | 1 | Sec. 7 비교 문단 | READY |
| zkMatrix/DualMatrix/zkMaP positioning과 comparison table | 1, 3 | Sec. 2/7 diff와 출처 | IN PROGRESS |
| Original-matrix variant와 model-commitment 범위 | 1 | Construction/limitation diff | READY |
| Public-coin theorem, FS future-work 한정 및 setup 설명 | 1, 3 | Sec. 6/7/Appendix diff | IN PROGRESS |
| 기존 수치의 provenance와 GPT-2/`196 B` 설명 | 1, 3 | protocol-version 표기, raw evidence와 최종 표 | IN PROGRESS |
| 수정 LAMP--DualMatrix 실험 방법·조건·결과 | 2, 3 | raw logs, 환경, Sec. 7 diff | TODO |
| $A/C$ folding과 independent $B$ test | 2, 3 | code, construction/theorem diff | READY |
| Proximity radius, cited gap bound, extraction 및 full proof | 3 | Sec. 6와 Appendix | READY |
| Repetitions, memory 및 encoding-time accounting | 2, 3 | raw CSV와 Sec. 7 diff | READY |
| 문단·참고문헌·표기·오탈자 수정 | 1 | 전역 검색과 전체 diff | READY |

상태는 `TODO`, `IN PROGRESS`, `READY`, `VERIFIED`만 사용한다. 논문 diff와 proof/data evidence가 모두 준비된 뒤에만 `VERIFIED`로 변경한다.

## 9. Definition of Done

- [x] 1단계의 실험 비의존 수정이 완료됨
- [ ] Compact transcript, relation figures, theorem 및 구현 transcript의
  challenge/commit/query 순서가 동일함
- [x] $A/C$ folding과 독립 $B$ test가 construction, implementation 및 proof에 반영됨
- [x] Revised theorem과 full proof가 미검증 valid-codeword assumption 없이 soundness를 분석함
- [ ] Failure bound의 $t$, code rate, $\tau$ 및 목표 security level이 구현과 일치함
- [ ] 수정 LAMP의 성능 수치가 추가 $B$ 검사를 포함한 raw log로 재현됨
- [ ] 수정 LAMP--DualMatrix 결과와 네 기법의 comparison table이 Section 7에 포함됨
- [ ] 모든 직접 수치가 raw evidence에 연결되고 비교 범위 차이가 명시됨
- [ ] Abstract부터 Conclusion까지 수치와 claim scope가 일치함
- [ ] `Rebuttal_EN.md`의 모든 미래형 약속이 revised PDF와 diff PDF에서 확인됨
- [ ] pdfLaTeX clean build와 diff PDF 생성이 성공함
- [ ] 본문 $\le 13$페이지, References+Appendix $\le 5$페이지, 전체
  $\le 18$페이지이고 IEEE S&P 2027 형식을 유지함
- [ ] 전체 공동저자가 보안·성능 주장과 제출 파일을 승인함
- [ ] HotCRP 업로드 후 재다운로드한 두 PDF를 검증함
