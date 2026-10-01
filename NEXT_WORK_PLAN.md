# LAMP: 현재 수정 작업 계획

- 갱신일: **2026-10-01, 한국 시간**
- 논문: **S&P 2027 #1646 — LAMP: Linear Verification of Matrix Multiplication via Proximity Testing**
- 현재 단계: 채택 후 shepherding. **10/1 단일 행렬 128~2048 및 n=128, q=1~10 배치를 LAMP·zkMatrix 각각 10회 완료했고, 원시 결과를 로컬에 보존·검증했다. `Paper/`에 zkMatrix 비교와 trade-off, zkMaP 비교 제외 사유를 반영하고 18쪽 PDF를 빌드했다. 다음 작업은 공동저자 검토와 shepherd 대응·제출 패키지 확정이다.**
- AE는 동료 담당이다. 현재 AE 제출 상태·배지·평가 진행 상황은 이번 작업에서 재조회하지 않았다.
- 저장소 역할을 확정했다. 논문·수정 계획·실험 비교 근거는 [lysias9049/LAMP](https://github.com/lysias9049/LAMP), 실행 구현체·아티팩트는 [lysias9049/LAMP-artifact](https://github.com/lysias9049/LAMP-artifact)에서 관리한다. 현재 로컬 폴더는 논문 작업용이다. 10/1 확인 당시 아티팩트 main은 기존 측정 소스와 같은 `b34d2287c30730a3990d92630185a0a792a2897f`다. 이전 저장소명이 남아 있는 원시 측정 기록·소스 출처는 당시 기록으로 보존한다.
- 로컬 Git은 `origin`을 논문 저장소, `artifact`를 구현체 저장소에 연결했다. 현재 작업 브랜치의 추적 대상과 push 대상은 논문 `origin`이다. 사용자의 요청에 따라 수정 전 로컬 자료를 commit하고, 새 논문 저장소의 초기 README 이력을 합쳐 `3930ecccdd06aee857da3522118e1bcd0fcf34ea`를 `origin/main`에 push·확인했다. 이어서 아래 논문 보완을 완료했다.

## 1. 현재 상황

### 10/1 단일 행렬·배치 10회 결과 수신 및 검증

- 논문 수정 대상은 사용자가 지정한 `Paper/main.tex`다. Section 7은 이 파일에서 불러오는 `Paper/Contents/evaluation.tex`에 있다. `Paper_original/`은 수정 전 백업으로 보존하며, 다른 논문 버전에 자동 복제하지 않는다.
- 제출 기준본을 확인했다. `Paper/LAMP-1st-revision.pdf`와 현재 `Paper/main.pdf`는 18쪽 전체의 텍스트·페이지 내용 스트림·렌더링 결과가 같으며, 파일 차이는 생성·수정 시각과 PDF 문서 ID뿐이다. `Paper_original/main.pdf`는 제출 기준본과 바이트 단위로 같고, 두 논문 폴더의 TeX·참고문헌·스타일 소스도 같다. 현재 `Paper/`에서 제출본 수정을 이어간다.
- 9/30 측정은 정방행렬 128~1024 및 n=128, q=1~10 배치에서 각 3회 완료했고, 결과는 `Benchmark/epyc/archive/lamp-results-20260930T062910Z/`에 있다. 논문 보강의 정량 비교는 새 10회 결과를 사용하고, 기존 결과는 실험 기록으로 보관한다.
- 10/1 단일 행렬 n=128,256,512,1024,2048에서 LAMP·zkMatrix 각각 10회를 완료했다. 결과는 `Benchmark/epyc/lamp-three-results-10reps-k7-k11-20260930T233536Z/`에 있다. zkMaP 수정판 측정 50건도 이 폴더에 있으나 논문의 성능 비교에서 제외한다. 사용자는 다운로드 후 VM을 중지했다고 보고했다.
- 새 측정 소스는 `lysias9049/FastMatMul`, 커밋 `b34d2287c30730a3990d92630185a0a792a2897f`로 고정한다. LAMP·zkMatrix 코드는 이전 비교 구현에서 가져온 것이다.
- 추가 배치 실행은 **LAMP·독립 zkMatrix만, n=128, q=1~10에서 각각 10회**, BN254, 32 threads, LAMP rho=1/2, t=309로 완료됐다. 110개 실행 명령이 모두 성공했고, LAMP 100건·zkMatrix 100건을 확인했다. 실제 실행 시간은 약 114.1분이다.
- 배치 결과는 `Benchmark/epyc/lamp-batch-results-10reps-k7-q1-q10-20261001T032827Z/`다. Downloads의 압축파일 SHA-256이 서버 출력과 일치하고, 압축 해제된 561개 파일이 아카이브와 바이트 단위로 일치했다. 설정·원시 기록의 10회 반복·행렬 크기·thread 수·정상 입력 검증 성공을 대조했다.
- EPYC 실험 결과 세 폴더를 `Benchmark/epyc/` 아래로 이동했다. 폴더 내부의 원시 결과·실행 설정·로그·측정 코드와 서버 경로 기록은 그대로 보존했고, 이동 전후 모든 파일의 SHA-256이 일치한다.
- 중복된 `Implementation/`을 정리했다. zkMaP 프로토콜 Go 파일 8개는 `lysias9049/FastMatMul`의 `b34d2287c30730a3990d92630185a0a792a2897f`와 바이트 단위로 같고, 확인 당시 원격 main도 이 커밋이었다. 로컬 독립 모듈·CLI·계획·테스트 로그·바이너리 42개 파일은 `Revision/archive/zkmap-local-implementation-20261001.tar.gz`에 압축 보존했다. 압축파일과 모든 파일의 해시 검증 기록은 같은 이름의 `.json`이다. 실행 코드 관리는 별도 Git 저장소에서 이어간다.
- 단일 행렬과 새 배치의 측정 소스 commit 및 source-tree fingerprint가 모두 같다. 원시 기록을 재집계한 평균·표본 표준편차가 서버 요약과 부동소수점 반올림 범위에서 일치한다. 검증·집계 기록은 `Benchmark/epyc/batch_10reps_verified_summary_20261001.json`이다. 이 확인은 프로토콜 soundness의 형식적 인증을 뜻하지 않는다.
- 배치 q=1~10에서 zkMatrix의 증명 생성 시간이 더 짧다. q=10의 commitment 포함 평균은 LAMP 약 11.796초, zkMatrix 약 1.088초다. 이 범위에서 LAMP의 압축 증명 크기(약 24.3KB)와 검증 시간(약 0.13초)은 거의 일정하다. 논문에는 단일 행렬 크기 증가 시의 이점과 배치 trade-off를 함께 설명한다.
- 새 배치 종료 후 다운로드와 로컬 보존을 확인했고, 사용자는 VM을 중지했다고 보고했다.
- 배치 전용 준비 파일은 `Experiment/run_epyc_batch_10reps.sh`, `comparison_batch_10reps.json`, `epyc_batch_tools.py`, `prepare_comparison_3reps.py`다. 업로드 묶음은 `Experiment/lamp-batch-server-setup-20261001.tar.gz`다. 기본 동작은 계획 확인이며 VM 시작·중지·예약 작업은 하지 않는다.
- 새 배치 실행의 결과는 서버에서 `lamp-batch-results-10reps-k7-q1-q10-<UTC시각>.tar.gz`로 보존한다. 1분마다 진행 상황을 표시하고, 실패를 발견하면 남은 실행을 중단하며 로그와 부분 결과를 보존한다. 완료 표시는 모든 배치 설정의 10회 결과가 확인된 뒤에만 기록한다.
- **zkMaP 수정판에서 false-statement 수락 반례를 확인했다.** 정상 C=AB의 증명이 C'=AB+E00의 commitment에 대해서도 통과하며, 항등원 증명도 통과한다. 자료는 `Revision/zkmap_soundness_audit_20261001/`에 보관했다. 이 결과는 로컬 수정판에 관한 것이며 출판된 zkMaP 전체에 대한 결론으로 확대하지 않는다. 현재 범위에서 수정판의 soundness 보완·재측정은 진행하지 않는다.
- 실제 runner의 배치 전용 실행 계획과 준비 도구 테스트를 로컬에서 확인했다. 이번 준비 작업에서는 VM 접속이나 서버 성능 측정을 실행하지 않았다.

### 10/1 EPYC 결과를 반영한 논문 수정

- Section 7에 독립 zkMatrix와의 단일 행렬·배치 비교표 두 개를 추가했다. 정방행렬은 128~2048, 배치는 128×128에서 q=1~10, 시스템·설정당 10회이며 평균과 표본 표준편차를 표시한다.
- 서버 원시 결과 300건·30조건을 소스 commit/fingerprint, 실행 명령, host, BN254, 32 threads, LAMP rho=1/2·t=309와 대조했다. 재집계가 서버 요약과 일치한다. `Benchmark/epyc/generate_comparison_tables.py`는 검증·표 재생성만 하며 실험을 실행하지 않는다.
- 새 비교는 encoding·commitment·witness 준비를 포함한 online proving 시간을 사용한다. setup·compile·C=AB 계산·serialization은 제외한다. 증명은 canonical compressed payload 크기, 공개 statement는 별도 집계다. 기존 표와 byte 집계가 달라 직접 비교하지 않는다고 설명했다.
- 독립 zkMatrix의 최적화한 4-IPA, masking, structured SRS, pairing accelerator, Algorithm 6 배치를 명시했다. 출판 논문의 BLS12-381을 BN254로 옮긴 구현이며 동일 보안수준이나 원저자 코드 재현으로 주장하지 않는다. LAMP 구현의 evaluation-basis 인코딩과 challenge transcript도 공개하고, 논문의 public-coin 보안 분석과 구분한다.
- 측정한 단일 행렬에서 zkMatrix는 128·256에서 더 빠르고, LAMP는 512·1024·2048에서 더 빠르다. 2048에서는 LAMP 약 28.310초, zkMatrix 약 113.180초로 약 4.00배다. 반면 zkMatrix의 검증·증명 크기가 이 전체 구간에서 더 좋다.
- 배치에서는 zkMatrix가 모든 q=1~10에서 더 빠르며, q=10에서 약 1.088초 대 LAMP 약 11.796초다. LAMP의 증명 크기·검증은 거의 일정하나, 이 구간에서는 zkMatrix의 절대 비용이 더 작다. 측정 밖 crossover를 주장하지 않는다.
- zkMaP의 출판된 식을 재현할 때 정상 입력에서 발생한 completeness 문제와 로컬 수정판의 statement-binding 실패를 구분해 설명했다. 수정판 성능 수치는 본문·표에 넣지 않았으며, 출판 프로토콜 전체의 실패로 확대하지 않는다.
- Introduction·conclusion의 비교 주장도 범위에 맞춰 수정했다. 기존 Freivalds·DualMatrix·GPT-2 및 code-rate 표 5개의 블록은 수치·내용이 같다. 세부 component와 LAMP 단독 배치 표를 부록 F로 이동했으며, 기존 구성·보안 증명은 보존했다. `Paper_original/`은 변경하지 않았다.
- pdfLaTeX·BibTeX 빌드와 렌더링을 확인했다. 총 18쪽, 본문·새 비교표는 13쪽 안에 있으며 undefined reference/citation과 overfull box는 없다. 결과는 `Paper/main.pdf`, source/PDF hash와 검증 기록은 `Benchmark/epyc/paper_revision_validation_20261001.json`이다.
- 이는 zkMatrix 비교와 zkMaP 재현 문제 설명을 반영한 공동저자 검토용 원고다. Shepherd가 요구한 두 시스템의 완전한 공정 벤치마크를 모두 달성했다고 주장하지 않는다. 우려 제거 여부와 zkMaP 대응 범위는 shepherd의 판단·답변이 필요하다. HotCRP 제출이나 추가 코멘트 전송은 하지 않았다.

### 이전 계획 및 배경

- 최초 영문 수정 계획은 사용자 보고에 따라 shepherd에게 제출 완료했다.
- Shepherd는 우려를 제거하려면 **zkMaP과 zkMatrix 모두에 대해 Section 7과 같은 파라미터의 벤치마크와 trade-off 논의**가 필요하다고 답했다.
- 교수님이 독립적으로 구현한 zkMatrix의 M1 실험 결과를 `Paper_m1/`에 반영했다. 이는 원저자 구현의 재현이라고 주장하는 비교가 아니다.
- EPYC 비교는 우선 zkMatrix만 진행한다. 이 결과만으로 shepherd의 전체 요구가 충족됐다고 단정하지 않는다.
- zkMaP의 논문 식 재현 구현과 로컬 테스트를 당시 `Implementation/zkmap/`에 추가했다. 일반 정상 입력에서 세 가지 projection 인코딩 해석의 witness 생성이 실패하며, 128×128 기본 해석에서도 같은 실패를 확인했다. 원저자의 완전한 구현에 대한 결론으로 확대하지 않는다. 당시 구현 계획과 실패 기록은 위 로컬 구현 압축파일에 보존한다.
- 2026-10-01 요청에 따라 별도 `completeness-roots-v1` 수정판을 추가했다. 작은 정상 입력의 생성·검증이 성공하며, 원본 경로/기존 실패 기록을 보존했다. 이 수정판은 witness/검증식·G2 SRS·batch 비용이 달라진다. 이후 서버에서 진단용 측정을 했으나, soundness 반례를 확인하여 논문 성능 비교에서 제외했다. 수식과 변경 범위는 별도 저장소의 `docs/comparison/ZKMAP_COMPLETENESS_REPAIR.md` 및 위 압축파일에 보존한다.

## 2. 논문 및 데이터 위치

| 위치 | 역할 | 현재 상태 |
|---|---|---|
| `Paper_original/` | 수정 전 기준 논문 | GitHub `Han-16/FastMatMul`, `snp-revise-v1`, `Paper_snp_revise/`, 커밋 `930f306d5df1c378089ca181c0770745a930610c` 기준 |
| `Paper/` | 현재 수정할 논문 | 진입점 `main.tex`, Section 7은 `Contents/evaluation.tex`. 새 EPYC 단일 행렬·배치 비교, trade-off와 zkMaP 제외 사유 반영; 18쪽 빌드 |
| `Benchmark/original/` | 기존 논문 측정 자료 | 정방행렬·batch·GPT-2 CSV 세 개 보존 |
| `Benchmark/m1/` | 교수님 비교 측정 근거 | 원시 JSONL 280건, 실행 manifest, 측정 소스, 출처, 집계·표 생성 스크립트 보존 |
| `Benchmark/epyc/archive/lamp-results-20260930T062910Z/` | EPYC 3회 측정 기록 | 단일 행렬 128~1024 및 배치 n=128, q=1~10 |
| `Benchmark/epyc/lamp-three-results-10reps-k7-k11-20260930T233536Z/` | EPYC 단일 행렬 10회 기록 | n=128~2048; 배치 결과 없음; zkMaP 수정판은 논문 비교에서 제외 |
| `Benchmark/epyc/lamp-batch-results-10reps-k7-q1-q10-20261001T032827Z/` | EPYC 배치 10회 기록 | n=128, q=1~10; LAMP 100건·zkMatrix 100건 검증 완료 |
| `Benchmark/epyc/` | EPYC 실험 자료 보관 위치 | 새 10회 원시 결과와 검증 요약, `archive/`에 기존 3회 기록 보존 |
| `Experiment/` | EPYC 실행 준비 | 이번 실행은 `run_epyc_batch_10reps.sh`와 배치 전용 업로드 묶음 사용 |
| `Revision/archive/zkmap-local-implementation-20261001.tar.gz` | 이전 로컬 zkMaP 구현·테스트 기록 | `Implementation/` 정리 전 42개 파일을 해시 검증 후 보존; 현재 코드 관리 대상은 별도 LAMP-artifact 저장소 |
| `Revision/` | 리뷰·연락문·수정 계획·참고 논문 | 이전 문서의 작성 상태 표시는 당시 기록으로 취급 |

각 논문 폴더의 진입점은 `main.tex`, 컴파일 결과는 `main.pdf`다. 기존 제출용 `LAMP.pdf`와 예전 `LAMP_diff.pdf`는 정리했다. 현재 수정본과 `Paper_original/`의 1차 제출 기준본을 비교한 새 `Paper/LAMP_diff.tex`·`Paper/LAMP_diff.pdf`를 생성했다. 추가·수정과 새로 삽입하거나 부록으로 옮긴 표는 파란색으로 표시하며, 삭제된 내용과 첫 페이지 안내문은 표시하지 않는다. diff와 clean 원고 모두 18쪽이다. 원고 변경 후에는 `python3 Experiment/generate_revision_diff.py`로 다시 생성한다.

## 3. 지금 우선할 일

### P0. EPYC 결과 확보 및 비교 조건 확인

수신한 실행 설정과 원시 기록에서 다음 범위를 확인했다.

- 정방행렬: 128, 256, 512, 1024, 2048에서 각 10회 완료.
- 배치: 128×128, 독립 행렬곱 수 1–10.
- 배치도 각 시스템·설정당 10회 완료했다. 32 threads.
- LAMP: `rho=1/2`, 질의 수 `t=309`.
- 더 큰 행렬과 추가 GPT-2 비교는 현재 범위에서 보류한다.

- [x] 원시 결과와 manifest·명령·설정·소스 버전을 위 실제 로컬 경로에 보존하고, 검증·집계 기록을 `Benchmark/epyc/`에 저장한다.
- [x] 새 배치 manifest의 AMD EPYC 7B13, 32 vCPU, 약 251GiB usable memory, Linux, Go 1.26.2, 32 threads 및 순차 실행 기록을 확인한다.
- [x] 새 배치 결과에서 두 시스템의 q=1~10 각각 10개, 총 200개의 정상 입력 검증 성공 기록을 확인한다. 중단·실패한 실행은 없다.
- [x] 곡선, 행렬·배치 의미, setup 및 encoding·commitment 포함 범위, proof·statement byte 집계를 대조한다.
- [x] 새 배치 원시 결과로 평균과 표본 표준편차를 재계산한다. M1과 EPYC, 기존 3회와 새 10회 결과를 한 평균으로 합치지 않는다.
- [x] 결과와 로그를 확보한 뒤 VM을 중지한다. 사용자가 중지를 완료했다고 보고했다.

### P1. EPYC 논문 보완

- [x] `Paper/main.tex`가 불러오는 `Paper/Contents/evaluation.tex`에 서버 환경, 10회 반복, 측정 범위, 독립 구현의 차이와 결과를 반영한다.
- [x] 필요한 표를 `Paper/Tables/`에 만들고 원시 결과와 수치를 대조한다.
- [x] introduction·conclusion 등 비교 주장을 결과와 맞춘다. 측정하지 않은 크기나 다른 시스템에 성능 우위를 확장하지 않는다.
- [x] zkMatrix와의 prover·verifier·proof 및 batch trade-off를 설명한다.
- [ ] zkMaP 비교가 남아 있다는 점과 대응 가능한 범위를 공동저자·shepherd와 조율한다.

### P2. 제출할 버전과 수정 패키지 확정

- [ ] `Paper/`의 EPYC 비교 반영본을 공동저자와 확정한다.
- [x] 비교 표·설명을 추가한 뒤 제출 안내의 허용 분량에 맞는지 페이지 수를 확인한다.
- [x] 선택한 원고를 pdfLaTeX·BibTeX으로 빌드하고 참조·표·수식·페이지 배치를 확인한다.
- [x] 수정 PDF와 1차 제출본 대비 파란색 diff PDF를 준비하고 표·본문 배치를 확인한다.
- [ ] shepherd response letter를 준비한다.
- [ ] 달성한 zkMatrix 비교 범위와 남은 zkMaP 비교를 구분해 설명한다.
- [ ] 제출 PDF·소스·측정 자료의 버전과 접수 기록을 보존한다.

## 4. 예정 일정

기존 이메일·공지와 사용자 대화에서 정리한 준비 기준이다. 최신 연장 여부와 정확한 제출 시각은 이번 문서 정리에서 재확인하지 않았다.

| 날짜 | 작업 |
|---|---|
| 10/2 | Shepherd 검토용 수정본 준비·제출 목표 |
| 10/9 | 거의 최종인 수정본 및 shepherd 승인 목표 |
| 10/16 | 최종 카메라레디 제출 |

카메라레디에는 저자·소속, 필수 출판 서류와 최종 메타리뷰 관련 요구도 후속 안내에 맞춰 반영한다. AE 후속 조치는 동료에게 진행 상황을 확인해 별도로 관리한다.

## 5. 과거 기록

- `Revision/archive/NEXT_WORK_PLAN_20260916_KO.md`: 9/16 당시 계획의 원문.
- `Revision/archive/AE_REVIEW_20260918_KO.md`: 9/18 당시 AE 검토와 후속 정정 기록. 그 문서의 draft 상태·배지·메모리 지적이 현재도 그대로인지는 재확인해야 한다.

이전 문서의 미완료 체크나 당시 상태만으로 현재 미제출·결함이 있다고 판단하지 않는다.
