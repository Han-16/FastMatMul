# IEEE S&P 2027 Post-Rebuttal Action Plan

## 1. 목적과 기준

이 문서는 text rebuttal 제출 이후부터 2026년 9월 3일 수정 원고 제출까지 수행할 작업만 관리한다. 기존 `Plan.md`의 rebuttal 작성 과정과 아직 결정되지 않았던 여러 대안은 제거하고, 공동저자가 합의한 수정 방향만 남긴다.

- **공식 제출물:** revised paper PDF와 submitted version 대비 diff PDF
- **공식 마감:** 2026년 9월 3일, HotCRP에 표시되는 시각 기준
- **내부 마감:** 2026년 9월 2일 18:00 KST
- **원본 기준:** `origin/snp-2027-제출버전`, `Paper/main-submitted.pdf`
- **수정 작업본:** `main` 브랜치, `Contents/`, `Paper/main.tex`
- **원칙:** 9월 3일에는 본문·증명·실험을 새로 고치지 않고 업로드와 재다운로드 검증만 수행한다.

`Paper/main-submitted.pdf`와 제출 버전 브랜치는 수정하지 않는다. 모든 성능 수치와 보안 주장은 수정된 protocol, theorem, implementation 및 raw log 중 적어도 하나와 추적 가능해야 한다.

## 2. 확정된 protocol 수정 방향

### 2.1 Input-encoding validity

수정본에서는 다음 하나의 설계만 사용한다.

1. $A$와 $C$에는 기존 structured challenge

   \[
   \mathbf v(r)=(1,r,\ldots,r^{k-1})
   \]

   로 생성되는 fold를 유지한다. 이 structured random-folding 성질은 별도 lemma를 추가하지 않고 revised theorem의 soundness argument에서 직접 사용한다.
2. $B$에는 $\mathbf x=\mathbf v(r)A$를 계수로 사용하는 기존 검사와 별개로, 독립적인 uniform challenge

   \[
   \mathbf s\sample\mathbb F^k
   \]

   를 추가한다.
3. Prover는

   \[
   \mathbf b_s=\mathbf s B,
   \qquad
   \widehat{\mathbf b}_s=\mathsf{Enc}(\mathbf b_s)
   \]

   를 계산하고 query positions가 선택되기 전에 원본 벡터와 encoded view를 commitment로 고정한다.
4. Circuit은 `EncCheck`로 $\widehat{\mathbf b}_s$와 $\mathbf b_s$의 encoding consistency를 검사하고, 각 $j\in I$에 대해

   \[
   \widehat{\mathbf b}_s[j]
   =
   \langle\mathbf s,\widehat B[*,j]\rangle
   \]

   을 검사한다.

Certified encoder를 우선안으로 두는 이전 계획과 $A,B,C$ 모두에 새로운 full-uniform challenge를 추가하는 대안은 이번 수정본의 active path가 아니다. 다시 사용해야 할 경우에는 공동저자 전원의 명시적 결정과 rebuttal/논문 문구의 동시 수정이 필요하다.

### 2.2 Transcript와 binding 순서

논문의 protocol figure, theorem 및 구현은 다음 순서를 동일하게 표현해야 한다.

1. Prover가 $\rt_{ABC}$를 고정한다.
2. Verifier가 $r$과 $\mathbf s$를 독립적으로 생성한다.
3. Prover가 $\mathbf x,\mathbf y,\mathbf z,\mathbf b_s$ 및 각 encoded view를 계산한다.
4. Prover가 이 원본 벡터들과 encoded views를 binding commitment로 고정하고, 이후 CP-SNARK가 바로 그 committed values를 사용하도록 연결한다.
5. 그 뒤에만 verifier가 query tuple $I$와 code-check points $\alpha_x,\alpha_y,\alpha_z,\alpha_B$를 생성한다.
6. Prover가 CP-SNARK proof, sampled openings 및 CP-Link proofs를 생성한다.

현재 구현이 이 순서를 보장한다는 사실을 Construction의 statement/witness 정의와 protocol figure에 명시한다. 특히 honest-prover algorithm의 계산 순서만 설명하지 말고, malicious prover도 $I,\alpha$ 이후 commitment에 사용된 값을 바꿀 수 없다는 binding 관계를 theorem의 전제로 정확히 적는다.

### 2.3 보안 범위

- Formal theorem은 **public-coin interactive protocol**만 다룬다.
- 구현된 multi-round Fiat--Shamir transform의 정식 ROM 분석은 future work로 제한한다.
- Verifier가 $\rt_{ABC}$가 의도한 model weights에 대한 commitment임을 확인하는 문제는 별도의 application-level issue로 구분한다.
- Original matrices가 같은 SNARK circuit의 다른 relation에도 사용된다면 full-matrix commit-carrying SNARK variant와 그 $O(k^2)$ witness-commitment cost를 명시한다.
- “linear”은 전체 prover time이 아니라 fixed $t$에서의 핵심 in-circuit constraint complexity를 의미한다.

## 3. 추가 $B$ 검사의 비용 분석

추가 검사는 LAMP의 전체 asymptotic prover complexity를 바꾸지는 않지만 다음 비용을 더한다.

| 항목 | 추가 비용 | 논문에 명시할 범위 |
|---|---:|---|
| $\mathbf b_s=\mathbf sB$ | $O(k^2)$ field operations | 서킷 밖 native prover work |
| $\mathbf b_s$ encoding | 실제 encoder 비용 $E_{\mathsf{enc}}(k,n)$ | 사용한 구현 경로와 timer 범위 |
| Encoded-vector commitment | 현재 packing 방식에 따른 $O(n)$ 수준의 추가 group/hash work | 기존 root 확장인지 별도 root인지 구분 |
| Sampled $B$ fold | $O(tk)$ constraints | 서킷 내부 |
| 추가 `EncCheck` | $E_{\mathsf{code}}(k,n)$ constraints | 서킷 내부 |
| Setup/link | 변경된 circuit와 message layout에 따른 새 setup | Groth16 및 QALink configuration 명시 |

기존에도 $\mathbf v(r)A$, $\mathbf xB$, $\mathbf v(r)C$ 등의 native computation과 input encoding/commitment가 $O(k^2)$이므로 전체 prover-side asymptotic complexity는 $O(k^2)$로 유지된다. Fixed $t$와 fixed code rate에서는 추가 circuit cost도 선형이지만 상수 배 증가는 숨기지 않는다.

같은 연산을 `b_s` 계산과 encoded-row fold 양쪽에서 중복 계상하지 않는다. 실제 구현이 `b_s`를 먼저 계산한 뒤 encoding하는지, $\mathbf s\widehat B$를 직접 계산하는지를 확인하고 측정표에 실제 경로만 기록한다.

## 4. Reviewer concern 추적표

| Reviewer concern | 수정 내용 | 대상 위치 | 완료 증거 | 담당 |
|---|---|---|---|---|
| 기존 연구 대비 위치가 불명확함 | LAMP, zkMatrix, DualMatrix, zkMaP의 statement와 비용 모델을 직접 비교하고 범용 code-based/zkML systems와 scope 차이를 설명 | Sec. 2, Sec. 7 | 출처가 연결된 비교표와 문단 | 이경태 |
| 관련 연구와 실험 비교가 없음 | 재현 가능한 DualMatrix 결과를 조건·한계와 함께 추가하거나, 근거가 부족하면 complexity 비교만 제시 | Sec. 7 | raw log, commit hash, 실행 명령, 환경 | 한병규/이경태 |
| $\widehat A,\widehat B,\widehat C$ validity가 불명확함 | $A/C$ structured folding argument, 독립 $B$ test, extraction/composition theorem 추가 | Sec. 4--6, Appendix | 공동저자가 승인한 full proof | Protocol/Proof 담당 |
| Original matrices를 circuit에서 사용할 때의 비용 | full-matrix commit-carrying variant, $O(k^2)$ witness-commitment 비용, AI weights/activations 예시와 model-commitment 확인 범위 설명 | Sec. 5 또는 limitation, Sec. 7 | 명시적 construction과 비용식 | 이경태 |
| Theorem 6.2 proof가 짧음 | 수정 protocol에 대한 detailed proof 제공 | Sec. 6, Appendix | proof checklist 통과 | Protocol/Proof 담당 |
| Fiat--Shamir와 setup 설명 부족 | interactive theorem과 implemented FS 범위를 분리하고 Groth16/QALink setup 의존성 설명 | Sec. 6--7, Appendix | section 간 주장 충돌 없음 | 이경태/Protocol 담당 |
| 수치·표현 불일치 | `0.06 s`, `8.43x`, `1.77x`, $O(tk+E_{\mathsf{code}})$, $E_{\mathsf{link}}(k,t)$, GPT-2 trade-off, `196 B` 설명을 전역 점검 | Abstract, Intro, Sec. 5, Sec. 7, Conclusion | 전역 검색과 표 재계산 | 이경태 |
| Encoding·통계·memory 보고 부족 | timer 범위, 반복 횟수, 분산 또는 범위, 대표 peak RSS를 기록 | Sec. 7, artifact | raw CSV/log에서 재생성 가능 | 한병규 |
| 오탈자·표기 문제 | 중복 Brakedown 참고문헌, index convention 및 review에 열거된 오탈자 수정 | 전체 원고 | diff 검토 | 이경태 |

## 5. Protocol과 soundness 작업

### 5.1 Construction 수정

- $\mathbf s,\mathbf b_s,\widehat{\mathbf b}_s,\alpha_B$를 statement, witness, commitment layout 및 protocol figure에 추가한다.
- `b_s`를 기존 intermediate root에 packing할지 별도 root로 둘지 구현과 동일하게 명시한다.
- $\mathbf x,\mathbf y,\mathbf z,\mathbf b_s$와 full encoded views가 $I,\alpha$ 전에 고정되는 commitment를 정확히 열거한다.
- CP-SNARK witness commitment, external commitments, Merkle leaves 및 CP-Link가 어떤 값을 연결하는지 타입과 순서를 맞춘다.
- Fiat--Shamir 구현에서는 각 challenge의 domain separation과 입력 transcript를 표로 정리한다. Formal theorem은 interactive protocol에만 적용한다.

### 5.2 필요한 proof components

1. **Structured $A/C$ folding argument:** $\mathbf v(r)$로 만든 fold의 표준 random-folding 성질을 revised theorem의 soundness proof에 직접 적용한다.
2. **Uniform $B$ proximity lemma:** 독립적인 $\mathbf s\sample\mathbb F^k$가 $\widehat B$의 숨겨진 malformed component를 검출하고 decoded $B$를 추출할 수 있음을 증명한다.
3. **Pre-query binding lemma:** EncCheck와 sampled equations에 사용되는 원본/encoded intermediate values가 query 전에 고정되고 실제 circuit witness와 동일함을 증명한다.
4. **Composition lemma:** 추출된 $A,B,C$, structured Freivalds check, sampled equations 및 backend soundness를 합성한다.

Code distance $\delta_{\mathcal C}$, proximity radius $\tau$, effective sampled gap 등 서로 다른 파라미터를 하나의 $\delta$로 혼용하지 않는다. 기존 $4(1-\delta)^t$ 항을 그대로 재사용하지 말고 revised proof에서 failure bound와 union-bound 상수를 다시 계산한다. 그 결과에 따라 $t=128$이 목표 security level에 충분한지 재검증하고, 필요하면 $t$와 실험을 함께 갱신한다.

### 5.3 Revised theorem 완료 조건

- Exact valid-codeword assumption을 몰래 유지하지 않고, proximity test로부터 추출되는 decoded $A,B,C$에 대해 statement를 정의한다.
- Backend failure, code consistency, $A/C$ structured test, $B$ uniform test, Freivalds 및 sampling error를 각각 표시한다.
- 전체 오류확률과 parameter instantiation을 수치로 확인한다.
- $A=0$, $C=0$, rank-deficient $A$, 일부 row/symbol이 malformed인 경우를 공격 테스트로 검토한다.
- 동일한 $r$을 $A/C$ proximity와 Freivalds에 사용하는 conditioning이 정당함을 확인한다.
- Protocol 작성자 외 공동저자 한 명이 theorem statement와 full proof를 독립 검토한다.

## 6. 구현과 실험 작업

### 6.1 구현

- $\mathbf s$ 생성, $\mathbf b_s$ 계산, encoding 및 commitment를 구현한다.
- `EncCheck`와 sampled $B$-fold equation을 circuit에 추가한다.
- Commitment/root packing, sampled openings, CP-Link statement 및 proof serialization을 수정한다.
- 변경된 circuit와 block length에 맞춰 Groth16/QALink setup을 다시 생성한다.
- 다음 회귀 테스트를 추가한다.
  - 올바른 $AB=C$ witness는 accept한다.
  - $A=0$ 또는 rank-deficient $A$에서도 malformed $B$는 reject한다.
  - Commitment 뒤 $B$, $\mathbf b_s$ 또는 encoded view를 바꾸면 reject한다.
  - $\mathbf s$는 $\rt_{ABC}$ 이후, $I$ 이전에 고정된다.
  - $\mathbf x,\mathbf y,\mathbf z$와 encoded views의 기존 pre-query binding 경로가 유지된다.

### 6.2 측정 규격

각 raw log/CSV에 다음을 기록한다.

- `k`, `t`, code rate, field/curve, security setting
- code commit hash, 실행 명령, seed, `run_id`
- constraints, setup/prove/verify time, serialized proof bytes
- $\mathbf sB$, encoding, commitment, Merkle, Groth16, CP-Link component time
- peak RSS, success/OOM/timeout 및 exit status
- $C=AB$ 생성 비용과 setup을 total에 포함했는지 여부

수정 LAMP는 최소 `k=1024`와 대표 대형 지점 하나를 각각 3회 측정한다. 현재의 “every tested size from `k=128` to `k=8192`” 주장을 유지하려면 전체 범위를 같은 수정 protocol로 다시 측정한다. 기존 pre-$B$ 결과와 revised 결과를 같은 표에서 최종 protocol 수치처럼 혼합하지 않는다.

### 6.3 DualMatrix 비교

직접 수치를 유지하려면 다음 근거가 있어야 한다.

- 공개 저장소 URL과 정확한 commit hash
- build profile과 실행 명령
- curve/security parameters, dense-input 생성 방식과 seed
- CPU/RAM/thread 수
- 각 인용 지점의 원시 출력과 반복 통계
- LAMP와 statement, setup, proof contents가 다른 지점

특히 `k=1024`의 `19.06 s`, `0.15 s`, `88,844 B`는 raw evidence에 연결한다. 근거를 확보하지 못하면 해당 직접 수치와 “모든 크기에서 우수” 주장을 제거하고 asymptotic comparison만 남긴다.

### 6.4 GPT-2와 기존 결과

- 가능하면 추가 $B$ 검사를 포함해 GPT-2 workload를 재측정한다.
- 재측정하지 못하면 기존 결과를 pre-$B$ implementation case study로 명확히 제한하고 revised-protocol 성능 근거로 사용하지 않는다.
- Proving 개선뿐 아니라 verifier time과 proof-size 증가를 Abstract, Evaluation 및 Conclusion에서 함께 보고한다.
- Freivalds baseline을 state of the art가 아니라 동일 backend에서 reduction 효과를 분리하는 baseline으로 설명한다.

## 7. 논문 통합 작업

| 위치 | 필수 수정 |
|---|---|
| Abstract | revised scope와 실제 수치만 유지하고 “linear”을 constraint count로 한정 |
| Introduction | $O(k^3)$/$O(k^2)$, proximity, code distance 직관 및 기여 범위 보강 |
| Related Work | matrix-specific comparison table과 범용 code/zkML systems의 scope 차이 설명 |
| Technical Overview | 독립 $B$ challenge의 필요성과 새 consistency chain 설명 |
| Construction | transcript, commitments, relation, figure, 비용식 전면 일치 |
| Security Analysis | revised theorem, 명시적 error terms, interactive scope |
| Evaluation | revised 결과, DualMatrix 근거, encoding accounting, 통계·memory, `196 B` 설명 |
| Conclusion | prover/circuit 이점과 verifier/proof/setup 비용을 함께 요약 |
| Appendix | A/C folding argument, B lemma, full composition proof, FS claim 축소, setup 세부사항 |

비교표는 LAMP, zkMatrix, DualMatrix, zkMaP에 집중한다. Ligero, Brakedown, Blaze, Orion과 zkCNN, zkGPT, zkLLM은 동일한 end-to-end benchmark처럼 취급하지 않고 statement와 scope 차이를 prose로 설명한다.

## 8. 일정과 결정 게이트

| 날짜 | 필수 산출물 | Gate |
|---|---|---|
| **8/28** | protocol transcript와 commitment layout 동결, 역할 배정, reproducible build 방법 확인 | G0: 구현·논문·theorem의 순서가 일치해야 함 |
| **8/29** | Construction/figure/relation 초안, lemma/theorem skeleton, $B$-test smoke run, comparison table 초안 | G1: `k=1024` proof 생성·검증 성공 |
| **8/30** | B lemma와 revised theorem 1차본, `k=1024` 3회 raw log, 비용 재계산 | G2: 근거 없는 수치·주장을 즉시 제거 |
| **8/31** | full proof, 대표 대형 실험, Sec. 2/4/5/6/7/Appendix 통합 | G3: protocol과 proof 내용 동결 |
| **9/1** | 전체 실험·parameter 확정, 공동저자 technical review, rebuttal 약속과 diff 대조 | G4: 주장과 데이터 동결 |
| **9/2** | clean PDF, diff PDF, 독립 열람, HotCRP 사전 업로드 | G5: 내부 제출 완료 |
| **9/3** | 업로드 파일 재다운로드·열람 및 제출 상태 확인 | 실질적 내용 수정 금지 |

G1 또는 G2가 지연되면 실험 범위를 대표 지점으로 축소하고 전체 범위 우위나 revised GPT-2 수치를 주장하지 않는다. G3까지 full soundness proof가 검토되지 않으면 unconditional input-validity 주장을 유지하지 말고 공동저자와 더 제한적인 theorem 및 HotCRP 후속 설명을 즉시 결정한다.

## 9. 역할 분담

| 역할 | 책임자 | 승인자 |
|---|---|---|
| Paper integration, related work, 표현·수치 정리, build/diff/submission | 이경태 | 전체 공동저자 |
| Protocol implementation, regression tests, revised experiments | 한병규 | Protocol 공동저자 |
| Soundness lemma와 theorem | Protocol 담당 공동저자 | 별도 공동저자 1인 이상 |
| 최종 보안·성능 주장 | 전체 공동저자 | 전체 공동저자 |

각 산출물에는 작성자와 승인자를 분리한다. Proof 작성자가 혼자 최종 soundness 승인을 하지 않는다.

## 10. Rebuttal 약속 추적

Text rebuttal의 각 미래형 약속을 최종 diff와 연결한다.

| Rebuttal promise | 최종 근거 | 상태 |
|---|---|---|
| Related-work positioning과 comparison table | Sec. 2/7 diff, 출처표 | TODO |
| DualMatrix 비교 및 비교 불가능성 설명 | raw logs, 환경, Sec. 7 diff | TODO |
| A/C structured folding argument | theorem/appendix diff | TODO |
| Independent $B$ test | construction, code commit, experiment log | TODO |
| Revised proximity/extraction theorem | Sec. 6와 full appendix proof | TODO |
| Full-matrix commit-carrying variant와 model-commitment 범위 | construction/limitation diff | TODO |
| Interactive-only theorem과 setup 설명 | Sec. 6/7/Appendix diff | TODO |
| 수치 수정, GPT-2 trade-off, `196 B` 설명 | 전역 검색, 표 재계산 | IN PROGRESS |
| Encoding accounting, repetitions, variance/memory | raw CSV와 Sec. 7 diff | TODO |

상태는 `TODO`, `IN PROGRESS`, `READY`, `VERIFIED`만 사용한다. 논문 diff와 proof/data evidence가 모두 준비된 뒤에만 `VERIFIED`로 변경한다.

## 11. Build, diff 및 제출

- `Paper/main.tex`, root `Contents/`, `Paper/Styles/`를 사용하는 하나의 재현 가능한 pdfLaTeX/BibTeX build 명령을 고정한다.
- Clean environment에서 pdfLaTeX, BibTeX, pdfLaTeX 두 번을 실행하고 unresolved reference/citation과 overfull box를 확인한다.
- 제출본 기준 PDF는 `Paper/main-submitted.pdf`로 보존한다.
- Submitted source와 revised source의 diff PDF를 생성하고 모든 rebuttal 약속이 diff에서 보이는지 확인한다.
- 표·그림의 page overflow, 익명성, artifact URL, 참고문헌 및 페이지 제한을 확인한다.
- HotCRP에 revised PDF와 diff PDF를 업로드한 뒤 다시 내려받아 각각 열어본다.
- 최종 commit hash와 업로드한 파일의 해시를 내부 기록에 남긴다.

## 12. Definition of Done

- [ ] Reviewer primary asks가 모두 논문 section 및 diff와 연결됨
- [ ] $A/C$ structured folding argument와 독립 $B$ test만 active input-validity 설계로 사용됨
- [ ] Protocol figure, theorem, implementation transcript의 challenge/commit/query 순서가 동일함
- [ ] $\mathbf x,\mathbf y,\mathbf z,\mathbf b_s$ 및 encoded views의 pre-query binding과 CP witness linkage가 명시됨
- [ ] Revised theorem과 full proof가 exact-codeword assumption 없이 추출된 $A,B,C$의 relation을 분석함
- [ ] Failure bound, $t$, code rate 및 목표 security level이 일치함
- [ ] 추가 $O(k^2)$ native work, linear circuit cost, setup과 proof-size 변화가 모두 반영됨
- [ ] 모든 revised 성능 수치가 추가 $B$ 검사를 포함한 raw log로 재현됨
- [ ] DualMatrix 직접 수치가 raw evidence에 연결되거나 최종 원고에서 제거됨
- [ ] Abstract부터 Conclusion까지 수치와 scope가 일치함
- [ ] pdfLaTeX clean build와 diff PDF 생성이 성공함
- [ ] 전체 공동저자가 보안·성능 주장과 최종 제출 파일을 승인함
- [ ] HotCRP 업로드 후 재다운로드한 PDF 두 개를 검증함
