# Quality Check — 100-Point Rubric

## Evidence Boundary

- **Account-observed pattern / 계정 관찰 패턴:** 승인된 공개 게시물의 54개 고유 프롬프트·42개 계열 표본에서 관계형 구성, 제작 동작, 역할·면적 기반 색, 구성적 타이포그래피와 표적 제한이 관찰되었다. 보존 우선 구조는 후기 참고사진 변환 13개·한 계열에 집중되었으며, 넓은 `유지` 표현 47/54는 참고 이미지 보존 성능을 뜻하지 않는다. 이는 계정 소유자의 의도나 공식 채점법을 뜻하지 않는다.
- **Analyst generalization / 분석자 일반화:** 아래 100점 루브릭과 사전 점검은 그 관찰을 평가 가능한 프로젝트 권장안으로 바꾼 것이다. 모든 게시물에 공통인 사실이나 공식 알고리즘이 아니다.
- **Low-evidence extension / 근거가 약한 확장 적용안:** 강한 계정별 표본이 없는 유형에 이 평가법을 적용할 때는 확장 라벨을 유지한다. 그 결과를 확립된 계정 패턴으로 소개하지 않는다.

## Scoring Rubric

각 항목은 배점 범위 안에서 독립적으로 채점한다. 관계가 보이도록 구체화한 정도를 평가하며, 막연한 품질 형용사를 많이 쓴 것 자체에는 점수를 주지 않는다. 총점은 정확히 **100점**이다.

| Criterion | Points |
| --- | ---: |
| Purpose clarity | 10 |
| Subject clarity | 10 |
| Scene construction | 10 |
| Composition clarity | 10 |
| Color and light consistency | 10 |
| Material and texture specificity | 8 |
| Style consistency | 8 |
| No conflicting instructions | 10 |
| No redundant modifiers | 6 |
| Output conditions | 6 |
| Appropriate restrictions | 6 |
| Model suitability | 6 |

### Item Guidance

- **Purpose clarity (10):** 사용처와 성공 기준이 분명하고 장면 선택에 실제로 영향을 주는가.
- **Subject clarity (10):** 주제와 초점이 명확하며, 반드시 유지할 정체성·형태·구조·문구가 특정되어 있는가.
- **Scene construction (10):** 첫눈에 읽힐 장면과 대비가 위치, 크기, 겹침, 가장자리 같은 관찰 가능한 관계로 구성되었는가.
- **Composition clarity (10):** 축, 비율, 배치, 가림, 여백과 정보 밀도가 서로 모순 없이 설명되었는가.
- **Color and light consistency (10):** 색 개수, 역할, 대략적 면적과 빛의 방향이 하나의 일관된 체계인가.
- **Material and texture specificity (8):** 재료의 표면과 반응, 제작 동작 또는 렌더링 특성이 결과에서 확인 가능하게 적혔는가.
- **Style consistency (8):** 스타일 이름이 제작 동작과 시각 관계로 변환되었고 목적·주제·마감이 같은 방향을 가리키는가.
- **No conflicting instructions (10):** 충돌을 드러내고 must-keep, 목적, 보조 스타일 순으로 해결했으며 선택한 해결을 밝혔는가.
- **No redundant modifiers (6):** 같은 뜻의 형용사나 지시를 반복하지 않고 각 열 블록이 구별되는 일을 하는가.
- **Output conditions (6):** 형식, 개수, 화면비, 독립 출력/콜라주 상태와 보존 요구가 정확히 유지되는가.
- **Appropriate restrictions (6):** 네거티브가 예상 실패에만 한정되고 긍정 지시와 충돌하지 않으며 불필요하게 강제되지 않는가.
- **Model suitability (6):** 모델 경계를 지키고, 직접 지원이 확인되지 않은 문법은 자연어와 `확인 불가`로 처리했는가.

## Score Bands

- `90–100 excellent`
- `80–89 usable`
- `70–79 revise`
- `below 70 rebuild`

80점 미만이면 낮은 항목부터 고친 뒤 전체 충돌을 다시 확인한다. 점수대 이름은 출판 가능성의 보증이 아니라 수정 우선순위를 정하는 기준이다.

## Mandatory Preflight

- [ ] 적용 가능한 10개 블록이 모두 있으며 각 블록의 역할이 중복되지 않는다.
- [ ] 모호한 스타일·품질 단어를 보이는 관계 또는 제작 동작으로 바꿨다.
- [ ] 제공되지 않은 문구를 만들지 않았다. no-text 요청에는 임의의 텍스트, 숫자, 로고, 워터마크, 서명, 라벨이 없다.
- [ ] 비사진 작업에 카메라나 렌즈 세부사항을 강제로 넣지 않았다.
- [ ] 사용자 또는 실제 첨부 이미지로 근거가 확인된 보존 요구만 사용했다. 그런 요구가 있으면 보조 스타일보다 먼저 두고 **must-keep → purpose → supporting style** 우선순위로 충돌을 해결했으며 선택한 해결을 밝혔다. 참고 이미지가 없으면 이미지 기반 보존 조건을 추정하지 않았다.
- [ ] 네거티브는 예상 실패에만 한정하고 긍정 지시와 모순되지 않으며, 선택 사항으로 두고 맹목적으로 강제하지 않았다.
- [ ] 모델 전용 문법은 직접 지원됨이 확인되었다. 그렇지 않으면 모델 중립 자연어를 쓰고 `확인 불가`를 표시했다.
- [ ] 모호한 요청이면 정확히 네 개의 완성된 방향이 있다. 모든 방향 쌍은 승인된 일곱 축(**medium, layout, color, typography, texture, mood, rendering**) 중 최소 네 축에서 다르며, 색·제목·형용사만 바꾼 차이는 세지 않았다.
- [ ] **Low-evidence extension / 근거가 약한 확장 적용안** 템플릿을 사용했다면 확장 라벨이 최종 출력에도 보인다.

최종 점검에서는 형식, 개수, 콜라주 상태, must-keep 요구와 모델 경계가 모두 보존되었는지 루브릭 점수와 별도로 다시 확인한다.

## Reference-Image Preflight Gate

참고 이미지를 사용하는 작업은 기존 100점 프롬프트 루브릭과 별도로 아래 항목을 모두 통과해야 한다. 하나라도 빠지면 점수와 관계없이 수정한다.

- [ ] 모든 첨부물이 content source, style-layout target, generated result, region-mask 중 하나로 구분되어 있다.
- [ ] content source가 정체성을 우선 통제하고, target이 source의 피사체를 대체하지 않는다.
- [ ] preserve / transform / ignore 목록이 서로 섞이지 않는다.
- [ ] 참고에 QR, 바코드, UI, 워터마크, 무관한 간판이나 작은 글자가 보이는 경우에만 옮길지 제거할지가 명시되어 있다.
- [ ] 분할 구성을 사용하는 경우에만 비율의 합이 100%이며 경계 위치가 하나뿐이다.
- [ ] `정확히`라고 쓴 화면비·비율·여백·경계 수치는 사용자 입력 또는 접근 가능한 파일·픽셀 측정에서 나온 값이며, 눈대중 값은 `약`으로 표시되어 있다.
- [ ] 피사체 수, 구조 단계 수, 제목 줄 수와 보조 라벨 수가 필요한 경우 정확히 하나의 값으로 고정되고 사용자 입력·관찰한 개수·디자인 선택 중 출처가 구분되어 있다.
- [ ] 타이포그래피를 사용하는 경우에만 제목 앵커, 정렬, 점유 면적과 보호 여백이 단일 geometry contract에 들어 있다.
- [ ] 보이지 않는 재료·브랜드·내부 구조를 사실처럼 단정하지 않는다.
- [ ] 생성 결과 비교라면 성공한 요소와 실패한 요소를 분리하고 실패 블록만 수정한다.

## Optional Visual Fidelity Rubric

사용자가 **서로 다른 이미지 두 개 이상**, 즉 생성 결과와 비교할 참고 또는 타깃을 함께 제공하고 비교를 요청한 경우에만 사용한다. 이미지가 없거나 한 장뿐이면 시각 유사도는 `N/A`이며, 프롬프트 분석 점수나 한 장의 인상 평가로 대체하지 않는다. 이 점수는 현재 제공된 이미지 쌍의 가시적 일치도를 설명할 뿐 모델 성능, 예상 품질, 성공률 또는 다음 생성의 보증으로 표현하지 않는다.

채점 전에 preserve / transform / ignore 계약을 기준으로 적용 항목을 선택한다. 요청에서 사용하지 않는 항목은 0점 처리하지 말고 `N/A`로 표시한다. 각 축의 재정규화 점수는 `획득한 적용 항목 점수 합 ÷ 적용 항목 최대점 합 × 100`으로 계산한다. 적용 항목이 하나도 없으면 그 축 전체를 `N/A`로 둔다. 예를 들어 no-text 작업의 타이포그래피, 배경 변경이 허용된 작업의 원본 배경색, 조명 변경이 허용된 작업의 원본 빛은 보존도 감점 대상이 아니다.

### A. Target Design Reproduction — 100 points

| Criterion | Maximum | Apply when |
| --- | ---: | --- |
| Layout and geometry contract | 25 | target or user controls layout |
| Semantic composition and subject relationships | 20 | target controls composition |
| Medium and material treatment | 20 | medium or material transfer is requested |
| Palette, light, and finish | 20 | target controls any of these fields |
| Typography and information hierarchy | 15 | requested text exists, or target typography is explicitly authorized under transform; always N/A for a no-text contract even if the target contains type |

### B. Content-Source Preservation — 100 points

| Criterion | Maximum | Apply when |
| --- | ---: | --- |
| Subject identity and required subject count | 30 | always for a content source |
| Pose, proportions, orientation, and viewpoint | 25 | listed under preserve |
| Required subject/background relationships | 20 | listed under preserve |
| Protected visible color, material, logo, or text | 15 | explicitly listed under preserve |
| Distortion, omission, and unsupported-invention suppression | 10 | always for a content source |

각 축은 기본적으로 따로 보고한다. 사용자가 종합점수를 명시적으로 요구한 경우에만 가중치를 먼저 공개한 뒤 계산한다. 그 경우에도 **모든 명시적 must-keep 항목**(예: 정체성, 피사체 수, 포즈, 관찰 방향, 로고, 정확한 문구, 색 배치, 출력 기하)의 실패 또는 명시적 금지 요소의 생성은 평균으로 상쇄하지 않고 별도의 **FAIL gate**로 표시한다. 평가자는 적용/비적용 판정, 항목별 가시적 근거, 가장 큰 차이와 신뢰도를 함께 기록한다. 원본 파일을 확인할 수 없거나 시각 추정만 가능한 값은 신뢰도를 낮춘다.
