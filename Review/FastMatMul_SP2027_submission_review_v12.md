# FastMatMul S&P 2027 Submission Review v12

검토일: 2026-05-26  
대상: `FastMatMul/main.tex`, 최신 `FastMatMul/main.pdf` 빌드 산출물  
기준: IEEE S&P 2027 CFP 및 submission instructions

## Overall Recommendation

**현재 상태: 제출 전 No-Go.**  
기술 원고는 이전보다 훨씬 정리되었지만, 현재 PDF는 S&P 2027 page rule을 만족하지 않는다. 이 상태로는 기술 리뷰 전에 desk reject 위험이 있다.

**S&P-style score:** 2.5 / 5, Weak Reject  
**Reviewer confidence:** 4 / 5  
**핵심 이유:** 포맷 위반이 즉시 수정되어야 하고, CP-link/QA-NIZK 백엔드의 구체 보안 정리와 batched proof 설명이 아직 제출판 기준으로 충분히 닫혀 있지 않다.

## 1. S&P 2027 Format Check

### Hard violation: main text exceeds 13 pages

S&P 2027 공식 안내는 제출 논문을 최대 13쪽의 본문과 최대 5쪽의 references/appendices, 총 18쪽으로 제한한다. 또한 13쪽 이후의 text/figures는 appendix로 명확히 표시되어야 한다. 공식 안내는 template 위반이나 page-limit 위반은 review 없이 reject될 수 있다고 명시한다.

현재 `main.log` 기준 PDF는 **18 pages**라서 총량은 맞지만, `main.aux` 기준 본문 구조가 다음과 같다.

- Section 6 `Implementation and Evaluation`: page 12-14
- Table 4-6: page 14
- Section 7 `Related Work`: page 14
- Table 7: page 15
- Section 8 `Conclusion`: page 15
- References: page 15
- Appendix A: page 16

따라서 **Related Work, Conclusion, 일부 evaluation tables가 page 13 이후에 있지만 appendix가 아니다.** 현재 상태는 S&P submission format에 맞지 않는다.

**수정 우선순위:** 모든 non-appendix 본문을 page 13 안에 끝내야 한다. References는 page 14부터 시작해도 되지만, Conclusion까지는 page 13 안에 들어와야 한다. Table 4-7 중 상세 accounting 성격의 표는 appendix로 이동하고, Related Work는 0.5 column 수준으로 압축하는 것이 가장 빠른 해결책이다.

### Template/anonymity/required sections

- `\documentclass[conference,compsoc]{IEEEtran}`는 올바르다.
- 익명성은 title page 기준으로는 맞다.
- `Ethics considerations`에 `None.`을 둔 것은 공식 안내와 충돌하지 않는다. 다만 S&P는 왜 ethics issue가 없는지 간단히 설명하는 것을 권장하므로, 여유가 있으면 1문장 추가가 좋다.
- `LLM usage considerations`는 명시되어 있어 제출 리스크를 줄인다.
- `Styles/packages.tex`의 `\usepackage{kotex}`는 불필요한 포맷 리스크다. 논문이 영어 원고이고 S&P template compliance가 중요한 상황이므로 제거하는 편이 안전하다.

## 2. Critical Technical Issues

### C1. CP-link/QA-NIZK backend is still a core assumption, not a fully closed theorem

`Contents/construction.tex`는 CP-linked sampled-opening backend를 정의하고, Pedersen-style handle에서 `Gamma - L = Delta H`를 증명하는 구체 instantiation을 제시한다. 이 방향은 맞다. 그러나 S&P crypto reviewer 기준에서는 다음이 아직 충분히 닫혀 있지 않다.

- `epsilon_link`가 어떤 구체 가정에서 나오는지 lemma/theorem 형태로 정리되어 있지 않다.
- multi-generator Pedersen handle의 binding assumption, generator derivation, CRS/setup model, QA-NIZK soundness, Fiat-Shamir 적용 여부가 하나의 concrete backend theorem으로 연결되어 있지 않다.
- 논문은 per-object proof `tau_{chi,j}`를 정의하지만 evaluation은 768 sampled objects에 대해 **batched CP-link proof = 128 B**로 보고한다. 이 batching relation, batching challenge, soundness loss, 실패확률 union bound가 formal하게 설명되어야 한다.

**필요 수정:** “Concrete CP-link instantiation theorem”을 짧게라도 추가해야 한다. 증명은 appendix로 보내도 되지만, main text에는 statement와 assumptions를 남겨야 한다. 시간이 부족하면 적어도 128 B claim을 “batched QA-NIZK proof under the following backend assumption”으로 명확히 낮춰야 한다.

### C2. End-to-end raw input certification gap remains an acceptance risk

원고는 이제 “checking layer over certified roots”라고 매우 명확히 밝히고 있다. 이 점은 개선되었다. 하지만 S&P reviewer는 GPT-2/VC motivation을 보고 여전히 end-to-end cost를 물을 가능성이 높다.

현재 artifact는 raw matrices 또는 per-request activations/outputs에서 certified encoded roots를 생성하고 검증하는 비용을 측정하지 않는다. `Deployment bound for root certification`은 좋은 방어 논리지만, 실제 instantiation이 없으면 “speedup is only for a subcomponent”라는 약점이 남는다.

**필요 수정:** 시간이 부족하면 full implementation보다 다음 중 하나를 넣는 것이 현실적이다.

- static weight roots와 per-request activation roots를 분리한 threat/deployment model을 더 선명하게 제시한다.
- root certification cost가 online win을 지우지 않는 충분조건을 abstract/introduction/evaluation conclusion에 반복해서 일관되게 둔다.
- “end-to-end VC”가 아니라 “matrix-multiplication checking layer”라는 표현을 제목, abstract, conclusion에서 끝까지 유지한다.

### C3. Setup/key/CRS size omission weakens the proof-size/scalability claim

Evaluation은 proof size를 강하게 주장하지만, setup table은 key/CRS size를 “Not reported”로 남긴다. 특히 CP-link setup이 `d_max = k` handle parameters를 사용하고, direct serialization이면 `(k+1)|G|` 규모가 된다고 직접 인정한다.

S&P reviewer는 proof size가 작아진 대신 CRS/key material 또는 setup assumptions로 비용이 이동한 것인지 확인하려고 할 것이다.

**필요 수정:** 최소한 `k=1024`와 `k=4096`에 대해 proving key, verifying key, CP-link parameter/CRS size를 byte 단위로 보고해야 한다. 구현에서 seed-derived generators라면 seed size와 derivation assumption을 명시한다.

## 3. Consistency Check

전체 framing은 이전보다 일관적이다. Abstract, Introduction, Construction, Security, Evaluation이 모두 “certified roots 위의 checking layer”로 정렬되어 있다. raw sampled matrix columns가 serialized proof bytes가 아니라 Groth16 witness라는 설명도 이제 반복적으로 일관된다.

남은 consistency 문제는 다음 네 가지다.

1. **CP-link transcript tag가 세 군데에서 다르다.** Definition은 `Hash(FMM-link, para, {cm_chi}, mu_x, mu_y, mu_z, r, I, chi, j, Gamma, L)` 형태이고, protocol/security text는 `Hash(FMM-link, Cm_ABC, Cm_XYZ, I, chi, j, Gamma, L)` 형태다. 같은 relation을 주장하려면 tag definition을 하나로 통일해야 한다.
2. **Per-link proof와 batched proof가 섞여 있다.** Construction은 `tau_{chi,j}`를 per sampled object로 정의하지만, Evaluation은 aggregate/batched CP-link proof가 128 B라고 말한다. 이 둘을 연결하는 batching layer가 필요하다.
3. **Strict 128-bit parameter wording이 약간 흔들린다.** Security/Evaluation은 conservative per-term target에 `t=133`을 쓰고, appendix parameter table은 proximity-only target처럼 `t=130`을 말한다. “proximity-only”와 “aggregate per-term budget”을 명확히 구분해야 한다.
4. **Old protocol files are stale if artifact is submitted.** `Protocols/protocol.tex`는 현재 `main.tex`에 input되지 않지만, artifact repository에 포함되면 예전 relation/protocol처럼 보일 수 있다. 제출 artifact에서 제거하거나 “unused legacy draft”로 분리해야 한다.

## 4. Typos, Build Warnings, and Minor Errors

치명적인 LaTeX error, undefined citation, undefined reference는 보이지 않는다. 다만 제출 직전에는 다음을 정리하는 것이 안전하다.

- `\usepackage{kotex}` 제거 권장. 영어 S&P 원고에는 불필요하고 template/font risk를 만든다.
- `main.log`에 `Underfull \hbox/\vbox` 경고가 많다. desk reject 사유는 아니지만, page-limit 압축 후 표와 figure caption이 깨지는지 PDF 육안 확인이 필요하다.
- `cryptocode` 관련 “already defined” warning이 있다. 현재 빌드는 성공하지만, camera-ready 전에는 package conflict 여부를 확인하는 편이 좋다.
- Ethics section의 `None.`은 허용 가능하지만, “This work uses synthetic/local benchmark data and does not involve human subjects, live systems, or vulnerability disclosure.” 정도의 짧은 설명이 reviewer 판단을 돕는다.

## Required Fixes Before Submission

1. **Page-limit fix first.** Conclusion까지 page 13 안에 끝내고, 상세 accounting tables는 appendix로 이동한다.
2. **CP-link concrete backend theorem 추가.** Assumptions, batching, soundness loss, CRS/setup model을 명시한다.
3. **Per-link vs batched 128 B proof claim 정리.** Evaluation의 128 B가 무엇을 aggregate하는지 formal relation과 연결한다.
4. **CRS/key/setup size를 byte 단위로 보고하거나 claim을 낮춘다.**
5. **Transcript tag 정의를 하나로 통일한다.**

## Bottom Line

내용 자체는 제출판에 가까워졌지만, 현재 상태로는 **S&P format 위반 때문에 제출하면 안 된다.** 포맷을 고친 뒤에도 CP-link batching과 CRS/key-size accounting을 닫지 않으면, crypto/system reviewer가 “핵심 비용을 backend assumption으로 밀었다”고 판단할 가능성이 높다.

공식 기준:

- S&P 2027 CFP: https://sp2027.ieee-security.org/cfpapers.html
- S&P 2027 submission instructions: https://sp2027.ieee-security.org/cfsubmission.html
