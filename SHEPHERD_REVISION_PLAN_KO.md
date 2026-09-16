# 9월 21일 Shepherd 수정 계획 — 내부 검토안

- 작성일: **2026년 9월 16일**
- 대상: S&P 2027 논문 #1646, LAMP
- 상태: **공동저자 검토용 초안. HotCRP에 전송하지 않음.**
- 역할: AE 준비는 동료가 담당한다. 우리는 메타리뷰 대응과 원고 수정 계획에 집중한다.
- 제출용 영문: [SHEPHERD_MESSAGE_EN.md](/Users/kyeongtae/Project/LAMP/SHEPHERD_MESSAGE_EN.md)

## 1. 이번 연락의 목적

**9/21까지 수정 방향을 shepherd에게 전달하고, 남은 비교 평가 우려를 해소할 수 있는 보완 범위를 협의한다.** 합격 이메일이 요구한 이 시점의 행동은 proposed changes 또는 “No changes”의 전달이다. 추가 실험과 수정 PDF 전체가 이날까지 완료돼야 한다는 지시는 이메일에 없다. 이후 별도 요청이 있으면 일정을 반영한다. [합격 이메일](/Users/kyeongtae/.codex/attachments/7329cc08-eaf6-4b9d-9e0e-2d59447fc917/pasted-text.txt)

대상은 최종 메타리뷰의 Noteworthy Concern 1이다.

> While DualMatrix is the only relevant prior work with available code, it is not state of the art when it comes to a performance comparison.

우리는 **수정 후 해당 우려의 재검토를 요청**하는 방향을 제안한다. 수정 계획 단계에서는 특정 우려의 삭제를 확정하지 않고, 최종 수정본의 근거에 따라 문구 변경을 요청한다.

## 2. 현재 원고에서 이미 한 일

| 위치 | 이미 반영된 내용 | 이번 수정에서 추가할 내용 |
|---|---|---|
| Section 2, Table 1 | zkMatrix·DualMatrix·zkMaP 등의 이론적 복잡도 비교 | 추가 관련 기법, 비교 모델과 비용 기준, 구현 가용성의 근거 |
| Section 7.1, Table 3 | Freivalds 기반 baseline 및 DualMatrix 정방행렬 실험 | 새로운 비교 대상의 실행 가능성 검토와 가능한 정량 비교 |
| Section 7.4, Table 6 | GPT-2 행렬 곱 workload에서 세 시스템 비교 | matrix-product workload와 전체 추론 검증의 차이, 일반화 범위 |
| Abstract, Introduction, Conclusion | 제약 수 감소와 proving speedup 강조 | 검증·통신 비용까지 포함한 장단점과 측정 대상에 한정된 결론 |

표 번호는 현재 로컬 원고 기준이며, 최종 제출본과 대조한다. 이번 계획은 기존 수정 사항을 새 작업으로 다시 약속하지 않는다.

## 3. 추가 비교 후보에 관한 현재 증거

### Evalyn: 우선 검토할 구체적인 후보

- 논문: *Scalable zkSNARKs for Matrix Computations: A Generic Framework for Verifiable Deep Learning*. 저자 페이지에 ASIACRYPT 2025 연구로 기재돼 있다. [저자 출판 목록](https://thyuen.github.io/publications/), [ePrint](https://eprint.iacr.org/2025/1646)
- 저자 측 공개 저장소에 구현과 neural-network 실행 예제가 존재한다. **저장소 접근과 README 확인까지 완료했으며, 빌드·실험은 아직 하지 않았다.** [구현](https://github.com/mirandaprivate/evalyn_asiacrypt)
- 현재 LAMP의 related work와 bibliography에서 이 연구를 찾지 못했다.
- 비교 후보라는 판단은 matrix-computation 연구와 공개 구현이 있다는 점에 근거한다. 가장 빠른 시스템인지, LAMP와 같은 관계·보안 모델을 직접 비교할 수 있는지는 아직 확인하지 않았다.
- ePrint 버전, 출판 버전, 구현 snapshot의 대응부터 확인한다. 전체 neural-network 예제 시간을 LAMP의 행렬 곱 workload 시간과 직접 나누지 않는다.

### 다른 후보

- zkMatrix·zkMaP: 원고의 기존 이론 비교를 재검토하고, 저자 자료와 구현의 현재 접근 가능성을 확인한다. 이번 웹 조회에서 zkMaP 관련 링크를 열지 못한 사실만으로 공개 구현이 없다고 결론내리지 않는다.
- Sum-check/GKR 및 code-based proof systems: 우리 기여와의 관계를 설명할 대상으로 검토한다. 모든 시스템에 대한 새 구현·벤치마크를 이번 계획에서 약속하지 않는다.
- DualMatrix: 현재 실험은 유지하되 코드 버전과 측정 조건을 명시한다. 관측한 성능 개선의 적용 범위를 해당 실험으로 한정한다.

**핵심 판단:** “DualMatrix 외에는 관련 공개 코드가 없다”는 포괄적 설명을 새 연락에서 반복하지 않는다. 구체적인 후보의 검토 결과로 비교 범위를 설명한다.

## 4. Shepherd에게 제안할 수정 항목

### R1. Section 2와 Table 1의 비교 근거 확장

- Evalyn을 포함한 관련 연구를 검토하고, 해당되는 연구를 related work에 반영한다.
- 비교표에 증명 대상, committed-input 인터페이스, 보안·setup 가정, dense/sparse 조건과 비용 포함 범위를 설명한다.
- field operations와 group operations 등 다른 비용 단위를 혼동하지 않도록 복잡도 항목을 확인한다. 공개 입력 처리·commitment 생성·linking 비용의 포함 여부도 표시한다.
- LAMP의 회로 제약 수와 전체 prover 작업량을 구분하고, code-consistency 비용을 생략할 수 있는 조건을 명시한다.

**산출물:** 보강한 related work와 비교표·주석.

### R2. Section 7의 추가 정량 비교 가능성 검토

우선 목표는 **Evalyn 등 적절한 공개 구현에서 LAMP와 대응하는 행렬 곱 관계를 설정할 수 있는지 확인하는 것**이다.

추가 실행 비교의 조건:

1. 행렬 크기·값의 범위·밀도·batch 구성이 대응한다.
2. 공개/비공개 입력, commitment와 zero-knowledge 보장이 명시된다.
3. curve·field·보안 파라미터 차이를 기록하고 비용에 미치는 영향을 설명한다.
4. 동일 서버·스레드 설정에서 실행하고, setup·commit·prove·verify·통신량·메모리의 포함 범위를 맞춘다.
5. 한 시스템의 전체 파이프라인과 다른 시스템의 일부 검사를 같은 작업으로 취급하지 않는다.

조건을 만족하는 비교가 가능하면 대표 크기의 실험부터 추가한다. 조건을 맞추기 어렵다면 그 이유를 문서화하고, 원 논문이 보고한 결과를 환경·모델·비용 차이와 함께 별도 표시한다. 출처가 다른 시간을 동일 조건 speedup으로 제시하지 않는다.

**산출물:** 실행 가능성 기록, 가능한 경우 새 비교 실험, 또는 차이를 명시한 출판 결과 비교와 한계 설명.

**Shepherd에게 확인할 사항:** 우선적으로 고려해야 할 시스템이 있는지, 제안한 비교 범위가 우려를 다루기에 적절한지. 문헌·코드 검토는 답변을 기다리지 않고 진행한다.

### R3. 성능 주장의 범위와 trade-off 명확화

- Abstract·Introduction·Conclusion에서 성능 우위의 대상과 측정 조건을 명시한다.
- 전체 최첨단 기법에 대한 우위로 해석될 수 있는 표현을 점검한다.
- GPT-2 결과에 proving 개선과 함께 verification·proof-size 비용을 반영한다.
- 현재 GPT-2 평가가 검증하는 연산의 범위를 설명하고, 전체 모델 추론을 증명한 결과와 구분한다.
- 다른 연산과 결합할 때의 추가 linking 비용을 논할 경우, 동일한 기준을 LAMP에도 적용한다.

**산출물:** 요약·기여·평가·결론의 일관된 주장과 한계 서술.

## 5. 일정과 역할

| 날짜 | 우리 작업 | 산출물 |
|---|---|---|
| 9/16 | 메타리뷰와 원고 대조, 수정 계획 초안 작성 | 이 문서와 영문 연락문 |
| 9/17–9/18, 내부 목표 | Evalyn 등의 논문·구현·비교 조건 조사 | 비교 대상 후보와 실행 가능성 메모 |
| 9/19–9/20, 내부 목표 | 교수님·공동저자와 약속할 범위 검토 | 9/21 연락문 확정 |
| 9/21 | HotCRP에서 수정 계획 전달 | 전송 기록, shepherd에게 확인할 쟁점 |
| 9/22–10/2, 조율할 목표 | 합의된 비교·원고 보완, 필요한 실험 | 수정 PDF·diff·response letter |
| 10/9, 이메일상 목표 | 피드백 반영 및 near-final 승인 | 승인 기록·최종 메타리뷰 확인 |
| 10/16 | 카메라레디 최종 제출 | 최종 PDF·소스·접수 기록 |

10/2는 공개 CFP의 shepherd 제출일이며, 9/21 첫 연락에서 세부 일정을 조율한다. [공식 CFP](https://sp2027.ieee-security.org/cfpapers.html)

동료에게 필요한 정보는 AE 업무와 겹치는 **최종 구현 버전, 실험 환경, 원시 로그, 재실험 가능한 자원**이다. 새 비교 실험이 필요해지면 실제 담당과 실행 가능 일정을 먼저 정한다. AE 준비·접수·Zenodo 공개의 진행 관리는 동료 담당으로 둔다.

## 6. 이 계획에서 확정하지 않는 사항

- 특정 시스템보다 빠르다는 새 결과: 아직 측정하지 않았다.
- 추가 시스템의 재현 성공: 아직 빌드·실행하지 않았다.
- 메타리뷰 우려의 삭제: shepherd의 검토 결과에 따른다. 설명을 보강해도 실증 비교 한계가 남으면 해당 사실을 정직하게 남긴다.
- 새 비대화형 보안 증명이나 광범위한 프로토콜 재설계: 이번 비교 우려 대응의 기본 약속에 넣지 않는다. 별도 검토에서 정확성 문제가 확인되면 필요한 수정을 우선한다.
- AE 평가 완료가 비교 우려를 해결한다는 주장: 두 절차의 목적과 증거를 각각 관리한다.

## 7. 9/21 전 체크리스트

- [ ] 최신 HotCRP 메타리뷰와 대상 문구가 같은지 확인한다.
- [ ] 현재 로컬 원고가 interactive rebuttal 제출본과 일치하는지 확인한다.
- [ ] 추가 비교 후보의 관계·모델·공개 코드·실행 가능성에 대한 1차 검토를 마친다.
- [ ] 영문 연락문의 계획과 실제로 수행한 일을 구분해 문장을 갱신한다.
- [ ] 공동저자가 약속할 수정 범위와 일정에 동의하는지 확인한다.
- [ ] HotCRP에 전달하고 접수·전송 기록을 남긴다.

참고: 500단어 미만 제한은 최종 PDF에 실을 **선택적 메타리뷰 답변**에 관한 것이다. 아래 영문 수정 계획 초안은 그 답변과 별개의 첫 연락문이다. [합격 이메일](/Users/kyeongtae/.codex/attachments/7329cc08-eaf6-4b9d-9e0e-2d59447fc917/pasted-text.txt)
