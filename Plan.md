# IEEE S&P 2027 Interactive Rebuttal 계획

## 1. 목표와 제출물

이번 rebuttal의 목표는 새로운 기여를 과장하는 것이 아니라, 현재 원고에서 불명확한 보안 보장과 기존 연구 대비 위치를 정확히 밝히고 핵심 주장을 측정 결과와 일치시키는 것이다.

필수 제출물은 다음 두 가지이다.

1. **Text rebuttal**: 2026년 8월 27일까지, 최대 750단어
2. **수정 논문과 diff**: 2026년 9월 3일까지

내부 마감은 공식 마감보다 하루 빠른 **8월 26일**과 **9월 2일**로 정한다. HotCRP의 시간대와 업로드 문제를 고려하여 공식 마감 당일 제출은 피한다.

## 2. 최우선 과제

### P0. 커밋된 행렬 인코딩의 유효성

가장 먼저 다음 질문에 명확하게 답해야 한다.

> 프로토콜은 커밋된 \(\widehat A,\widehat B,\widehat C\)가 실제로 코드 \(\mathcal C\)의 유효한 codeword임을 어디에서 보장하는가?

작업 순서는 다음과 같다.

- Theorem 6.2의 statement와 proof에서 사용하는 가정을 모두 열거한다.
- Figure 1 및 offline/online relation에서 \(\widehat A,\widehat B,\widehat C\)에 적용되는 검사를 추적한다.
- `EncCheck`가 \(\widehat x,\widehat y,\widehat z\)에만 적용되는 이유와 fold argument가 요구하는 전제조건을 확인한다.
- commitment root가 고정된 encoded words에만 binding하는지, 원본 행렬과 그 올바른 인코딩 관계에도 binding하는지 구분한다.
- 기존 프로토콜이 이미 유효성을 보장한다면 해당 단계와 lemma를 본문에서 명시적으로 연결한다.
- 보장이 없다면 필요한 검사 또는 입력 statement의 변경을 설계하고, soundness와 prover/verifier/constraint complexity를 다시 계산한다.
- 해결할 수 없는 가정을 숨기지 말고 security claim의 정확한 적용 범위를 명시한다.

**완료 조건:** 공동저자 전원이 동의하는 한 문단짜리 직접 답변, 수정된 theorem statement, 필요한 경우 보완된 proof가 준비되어야 한다.

### P0. 기존 연구와의 비교

Section 2와 Section 7을 함께 보강한다. 최소 비교 대상은 다음 범주를 포함한다.

- committed matrix multiplication: zkMatrix, zkMaP
- code-based proof systems: Ligero, Brakedown, Blaze, Orion
- neural-network proof systems: zkCNN, zkGPT, zkLLM
- baseline: direct circuit 및 Freivalds-in-SNARK

다음 열을 포함하는 비교표를 작성한다.

| 항목 | 비교 내용 |
|---|---|
| Statement | 각 기법이 실제로 증명하는 관계 |
| Prover cost | 산술 연산, group operation, encoding 및 commitment 비용 |
| Circuit/constraint cost | 행렬 크기와 보안 파라미터에 대한 점근식 |
| Verifier cost | circuit 내부 및 외부 검증 비용 |
| Proof size | 점근식과 보고된 실제 크기 |
| Setup | transparent/universal/per-circuit setup 여부 |
| Assumptions | pairing, random oracle, code proximity 등 |
| Input model | committed/encoded/original matrix 사용 방식 |
| Implementation | 공개 구현과 재현 가능한 benchmark 존재 여부 |

실측 비교는 다음 원칙을 따른다.

- 실행 가능한 공개 구현이 있다면 최소 한 기법과 동일하거나 최대한 유사한 환경에서 비교한다.
- 하드웨어, security level, curve, statement가 다르면 실행시간을 직접적인 우열로 제시하지 않는다.
- 재현이 불가능하면 그 기술적 이유를 구체적으로 설명하고 complexity 표를 최소 결과로 제공한다.
- Freivalds baseline을 대표적인 state of the art처럼 표현하지 않는다.

**완료 조건:** Section 2에 개념적 차이가 설명되고, Section 7에 정량 표 또는 비교 불가능성에 대한 근거 있는 설명이 포함되어야 한다.

## 3. 보안 모델 보강

### 3.1 Interactive protocol과 Fiat--Shamir

- 두 challenge가 생성되는 정확한 transcript 순서를 명시한다.
- 각 challenge가 이전 commitment 전체에 domain-separated hash로 의존하는지 확인한다.
- multi-round Fiat--Shamir 변환에 적용할 수 있는 정리와 요구 조건을 확인한다.
- 완전한 증명을 제공하지 못하면, 증명된 interactive protocol과 구현된 non-interactive heuristic의 보안 범위를 구분한다.

### 3.2 Trusted setup

- Groth16과 CP/QALink가 요구하는 CRS 및 trapdoor를 정리한다.
- \(t\), block length 또는 circuit configuration 변경 시 새로운 setup이 필요한지 명시한다.
- setup time과 CRS size를 측정하거나, 측정할 수 없다면 배포상 한계로 논의한다.

### 3.3 Committed input의 출처와 활용

- \(rt_{ABC}\)가 보장하는 사실과 보장하지 않는 사실을 분리한다.
- AI 응용에서 verifier가 올바른 model weight commitment를 신뢰하는 방법은 별도의 provenance 문제임을 명시한다.
- 원본 행렬을 다른 SNARK circuit에서 다시 사용해야 할 때 encoded commitment와 원본 witness를 연결하는 방법과 추가 비용을 분석한다.

## 4. 실험 및 주장 정리

다음 불일치를 수정하고 논문 전체에서 동일한 수치를 사용한다.

- verification time: `0.01 s` 주장과 표의 `0.06 s` 불일치
- proving-time improvement: `8.34x`와 `8.43x` 불일치
- GPT-2 proving-time improvement: `1.78x`와 `1.77x` 불일치
- constraint complexity: \(O(tk)\)와 \(O(tk+E_{\mathrm{code}})\)의 사용 범위
- link cost 표기: \(E_{\mathrm{link}}(k)\)와 \(E_{\mathrm{link}}(k,t)\)

GPT-2 결과는 prover 성능만 강조하지 않고 다음 trade-off를 함께 설명한다.

- verifier time 증가
- proof size 증가
- 어느 응용 환경에서 prover 절감이 이러한 비용을 정당화하는지

추가 실험 및 보고 항목은 다음과 같다.

- 반복 횟수, 평균/중앙값, 표준편차 또는 범위
- peak memory 사용량
- setup time과 CRS size
- Table 3에서 encoding cost가 어느 열에 포함되는지
- matrix size 증가에 따라 commitment cost가 지배적으로 변하는 현상
- 점근적 constraint 개선과 실제 prover-time scaling의 차이

## 5. 증명 및 서술 보강

- Theorem 6.2의 full proof를 appendix에 제공하거나 proof sketch를 충분히 확장한다.
- Introduction에서 \(O(k^3)\), Freivalds의 \(O(k^2)\), proximity testing, code distance \(\delta\)에 대한 직관을 먼저 제공한다.
- “linear verification”이 verifier wall-clock time이 아니라 핵심 relation의 constraint complexity를 의미한다는 점을 명확히 한다.
- proof size가 Freivalds보다 커지는 이유를 Section 7에서 설명한다.
- Figure 2와 offline relation 설명을 Section 5.4의 적절한 위치로 이동한다.
- 중복된 Brakedown 참고문헌을 병합한다.
- \([n]\)과 \(i=1,\ldots,n\) 표기를 일관되게 수정한다.
- 알려진 오탈자와 문법 오류를 전수 점검한다.

## 6. Text rebuttal 구성

최종 답변은 **650--700단어**를 목표로 하고 절대 750단어를 넘기지 않는다. 다음 구조를 사용한다.

1. **Related-work positioning:** LAMP의 statement와 비용 모델이 기존 기법과 어떻게 다른지 설명하고 추가할 비교표/실험을 명시한다.
2. **Validity of encoded matrices:** 유효성이 보장되는 정확한 위치를 설명하거나 보완안을 명시한다.
3. **Original-to-encoded bridge:** 원본 행렬을 다른 circuit에서 사용할 때의 연결 방식과 비용을 답한다.
4. **Security scope:** multi-round Fiat--Shamir와 trusted setup에 추가할 설명을 명시한다.
5. **Measurements and corrections:** 수치 오류를 인정하고 GPT-2의 verifier/proof-size trade-off를 포함해 수정한다고 답한다.

작성 원칙은 다음과 같다.

- 리뷰 내용을 길게 반복하지 않고 질문에 직접 답한다.
- 방어적인 표현이나 reviewer의 전문성을 문제 삼는 표현을 사용하지 않는다.
- 현재 원고에 없는 결과를 이미 존재하는 것처럼 말하지 않는다.
- 수정 약속은 section, table, theorem 단위로 구체화한다.
- 단어 수는 HotCRP 표시와 별도의 로컬 count를 모두 확인한다.

## 7. 일정

| 날짜 | 작업 | 산출물 |
|---|---|---|
| 8월 21일 | 이슈 정리 및 역할 분담 | 본 계획, 담당자 목록 |
| 8월 22일 | encoding validity와 soundness 집중 검토 | security 답변 초안, 필요한 protocol 수정안 |
| 8월 23일 | 관련 연구 원문 및 artifact 조사 | 비교표 초안, benchmark 가능성 판단 |
| 8월 24일 | 비교 실험 또는 complexity 분석 완료 | Section 2/7용 표와 결과 |
| 8월 25일 | rebuttal 및 수정 원고 1차 통합 | 750단어 이하 초안, 수정 PDF |
| 8월 26일 | 공동저자 최종 검토 및 text rebuttal 제출 | 최종 text rebuttal |
| 8월 27일 | 공식 text rebuttal 마감 및 추가 질문 확인 | 제출 상태 확인 |
| 8월 28일--9월 1일 | proof, evaluation, presentation 수정 및 전체 검수 | 수정 원고, 실험 로그 |
| 9월 2일 | 최종 PDF와 diff 사전 제출 | revised PDF, diff PDF |
| 9월 3일 | 공식 수정본 마감 및 업로드 확인 | 제출 완료 확인 |

## 8. 제출 전 체크리스트

### Text rebuttal

- [ ] 750단어 이하이며 HotCRP에 빨간색 초과 단어가 없음
- [ ] 관련 연구 비교 질문에 직접 답함
- [ ] encoded matrix validity에 직접 답함
- [ ] original/encoded matrix 연결 비용에 답함
- [ ] 잘못된 수치와 trade-off를 인정하고 수정 내용을 명시함
- [ ] 모든 공동저자가 보안 관련 답변에 동의함

### 수정 논문

- [ ] Section 2 비교 논의 확장
- [ ] Section 7 비교표 또는 benchmark 추가
- [ ] Theorem 6.2와 proof 보강
- [ ] Fiat--Shamir 보안 범위 명시
- [ ] trusted setup 논의 추가
- [ ] GPT-2의 verifier/proof-size trade-off 반영
- [ ] 수치, 표기, 참고문헌, 오탈자 정정
- [ ] pdfLaTeX 컴파일 성공
- [ ] 표와 그림이 페이지 경계를 넘지 않음
- [ ] 익명성 및 제출 형식 준수

### Diff와 제출

- [ ] 변경된 부분이 명확히 보이는 diff PDF 생성
- [ ] diff가 특정 요청에 집중되어 있고 불필요한 전면 개정이 아님
- [ ] revised PDF와 diff PDF를 별도 환경에서 열어 확인
- [ ] HotCRP 업로드 후 내려받은 파일을 다시 확인
- [ ] 추가 review/comment가 도착했는지 매일 확인

## 9. 의사결정 원칙

- **Soundness가 우선이다.** 성능 비교보다 protocol statement와 proof의 일치 여부를 먼저 확정한다.
- **비교는 공정해야 한다.** 서로 다른 statement나 환경의 수치를 같은 조건처럼 제시하지 않는다.
- **불리한 결과도 숨기지 않는다.** verifier time, proof size, setup, commitment bottleneck을 포함해 전체 trade-off를 설명한다.
- **주장은 증거 수준에 맞춘다.** 증명하지 못한 non-interactive security나 측정하지 않은 성능은 제한사항으로 명시한다.
- **수정 범위를 통제한다.** interactive rebuttal에서 요청된 핵심 항목에 집중하고 논문 전체를 불필요하게 다시 쓰지 않는다.
