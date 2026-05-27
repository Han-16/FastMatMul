# FastMatMul S&P 2027 Submission Review v13

검토일: 2026-05-26  
대상: 최신 `FastMatMul/main.tex`, `main.pdf`, build artifacts  
기준: IEEE S&P 2027 CFP 및 submission instructions

## Overall Recommendation

**현재 상태: 포맷 No-Go는 해소. 기술적으로는 Borderline / Weak Reject.**  
지난 v12의 가장 큰 문제였던 page-limit violation은 해결되었다. 이제 즉시 desk reject될 포맷 문제는 보이지 않는다. 다만 S&P crypto/system reviewer 기준에서는 CP-link/QA-NIZK batching 정의와 key/CRS accounting이 아직 약해서, 제출 전 최소 보강이 필요하다.

**S&P-style score:** 3.3 / 5, Borderline Weak Reject  
**Reviewer confidence:** 4 / 5  
**핵심 이유:** 논문은 이제 “checking layer over certified roots”로 일관되지만, 핵심 backend가 여전히 assumption-heavy하고 artifact/proof-size boundary가 reviewer에게 공격받기 쉽다.

## 1. S&P 2027 Format Check

### Page limit: now compliant

S&P 2027 공식 page rule은 “up to 13 pages of text and up to 5 pages for references and appendices, totaling no more than 18 pages”이며, page 13 이후의 text/figures는 appendix로 명확히 표시되어야 한다. 현재 빌드 결과는:

- `main.pdf`: **17 pages**
- Section 6 `Implementation and Evaluation`: page 12-13
- Section 7 `Conclusion and Related Work`: page 13
- References: page 13
- Appendix A: page 14
- Appendix B: page 15
- Appendix C: page 16-17

따라서 v12의 hard format violation은 해소되었다. 현재 구조는 S&P page rule을 만족한다.

### Template / required sections

- `\documentclass[conference,compsoc]{IEEEtran}` 사용: OK.
- `kotex` 제거: OK.
- Anonymous title page: OK.
- Ethics section: OK. 이제 `None.`보다 낫고, human subjects/live systems/vulnerability disclosure가 없음을 설명한다.
- LLM usage section: OK. S&P의 generative AI disclosure 취지와 맞는다.
- PDF metadata: `strings main.pdf` 기준 local username은 보이지 않고, `/Author()`가 비어 있다.

### Administrative risk: artifact anonymity

`FastMatMul/main.fls` line 1에 `PWD /Users/kyeongtae/FastMatMul/Paper`가 남아 있다. `.fls`, `.fdb_latexmk`, `.log`, `.aux`, `.blg`, `.out`, `.DS_Store` 같은 build artifacts를 artifact repository에 포함하면 anonymization risk가 생긴다. S&P는 artifact repository도 익명화해야 한다고 명시하므로, 제출 artifact에는 source/PDF와 필요한 재현 스크립트만 남기고 로컬 경로가 들어간 산출물은 제거해야 한다.

## 2. Critical Technical Issues

### C1. CP-link/QA-NIZK theorem is improved but still underspecified

`Contents/construction.tex`에 Concrete CP-link backend theorem이 추가된 것은 좋은 수정이다. 그러나 현재 theorem은 다음을 “구체 instantiation”이라기보다 assumption으로 둔다.

- Pedersen handle parameters are generated so that vector handle commitment is binding
- QA-NIZK link proof is sound
- batching challenge is sampled by Fiat-Shamir

이 정도면 modular assumption으로는 가능하지만, 논문이 “current QA-NIZK implementation”과 “128-byte batched CP-link proof”를 핵심 평가 결과로 쓰기에는 아직 설명이 부족하다. 특히 QA-NIZK가 preliminaries에서 정의되지 않고, 구체 construction/citation/CRS model이 없다. S&P crypto reviewer는 여기서 “what exactly is the backend?”라고 물을 가능성이 높다.

**필요 수정:** main text에서는 theorem 이름을 “Concrete”로 강하게 부르기보다, “Batched CP-link backend assumption/instantiation”처럼 낮추거나, 실제 QA-NIZK construction과 CRS/generator generation model을 3-5문장으로 명시해야 한다. Appendix에는 QA-NIZK statement, witness, CRS, proof size가 왜 128B인지 적어야 한다.

### C2. Batched CP-link transcript is not fully pinned down

Appendix B의 batching equation은 핵심 보강이지만, line-level로 아직 불명확하다.

- `appendix.tex`의 batching challenge가 `Hash(FMM-link-batch, T, {Gamma_q,L_q})`를 사용하지만, 여기서 `T`가 정의되지 않는다.
- per-object tag `T_{chi,j}`와 batch tag가 어떤 관계인지 명확하지 않다.
- Construction/protocol figure는 여전히 `{tau_{chi,j}}`를 aux로 보내는 형식이고, theorem/evaluation은 하나의 `tau_I`를 말한다.

이건 사소한 표기 문제가 아니라, 128B proof-size claim과 transcript-binding soundness를 연결하는 부분이다.

**필요 수정:** batch statement를 하나로 정의한다. 예를 들어 `T_I = Hash(FMM-link-batch, Cm_ABC, Cm_XYZ, I, {(chi,j,Gamma_{chi,j},L_{chi,j})})`처럼 쓰고, protocol figure의 aux를 `{L,pi}_{chi,j}, tau_I`로 바꾼다. Security theorem에서는 `epsilon_link = epsilon_ped + epsilon_QA + Q/|F|`를 명시적으로 연결한다.

### C3. Key/CRS size remains a main evaluation weakness

논문은 이제 proof-size claims를 “online proof excluding setup/key/CRS material”로 낮췄다. 이 수정은 정확하다. 그러나 S&P systems/crypto reviewer에게는 여전히 다음 질문이 남는다.

- CP-link/Pedersen generator material은 seed-derived인가, serialized인가?
- Groth16 proving/verifying keys는 baseline과 비교해 어느 정도인가?
- setup/key/CRS가 proof-size win을 상쇄하지 않는가?

현재 `evaluation.tex`와 Appendix C는 key/CRS size를 “not reported”로 남긴다. 정직한 disclosure라서 reject-level inconsistency는 아니지만, acceptance risk는 크다.

**필요 수정:** 제출 전 시간이 있으면 최소 2개 row만이라도 byte 단위로 추가한다: `k=1024`, `k=4096`의 Groth16 proving key, verifying key, CP-link public parameters/CRS. 측정이 불가능하면 abstract/introduction의 proof-size 문장을 모두 “online proof bytes”로 통일한다.

### C4. Raw-input certification gap is now well disclosed but still a scope risk

raw-input certification이 out of scope임을 abstract, introduction, evaluation, conclusion이 반복해서 밝히고 있다. 이 점은 충분히 개선되었다. 다만 S&P reviewer가 verifiable ML motivation을 강하게 읽으면, “the measured result is not end-to-end VC”라는 비판은 여전히 가능하다.

현재로서는 이 문제를 더 구현으로 닫기 어렵다면, claim scope를 유지하는 것이 최선이다. 제목과 abstract가 이미 “checking layer”로 되어 있으므로, 이 방향은 맞다.

## 3. Consistency Check

전체 consistency는 v12보다 좋아졌다. 특히 page budget 때문에 Related Work를 Conclusion과 합치고 상세 tables를 appendix로 보낸 결정은 제출판에는 적절하다.

남은 consistency issue는 다음이다.

1. **`tau_{chi,j}` vs `tau_I`:** notation table, relation, protocol figure는 per-object proof를 보내는 것처럼 보이고, theorem/evaluation은 one batched proof를 말한다. “logical per-link proof”와 “serialized batch proof”를 구분하는 문장이 있지만, protocol figure까지 반영하지 않으면 reviewer가 proof-size table을 의심할 수 있다.
2. **`epsilon_link` mapping:** main security theorem은 `epsilon_cc <= epsilon_msg + epsilon_link`라고 쓰고, Concrete CP-link theorem은 `epsilon_ped + epsilon_QA + Q/|F|`를 준다. 이 둘을 한 문장으로 연결해야 한다.
3. **`T` undefined in Appendix B:** batch challenge의 `T`가 정확히 무엇인지 정의되지 않는다.
4. **Old `Protocols/` files remain stale:** `FastMatMul/Protocols/protocol.tex`와 `protocol_cp.tex`는 현재 `main.tex`에 input되지 않지만, artifact repository에 포함되면 이전 protocol/relation처럼 보인다. 제출 artifact에서는 제거하거나 `attic/legacy-not-submitted/`로 분리해야 한다.
5. **Intro proof-size wording:** abstract는 “online proof excluding setup/key/CRS”라고 정확히 쓰지만, introduction bullet은 “Proof sizes are 104 KB...”라고만 쓴다. 여기에도 “online” 또는 “excluding key/CRS”를 붙이는 것이 안전하다.

## 4. Typos, Build Warnings, and Minor Errors

치명적인 LaTeX error, undefined citation, undefined reference는 보이지 않는다.

남은 제출 전 정리 항목:

- `main.log`에는 `cryptocode` command redefinition warning과 다수의 underfull box warning이 있다. desk reject 사유는 아니지만 최종 PDF 육안 확인은 필요하다.
- Appendix B의 undefined `T`는 typo처럼 보이지만 보안 transcript 정의와 연결되므로 critical consistency issue로 봐야 한다.
- `main.fls`의 local path leak은 artifact anonymization issue다.
- PDF metadata는 `strings` 기준 author/title이 비어 있고 local username은 보이지 않는다.

## Required Fixes Before Submission

1. Batch CP-link statement를 명확히 정의하고 `T`를 제거하거나 정의한다.
2. Protocol figure/notation을 `tau_I` batched proof와 일치시킨다.
3. `epsilon_link = epsilon_ped + epsilon_QA + Q/|F|` 연결 문장을 security theorem 또는 직후에 넣는다.
4. QA-NIZK backend의 construction/citation/CRS model을 최소한 preliminaries 또는 Appendix B에 추가한다.
5. Introduction의 proof-size 문장을 “online proof bytes excluding key/CRS”로 통일한다.
6. Artifact 제출본에서 `.fls`, `.fdb_latexmk`, `.log`, `.aux`, `.blg`, `.out`, `.DS_Store`, stale `Protocols/` draft files를 제거한다.

## Bottom Line

이제 포맷 때문에 바로 떨어질 상태는 아니다. 제출까지 시간이 없다면, 가장 높은 ROI는 **CP-link batching 표기 정리 + `epsilon_link` 연결 + artifact anonymization 정리**다. key/CRS size까지 측정하면 점수가 올라가지만, 시간이 없으면 최소한 모든 headline proof-size claim을 “online proof excluding key/CRS”로 엄격히 제한해야 한다.

공식 기준:

- S&P 2027 CFP: https://sp2027.ieee-security.org/cfpapers.html
- S&P 2027 submission instructions: https://sp2027.ieee-security.org/cfsubmission.html
