# Templates

## How to Use These Templates

이 템플릿은 복사된 프롬프트나 고정된 시각 프리셋이 아니라, 사용자가 채우는 작성 뼈대다. 먼저 목적과 사용자가 명시했거나 실제 첨부 이미지에서 확인되는 보존 조건을 채우고, 적용되지 않는 항목은 생략한다. 참고 이미지가 없으면 이미지 기반 보존 조건을 추정하지 않는다. 특히 글자가 필요하지 않으면 타이포그래피를 억지로 넣지 않는다. 출력 전에는 [quality-check.md](quality-check.md)를 실행한다.

- **Account-observed pattern / 계정 관찰 패턴:** 공개 게시물의 54개 고유 프롬프트·42개 계열 표본에서 관계형 구성, 제작 동작, 역할·면적 기반 색, 필요한 경우의 구성적 타이포그래피와 표적 제한이 관찰되었다. 보존 우선 구조는 후기 참고사진 변환 13개·한 계열에 집중되었으며, 넓은 `유지` 표현 47/54를 참고 이미지 보존 능력으로 해석하지 않는다. 이는 계정 소유자의 의도나 공식 방법에 대한 주장이 아니다.
- **Analyst generalization / 분석자 일반화:** 아래 뼈대와 필드 순서는 관찰을 재사용 가능한 설계 절차로 바꾼 이 프로젝트의 권장안이다.
- **Low-evidence extension / 근거가 약한 확장 적용안:** 강한 계정별 표본이 없는 유형에 핵심 문법을 넓혀 쓰는 제안이다. 확립된 계정 패턴으로 취급하지 않는다.

각 템플릿의 대괄호 항목을 채우고, 적용되지 않는 선택 항목은 삭제한다. no-text를 선택했다면 임의의 단어, 로고, 워터마크를 금지한다.

| Type | Evidence level in the coded corpus | Use |
| --- | --- | --- |
| Poster/editorial | Strong: 28/54 prompt units; about 16/42 families after repeated-family correction | Account-grounded template |
| Product advertising | Medium: 4/54 | Provisional type template |
| Presentation/PPT | Medium: 3/54 | Apply the core grammar provisionally; no dedicated account formula |
| Cinematic/sequential story | Medium: 4/54 | Apply the core grammar provisionally; no dedicated account formula |
| Reference-photo transformation | Narrow: 13/54 late variants, one family | Use only with an actual attachment; not an account-wide rule |
| Portrait/fashion, architecture/space, specialized 3D | Low | Label as project extension |

## Beginner Fill-in Template — evidence sufficient

**Analyst generalization / 분석자 일반화 — evidence sufficient:** 계정 관찰 패턴에서 도출한 짧은 입문용 뼈대다.

```text
목적/사용처: [purpose/use]
주제: [subject]
반드시 유지: [user-stated or attachment-grounded requirements] 또는 [해당 없음]
첫눈에 보일 장면/대비: [scene/first-glance thesis]
구성(위치·크기·겹침·여백): [composition]
매체와 제작 동작: [medium and making actions]
색 역할과 대략적 면적: [palette roles and approximate area]
글자: [typography with exact text/language/placement] 또는 [no text; no invented words, logos, or watermarks]
재료·빛·표면 또는 렌더링: [material/light/surface or rendering]
분위기: [mood]
출력 조건: [aspect ratio/output contract]
예상 실패에만 적용할 제한: [targeted negatives limited to likely failure modes]
```

## Expert Detailed Template — evidence sufficient

**Analyst generalization / 분석자 일반화 — evidence sufficient:** 열 블록에 직접 대응하는 상세 뼈대다.

```text
1. Output contract — [aspect ratio/output contract]; 목적/사용처 [purpose/use].
2. First-glance thesis — [scene/first-glance thesis] 속에서 [subject]가 먼저 읽힌다.
3. Grounded constraints — [user-stated or attachment-grounded requirements]를 바꾸지 않는다. 근거가 없으면 이 블록을 생략한다.
4. Composition — [composition].
5. Medium/actions — [medium and making actions].
6. Color system — [palette roles and approximate area].
7. Typography — [typography with exact text/language/role/placement] 또는 [no text; no invented words, logos, or watermarks].
8. Finish — [material/light/surface or rendering].
9. Emotion — [mood]가 [observable relationship]으로 드러난다.
10. Targeted negatives — [targeted negatives limited to likely failure modes].
```

## Poster Template — strong evidence, 28/54 units; about 16/42 families

**Account-observed pattern / 계정 관찰 패턴 — strong evidence, 28/54 units; about 16/42 families:** 포스터 관련 표본에서 반복 관찰된 설계 요소를 바탕으로 한 뼈대다. 28개 단위에는 같은 후기 골격의 변형이 포함되므로 계열 보정값도 함께 표시하며, 원문 프롬프트나 공식 방법의 복제가 아니다.

```text
[purpose/use]용 포스터. 주제는 [subject]이며 [user-stated or attachment-grounded requirements]가 있으면 유지한다.
첫눈에는 [scene/first-glance thesis]가 읽힌다. [composition]으로 제목, 주제, 여백의 관계를 만든다.
[medium and making actions]으로 제작하고, [palette roles and approximate area]의 역할·면적 체계를 쓴다.
타이포그래피는 [typography with exact text/language/role/placement] 또는 [no text; no invented words, logos, or watermarks]다.
[material/light/surface or rendering]으로 마감해 [mood]를 구체적으로 보이게 한다.
출력은 [aspect ratio/output contract]. [targeted negatives limited to likely failure modes]만 제한한다.
```

## Product Advertisement Template — medium evidence, 4/54

**Account-observed pattern / 계정 관찰 패턴 — medium evidence, 4/54:** 제한된 제품 광고 표본에서 관찰된 보존 우선 원리를 쓰는 뼈대다. 계정 소유자의 공식 제품 프롬프트를 뜻하지 않는다.

```text
[purpose/use]용 제품 광고. 사용자 설명 또는 실제 첨부 이미지로 근거가 확인된 경우에만 [subject]의 [grounded requirements: silhouette, proportions, visible material appearance, color placement, stitching, sole, supplied logo only]를 스타일보다 먼저 보호한다. 그런 근거가 없으면 이 보존 목록을 만들지 않는다.
첫눈에는 [scene/first-glance thesis]가 보이고, 제품은 [composition]에 놓인다.
[medium and making actions]을 적용하되 제품 정체성을 바꾸지 않는다. 색은 [palette roles and approximate area]로 운용한다.
글자는 [typography with exact text/language/role/placement] 또는 [no text; no invented words, logos, or watermarks]다.
[material/light/surface or rendering]으로 [mood]를 만든다.
출력은 [aspect ratio/output contract]. [targeted negatives limited to likely failure modes]만 금지한다.
```

## Reference-Image Transformation Template — narrow repeated evidence, 13/54 variants in one family

**Account-observed pattern / 계정 관찰 패턴 — narrow repeated evidence, 13/54 variants in one family:** 후기 사진 변환 계열에서 반복된 출력 계약과 보존 우선 구조를 일반화한 뼈대다. 13개는 서로 독립적인 유형이 아니라 한 계열의 변형이며, 참고사진이 실제로 제공된 작업에만 적용한다. 계정 전체의 범용 공식이나 참고 이미지 보존 성능으로 취급하지 않는다. 상세 규칙은 [reference-image-fidelity.md](reference-image-fidelity.md)를 따른다.

```text
이미지 역할: content source=[identity source], style/layout target=[optional target], generated result=[optional result]. content source가 정체성을 우선 통제한다.
기하 계약: [count], [aspect ratio], [independent output/no collage], [regions/order/orientation/percentages totaling 100%], [subject count and placement], [boundary], [layer/component count], [negative-space area], [title anchor/alignment/max lines/occupied area], [label count]. 각 값은 사용자 입력·측정·관찰한 이산 개수·디자인 선택 중 출처를 밝히며 이 블록 밖에서 수치로 반복하지 않는다.
보존: [identity, subject count, silhouette, pose, proportions, viewpoint, perspective, visible color placement, decisive relationships].
허용된 변형: [authorized region/background/medium/layout treatment]만 바꾼다.
무시/제거: [incidental QR/barcode/UI/watermark/signage/stray text/unrelated objects]는 사용자가 요구하지 않는 한 옮기지 않는다.
구성: 수치 계약을 바꾸지 않는 범위에서 [qualitative hierarchy, rhythm, and information density].
표현: [medium and making actions]. 색은 [palette roles and qualitative dominance].
타이포그래피: [exact wording/language and type style] 또는 [text-free safe area for post-production]. 위치·줄 수·점유 면적은 기하 계약을 따른다.
마감: [material/light/surface/rendering].
제한과 검증: [likely failures only]. 출력에서 identity, geometry, typography hierarchy, incidental artifacts, and exact counts를 확인한다.
```

### Split Photo + Layered Paper Editorial Profile — internal-observation narrow profile

**Internal one-run observation / 내부 1회 관찰 — two non-blind trials:** 종이공예 사례 두 개에서 디자인 계열과 참고사진 보존은 높았지만, 제목 과대화·여백 감소·QR 재사용이 반복 위험으로 확인되었다. [검증 기록과 한계](reference-fidelity-validation-ko.md)를 함께 보며, 아래 값은 타깃 또는 사용자가 같은 구조를 요구할 때만 사용한다.

```text
기하 계약: 3:4 세로 포스터 한 장, 위 50% 사진/아래 50% 종이공예, 화면 중앙의 수평 경계 하나, [subject count and placement], [exact or deliberately unspecified layer count], [negative-space side and share], 제목 [anchor/max lines/occupied share], 보조 라벨 [count]. 이 구조가 사용자 입력이나 측정된 타깃과 일치할 때만 정확값으로 사용하고 다른 블록에서 반복하지 않는다.
보존: content source의 정체성·피사체 수·포즈·시점·배경 관계를 유지한다.
변형: 아래 영역만 [paper medium]으로 재구성하고 [decisive narrative relationship]을 유지한다.
색은 source에서 [palette roles]로 제한해 추출한다. [paper fibers/cut edges/fold thickness/contact shadows]를 보이게 한다.
제목 문구는 정확히 [text]이며, 서체 위계와 정렬은 기하 계약을 따른다.
source에 우연히 보이는 QR·바코드·간판 글자·UI·워터마크는 아래 영역에 재사용하지 않는다. 임의 장식, 반복 피사체, 과밀 구성, 추가 제목을 만들지 않는다.
```

### Split Photo + Structural Watercolor Study Profile — internal-observation narrow profile

**Internal one-run observation / 내부 1회 관찰 — one non-blind trial:** 구조 분해 사례 한 개에서 정체성과 재질 계열은 높게 보존됐지만 목표보다 구조 단계가 하나 늘어났다. [검증 기록과 한계](reference-fidelity-validation-ko.md)를 함께 보며, 다음 뼈대는 정확한 단계 수와 근거 없는 내부 구조를 통제한다.

```text
기하 계약: [aspect ratio] 세로 포스터 한 장, 위 [upper ratio]% source/아래 [lower ratio]% structural study, 합계 100%, 경계 하나, 정확히 [component count]단계, 제목 [anchor/max lines/occupied share], 주석 [count/alignment]. 연속 수치는 사용자 입력 또는 픽셀 측정일 때만 정확값으로 쓰고 다른 블록에서 반복하지 않는다.
보존: content source의 정체성, 전체 비율, 관찰 방향, 결정적 외형과 visible color placement를 유지한다.
변형: 아래 영역만 [isometric/structural watercolor study]로 재구성한다. 허용 단계는 [named visible or user-confirmed components]이며 [stable anchor/base]를 유지하고 동일한 축을 따라 절제된 간격으로 분리한다.
보이지 않거나 사용자가 확인하지 않은 내부 구조는 사실처럼 발명하거나 라벨링하지 않는다.
제목 문구는 정확히 [exact text]이며, 서체 위계와 배치는 기하 계약을 따른다. [watercolor paper/linework/transparent wash/construction guides]로 마감한다.
추가 구조 단계, 과장된 폭발, 임의 기계 부품, 기술 UI, 가짜 브랜드·연도·QR·바코드·중복 제목을 만들지 않는다.
```

아래 세 유형은 모두 강한 계정별 표본을 벗어난다. **Low-evidence extension / 근거가 약한 확장 적용안:** 프로젝트의 핵심 문법을 확장한 것이며, 확립된 계정 패턴이나 공식 방법이 아니다.

## Portrait or Fashion Template — extension, one close-read sample

**Low-evidence extension / 근거가 약한 확장 적용안:** this applies the project’s core grammar beyond a strong account-specific sample; it is not an established account pattern. 근거는 one close-read sample에 한정된다.

```text
[purpose/use]용 인물/패션 이미지. [subject]에서 [user-stated or attachment-grounded requirements]가 있으면 유지한다.
첫눈에는 [scene/first-glance thesis]가 읽히고, 인물·의상·여백은 [composition]의 관계를 따른다.
[medium and making actions]으로 표현하며, 사진이 명시된 경우에만 필요한 촬영 표현을 사용한다.
색은 [palette roles and approximate area]. 글자는 [typography with exact text/language/role/placement] 또는 [no text; no invented words, logos, or watermarks].
[material/light/surface or rendering]으로 [mood]를 보이게 한다.
출력은 [aspect ratio/output contract]. 제한은 [targeted negatives limited to likely failure modes].
```

## Architecture or Space Template — extension, one complete sample

**Low-evidence extension / 근거가 약한 확장 적용안:** this applies the project’s core grammar beyond a strong account-specific sample; it is not an established account pattern. 근거는 one complete sample에 한정된다.

```text
[purpose/use]용 건축/공간 이미지. [subject]의 [user-stated or attachment-grounded requirements]가 있으면 유지한다.
첫눈에 [scene/first-glance thesis]가 읽히고, 동선·덩어리·개구부·여백은 [composition]으로 조직한다.
[medium and making actions]을 쓰되 사진이 아닌 경우 카메라나 렌즈를 가정하지 않는다.
색은 [palette roles and approximate area]. 글자는 [typography with exact text/language/role/placement] 또는 [no text; no invented words, logos, or watermarks].
[material/light/surface or rendering]으로 [mood]를 형성한다.
출력은 [aspect ratio/output contract]. 제한은 [targeted negatives limited to likely failure modes].
```

## 3D Render or Illustration Template — extension

**Low-evidence extension / 근거가 약한 확장 적용안:** this applies the project’s core grammar beyond a strong account-specific sample; it is not an established account pattern. 유형 이름만으로 3D, 타이포그래피, 카메라 또는 렌즈를 자동 가정하지 않는다.

```text
[purpose/use]용 3D 렌더 또는 일러스트레이션. 사용자가 선택한 [subject]의 [user-stated or attachment-grounded requirements]가 있으면 유지한다.
첫눈에는 [scene/first-glance thesis]가 읽히고, 요소는 [composition]으로 관계를 맺는다.
표현 방식은 사용자가 정한 [medium and making actions]이며, 색은 [palette roles and approximate area]로 나눈다.
글자는 [typography with exact text/language/role/placement] 또는 [no text; no invented words, logos, or watermarks].
[material/light/surface or rendering]을 사용해 [mood]를 보이게 한다.
출력은 [aspect ratio/output contract]. 제한은 [targeted negatives limited to likely failure modes].
```
