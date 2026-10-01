# S&P 2027 AE #35 검토

검토일: 2026-09-18. 외부 제출 내용은 수정하거나 제출하지 않았다.

## 재확인 결과 — 세 항목에 대한 정정

후속 검토에서 HotCRP 첨부 `metadata.toml` 본문을 읽을 수 있었다. 아래는 최초 검토의 해당 판단을 대체한다.

1. **10회 평균 / CSV 덮어쓰기:** 사실관계는 맞다. 다만 metadata의 `destructive`에 CSV와 `system_info.json` 덮어쓰기가 이미 고지되어 있다. 따라서 경고 누락이 아니라 **논문의 10회 평균을 재현하는 결과 보존·집계 절차가 없는 것**이 핵심이다. 설정당 1회 실행 자체가 결함이거나 AE 탈락 사유라는 뜻은 아니다. 논문과 동일한 측정 절차를 재현하려면 보완을 권장한다.
2. **DualMatrix:** 공개 ZIP에는 재현 안내가 없지만 metadata의 `use`와 `claim1`–`claim3`는 LAMP/Freivalds 비교 및 LAMP 배치만 재현 대상으로 명시한다. 따라서 **DualMatrix가 반드시 포함되어야 한다는 식의 높은 우선순위 지적은 완화한다.** 우선 Zenodo의 Section 7 전체 결과를 제공한다는 설명을 실제 범위에 맞추고, DualMatrix 비교는 이 패키지에 포함되지 않는다고 명시하면 된다. DualMatrix 대비 성능 주장까지 재현 평가 대상으로 삼으려면 별도 실행 안내가 필요하다.
3. **GPT-2 메모리:** 누락 판단을 유지한다. metadata의 `script3`는 `--seq 10`을 명시하지만 `hw`와 HotCRP Hardware requirements 모두 정방행렬의 8 GiB/64 GB급 요구량과 원래 서버 256 GB만 설명한다. GPT-2 참조 결과의 약 100.44 GB peak RSS는 별도 명시되지 않았다. 이는 64 GiB 환경에서 제안된 GPT-2 실험을 실행하려는 평가자를 혼동시킬 수 있으므로 우선 보완한다.

정정된 우선순위: **GPT-2 메모리 명시 → 반복 실행·평균 계산 안내 → Zenodo와 metadata의 재현 범위 정렬.** 아래 본문은 최초 검토 기록이며, 세 항목의 해석은 이 정정을 우선한다.

## 결론

Zenodo에 실제 소스와 Dockerfile을 공개한 구성은 적절하다. 다만 현재 HotCRP는 **not ready for review** 상태이며, **Available만 신청**되어 있다. 실행 가능성과 결과 재현까지 평가받으려면 Functional/Reproduced 신청 여부와 아래 재현 안내를 함께 정비해야 한다. Available만 신청하는 것 자체는 잘못이 아니다.

## 검토 범위와 한계

- 로그인된 [HotCRP #35](https://cycle1-ae.sp2027.ieee-security.org/paper/35)의 입력값·배지·제출 상태를 확인했다.
- [Zenodo v1.0.0-artifact](https://zenodo.org/records/22819192)의 공개 상태, DOI, ZIP을 확인했다. 내려받은 ZIP의 MD5는 페이지 표시와 같은 `7cda2e3adbaec318e7b367dc094ae2c8`이다.
- ZIP의 README, 환경 설정, Dockerfile, 실행 스크립트, 주요 벤치마크 및 CSV 기록 코드를 정적으로 확인했다.
- 로컬 논문 `Paper/Contents/evaluation.tex`와 기존 실험 CSV를 대조했다.
- 실행 스크립트의 `sh -n` 문법 검사는 통과했다. Docker 빌드·벤치마크 실행·독립적인 결과 재현·암호학적 soundness 검증은 수행하지 않았다.
- HotCRP의 `metadata.toml`과 PDF가 업로드되어 있다는 것은 확인했지만, 인증된 첨부파일의 본문을 확보하지 못했다. 따라서 메타데이터에 별도 재현 지침이 있는지는 미확인이다. 아래 문서 누락 지적은 공개 ZIP을 기준으로 한다.

## 1. 제출 전에 처리할 사항

### 1.1 심사 준비 완료 상태

현재 `The submission is ready for review`가 체크되어 있지 않고 `Save draft` 상태이다. 내용 검토를 마친 뒤 준비 완료를 체크하고 저장하여, 초안 경고가 사라지는지 확인해야 한다.

현재 HotCRP에 표시된 마감은 **2026-09-19 07:59:59 EDT = 한국시간 2026-09-19 20:59:59**이다. 이전에 이야기한 날짜보다 실제 제출 시스템의 현재 표시를 기준으로 행동하되, 가능한 한 오늘 완료하는 것이 좋다.

### 1.2 목표 배지 확인

- 현재: Available 체크, Functional 및 Reproduced 미체크.
- Available: 영구 공개·검색/다운로드 가능성에 관한 배지.
- Functional: 문서화, 구성요소의 완전성, 다른 환경에서 실행 가능성을 평가.
- Reproduced: 주요 결과와 주장을 독립 실행으로 뒷받침할 수 있는지 평가.

권장: 공개만 목표였다면 현재 선택을 유지할 수 있다. 실행 검증까지 목표라면 깨끗한 환경의 Docker 빌드 및 작은 실험 성공을 확인하고 Functional도 신청한다. Reproduced까지 신청하려면 아래 비교 대상·반복 실행·기준 결과 안내를 보완한다. 배지 추가만으로 재현 준비가 완료되는 것은 아니다.

### 1.3 업로드한 논문 버전 확인

HotCRP는 “accepted version”을 업로드하라고 명시한다. 현재 PDF 체크섬 접두사는 `741b413d`, 로컬 `Paper/main.pdf`는 `1f7163f5`로 서로 다르다. 재컴파일만으로도 해시가 달라질 수 있으므로 잘못된 PDF라는 뜻은 아니다. 다만 최종 심사에 사용된 리비전인지, Table 3 및 GPT-2 결과와 보안 파라미터가 동일한지 확인해야 한다.

## 2. 재현 문서에서 보완할 사항

### 2.1 “Section 7 전체 결과 재현”과 실제 제공 범위 정렬

Zenodo 설명은 Section 7의 실험 결과를 재현하는 전체 소스·스크립트·문서를 제공한다고 쓴다. ZIP에는 LAMP와 Freivalds의 정방행렬·배치·GPT-2 실행 코드가 있지만, DualMatrix 코드/실행 방법/수정 패치/기준 결과가 없다.

대응 방법:

1. DualMatrix의 사용 버전, 패치, 빌드·실행 명령, 입력 구성, 측정 방법을 제공한다. 또는
2. 실제 제공 범위를 LAMP/Freivalds로 명시하고, DualMatrix 비교는 이 패키지의 재현 범위에서 제외됨을 설명한다.

Available만 신청할 때도 공개 설명의 범위는 실제 내용과 맞추는 것이 좋다. Reproduced 목표라면 비교 속도 향상 주장을 어떻게 검증할지 별도로 설명해야 한다.

### 2.2 10회 평균 재현 방법과 결과 보존

논문은 각 실험을 10회 반복한 평균이라고 명시한다. 현재 실행 코드는 설정당 한 번 실행하며, 스크립트는 단일 실행 또는 범위 실행의 첫 설정에서 `BENCHMARK_APPEND_CSV=false`를 전달한다. CSV 기록 코드는 이때 기존 파일을 덮어쓴다. 같은 명령을 단순히 10회 반복하면 10회 결과가 자동으로 보존되지 않는다.

추가할 내용:

- 반복마다 다른 출력 폴더 또는 run ID로 결과를 보존하는 실행 방법.
- 10회 결과를 합쳐 평균을 계산하는 스크립트/명령.
- 논문의 표와 출력 CSV 열의 대응, 시간 단위 및 측정 범위.
- 장비 차이를 고려한 판단 기준: 절대 시간만 일치시키려 하지 말고, 동일 환경의 비교 비율과 정성적 경향도 평가.

### 2.3 기준 결과 및 claim-to-command 대응표

ZIP에는 기존 결과 CSV나 로그가 없고 README에도 예상 constraint 수·증명 크기·성공 출력·허용 편차가 없다. 제출 폼의 “included result”라는 표현은 공개 ZIP만으로는 근거 파일을 찾을 수 없다.

최소한 다음을 추가하면 평가자가 비교하기 쉽다.

| 실험 | 명령의 핵심 설정 | 로컬 논문/결과의 기준 | 주의점 |
|---|---|---|---|
| 정방행렬 LAMP | `lamp --K 10 --rho 1/2 --L 309` | constraint 1,306,973 | 실제 공개 코드 출력과 먼저 대조 |
| 큰 정방행렬 | `lamp --K 12 --rho 1/2 --L 309` | constraint 5,214,878, proving 70.73 s | 시간은 원래 서버 기준 |
| 배치 | `lamp_batch --K 7 --batch-range --batch-from 1 --batch-to 10` | 배치 수 증가에 따른 추세 | 논문 표와 CSV 열 연결 |
| GPT-2 행렬곱 | `run_gpt2_bench.sh lamp --seq 10 --rho 1/2 --L 309` | constraint 62,460,189, proving 317.13 s | 대용량 메모리 필요 |

위 값은 로컬 논문에서 가져온 기준이며, 이번 검토에서 공개 코드로 재측정한 값이 아니다. 공개 버전과 논문 버전이 다르면 차이의 이유를 설명해야 한다.

### 2.4 GPT-2 메모리 요구량과 안전한 실험 순서

HotCRP는 기본 정방행렬에 8 GiB, 가장 큰 정방행렬에 64 GiB를 권장한다. 하지만 `.env.example`의 GPT-2 기본값은 `seq=10`이고, 로컬 GPT-2 결과의 peak RSS는 **100,436,226,048 B (약 100.44 GB / 93.54 GiB)**이다. 따라서 “largest LAMP experiment”가 64 GiB면 충분하다고 읽히지 않게 구분해야 한다.

권장 추가 문구:

> The full GPT-2 matmul-only benchmark at sequence length 2^10 used approximately 100.44 GB peak RSS in our reference run. We recommend at least 128 GiB of memory available to the container for this experiment; the original evaluation used 256 GB RAM. Smaller sequence lengths may be used for a preliminary run, with their resource requirements reported separately.

128 GiB는 여유를 둔 권장치이며 실제 최소 요구량을 검증한 수치는 아니다. Docker Desktop에서는 호스트 RAM 외에 VM에 할당된 메모리도 확인해야 한다.

또한 Freivalds 범위 실행의 기본 상한은 `K=2^13`이다. 제출 폼 스스로 이 설정은 256 GB에서도 OOM이라고 명시하므로, 평가용 명령은 기본적으로 `--to 12`까지로 제한하고 `2^13`은 알려진 실패 사례로 분리하는 것이 좋다.

### 2.5 총 실행 시간 및 빌드 네트워크

README에는 설치·전체 평가 예상 시간과 1일 이내의 추천 실험 묶음이 없다. 작은 동작 확인과 본 평가를 구분하고 각각의 예상 시간·메모리를 적는다. Dockerfile이 베이스 이미지와 Go 모듈을 다운로드하므로 최초 빌드에는 인터넷 연결이 필요하다는 점도 명시한다.

## 3. 입력값 및 공개 메타데이터 정리

- HotCRP Authors의 네 명 이메일 입력칸이 비어 있다. Contacts 등록과 별개이므로 저자 이메일을 채운다.
- Additional questions가 모두 미선택이다. 현재 설명상 앞의 조건들이 적용되지 않는다면 `None of the statements apply`를 선택한다.
- Abstract는 optional이므로 공란 자체는 문제 아니다.
- PC conflicts는 전부 미선택이다. 실제 공동연구/지도관계가 없다면 문제 없지만 각 저자가 확인해야 한다.
- Zenodo creators가 `ByeongKyu_Han1`, `anonymouscommitter`로 표시된다. 실제 아티팩트 기여자를 기준으로 실명·소속을 정리하면 인용과 식별이 명확해진다. 논문 저자와 아티팩트 기여자가 반드시 동일해야 한다는 뜻은 아니다.
- Zenodo에는 CC BY 4.0이 표시되지만 ZIP 최상위에는 LAMP 자체의 LICENSE 파일이 없다. 프로젝트에 적용할 라이선스를 README/LICENSE에 명확히 적고 포함된 gnark의 라이선스 고지는 유지한다.

## 동료에게 전달할 요약

> Zenodo 공개와 Docker 패키징은 확인했어. 우선 HotCRP가 아직 draft이고 Available만 체크되어 있으니 목표 배지와 최종 제출 상태를 확인해줘. 실행 검증까지 받을 거라면 깨끗한 환경에서 빌드/작은 실험을 확인하고 Functional도 신청하는 게 좋겠어. 재현 문서는 ① DualMatrix 포함 여부와 범위, ② 10회 반복 결과 보존 및 평균 계산, ③ 기준 CSV·예상 출력과 표 대응, ④ GPT-2 약 100 GB peak memory, ⑤ 1일 이내 평가 명령/소요 시간을 보완해줘. 업로드 PDF가 최종 accepted revision인지도 확인 부탁해.

## 근거

- [AE 제출 페이지](https://cycle1-ae.sp2027.ieee-security.org/paper/35)
- [Zenodo 공개 아티팩트](https://zenodo.org/records/22819192)
- [해당 GitHub 릴리스 소스](https://github.com/Han-16/LAMP/tree/v1.0.0-artifact)
- [S&P 2027 공식 AE 지침](https://sp2027.ieee-security.org/artifact_instructions.html)
