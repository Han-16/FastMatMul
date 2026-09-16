Shepherd께,

저희 논문 #1646, 「LAMP: Linear Verification of Matrix Multiplication via Proximity Testing」에 대한 프로그램 위원회의 의견과 shepherding에 감사드립니다. DualMatrix 외의 최신 기법과의 성능 비교 범위에 관한 Noteworthy Concern 1을 다루기 위해 논문을 수정하고자 합니다.

Interactive rebuttal에서 제출한 수정본에는 이미 zkMatrix, DualMatrix, zkMaP와의 점근적 복잡도 비교 및 DualMatrix와 Freivalds 기반 SNARK baseline에 대한 실험이 포함되어 있습니다. 이에 더해 다음과 같은 수정을 제안드립니다.

**1. Section 2와 Table 1의 비교 범위를 확장하고 비교 조건을 명확히 하겠습니다.** 공개 구현이 있는 *Scalable zkSNARKs for Matrix Computations: A Generic Framework for Verifiable Deep Learning* (Evalyn)을 포함해 추가 관련 연구를 검토하겠습니다. 각 시스템이 증명하는 명제, commitment 인터페이스, setup 및 보안 가정, 복잡도 비교에 포함되는 비용을 명확히 설명하겠습니다. 이를 통해 LAMP의 회로 제약 수 감소와 전체 prover 작업량을 구분하겠습니다.

**2. Section 7에 추가 실험 비교를 포함할 수 있는지 검토하겠습니다.** Evalyn의 공개 구현으로 LAMP와 비교 가능한 행렬 곱 workload를 구성할 수 있는지 확인하겠습니다. 입력 commitment, 증명 생성, 검증, 통신 비용을 명시적으로 집계하고 조건을 맞춘 비교를 목표로 합니다. 우선 증명 관계와 파라미터, 측정 범위가 서로 대응하는지 확인하겠습니다. 비교 가능한 실험을 구성할 수 있다면 조건을 맞춰 측정 결과를 추가하고, 남아 있는 차이도 공개하겠습니다. 그렇지 않은 경우에는 구체적인 제약을 설명하고, 기존 논문에 보고된 결과를 해당 실험 조건과 함께 별도로 논의하겠습니다. 서로 다른 논문의 실행 시간을 단순히 나눈 값을 동일 조건에서의 성능 향상으로 제시하지 않겠습니다.

**3. 성능에 관한 결론의 적용 범위를 명확히 하겠습니다.** 필요에 따라 초록, 기여 목록, 평가 논의, 결론을 수정하여 실험에서 관측한 이점이 평가한 baseline과 workload에 대한 것임을 명시하겠습니다. 또한 증명 생성 시간, 검증 시간, 증명 크기 사이의 trade-off를 분명하게 설명하겠습니다. GPT-2 행렬 곱 workload에 대한 평가와 전체 추론 과정의 검증 사이의 차이도 명확히 하겠습니다.

제안한 수정 범위가 해당 우려를 적절히 다루는지, 우선적으로 비교하기를 권하시는 특정 시스템이 있는지 의견을 부탁드립니다. 10월 9일의 거의 최종인 원고 승인 목표 전에 피드백을 반영할 수 있도록, 10월 2일까지 수정 원고, 변경 사항을 표시한 diff, response letter를 제공하는 것을 목표로 하겠습니다. 이후 수정본에 제시된 근거를 바탕으로 해당 우려의 재검토를 요청드리고자 합니다.

감사합니다.
저자 일동

추가 비교 후보에 관한 참고 자료:

- [논문](https://eprint.iacr.org/2025/1646)
- [공개 구현](https://github.com/mirandaprivate/evalyn_asiacrypt)
