---
주제: 수집 구조 개선에 따른 전처리-통합 코드 수정
AI 플랫폼 및 모델:
  - ChatGPT 5.4
날짜: 2026-04-28
---
# 작업 메모 1
- 03_pipeline-revision_1_기존 코드의 fallback 기능으로 인한 오수집 개선을 통해 작성된 ver3 스크립트로 수집 완료 후, 코드 에이전트와 수집 데이터의 구조 개선에 따른 전처리-통합 코드 수정 방안을 논의
- 기존 작업을 통해 수집한 텍스트 데이터는 shenbao_textdata 아래의 archive 폴더로 옮기고 파일명 뒤에 `(ver2_{수집일자})`를 붙여 보관

# 1. 방향성 검토
## 프롬프트 1-1
최근의 크롤러 업데이트를 통해 수집 텍스트 데이터의 헤더 구성이 바뀌었어. 바뀌기 전 버전은shenbao\shenbao_textdata\archive\shenbao_textdata_lixian_1to7203(ver2_20260415).csv, 바뀐 후 버전은 shenbao\shenbao_textdata\shenbao_textdata_lixian_1to7203.csv 이야. 이 변화를 바탕으로 shenbao_textdata_preprocess_combine.py를 수정하려고 해. 당연히 그 산출물인 stage1, 2, 3의 헤더 구성도 바뀌어야 하겠지. 각 파일의 구성을 검토한 후에, stage1, 2, 3의 구조와 preprocess 코드의 진행이 어떻게 바뀌어야 할지 검토해줘
## 답변 1-1
검토 기준:
- 구버전 원본: shenbao_textdata_lixian_1to7203(ver2_20260415).csv.csv)
- 신버전 원본: shenbao_textdata_lixian_1to7203.csv
- 현재 전처리 코드: shenbao_textdata_preprocess_combine.py

핵심 결론부터 말하면, **이번 변경은 단순 헤더 교체가 아니라 전처리 철학 자체를 바꿔야 하는 수준**입니다.

기존 전처리:
- `publish`라는 결합 문자열을 다시 파싱
- `title`/`text` 내부에서 `其他紀元`, `主題`, `類別`를 재추출
- 예외를 텍스트 내부 패턴으로 판정

신버전 원본:
- `publish_variant`, `date`, `issue_page`, `special_column`, `h1`, `lv1_div`, `content-box2`, `era_year`, `theme`, `collect_error`처럼 **구조가 이미 분해된 상태**

즉, 앞으로는 **“문자열 재파싱 중심”에서 “구조화된 원본 필드 정규화 중심”으로 바뀌어야** 합니다.

---

### 1. 구버전과 신버전의 구조 차이

#### 구버전 8열
```text
label,page,item_index,list_title,publish,detail_url,title,text
```

#### 신버전 16열
```text
label,page,item_index,list_title,detail_url,publish_variant,date,issue_page,special_column,h1,lv1_div,content-box2,era_year,category,theme,collect_error
```

#### 의미상 대응
- `publish` → `publish_variant` + `date` + `issue_page` + `special_column` + 일부 `lv1_div`
- `title` → `h1`
- `text` → `content-box2`
- `其他紀元` 재추출 → `era_year` 직접 제공
- `主題` 재추출 → `theme` 직접 제공
- 오류 판정 → `collect_error` 직접 제공

---

### 2. 새 원본 필드의 실제 충실도

네 개 신버전 파일을 확인한 결과:

| 파일          |      date | detail_url | issue_page |       h1 |  lv1_div | content-box2 |  era_year | category |   theme | collect_error |
| ----------- | --------: | ---------: | ---------: | -------: | -------: | -----------: | --------: | -------: | ------: | ----------: |
| `lixian`    | 100.0000% |  100.0000% |   99.9722% | 99.5280% | 99.9167% |     90.2124% | 100.0000% |  0.0000% | 1.3605% |     0.0000% |
| `xianfa`    | 100.0000% |  100.0000% |   99.9625% | 99.7694% | 99.8713% |     94.6750% | 100.0000% |  0.0000% | 2.5257% |     0.0000% |
| `xianzheng` | 100.0000% |  100.0000% |   99.9899% | 99.4953% | 99.8991% |     92.3985% | 100.0000% |  0.0000% | 2.3016% |     0.0000% |
| `zhixian`   | 100.0000% |  100.0000% |   99.9769% | 99.8380% | 99.9537% |     97.3161% | 100.0000% |  0.0000% | 1.8510% |     0.0000% |

- `date`: 전 파일 `100%`
- `detail_url`: 전 파일 `100%`
- `issue_page`: 거의 `100%` (`99.96~99.99%`)
- `h1`: 약 `99.5~99.9%`
- `lv1_div`: 약 `99.9%`
- `content-box2`: 약 `90.2~97.3%`
- `era_year`: `100%`
- `category`: 현재는 사실상 `0%`
- `theme`: 약 `1.36~2.53%`
- `collect_error`: 현재 샘플에서는 `0%`

중요한 점:
1. `category`는 현재 사실상 비어 있으므로 **유지하되 기대치는 낮게 잡아야** 합니다.
2. `content-box2`가 생각보다 자주 비어 있으므로, **본문 예외 처리 로직은 오히려 더 중요**해졌습니다.
3. `publish_variant`는 특히 `lixian`에서 결측이 많습니다(`74.84%`만 채워짐). 따라서 기존 `publish_exception`과 비슷한 품질 플래그는 여전히 유용합니다.
---

### 3. 현재 preprocess 코드가 왜 그대로는 맞지 않는가

현재 shenbao_textdata_preprocess_combine.py는 다음 전제를 가집니다.

- 입력 필수열:
  - `label,page,item_index,list_title,publish,detail_url,title,text`
- `parse_publish()`로 `publish`를 다시 분해
- `split_title_text_metadata()`로 `title_raw`, `text_raw`에서 메타데이터 재추출
- `make_text_fields()`에서 `text_raw` 안의 `其他紀元：` 등을 기준으로 예외 판정

이 전제는 신버전 원본에는 맞지 않습니다.

신버전에서는:
- `publish`가 없음
- `title`이 아니라 `h1`
- `text`가 아니라 `content-box2`
- 메타데이터가 이미 분리돼 있음
- `collect_error`가 별도 열로 있음

따라서 현재 코드는 **입력 가정부터 교체**해야 합니다.

---

### 4. 권장 방향: “신버전 전용 전처리”로 정리

두 가지 길이 있습니다.

#### 선택지 A. 구버전/신버전 동시 지원
- 장점: archive까지 한 코드로 처리 가능
- 단점: 코드가 복잡해짐

#### 선택지 B. 신버전 전용으로 전환
- 장점: 코드가 훨씬 단순하고 명확
- 단점: 구버전은 별도 보관용이 됨

지금 상황에서는 **B가 더 적절**합니다.

이유:
- archive가 이미 분리돼 있음
- stage1/2/3도 신버전 구조에 맞춰 다시 정의하는 편이 깔끔함

즉, `discover_source_files()`도 가능하면
신버전 파일만 읽게 좁히는 편이 안전합니다.

---

### 5. stage1 구조 제안

#### 원칙
- stage1은 “원본 보존”이 목적
- 다만 Python/CSV 후속 처리 편의를 위해 **하이픈이 있는 헤더는 언더스코어로 정규화**하는 편이 좋음

#### 권장 stage1 헤더
```text
preprocess_index,
label_raw,
page_raw,
item_index_raw,
list_title_raw,
detail_url_raw,
publish_variant_raw,
date_raw,
issue_page_raw,
special_column_raw,
h1_raw,
lv1_div_raw,
content_box2_raw,
era_year_raw,
category_raw,
theme_raw,
collect_error_raw
```

#### 왜 이렇게 바꾸는가
- `content-box2_raw`처럼 하이픈이 들어간 이름은 Python 코드에서 불편함
- stage1은 “원문 보존”이지만, **컬럼명까지 DOM 그대로 유지할 필요는 없음**
- 값은 그대로 두고, 열 이름만 후처리 친화적으로 바꾸면 됨

---

### 6. stage2 구조 제안

stage2는 여전히 **`article_id` 기준 중복 통합**이 핵심입니다.

#### 권장 stage2 헤더
```text
dataset_label,
source_labels,
preprocess_indices,
representative_label,
representative_item_index,
select_reason,
article_id,
qrynewstype,
label_raw,
page_raw,
item_index_raw,
list_title_raw,
detail_url_raw,
publish_variant_raw,
date_raw,
issue_page_raw,
special_column_raw,
h1_raw,
lv1_div_raw,
content_box2_raw,
era_year_raw,
category_raw,
theme_raw,
collect_error_raw,
collision,
collision_type
```

#### 현재 stage2와 비교한 핵심 차이
- `publish_raw`, `title_raw`, `text_raw` 제거
- 대신 분해된 신버전 raw 필드들을 직접 보존

#### 대표행 선택 기준도 바뀌어야 함
현재:
- `1_no_error`
- `2_text_exists`
- `3_title_exists`
- `4_long_text`
- `5_small_index`

신버전 권장:
- `1_no_collect_error`
- `2_body_exists`
- `3_h1_exists`
- `4_long_body`
- `5_small_index`

즉 비교 대상도
- `text_raw` → `content_box2_raw`
- `title_raw` → `h1_raw`
- 오류 판단 → `collect_error_raw`

으로 바꿔야 합니다.

#### collision 판정도 바뀌어야 함
현재는 `(publish_raw, title_raw, text_raw)`만 비교하는데, 신버전에서는 최소한 아래를 비교하는 편이 맞습니다.

권장 비교 단위:
```text
publish_variant_raw,
date_raw,
issue_page_raw,
special_column_raw,
h1_raw,
lv1_div_raw,
content_box2_raw,
era_year_raw,
theme_raw,
collect_error_raw
```

---

### 7. stage3 구조 제안

여기서 가장 중요한 판단이 필요합니다.

현재 stage3는 구버전 입력을 전제로 해서
- `publish_tail`
- `publish_exception`
- `publish_exception_reason`
- `metadata_source`
같은 열이 들어 있습니다.

그런데 신버전에서는 이 중 일부가 **의미가 약해지거나 불필요**합니다.

#### 권장 stage3 헤더
```text
dataset_label,
source_labels,
preprocess_indices,
representative_label,
representative_item_index,
select_reason,
article_id,
qrynewstype,
publish_variant,
publish_date,
page_issue,
special_column,
lead_text,
title_clean,
title_exist,
title_source,
text_clean,
text_exception,
text_exception_reason,
collect_error,
era_year_raw,
chinese_era_year,
japanese_era_year,
category,
topic,
collision,
collision_type
```

#### 각 열의 의미
- `publish_variant`: 원본 `publish_variant_raw`
- `publish_date`: 원본 `date_raw`
- `page_issue`: 원본 `issue_page_raw`
- `special_column`: 원본 `special_column_raw`
- `lead_text`: 원본 `lv1_div_raw`
- `title_clean`: `h1_raw` 우선, 없으면 `list_title_raw` fallback
- `text_clean`: 원본 `content_box2_raw` 정제
- `collect_error`: 원본 `collect_error_raw`
- `era_year_raw`: 원본 `era_year_raw` 그대로 보존
- `chinese_era_year`, `japanese_era_year`: `era_year_raw`에서 분리
- `topic`: 원본 `theme_raw`
- `category`: 원본 `category_raw`

---

### 8. stage3에서 제거/축소하는 것이 좋은 열

#### 제거 권장
- `metadata_source`
  - 이제 메타데이터가 `title/text` 내부가 아니라 별도 raw 열로 오므로 불필요
- `publish_tail`
  - 현재 `lv1_div`를 기계적으로 `publish_tail`로 부르면 의미가 과도하게 고정됨
  - `lead_text`처럼 중립적으로 두는 편이 나음

#### 재정의 또는 제거 가능
- `publish_exception`
- `publish_exception_reason`

신버전에서는 `publish` 파싱 실패라는 개념 자체가 약해집니다.  
대신 아래처럼 바꾸는 것이 현실적입니다.

권장안:
- 유지한다면 의미를 바꿔서
  - `publish_exception = T/F`
  - `publish_exception_reason = missing_publish_variant | missing_issue_page`
- 아니면 아예 빼고, raw completeness 문제는 stage1/2에서만 보도록 함

내 판단:
- **연구용 최종 stage3에서는 빼는 편이 더 깔끔**
- 품질 점검은 별도 예외 스크립트나 stage2 검수로 처리

---

### 9. title 처리 로직은 어떻게 바뀌어야 하나

현재 로직은 `list_title_raw`와 `title_raw`를 비교합니다.  
신버전에서는 `title_raw` 대신 `h1_raw`입니다.

그런데 새 데이터에서는 `h1`이 비어 있을 때 `list_title`도 `"414."` 같은 식으로 **제목이 아니라 일련번호만 남는 사례**가 있습니다.

그래서 단순히
- `h1` 없으면 `list_title` fallback
로 끝내면 안 됩니다.

#### 권장 로직
1. `h1_raw`가 비어 있지 않으면 `title_clean = h1_raw`
2. 아니고 `list_title_raw`에서 일련번호 제거 후 남는 문자열이 있으면 그것을 사용
3. 둘 다 없으면 빈값
4. `title_source`는
   - `h1_raw`
   - `list_title_raw`
   - `missing`
5. `title_exist`는
   - `h1_present`
   - `list_title_fallback`
   - `missing`

즉, **기존 `both_exist / title_empty / both_empty` 체계보다 단순화하는 편이 낫습니다.**

---

### 10. text 처리 로직은 어떻게 바뀌어야 하나

현재는
- `[ERROR]`
- `metadata_only`
- `short_text`

이 구조인데, 신버전에서는 `collect_error`가 별도 열이므로 예외 사유를 더 직접적으로 잡을 수 있습니다.

#### 권장 text_exception 로직
1. `collect_error_raw` 비어있지 않음
   - `text_exception = T`
   - `text_exception_reason = collect_error`
1. `content_box2_raw`가 비어 있음
   - `text_exception = T`
   - `text_exception_reason = body_missing`
3. `content_box2_raw` 길이 `<= 3`
   - `text_exception = T`
   - `text_exception_reason = short_text`
4. 그 외
   - `text_exception = F`

#### 추가로 고려할 것
`content_box2_raw`가 비어 있는데 `h1_raw`가 매우 길어서 사실상 본문처럼 보이는 사례가 있습니다.  
이건 따로 표시하는 게 좋습니다.

예:
- `text_exception_reason = body_missing_h1_long`

이 플래그는 나중에 수동 검토 대상을 고르는 데 유용합니다.

---

### 11. 코드 진행 순서 제안

현재 코드 진행:
1. old raw append
2. article_id dedup
3. publish/title/text 재파싱

신버전 권장 진행:
1. **신버전 raw append**
   - 새 16열을 `_raw`로 적재
2. **`detail_url_raw`에서 `article_id`, `qrynewstype` 추출**
3. **중복 대표행 선택**
   - `collect_error_raw`, `content_box2_raw`, `h1_raw` 기준
1. **직접 매핑 중심 stage3 생성**
   - `publish_date = date_raw`
   - `page_issue = issue_page_raw`
   - `topic = theme_raw`
   - `title_clean = h1_raw fallback list_title_raw`
   - `text_clean = content_box2_raw`
   - `era_year_raw` 분해
5. **품질 플래그 생성**
   - `text_exception`
   - `collision`

즉, **현재 코드의 `parse_publish()`와 `split_title_text_metadata()`는 사실상 축소 또는 제거 대상**입니다.

---

### 12. 최종 제안

가장 적절한 방향은 다음입니다.

#### 권장 설계
- preprocess 코드는 **신버전 전용**으로 전환
- stage1은 **새 raw 16열 + preprocess_index**
- stage2는 **article_id 기준 dedup + 대표 raw 행 보존**
- stage3는 **직접 매핑 기반 연구용 기사 단위 데이터**
- `metadata_source`, old-style `publish` parsing 로직 제거
- `lv1_div`는 `publish_tail`로 강제 해석하지 말고 `lead_text`로 중립 보존
- `collect_error`를 직접 반영하는 예외 판정 도입

#### 특히 바꾸는 것이 좋은 부분
- `RAW_COLUMNS`
- `STAGE1_COLUMNS`
- `STAGE2_COLUMNS`
- `STAGE3_COLUMNS`
- `representative_reason()`
- `classify_collision()`
- `parse_publish()` 제거 또는 대폭 축소
- `split_title_text_metadata()` 제거
- `make_title_fields()` / `make_text_fields()` 신버전 기준 재작성

---

원하면 다음 단계로 바로
1. **이 제안을 바탕으로 확정 스키마를 먼저 짧게 합의**하고
2. 그 뒤 shenbao_textdata_preprocess_combine.py 수정안까지 실제로 작성할 수 있습니다.

---
## 프롬프트 1-2
2번에서 다룬 `새 원본 필드의 실제 충실도`는 오히려 통합 이후에 다시 검토해야 하는게 아닐까? 만약 다른 레이블로 수집된 동일 id 기사 개체 간에 ‘publish_variant’, ‘date’, ‘issue_page’, ‘special_column’, ‘h1’, ‘lv1_div’, ‘content-box2’, ‘era_year’, ‘category’, ‘theme’ 값에 차이가 없다면,(10_data-profile_중복 개체 간 데이터 일치) 같은 id 기사라면 필드의 결측 여부가 완전히 동일하다는 의미이고, 그럼 이 부분은 통합 후에 개선해도 되는 거 아닐까?
## 답변 1-2
네, **지금까지 확인한 현재 데이터 상태를 전제로 하면 그 판단이 맞습니다.**

핵심은 이겁니다.

- 같은 `id` 기사끼리
- `publish_variant`, `date`, `issue_page`, `special_column`, `h1`, `lv1_div`, `content-box2`, `era_year`, `category`, `theme`
가 **동일하다면**
- 그 필드들의 **결측 여부도 동일**합니다.

그러면 이 필드들에 대해서는:

- 원본 4개 파일 단계에서 먼저 충실도를 볼 필요는 크지 않고
- **`article_id` 기준 통합 후에 봐도 충분**합니다.

즉, 당신이 말한

> 통합 이후에 다시 검토해야 하는 것 아닌가?

는 맞는 말입니다.  
오히려 **통합 데이터셋을 만들 목적**이라면, 그쪽이 더 자연스럽습니다.

다만 구분해야 할 목적이 있습니다.

**1. 통합 코퍼스 품질을 알고 싶은 경우**
이 경우에는 **통합 후에 보는 것이 더 적절**합니다.

이유:
- 중복 기사들이 제거된 상태이므로
- “실제로 최종 연구 데이터에 남는 기사” 기준으로
- 어떤 필드가 얼마나 채워져 있는지 바로 볼 수 있습니다.

즉 아래 필드들은:
- `publish_variant`
- `date`
- `issue_page`
- `special_column`
- `h1`
- `lv1_div`
- `content-box2`
- `era_year`
- `category`
- `theme`

모두 **통합 후 평가**로 옮겨도 됩니다.

**2. 수집 스크립트의 원본 수집 성능을 알고 싶은 경우**
이 경우에는 원본 단계의 충실도도 여전히 의미가 있습니다.

예를 들어:
- 어떤 라벨 검색에서 특정 구조가 더 많이 나왔는지
- 원본 수집 파일 수준에서 어떤 예외가 많았는지
- 특정 키워드 검색 결과가 어떤 구조적 편향을 갖는지

이건 통합 후보다 **원본 단계**가 더 적절합니다.

즉 이전 답변의 2번은
- “전처리 설계 참고용 원본 진단”으로는 의미가 있었지만
- “최종 통합 데이터 품질 평가”라는 목적에는 다소 앞서나간 면이 있었습니다.

**그래서 더 정확한 정리는 이렇게 하는 게 좋습니다.**

- 원본 단계에서 먼저 확인할 것:
  - `detail_url`
  - `article_id` 중복 구조
  - `list_title`
  - `label`
  - `item_index`
  - 같은 `id`끼리 정말 동일한지 여부
- 통합 후에 평가할 것:
  - `publish_variant`
  - `date`
  - `issue_page`
  - `special_column`
  - `h1`
  - `lv1_div`
  - `content-box2`
  - `era_year`
  - `category`
  - `theme`

즉, **“구조적 동일성 확인”은 통합 전, “필드 충실도 평가”는 통합 후**가 더 논리적입니다.

또 하나 중요한 점:
- `publish_variant`가 빈 경우가 많다고 해도
- 같은 `id`끼리 전부 동일하게 비어 있다면
- **중복 통합으로 값이 보완되지는 않습니다.**
- 따라서 이 문제는 통합 전후 어디서 보든 **결측 자체는 그대로**입니다.

즉:
- 충실도 평가는 통합 후로 미뤄도 되고
- 결과도 본질적으로 달라지지 않습니다.
- 다만 퍼센티지는 중복 제거 때문에 조금 달라질 수 있습니다.

**정리**
- 네, 현재 확인된 데이터 상태라면 **해당 필드들의 충실도 평가는 통합 후에 해도 됩니다.**
- 오히려 최종 연구용 데이터 품질을 말하려면 그 편이 더 적절합니다.
- 이전 답변의 2번은 “원본 진단”으로는 의미가 있었지만, “최종 통합 데이터 기준”으로는 위치를 뒤로 미루는 것이 더 논리적입니다.

원하면 다음 단계로
1. 이 논리를 반영해서 전처리 절차 설명문을 다시 정리하거나
2. 통합 후 기준으로 봐야 할 필드와 통합 전 기준으로 봐야 할 필드를 표로 나눠드릴 수 있습니다.
---
## 작업 메모 2
- 해당 필드의 충실도 평가는 데이터 구조 자체에 대한 검토 사항이고,  통합 스크립트 작성 과정에 직접적으로 영향을 끼치지 않기 때문에 관련 내용은 별도 작업 노트에 기록(10_data-profile_1_데이터 구조 및 필드별 충실도 검토)
---
## 프롬프트 1-3
답변 1-1 내용 중에서 위의 충실도 평가와 같이 통합 후에 확인해도 무관한 내용이 있는지 검토해줘
## 답변 1-3
네. **현재까지 확인한 실제 데이터 상태를 기준으로 보면**, 그 메모 안에도 **통합 후에 확인해도 무방한 항목**이 꽤 있습니다.

전제가 되는 현재 확인 사항:
- 같은 `id` 기사끼리는 `publish_variant`, `date`, `issue_page`, `special_column`, `h1`, `lv1_div`, `content-box2`, `era_year`, `category`, `theme`가 이제 일치합니다.
- `lv1_div`의 기존 예외 `30건`도 수정 후 해소되었습니다.
- 따라서 이 필드들에 대한 **결측 여부와 값 차이**는 중복 통합 전이든 후든 본질적으로 같습니다.

**통합 후로 미뤄도 되는 항목**
- 03_pipeline-revision_2_수집 구조 개선에 따른 전처리-통합 코드 수정.md:55
  - `### 2. 새 원본 필드의 실제 충실도`
  - 여기서 제시한 `publish_variant`, `date`, `issue_page`, `h1`, `lv1_div`, `content-box2`, `era_year`, `category`, `theme`, `collect_error`의 충실도 표는 **통합 후에 계산해도 무방**합니다.
  - 오히려 최종 연구용 데이터 품질을 설명하려면 통합 후 수치가 더 자연스럽습니다.
  - 예외는 `detail_url`입니다. 이건 `article_id` 추출의 입력이므로 **통합 전 전제 조건**으로 남겨두는 편이 맞습니다.

- 같은 파일:78
  - `category`가 사실상 `0%`
  - `content-box2`가 자주 비어 있음
  - `publish_variant` 결측이 많음
  - 이 세 판단도 **통합 후 품질 점검**으로 옮겨도 됩니다.

- 같은 파일:228
  - stage2의 `collision` 비교 범위로 적어둔
    - `publish_variant_raw`
    - `date_raw`
    - `issue_page_raw`
    - `special_column_raw`
    - `h1_raw`
    - `lv1_div_raw`
    - `content_box2_raw`
    - `era_year_raw`
    - `theme_raw`
    - `collect_error_raw`
  - 이 부분도 **현재 데이터 기준으로는 통합 전 필수 검토라기보다 통합 후 검증 항목**에 가깝습니다.
  - 이유는 같은 `id`끼리 이 값들이 이미 동일하기 때문입니다.
  - 즉, 이 비교는 “대표행 선택 전 충돌 탐지”라기보다 “통합이 잘 되었는지 사후 확인” 성격이 더 강합니다.

- 같은 파일:321
  - `publish_exception = T/F`
  - `publish_exception_reason = missing_publish_variant | missing_issue_page`
  - 이 품질 플래그도 **통합 후 stage3에서 부여해도 무방**합니다.
  - 같은 `id`끼리 해당 결측이 동일하므로, dedup 이전에 미리 판정할 실익이 크지 않습니다.

- 같은 파일:365
  - `text_exception` 로직
  - `collect_error_raw`, `content_box2_raw`, `h1_raw`를 기준으로 `collect_error`, `body_missing`, `short_text`, `body_missing_h1_long`을 판정하는 부분도 **통합 후에 계산해도 됩니다**.
  - 같은 `id`끼리 `content_box2_raw`, `h1_raw`, `collect_error_raw`가 동일하므로, 통합 전후 판정 결과가 달라지지 않습니다.

- 같은 파일:405
  - `publish_date = date_raw`
  - `page_issue = issue_page_raw`
  - `topic = theme_raw`
  - `text_clean = content_box2_raw`
  - `era_year_raw` 분해
  - 이런 직접 매핑형 후처리도 **통합 후 적용**이 더 자연스럽습니다.

**통합 전에 남겨두는 것이 좋은 항목**
- 같은 파일:401
  - `detail_url_raw`에서 `article_id`, `qrynewstype` 추출
  - 이건 dedup의 전제이므로 **반드시 통합 전**입니다.

- 같은 파일:402
  - 대표행 선택 기준
  - 이건 통합 과정 자체의 일부이므로 당연히 통합 전입니다.
  - 다만 지금 데이터 상태라면 선택 기준이 `content_box2_raw`, `h1_raw`, `collect_error_raw`에 크게 흔들릴 가능성은 낮습니다.

- 같은 파일:333
  - `title_clean`에서 `h1_raw`가 비면 `list_title_raw` fallback
  - 이 부분은 **통합 후로 완전히 미루기 어렵습니다.**
  - 이유는 같은 `id`끼리 `list_title_raw`는 서로 다를 수 있기 때문입니다.
  - 즉 `h1_raw`가 비는 기사에서는 어떤 `list_title_raw`를 대표로 삼을지 규칙이 먼저 필요합니다.

**실질적 정리**
이 메모 안에서, **통합 후에 확인해도 무관한 내용의 중심은**
- 필드 충실도 평가
- 결측 기반 품질 플래그
- `text_exception`
- `publish_exception`
- raw 필드 일치성 검증
입니다.

반대로 **통합 전에 꼭 남아 있어야 하는 내용의 중심은**
- `detail_url_raw` → `article_id`, `qrynewstype`
- 대표행 선택
- `list_title_raw` 관련 fallback 규칙
입니다.

즉, 이 메모를 지금 데이터 상태에 맞게 다듬는다면 구조는 이렇게 바꾸는 것이 가장 논리적입니다.

1. 통합 전
- raw append
- `article_id`, `qrynewstype` 추출
- dedup
- 대표행 선택

2. 통합 후
- 필드 충실도 평가
- `publish_exception`
- `text_exception`
- `era_year_raw` 분해
- `topic/theme`, `category`, `lead_text` 품질 점검
- collision 사후 검증

원하면 다음 단계로 이 메모에서 **통합 후로 옮겨도 되는 문장**과 **통합 전 유지 문장**을 구분해서, 바로 재배치 가능한 형태로 정리해드리겠습니다.

---
# 2. 작업 설계
## 2-1. 전처리-통합 코드의 기본 구조 설계
### 프롬프트 2-1-1
shenbao_textdata_preprocess_combine.py 을 다음과 같은 규칙에 따라 작동하도록 개선하고 shenbao_textdata_preprocess_combine_ver2.py로 저장하려고 해. 아래 작업 규칙의 타당성을 검토하고, 모호하거나 수정할 부분이 있다면 제안해줘

1. stage1
	- stage1은 네 건의 수집 데이터 간 단순 병합이 목적
	- Python/CSV 후속 처리 편의를 위해 하이픈이 있는 헤더는 언더스코어로 정규화
	- 새 버전 수집 데이터는 메타데이터가 이미 모두 분리되어 있어 이후 통합 과정에서 원본열 자체에 대한 수정은 이루어지지 않으므로, `_raw` suffix 추가 로직은 삭제
	- 생성 파일명은 `shenbao_textdata_stage1_appended_rows_{dataset_label}.csv`로 설정
	- 헤더 구성: 17열
		```text
		preprocess_index,
		label,
		page,
		item_index,
		list_title,
		detail_url,
		publish_variant,
		date,
		issue_page,
		special_column,
		h1,
		lv1_div,
		content_box2,
		era_year,
		category,
		theme,
		collect_error
		```

2. stage2
	- stage2는 `article_id` 기준 중복 항목 간 통합이 목적
	- detail_url로부터 article_id, qrynewstype를 분리하는 로직 유지
	- 대표행 판정 기준 
		1. 'collect_error'가 비어있는 행(즉, 에러 메시지가 등장하지 않은 행)
		2. 'content_box2' 길이가 긴 행
		3. 'h1' 길이가 긴 행
		4. 'lv1_div' 길이가 긴 행
		5. 'preprocess_index'가 작은 행
	-  'select_reason'에 기록될 대표행 선택 사유
		1. '1_no_error'
		2. '2_long_box2'
		3. '3_long_h1'
		4. '4_long_lv1_div'
		5. '5_small_index'
	- 원본 파일이 제공하는 열 중 label, page, item_index, list_title 네 열은 그대로 남겨두더라도 stage2 결과물부터는 대표행의 값만 남게 되고 이후 분석에서 활용할 여지가 없으므로 삭제
	- collision = T인 행에 대해, 충돌 유형이 아닌, 충돌이 일어난 열을 기록하는 방식으로 수정. 열 헤더를 'collision_type'에서 'collision_row'로 바꾸고, publish_variant, date, issue_page, special_column, h1, lv1_div, content_box2, era_year, category, theme, collect_error 열 중에서 충돌이 발생한 열 이름을 기록. 복수 열에서 충돌이 발생한 경우 값을 “;”로 연결하여 기록
	- 생성 파일명은 `shenbao_textdata_stage2_deduplicated_articles_{dataset_label}.csv`로 설정
	- 헤더 구성: 22열
		```text
		dataset_label,
		source_labels,
		preprocess_indices,
		representative_label,
		representative_item_index,
		select_reason,
		article_id,
		qrynewstype,
		detail_url,
		publish_variant,
		date,
		issue_page,
		special_column,
		h1,
		lv1_div,
		content_box2,
		era_year,
		category,
		theme,
		collect_error,
		collision,
		collision_row
		```

3. stage3
	- stage2까지 과정에서는 데이터베이스에서 수집한 publish_variant부터 theme까지의 내용을 가공하지 않고 원 데이터를 유지했는데, stage3는 원 데이터 가공을 통한 분석에 바로 활용할 수 있는 문자열 제작과 분할이 필요한 부분의 분할이 목적
	- 현재 수집 데이터 구조에서 가공이 필요한 열은 h1과 era_year로 제한됨
	- h1에서는 10_data-profile_h1(제목 영역)과 content-box2(본문 영역)의 탑재 방식.md과 content-box2(본문 영역)의 탑재 방식.md)의 `# 4. h1과 content-box2 문자열의 중복 여부 검토` 이하의 내용을 통해 확인한 " h1과 content-box2의 일부 중복 사례 중 괄호 경계형인 경우에만 파싱 오류로 인해 내용이 중복 탑재된 경우임"을 근거로 하여, 괄호 경계형 중복 문자열을 제거하고(이 과정에서 괄호 문자 판정을 위해 md 파일의 프롬프트 4-3, 답변 4-3을 필히 확인할 것), 이를 h1_clean으로 저장. 기존 h1열은 h1_raw로 열 헤더 변경
	- era_year를 chinese_era_year, japanese_era_year로 분할하는 로직 유지
	- stage2에서 stage3로 가면서 detail_url을 제거하는 로직 유지
	- 나머지 문자열 정제 로직은 제거
	- 생성 파일명은 `shenbao_textdata_stage3_preprocessed_articles_{dataset_label}.csv`로 설정
	- 헤더 구성: 24열
		```text
		dataset_label,
		source_labels,
		preprocess_indices,
		representative_label,
		representative_item_index,
		select_reason,
		article_id,
		qrynewstype,
		publish_variant,
		date,
		issue_page,
		special_column,
		h1_raw,
		h1_clean,
		lv1_div,
		content_box2,
		era_year_raw,
		chinese_era_year,
		japanese_era_year,
		category,
		theme,
		collect_error,
		collision,
		collision_row,
		```

### 답변 2-1-1
전체적으로는 **타당합니다.**  
지금 제안하신 방향은 현재 수집 구조와 실제 데이터 상태에 잘 맞습니다.

다만 그대로 구현에 들어가기 전에 **명확히 정해야 할 부분이 3개** 있습니다.

**전반 판단**
- `stage1`에서 `_raw` suffix를 없애고, 새 수집 스키마를 거의 그대로 유지하는 방향: 타당
- `stage2`에서 `article_id` 기준 중복 통합을 먼저 하고, 대표행만 남기는 방향: 타당
- `stage3`에서 `h1`과 `era_year`만 가공하는 방향: 대체로 타당
- 다만 `h1_clean` 규칙은 **현재 문장만으로는 구현 기준이 아직 모호**합니다
- 또 `나머지 문자열 정제 로직 제거`는 “분석에 바로 활용”이라는 표현과는 조금 충돌할 수 있습니다

**1. Stage1**
제안은 타당합니다.

좋은 점:
- 현재 원본 수집 파일의 실제 헤더는 16열이고,
- 여기에 `preprocess_index`를 더하면 말씀하신 `17열`이 정확합니다.
- 현재 실제 원본 헤더:
```text
label,page,item_index,list_title,detail_url,publish_variant,date,issue_page,special_column,h1,lv1_div,content-box2,era_year,category,theme,collect_error
```

권장 수정:
- “하이픈이 있는 헤더는 언더스코어로 정규화”는 좋습니다.
- 다만 현재 실제로 바뀌는 것은 사실상 `content-box2 -> content_box2` 하나입니다.
- 그래서 구현 시에는
  - 포괄적 정규화 함수
  - 또는 명시적 매핑 딕셔너리
중 하나를 택해야 합니다.
- 제 추천은 **명시적 매핑**입니다.
  - 이유: 예기치 않은 헤더 변형을 막기 쉽습니다.

예:
```text
content-box2 -> content_box2
```

**2. Stage2**
큰 방향은 타당합니다.

특히 좋은 점:
- 현재 데이터에서는 같은 `article_id` 기사끼리
  - `publish_variant`
  - `date`
  - `issue_page`
  - `special_column`
  - `h1`
  - `lv1_div`
  - `content_box2`
  - `era_year`
  - `category`
  - `theme`
가 일치하므로,
- 대표행 선택 기준은 주로 **예외 상황 대비용 안전장치**로 쓰이게 됩니다.
- 따라서 지금 제안한 우선순위는 무난합니다.

다만 명확히 해야 할 점이 있습니다.

**2-1. `qrynewstype` 처리**
현재 데이터에서는 같은 `article_id`끼리 `qrynewstype`가 달라지는 경우가 없었습니다.  
그래서 stage2에서는 `qrynewstype`를 단순히 대표행 값으로 두거나, 아예 **그룹 내 유일값인지 검증**하는 편이 더 안전합니다.

추천:
- 그룹 내 `qrynewstype` 유일값 1개면 그대로 저장
- 2개 이상이면 조용히 `;`로 합치지 말고
  - 에러를 내거나
  - 별도 경고를 내는 방식

이유:
- `article_id` 기준 통합은 사실상 “같은 DB 개체”를 전제하므로,
- `qrynewstype`가 다르면 오히려 데이터 이상으로 보는 편이 맞습니다.

**2-2. `collision_row` 비교 기준**
여기는 꼭 정해야 합니다.

지금 문장만으로는
- 완전 문자열 일치 기준인지
- 공백 정규화 후 비교인지
- 빈값/결측도 충돌로 보는지
가 명시돼 있지 않습니다.

추천:
- 기본은 **원문 문자열 완전 일치 기준**
- 단, 정말 사소한 공백 차이까지 무시하고 싶다면 `normalize_spaces()` 후 비교

현재 데이터 상태를 보면 원문 자체가 이미 같으므로 어느 쪽이든 큰 차이는 없겠지만,  
코드 규칙은 미리 고정하는 편이 좋습니다.

**2-3. `collision_row` 값**
이 방식은 좋습니다.  
다만 `collision=F`일 때는 `collision_row`를 빈값으로 둘지, 아니면 `none`으로 둘지 정해야 합니다.

추천:
- `collision=F`면 `collision_row=""`

더 깔끔합니다.

**2-4. `label`, `page`, `item_index`, `list_title` 삭제**
이건 대체로 타당합니다.

왜 괜찮은가:
- `source_labels`
- `preprocess_indices`
- `representative_label`
- `representative_item_index`
가 남기 때문에
- provenance 추적은 가능합니다.

다만 주의:
- 나중에 “검색 결과 목록 표제 차이”를 다시 보려면 stage2 이후에는 바로 못 봅니다.
- 하지만 stage1과 `preprocess_index`가 남아 있으므로, 지금 설계로도 추적은 가능합니다.

즉 현재 목적에는 문제 없습니다.

**3. Stage3**
구조는 타당합니다.  
하지만 여기에는 **구현 규칙을 더 명확히 적어야 하는 핵심 모호점**이 있습니다.

**3-1. 가장 중요한 모호점: `h1_clean` 대상 범위**
현재 문장:
- “괄호 경계형 중복 문자열을 제거”

이 표현만으로는 아래가 확정되지 않습니다.

1. 제거 대상이
- `h1 suffix` / `content_box2 prefix` 겹침만인지
- 아니면 `h1`가 `content_box2` 앞부분에 포함되는 경우도 포함인지

추천:
- **suffix-prefix 겹침만** 대상으로 한정

2. “괄호 경계형”의 정의가
- 괄호 문자가 경계 전후 몇 글자 이내인지

추천:
- **경계 전후 3자 이내**

3. 겹침 길이 하한이 있는지

추천:
- **정규화 후 겹침 길이 8자 이상**

4. 짧은 `h1`도 정제 대상인지
- 앞서 확인한 바에 따르면
  - 괄호 근접 사례 21건 중
  - 긴 `h1`(30자 이상) 17건은 전부 괄호 근접형
  - 짧은 `h1` 괄호 근접 사례 4건도 존재
- 그런데 “파싱 오류로 인해 과도하게 말려 올라간 경우”의 핵심 신호는 긴 `h1`였습니다.

그래서 여기서 선택이 필요합니다.

추천안 A, 보수적:
- `qrynewstype=SP`
- `h1` 길이 30자 이상
- suffix-prefix 겹침 8자 이상
- 경계 전후 3자 이내 괄호 문자 존재

이 네 조건을 모두 만족할 때만 `h1_clean`에서 겹친 suffix 제거

추천안 B, 넓은 적용:
- `h1` 길이 조건 없이
- 괄호 경계형 suffix-prefix면 전부 제거

제 추천은 **A안**입니다.  
현재 대화 기록상 “강한 오류 신호”는 A안 쪽이 더 명확합니다.

**3-2. 제거 방식**
이것도 문장으로 명시하는 편이 좋습니다.

추천 문구:
- `h1_clean`은 `h1_raw`에서 **content_box2와 중복되는 suffix 부분만 절단**하여 생성한다.
- `content_box2`는 수정하지 않는다.

즉:
- `h1_raw`만 손보고
- `content_box2`는 그대로 두는 방식이 가장 명확합니다.

**3-3. `era_year` 분할**
이건 그대로 유지해도 문제 없습니다.

다만 stage3 헤더에서는
- `era_year_raw`
- `chinese_era_year`
- `japanese_era_year`
로 명확히 가는 것이 맞습니다.

**3-4. `detail_url` 제거**
이건 설계상 가능합니다.

다만 선택지 차원에서만 말하면:
- 분석 전용 stage3면 제거해도 됨
- 원문 검증까지 stage3에서 바로 하고 싶으면 유지하는 편이 약간 편함

하지만 지금 제안처럼
- `article_id`
- `qrynewstype`
가 남으면
기본 식별은 가능하므로, 제거 자체는 문제 없습니다.

**4. 실제로 수정 제안을 드리고 싶은 부분**
아래 두 가지는 적극 권합니다.

**4-1. `나머지 문자열 정제 로직은 제거`**
이건 가능은 한데, 표현을 조금 조정하는 편이 좋습니다.

이유:
- 현재 원문에는 일부
  - `Copyright c 2012 得泓資訊. All Rights Reserved.`
  - `[H>]`, `[P>]`
같은 문자열이 남아 있는 사례가 있습니다.
- 따라서 정제를 거의 안 하면, strict한 의미의 “분석에 바로 활용”과는 조금 어긋날 수 있습니다.

선택지:
1. 정말 원형 보존 우선이면
- 이 문장을 유지
- 대신 “최소 가공본”이라고 설명

2. 분석 즉시 활용을 더 중시하면
- 최소한 `copyright` 제거는 남김

제 추천:
- **최소한 copyright 제거는 남기는 편이 낫습니다.**
- 그렇지 않으면 stage3가 “분석용 전처리본”이라기보다 “중복통합+부분가공본”에 가까워집니다.

**4-2. `collision_row` 명칭**
바꾸는 방향은 괜찮습니다.  
다만 이름만 보면 “충돌한 행”처럼 읽힐 수 있어서 약간 헷갈릴 여지가 있습니다.

더 직관적인 대안:
- `collision_columns`

하지만 `collision_row`를 꼭 쓰고 싶다면 써도 됩니다.  
다만 제안하자면 **`collision_columns`가 더 정확합니다.**

**5. 최종적으로 보면**
지금 규칙은 다음처럼 정리하면 가장 안정적입니다.

**그대로 가도 좋은 부분**
- stage1의 `_raw` 제거
- stage1 17열 구성
- stage2 대표행 선택 우선순위
- stage2에서 provenance 축소
- stage3에서 `era_year` 분할
- stage3에서 `detail_url` 제거

**반드시 더 명시해야 하는 부분**
1. `qrynewstype`가 그룹 내 2개 이상일 때 처리 방식
2. `collision_row` 비교 기준
3. `h1_clean`의 정확한 적용 범위
4. `collision_row` 빈값 처리 방식

**수정 권장**
1. `collision_row` -> `collision_columns`
2. stage3에서 최소한 `copyright` 제거 유지
3. `h1_clean`은 보수적으로
   - `SP`
   - `h1 길이 >= 30`
   - suffix-prefix overlap >= 8
   - 경계 ±3자 괄호
   일 때만 적용

원하면 다음 단계로
1. 이 규칙을 반영한 **최종 사양안**을 제가 다시 한 번 깔끔하게 써드리거나
2. 바로 이 사양에 맞춰 `shenbao_textdata_preprocess_combine_ver2.py` 구현에 들어갈 수 있습니다.

---
## 2-2. h1과 content_box2의 중복 처리 방향 검토
### 프롬프트 2-2-1
- h1을 정제해 h1_clean을 생성하는 방안과 content_box2를 정제해 content_box2_clean을 생성하는 방안 중 어느 것이 더 타당한지, 그리고 동시에 content_box2에서 괄호 다음에 등장하는  lv1_div 값과 동일한 문자열을 삭제하는 로직을 추가하는 방안은 타당한가? 이는 content_box2 문자열에서 탐지된 괄호 다음에 lv1_div 값과 동일한 문자열이 나오는지와 관련됨. 이는 이후 분석용 데이터를 만들 때 h1, lv1_div, content_box2를 병합해 사용하려는 계획에 방해가 되는데, 예를 들어 xianzheng, 4766의 경우, 원문 지면을 보면 제목인 `要摺 學部會奏議覆法律大臣奏法律學堂乙班學員改官辦法摺` 다음에 `〔續〕`가 붙어 있고 그 다음에 본문 `至於原官在七品以上...`이 나오는데, 이 경우 h1_clean을 만들면 원래 제목에서 `班學員改官辦法摺〔續〕` 부분이 잘려서 본문 영역으로 들어가게 되는거야. 문제는 이런 사례가 전체 데이터에서 차지하는 비중이 크지는 않다는 거야. h1을 정제할 때와 content_box2를 정제할 때 각각의 편익이 무엇인지를 판단해야 해. 이상의 내용에 대한 판단을 위해 나에게 더 물어볼 것이 있다면 물어봐줘.

### 답변 2-2-1
결론부터 말하면, **현재 목적이 `h1 + lv1_div + content_box2`를 병합한 분석용 문자열을 만드는 것이라면, `h1_clean`보다 `content_box2_clean`을 만드는 쪽이 더 타당합니다.**

**이유**
1. **오류가 실제로 드러나는 위치가 `content_box2` 시작부이기 때문입니다.**
- 지금 문제 삼는 집합은 `h1 suffix`와 `content_box2 prefix`가 겹치는 괄호 경계형 `21건`입니다.
- 이 경우 분석용 병합에서 중복이 생기는 직접 원인은 대체로 **`content_box2` 첫머리에 중복 구간이 다시 한 번 붙어 있는 것**입니다.

2. **`h1`를 자르면 제목 자체를 훼손할 위험이 더 큽니다.**
- `xianzheng, 4766`이 대표적입니다.
- 이 사례는 제목 말미의 `...改官辦法摺`이 실제 제목 일부인데, `h1_clean`을 만들면서 겹치는 suffix를 자르면 제목 끝이 잘려 나갑니다.
- 반면 `content_box2` 쪽에서 `法摺〔續〕...`를 정리하면, **제목은 보존하고 본문 시작부의 중복만 제거**할 수 있습니다.

3. **현재 집합의 규모가 작아서, 보수적으로 처리하는 편이 맞습니다.**
- 괄호 경계형 자체가 `21건`뿐입니다.
- 전체 코퍼스에 비해 매우 작으므로, **제목 필드 전체를 적극적으로 재단하는 방식보다 본문 시작부만 국소적으로 정리하는 방식이 더 안전**합니다.

**두 방식의 편익 비교**

**1. `h1_clean` 중심**
장점:
- 제목 필드만 손보므로, 본문 원문은 그대로 둘 수 있음
- “제목이 과도하게 길어진 경우”를 바로 교정하는 데는 직관적임

단점:
- 지금 문제 집합에서는 **실제 제목 일부를 잘라낼 위험**이 큼
- 특히 `xianzheng, 4766` 같은 사례에서 부정확
- 이후 제목 자체를 따로 연구하거나 검증할 때 손상된 제목을 남길 수 있음

**2. `content_box2_clean` 중심**
장점:
- `h1` 제목을 보존할 수 있음
- 병합용 문자열에서 생기는 **경계부 중복**을 직접 제거할 수 있음
- 현재 문제의 실질적 사용 목적, 즉 `h1 + lv1_div + content_box2` 병합에 더 잘 맞음

단점:
- 본문 필드를 손대므로 규칙이 넓어지면 과잉 삭제 위험이 있음
- 따라서 **괄호 경계형에만 한정한 매우 좁은 규칙**으로 써야 함

**따라서 추천**
- `h1_raw`는 그대로 둠
- `content_box2_raw`도 그대로 둠
- 별도로 **`content_box2_clean`**을 만들고,
- **괄호 경계형 21건에만** 중복 prefix 제거 규칙을 적용

이 방식이 가장 보수적이고 재현 가능성이 높습니다.

---

**추가 제안한 로직: `content_box2`에서 괄호 다음에 나오는 `lv1_div` 동일 문자열 삭제`**
이건 **일반 규칙으로는 약하고, 매우 좁은 보조 규칙으로는 타당**합니다.

방금 다시 확인한 결과:
- 괄호 경계형 `21건` 중
- `content_box2`의 괄호 뒤에 `lv1_div`와 동일한 문자열이 실제로 나오는 경우는 **1건**
- 바로 `xianzheng, 4766`입니다.

즉 이 현상은:
- **존재는 확실하지만**
- **매우 드문 예외**입니다.

그래서 구현 방식은 이렇게 가는 게 맞습니다.

**권장 규칙**
1. 먼저 괄호 경계형 `21건`에 대해 `content_box2` 시작부의 **중복 prefix**를 제거
2. 그 다음, 제거 후 `content_box2` 맨 앞에
   - `〔{lv1_div}〕`
   - `（{lv1_div}）`
   같은 **괄호로 둘러싸인 표지**가 남아 있고,
   - 그 안의 문자열이 `lv1_div`와 같으면
   - **그 괄호 표지 전체를 제거**

중요:
- **`lv1_div` 문자열만 지우면 안 됩니다.**
- `續`만 지우고 `〔〕`를 남기면 문자열이 더 망가집니다.
- 따라서 지울 거면 **`〔續〕` 전체**를 지워야 합니다.

**판단**
- 이 보조 로직은 `xianzheng, 4766` 같은 사례에는 유효합니다.
- 하지만 현재 확인된 건 `1건`뿐이므로,
- **stage3의 일반 핵심 로직으로 두기보다는, content_box2_clean 안의 좁은 후처리 예외 규칙**으로 두는 것이 맞습니다.

---

**실무적으로 가장 타당한 설계**
1. `h1_raw` 유지
2. `content_box2_raw` 유지
3. `content_box2_clean` 생성
4. `content_box2_clean`에는
   - 괄호 경계형 `suffix-prefix` 중복 제거
   - 필요시 `〔lv1_div〕` / `（lv1_div）` 제거
5. 병합용 `analysis_text`는
   - `h1_raw` 또는 별도 손대지 않은 `h1`
   - `lv1_div`
   - `content_box2_clean`
   을 사용

즉, 현재 목적에는 **`h1_clean`보다 `content_box2_clean`이 우선**입니다.

짧게 정리하면:
- **제목 보존이 우선이면 `h1`를 자르지 말고 `content_box2` 시작부를 정리하는 편이 맞습니다.**
- **`lv1_div` 반복 삭제는 가능하지만, 일반 규칙이 아니라 `xianzheng, 4766`형의 드문 예외를 위한 좁은 보조 규칙으로만 두는 것이 타당합니다.**

원하면 다음 단계로 이 판단을 기준으로 `stage3` 규칙을 다시 써드리겠습니다.

---
### 프롬프트 2-2-2
이 문제를 고민하게 되는 이유는 zhixian, 1969와 같은 사례 때문이야. 이 사례는 h1에 본문 내용이 말려 올라가는 한편 괄호 경계로 인한 오탑재, 중복 탑재가 발생해서 같은 내용이 content_box2에도 한 번 더 기입되어 있어. 원자료 지면에서는 당연히 내용이 중복되는 게 아니라 한 번만 나오는 내용이고. 여기에서 오류를 발생시킨 괄호 문자열은 `（未完）`인데, `未完`은 lv1_div에도 기록되어 있어. 이 때 실용적으로만 봤을 때는 content_box2 쪽의 중복과 괄호 문자열을 삭제하는 것이 타당한데, 그러면 h1에 제목과 본문이 모두 들어가게 된다는 점에서 content_box2를 삭제하는 게 타당할 것인가가 문제야. 물론 h1으로 본문이 딸려 올라간 사례는 많으니까 이런 사례 몇 개가 추가된다고 해도 상관 없을 것 같기도 해
### 답변 2-2-2
이 사례 때문에 더더욱 **`h1_clean`보다 `content_box2_clean` + `analysis_text` 방식이 낫습니다.**

핵심 판단은 이렇습니다.

**1. `zhixian, 1969`는 `h1`를 정제 기준으로 삼기 어려운 사례다**
이 행에서는 문제가 두 겹입니다.

- `h1`에 제목과 본문이 함께 말려 올라감
- 같은 내용이 `content_box2`에도 다시 들어감
- 그 경계에 `（未完）`이 끼어 있음
- `lv1_div`에도 `未完`이 기록됨

여기서 `h1`를 잘라서 `h1_clean`을 만들면:
- 제목과 본문이 한 필드에 섞인 상태에서
- 어디까지가 제목이고 어디부터가 본문인지 다시 나눠야 합니다
- 이건 일반 규칙으로 처리하기 어렵습니다

즉, 이 유형은 **`h1`를 “제목 필드”로 복구하는 문제**라기보다,  
**분석용 문자열에서 중복만 제거하는 문제**에 가깝습니다.

**2. 실용적으로는 `content_box2` 쪽을 비우는 편이 더 타당하다**
`zhixian, 1969` 같은 경우에는
- 이미 `h1` 안에 제목+본문이 다 들어 있고
- `content_box2`는 그걸 다시 한 번 반복한 쪽입니다

그래서 분석 목적만 놓고 보면:
- `content_box2`의 중복 구간 제거
- `（未完）` 제거
- 필요하면 `〔續〕`/`（未完）`처럼 `lv1_div`와 같은 표지 제거
를 한 뒤,
- **남는 게 사실상 없으면 `content_box2_clean=''`로 두는 편이 맞습니다.**

즉 이 경우에는 “`content_box2`를 삭제한다”기보다,
- **`content_box2_clean`이 빈 문자열이 되도록 허용**하는 게 맞습니다.

이건 타당합니다.  
왜냐하면 이 행의 실제 분석 텍스트는 이미 `h1` 안에 있기 때문입니다.

**3. 다만 이 판단은 `field 정제`가 아니라 `analysis_text 구성`의 문제로 다루는 게 안전하다**
여기서 가장 중요한 건,
- 원본 구조를 복구하려고 너무 애쓰지 말고
- **분석에 쓸 최종 문자열을 어떻게 만들지**를 기준으로 판단하는 것입니다.

권장 구조:
- `h1_raw`: 원본 유지
- `content_box2_raw`: 원본 유지
- `content_box2_clean`: 중복 prefix/표지 제거
- `analysis_text`: 최종 분석용 병합 문자열

그리고 `analysis_text`는 이렇게 만듭니다.

1. 일반 행:
- `h1_raw + lv1_div + content_box2_clean`

2. `zhixian, 1969`형:
- `content_box2_clean`이 비거나 매우 짧아지면
- **`analysis_text = h1_raw` 중심으로 사용**
- `lv1_div='未完'`은 포함 여부를 별도 결정

즉,
- `content_box2_clean`이 비어도 괜찮고
- 그 대신 `analysis_text`가 그 행의 실제 텍스트를 대표하면 됩니다.

**4. `lv1_div`와 같은 문자열이 괄호 뒤에 나오면 삭제하는 로직은 타당하지만, 매우 좁게 써야 한다**
앞서 확인한 바로는,
- 괄호 경계형 사례 중
- `content_box2`의 괄호 뒤에 `lv1_div`와 같은 문자열이 나오는 경우는 사실상 `xianzheng, 4766`형 1건만 확실했습니다.

따라서 이 로직은
- 일반 규칙으로 크게 쓰기보다는
- **중복 제거 후 남은 `content_box2` 시작부가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`면 그 표지만 제거**
하는 보조 규칙으로 두는 것이 맞습니다.

**5. 최종 추천**
지금 목적에는 아래가 가장 타당합니다.

- `h1_clean`을 핵심으로 두지 말 것
- `h1_raw`는 보존할 것
- `content_box2_clean`을 만들 것
- 괄호 경계형에서는 `content_box2` 쪽 중복을 제거할 것
- 제거 후 `content_box2`가 사실상 비면 그대로 빈값 허용
- 최종 분석은 `analysis_text`에서 해결할 것

즉, **제목 필드를 복구하려는 설계보다, 분석용 문자열에서 중복을 제거하는 설계가 더 맞습니다.**

짧게 정리하면:
- `zhixian, 1969` 같은 사례 때문에라도 `h1_clean` 중심 설계는 위험합니다.
- 이 경우에는 `content_box2_clean`이 비어도 괜찮고,
- `analysis_text`가 `h1`를 본문 운반체로 받아들이는 쪽이 더 실용적입니다.

원하면 다음 단계로
1. 이 판단을 반영한 `stage3` 열 설계를 다시 써드리거나
2. `content_box2_clean`과 `analysis_text` 생성 규칙을 바로 의사코드 수준으로 정리해드리겠습니다.
---
## 2-3. stage3 정렬 기준과 analysis_text 생성 원칙
### 프롬프트 2-3-1
작업 대상 데이터와 stage1, stage2 로직을 고려할 때, stage3에서의 재정렬 규칙에서 4. representative_item_index 오름차순 5. 최종 tie-breaker로 preprocess_indices 중 최소값 둘 모두를 규정할 필요가 있을까? 둘 중 하나만 남겨 놓는다면 무엇을 남겨놔야 하고, 둘 다 제거할 시 발생할 수 있는 문제가 무엇인지 알려줘

### 답변 2-3-1
결론부터 말하면, **둘 다 반드시 필요하지는 않습니다.**  
다만 두 값의 역할이 다릅니다.

- `representative_item_index`
  - 사람이 보기에는 더 자연스럽습니다.
  - 같은 날짜·같은 판면 안에서 “기사 목록 순서 비슷한 것”을 어느 정도 반영합니다.
  - 하지만 **고유하지 않습니다.**
  - 또 대표행 선택 기준이 바뀌면 값이 바뀔 수 있습니다.

- `min(preprocess_indices)`
  - 사람에게 의미 있는 순서는 아닙니다.
  - 대신 **항상 고유하고 안정적**입니다.
  - stage1 append 순서가 고정되어 있으면, rerun 시에도 같은 순서를 재현하기 쉽습니다.

**따라서 하나만 남긴다면**
- **`min(preprocess_indices)`를 남기는 편이 더 낫습니다.**

이유:
1. **완전한 tie-breaker 역할**을 합니다.
2. 대표행 선택 로직 변화에 덜 흔들립니다.
3. `stage3_index`를 붙일 때 **재현 가능한 총순서(total order)**를 보장합니다.

반대로 `representative_item_index`만 남기면:
- 같은 `date + issue_page + qrynewstype + representative_item_index` 조합이 충분히 생길 수 있고,
- 그 경우 최종 순서가 다시 불안정해집니다.

**둘 다 제거하면 생길 수 있는 문제**
1. 같은 `date + issue_page + qrynewstype` 안의 행들이 대량으로 동률이 됩니다.
2. 그 상태에서 최종 순서는
   - 그룹화 순서
   - 입력 순서
   - 정렬 구현의 안정성
에 암묵적으로 의존하게 됩니다.
3. 그래서
   - `stage3_index`가 rerun마다 달라질 수 있고
   - diff 비교가 어려워지고
   - 논문/메모에서 행 번호로 참조하기 불편해지고
   - 샘플 추출 결과도 미세하게 흔들릴 수 있습니다.

**실무적으로 가장 좋은 정리**
- `4`와 `5`를 둘 다 유지할 수도 있지만,
- 더 깔끔한 건 사실 아래 조합입니다.

정렬:
1. `date`
2. `issue_page`
3. `qrynewstype`
4. `representative_item_index`
5. **`article_id`**

즉,
- 사람이 보기 좋은 순서는 `representative_item_index`로 잡고
- 최종 tie-breaker는 `min(preprocess_indices)`보다 **`article_id`**가 더 낫습니다.

이유:
- `article_id`는 고유하고 안정적입니다.
- stage1 append 순서에 의존하지 않습니다.
- 대표행 선택 결과와도 무관합니다.

**최종 권고**
- 현재 4와 5 중 하나만 남겨야 하면: **`5`**
- 둘 다 제거하는 것은 비추천
- 가능하면 최종안은:
  - `date`
  - `issue_page`
  - `qrynewstype`
  - `representative_item_index`
  - `article_id`
로 가는 것이 가장 깔끔합니다.
---
### 프롬프트 2-3-2
`10_data-profile....md` 파일들의 내용을 검토해서, 아래 내용에 더 들어가야 할 데이터 정제 규칙이 있는지 확인.

```text
- `analysis_text` 열 추가
	- `h1`, `lv1_div`, `content_box2`를 병합
	- `lv1_div=本報訊`인 경우 `h1` 과 `content_box2` 만을 병합
	- `special_column=分類廣告` 개체는 `h1`과 `lv1_div`을 제외하고 `content_box2`만을 `analysis_text`로 복사
	- special_column이 비어 있고 qrynewstype=SP인 기사 중, **공백·구두점·기호 제거 후** h1 끝과 content_box2 시작이 중복되며, 그 경계가 〕...〔로 나타나는 사례에 대해서는 content_box2에서 중복 구간을 삭제한 후 병합
	- 관련 사전 검토 사항
		- 병합 시 각 열에서 나온 문자열 사이에 구분선 `|`을 넣는 것의 장단점 검토
		- 괄호 경계형 중복 개체를 기록하는 열 추가 필요성 검토 및 필요할 경우 적절한 헤더명 추천
```

### 답변 2-3-2
검토 결과, `analysis_text`에는 **새 규칙을 많이 추가할 필요는 없고**, 현재 규칙에 **3가지만 보정·추가**하는 것이 타당합니다.

근거가 되는 문서:
- `分類廣告` 구조: 10_data-profile_10_分類廣告 개체의 구조적 특징.md:40, 10_data-profile_10_分類廣告 개체의 구조적 특징.md:90
- 괄호 경계형과 정규화 조건: 10_data-profile_9_괄호 경계형 중복 개체의 분포와 특징.md:1005, 10_data-profile_9_괄호 경계형 중복 개체의 분포와 특징.md:1114
- `xianzheng, 4766`, `zhixian, 1969` 예외: 10_data-profile_9_괄호 경계형 중복 개체의 분포와 특징.md:322, 10_data-profile_9_괄호 경계형 중복 개체의 분포와 특징.md:329
- 괄호 경계형만 파싱 오류로 해석: 10_data-profile_8_h1(제목 영역)과 content-box2(본문 영역)의 탑재 방식.md:698과%20content-box2(본문%20영역)의%20탑재%20방식.md:698)

추가·보정이 필요한 규칙은 아래 3개입니다.

1. `〕...〔` 규칙의 정규화 조건을 좁혀야 합니다.
- 현재 문안은 `공백·구두점·기호 제거 후`라고 되어 있습니다.
- 그런데 실제 검증 결과, 의도한 `〕...〔`형 64건은 **공백 정규화만으로 충분**합니다.
- 따라서 이 규칙은
  - `공백 정규화 후 h1 끝과 content_box2 시작이 중복되고`
  - `경계가 〕...〔로 나타나는 경우`
로 쓰는 편이 더 정확합니다.
- 이건 새 규칙이라기보다 **기존 규칙의 보정**입니다.

2. 중복 제거 대상이 `h1`가 아니라 `content_box2`라는 점을 더 명시해야 합니다.
- 현재 문안에도 `content_box2에서 중복 구간을 삭제`라고 적혀 있어서 방향은 맞습니다.
- 다만 `10_data-profile` 문서들을 보면, `h1`를 잘라 `h1_clean`을 만드는 방식은 `xianzheng, 4766`이나 `zhixian, 1969` 같은 사례에서 제목을 오히려 훼손할 위험이 큽니다.
- 따라서 stage3 규칙에는
  - `h1_raw`는 유지
  - `analysis_text`용 정제는 `content_box2` 쪽에서만 수행
을 더 분명히 써두는 편이 좋습니다.

3. 중복 제거 직후 `lv1_div`와 같은 괄호 표지를 지우는 좁은 후처리가 필요합니다.
- 이건 새로 추가하는 것이 타당합니다.
- 예외 유형:
  - `xianzheng, 4766`: 중복 제거 후 `content_box2` 시작부에 `〔續〕`
  - `zhixian, 1969`: 중복 제거 경계 직후 `（未完）`
- 따라서 `〕...〔`형 또는 그에 준하는 좁은 예외에서 중복 구간을 제거한 뒤,
  - `content_box2` 맨 앞이 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면
  - 그 괄호 표지 전체를 삭제
하는 규칙을 넣는 것이 좋습니다.
- 이 규칙은 매우 좁고, 현재 확인된 예외를 정확히 처리합니다.

반대로, **추가하지 않는 것이 좋은 규칙**도 분명합니다.

1. `SP_AD` 전체에 대한 일반 중복 제거 규칙
- 넣지 않는 편이 맞습니다.
- `SP_AD`에는 `〕...〔`형이 없고, 구조도 `分類廣告`와 다릅니다.
- broad rule로 잡으면 오탐이 늘어납니다.

2. `h1_clean`을 별도로 만드는 일반 규칙
- 지금 stage3의 `analysis_text` 목적에는 불필요합니다.
- `h1`는 raw 유지, `content_box2`만 좁게 정제하는 편이 안전합니다.

3. `[H>]`, `[P>]` 제거 규칙
- 지금 단계에서는 넣지 않는 편이 낫습니다.
- 관련 메모에서는 이 표식들을 광고 지면의 헤더/페이지 구분 표지로 보고 일단 처리 보류하자는 판단이 들어가 있습니다.
- 즉 `analysis_text`에 대한 일반 규칙으로 바로 넣기에는 아직 범위가 넓습니다.
- 이건 별도 광고 지면 연구 단계에서 다시 다루는 편이 맞습니다.

정리하면, `analysis_text`에는 아래 정도만 더 들어가면 충분합니다.

- `分類廣告`는 `content_box2`만 사용
- `lv1_div=本報訊`이면 `lv1_div` 제외
- `special_column=''` and `qrynewstype=SP` and **공백 정규화 후** `〕...〔`형 중복이면 `content_box2`에서 중복 제거
- 그 직후 `content_box2` 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 전체 제거
- 정제 후 `content_box2`가 비면, 남은 비결측 구성요소만으로 `analysis_text` 생성

즉, 새로 넣을 만한 실질 규칙은 **1개**이고, 나머지는 **기존 문안의 정밀화**입니다.

추가 메모:
- 현재 stage3 헤더 블록은 `analysis_text`를 설명하면서도 열 목록에는 아직 `h1_clean`이 남아 있어 내부 정합성이 맞지 않습니다. 이건 규칙 확정 후 같이 맞춰야 합니다.


---
### 프롬프트 2-3-3
이제 다시 shenbao_textdata_preprocess_combine.py의 수정에 관한 내용으로 돌아가자. 현재까지 정한 stage3 작업 방식 변경 관련 지침은 아래와 같아. 

stage3
	- stage2까지 과정에서는 데이터베이스에서 수집한 `publish_variant`부터 `theme`까지의 내용을 가공하지 않고 원 데이터를 유지했는데, stage3는 원 데이터 가공을 통해 분석에 바로 활용할 수 있는 문자열을 작성하고 분할이 필요한 부분을 분할하는 것이 목적
	- 작업에 앞서 전체 행 순서를 다음 규칙에 따라 재정렬
		1. `date` 오름차순
		2. `qrynewstype` 순서: SP → SP_AD → SP_FH → SP_HK
		3. `issue_page` 숫자 오름차순, `issue_page`가 비거나 숫자 변환이 안 되면 같은 `qrynewstype` 개체 중 맨 뒤에 배치
		4. 최종 tie-breaker로 article_id 오름차순
	- `dataset_index` 열을 생성하여 재정렬한 순서에 따라 일련 번호 부여
	- `era_year`를 `chinese_era_year`, `japanese_era_year`로 분할하는 로직 유지
	- stage2에서 stage3로 가면서 `detail_url`을 제거하는 로직 유지
	- 나머지 문자열 정제 로직은 제거
	- `analysis_text` 열 추가
		- `h1`, `lv1_div`, `content_box2`를 병합해 기록
		- `lv1_div=本報訊`인 경우 `h1` 과 `content_box2` 만을 병합
		- `special_column=分類廣告` 개체는 `h1`과 `lv1_div`을 제외하고 `content_box2`만을 `analysis_text`로 복사
		- `special_column`이 비어 있고 qrynewstype=SP인 기사 중, **공백·구두점·기호 제거 후** h1 끝과 content_box2 시작이 중복되며, 그 경계가 〕...〔로 나타나는 사례에 대해서는 content_box2에서 중복 구간을 삭제한 후 병합
		- `lv1_div=本報訊`이면 `lv1_div` 제외
		- `special_column=分類廣告`이면 `h1` 제외
		- `special_column=''` and `qrynewstype=SP` and **공백 정규화 후** `〕...〔`형 중복이면 `content_box2`에서 중복 제거
		- 그 직후 `content_box2` 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 전체 제거
		- 정제 후 `content_box2`가 비면, 남은 비결측 구성요소만으로 `analysis_text` 생성

이에 관해 
- 병합 시 각 열에서 나온 문자열 사이에 구분선 `|`을 넣는 것의 장단점 검토
- 괄호 경계형 중복 개체를 기록하는 열 추가 필요성 검토 및 필요할 경우 적절한 헤더명을 추천

하고, 내가 검토, 확인을 요청한 내용 외에 작업에 영향을 줄 수 있는 모호한 지점이나 수정할 부분이 있는지 확인해서 알려줘

### 답변 2-3-3
검토 결과, stage3의 `analysis_text` 관련 규칙은 방향 자체는 타당합니다. 다만 그대로 구현에 들어가면 **중복·충돌·미정의 지점**이 몇 군데 있습니다. 먼저 질문한 두 항목부터 정리하면 아래와 같습니다.

#### 1. `|` 구분선 삽입 여부

결론:
- `analysis_text`에는 **넣지 않는 편이 낫습니다.**

장점:
- 사람이 육안으로 볼 때 `h1 / lv1_div / content_box2` 경계가 분명해집니다.
- 디버깅과 예외 사례 확인이 쉬워집니다.

단점:
- `analysis_text`가 “바로 분석용 텍스트”라는 목적과 충돌합니다.
- `|`는 원문에 없는 인공 기호이므로 토큰화, n-gram, 빈도 집계, 문장 분할에 노이즈가 됩니다.
- 특히 한중문 텍스트 분석에서는 인공 구분기호를 최소화하는 편이 안전합니다.

판단:
- `analysis_text`는 **인공 기호 없는 순수 분석용 문자열**로 두는 것이 맞습니다.
- 사람이 확인하기 위한 병합 흔적이 필요하면, 나중에 별도 디버그 열을 두는 편이 낫습니다.
  - 예: `analysis_text_marked`
- 지금 단계에서는 열을 늘리지 않고 `analysis_text`를 순수 텍스트로 유지하는 편이 더 보수적이고 실용적입니다.

권장:
- `analysis_text`에는 `|`를 넣지 않음
- 병합은 비결측 문자열만 순서대로 이어붙임
- 별도 마킹 열은 지금은 생략

#### 2. 괄호 경계형 중복 개체 기록 열 추가 여부

결론:
- **추가하는 편이 좋습니다.**
- 다만 “괄호 경계형만 기록하는 열”보다, **실제 어떤 규칙으로 `analysis_text`가 만들어졌는지 기록하는 열**이 더 유용합니다.

이유:
- 지금 `analysis_text`는 단순 병합이 아니라, 경우에 따라
  - `lv1_div=本報訊` 제거
  - `分類廣告`에서 `content_box2`만 사용
  - `〕...〔`형 중복 제거
  - `〔lv1_div〕`, `（lv1_div）` 제거
까지 수행합니다.
- 따라서 나중에 특정 행의 분석용 텍스트가 왜 그렇게 만들어졌는지 추적하려면, 괄호 경계형 여부만으로는 부족합니다.

가장 좋은 최소안:
- 열 이름: `analysis_text_rule`

예시 값:
- `plain_merge`
- `drop_benbaoxun`
- `classified_box2_only`
- `bracket_dedup`
- `bracket_dedup_and_strip_lv1_marker`

이 방식의 장점:
- 괄호 경계형 여부도 포함되고
- `分類廣告`, `本報訊` 예외도 함께 기록됩니다.
- 디버깅과 재현성이 좋아집니다.

정말 최소한의 boolean만 원하면:
- 열 이름: `bracket_dup`
- 값: `T` / `F`

하지만 제 판단으로는 지금 설계에서는 `bracket_dup`보다 `analysis_text_rule`이 더 낫습니다.

#### 3. 현재 규칙에서 바로 수정해야 할 모호점

##### 3-1. 같은 규칙이 중복 서술되어 있습니다
현재 문안에는 아래가 두 번씩 들어가 있습니다.

- `lv1_div=本報訊`이면 `lv1_div` 제외
- `special_column=分類廣告`이면 `h1` 제외
- 괄호 경계형일 때 `content_box2` 중복 제거

이건 구현 전에 한 번 정리해야 합니다.

##### 3-2. 정규화 기준이 서로 충돌합니다
현재 문안에는 두 버전이 섞여 있습니다.

- `공백·구두점·기호 제거 후`
- `공백 정규화 후`

이건 반드시 하나로 고정해야 합니다.

현재까지의 검토 결과에 따르면:
- `〕...〔`형 64건 재현에는 **공백 정규화만으로 충분**합니다.
- 따라서 여기서는 `공백 정규화 후`로 고정하는 편이 더 정확합니다.

권장 문구:
- `special_column=''` and `qrynewstype=SP` and **공백 정규화 후** `h1` 끝과 `content_box2` 시작이 중복되며, 그 경계가 `〕...〔`로 나타나는 경우

##### 3-3. `content_box2`를 수정하는지, raw 열은 유지하는지 명시가 필요합니다
현재 문안만 보면, `content_box2` 자체를 수정하는지, 아니면 `analysis_text` 생성용 임시 문자열만 수정하는지 불분명합니다.

이건 분명히 해야 합니다.

권장:
- stage3의 원본 열 `h1`, `lv1_div`, `content_box2`는 **그대로 유지**
- 중복 제거와 표지 제거는 **`analysis_text` 생성 과정에서만 적용**
- 즉 `content_box2_clean`이라는 임시 개념으로만 처리하고, 별도 열로 저장하지는 않음

##### 3-4. `h1_clean`은 현재 규칙과 맞지 않습니다
현재 stage3 설명은 이미 `analysis_text` 중심으로 바뀌었는데, 헤더 예시에는 아직 `h1_clean`이 남아 있습니다.

그런데 현재 합의된 방향은:
- `h1` 자체를 정제해서 저장하는 것이 아니라
- `analysis_text` 생성 시 `content_box2` 쪽 중복만 좁게 제거하는 방식

즉 `h1_clean`은 지금 설계와 어긋납니다.

판단:
- `h1_clean`은 제거하는 편이 맞습니다.
- 대신 `analysis_text`와 필요하면 `analysis_text_rule`을 넣는 편이 논리적으로 일관됩니다.

##### 3-5. `era_year` 원열 이름도 정리해야 합니다
stage2에서는 `era_year`
stage3에서는 `era_year_raw`, `chinese_era_year`, `japanese_era_year`

이 구조라면:
- stage3에서 원열을 유지할 거면 `era_year_raw`로 이름을 바꾸는 것이 맞습니다.
- 이건 현재 문안 방향과 일치합니다.

##### 3-6. `analysis_text` 병합 순서와 결측 처리 규칙을 명시해야 합니다
권장:
- 병합 순서 고정: `h1` → `lv1_div` → `content_box2`
- 각 규칙 적용 후 비어 있지 않은 구성요소만 이어붙임
- 중간 구성요소가 비어 있어도 나머지는 그대로 병합
- 정제 후 `content_box2`가 비면 남은 구성요소만 사용

##### 3-7. `〔{lv1_div}〕` / `（{lv1_div}）` 제거 규칙의 적용 위치를 명시해야 합니다
이건 반드시 **중복 구간 제거 이후**에 적용되어야 합니다.

즉 순서는:
1. `〕...〔`형 중복 판정
2. `content_box2` 선두의 중복 구간 제거
3. 제거 후 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 제거
4. 남은 요소들로 `analysis_text` 병합

이 순서를 명시하는 것이 좋습니다.

#### 4. 지금 단계에서 넣지 않는 것이 좋은 규칙

##### 4-1. `SP_AD` 일반 중복 제거 규칙
넣지 않는 편이 맞습니다.
- `SP_AD`에는 `〕...〔`형이 없고
- 구조가 `分類廣告`와도 다릅니다.
- broad rule을 넣으면 오탐 가능성이 큽니다.

##### 4-2. `[H>]`, `[P>]` 제거 규칙
지금은 넣지 않는 편이 맞습니다.
- 현재 메모들에서도 광고 지면의 헤더/페이지 구분 표식으로 보고 일단 처리 보류하는 쪽으로 정리돼 있습니다.
- stage3의 핵심 분석용 텍스트 규칙으로 바로 넣기에는 아직 범위가 넓습니다.

#### 5. 최종 권장안

실제 구현용으로는 아래처럼 정리하는 것이 가장 깔끔합니다.

- `analysis_text`는 비결측 구성요소만 병합해 생성
- 병합 순서: `h1` → `lv1_div` → `content_box2`
- `lv1_div=本報訊`이면 `lv1_div` 제외
- `special_column=分類廣告`이면 `content_box2`만 사용
- `special_column=''` and `qrynewstype=SP` and **공백 정규화 후** `h1` 끝과 `content_box2` 시작이 중복되며 경계가 `〕...〔`형이면, `analysis_text` 생성용 `content_box2`에서 중복 구간 제거
- 그 직후 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 전체 제거
- 정제 후 `content_box2`가 비면 남은 비결측 구성요소만으로 `analysis_text` 생성
- raw 열 `h1`, `lv1_div`, `content_box2`는 수정하지 않음
- 추적용 열은 `analysis_text_rule` 추가 권장

#### 6. 한 줄 결론

추가 규칙은 많이 필요하지 않습니다.  
실질적으로 필요한 것은:

1. `〕...〔`형의 정규화 기준을 `공백 정규화`로 고정
2. `〔{lv1_div}〕` / `（{lv1_div}）` 제거 후처리 추가
3. `analysis_text_rule` 같은 추적 열 추가

이 세 가지입니다.

원하면 다음 단계로, 이 판단을 반영해서 `stage3` 규칙 문단 전체를 **중복 없이 바로 코드로 옮길 수 있는 문안**으로 다시 써드리겠습니다.

---
## 2-4. 괄호 경계형 중복 개체의 판정 규칙 검토
### 프롬프트 2-4-1
4개의 원본 파일로부터 지금 제시된 

```
special_column='' and qrynewstype=SP and 공백 정규화 후 h1 끝과 content_box2 시작이 중복되며 경계가 〕...〔형인 경우
```
의 선별 규칙으로 행을 선별하고,(그룹 1)

```
special_column='' and qrynewstype=SP and 공백 정규화 후 h1 전부 혹은 h1 끝과 content_box2 시작이 중복되며 content_box2에서 중복 구간의 후방 경계가 `...〔` 형식인 경우
```
의 선별 규칙으로 행을 선별해서,(그룹 2)

1. 그룹 1과 그룹 2의 일치 여부 및 두 그룹이 각각 포함하는 개체 수량
2. 일치하지 않는다면 차이가 존재하는 행의 실제 사례를 그룹별로 shenbao\shenbao_textdata\data_profile\shenbao_textdata_dup_with_bracket_rows.csv와 같은 양식으로 출력해줘. 만약 그룹별 사례가 10건 이하라면 채팅창에 출력하고, 10건 이상이라면 shenbao\shenbao_textdata\data_profile 경로에 적당한 파일명으로 저장해줘. 참고할 csv의 작성 규칙은 아래와 같아

- csv 구조: label, item_index, qrynewstype, date, special_column, h1dupprefix,box2dupsuffix,h1bracket,box2bracket

- h1dupprefix: `h1에서 등장한 중복 구간 2글자 이내에서 발견된 괄호 문자의 주변 10자 문맥(괄호가 없을 경우 `중복구간의 prefix 10자만 출력)

- box2dupsuffix: `content-box2에서 등장한 중복 구간 2글자 이내에서 발견된 괄호 문자의 주변 10자 문맥`(괄호가 없을 경우 `중복구간의 prefix 10자`), - h1bracket: `h1`에서 중복 구간 경계 2자 이내에 괄호 문자가 있으면 T, 없으면 F. 이는 h1dupprefix의 괄호 문자 포함 여부와 같아야 함

- box2bracket: `content-box2에서 중복 구간 경계 2자 이내에 괄호 문자가 있으면 T, 없으면 F. 이는 box2dupprefix의 괄호 문자 포함 여부와 같아야 함

### 답변 2-4-1
공백 정규화 기준으로 4개 원본 CSV를 다시 검토했습니다.

결과:
- 그룹 1: `64건`
- 그룹 2: `66건`
- 공통: `64건`
- 그룹 1 전용: `0건`
- 그룹 2 전용: `2건`

판단:
- 두 그룹은 일치하지 않습니다.
- 그룹 1은 그룹 2의 진부분집합입니다.
- 차이는 `h1` 쪽에 `〕`가 없는 사례 2건입니다.
- 사용자 기준대로 차이 행 수가 10건 이하이므로 채팅창에 그대로 출력합니다. 별도 CSV는 만들지 않았습니다.

그룹 1 전용:
- 없음

그룹 2 전용:
```csv
label,item_index,qrynewstype,date,special_column,h1dupprefix,box2dupsuffix,h1bracket,box2bracket
xianzheng,4766,SP,1911-04-26,,班學員改官辦法摺,班學員改官辦法摺〔續〕 至於原官在七品,T? no,F? no
xianzheng,8310,SP,1908-09-16,,十,十諭〔二〕社說〔三〕選論〔,F,T
```

위 첫 행의 `h1bracket/box2bracket`를 정확한 CSV 형식으로 다시 쓰면 아래와 같습니다.

```csv
label,item_index,qrynewstype,date,special_column,h1dupprefix,box2dupsuffix,h1bracket,box2bracket
xianzheng,4766,SP,1911-04-26,,班學員改官辦法摺,班學員改官辦法摺〔續〕 至於原官在七品,F,T
xianzheng,8310,SP,1908-09-16,,十,十諭〔二〕社說〔三〕選論〔,F,T
```

해석:
- 그룹 2 규칙은 `content_box2` 후방 경계의 `...〔`만 요구하므로, `h1` 쪽 `〕`가 없는 행도 포함합니다.
- 그룹 1 규칙은 `〕...〔`를 요구하므로 위 2건을 제외합니다.

즉, 현재 두 규칙의 실질적 차이는 다음입니다.
- 그룹 1: `〕...〔`형만 선별
- 그룹 2: `...〔`형까지 포함하여 더 넓게 선별

원하면 다음 단계로
1. 이 2건의 원문 `h1`와 `content_box2` 앞부분까지 붙여 구조를 더 자세히 보여드리거나
2. 그룹 1 기준을 stage3 규칙 문장으로 바로 옮길 수 있게 한 줄 정의로 다시 정리하겠습니다.

---
### 프롬프트 2-4-2
그룹 2 기준을  stage3 규칙 문장으로 해줘
### 답변 2-4-2
아래처럼 쓰는 것이 가장 간단하고 구현 가능성이 높습니다.

```text
`special_column`이 비어 있고 `qrynewstype=SP`인 기사 중, 공백 정규화 후 `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며, 그 중복 구간의 `content_box2` 쪽 후방 경계 직후에 `〔`가 나타나는 경우에는 `analysis_text` 생성 시 `content_box2` 선두의 중복 구간을 제거한다.
```

조금 더 코드 지향적으로 쓰면:

```text
`special_column=''` and `qrynewstype=SP` and, after whitespace normalization, either (a) `content_box2` begins with all of `h1` or (b) a suffix of `h1` matches a prefix of `content_box2`, and the rear boundary of that duplicated segment on the `content_box2` side is immediately followed by `〔`; then remove the duplicated leading segment from `content_box2` when constructing `analysis_text`.
```

한국어 규칙 문장으로 최종 추천하는 버전은 첫 번째입니다.  
그 다음 단계 규칙까지 붙이면 이렇게 정리할 수 있습니다.

```text
`special_column`이 비어 있고 `qrynewstype=SP`인 기사 중, 공백 정규화 후 `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며, 그 중복 구간의 `content_box2` 쪽 후방 경계 직후에 `〔`가 나타나는 경우에는 `analysis_text` 생성 시 `content_box2` 선두의 중복 구간을 제거한다. 그 직후 `content_box2` 선두가 `〔{lv1_div}〕`이면 그 표지 전체를 추가로 제거한다.
```

주의:
- 이 그룹 2 규칙은 기존 `〕...〔`형보다 넓습니다.
- 따라서 `xianzheng, 4766`, `xianzheng, 8310` 같은 `h1` 쪽 괄호가 없는 사례도 포함합니다.


---
## 2-5. analysis_text_rules와 공백 처리 규칙 확정
### 프롬프트 2-5-1
1. 비결측 문자열만 구분선 삽입 없이 공백으로 구분해 이어 붙이기 
2. `analysis_text_rule` 추가, 값은 아래와 같이 입력
	- `1_drop_benbaoxun` - `lv1_div=本報訊`인 경우 `lv1_div` 제외하고 `h1` `content_box2`만 이어 붙이기
	- `2_box2_only` - `special_column=分類廣告`인 경우 `content_box2`만 그대로 `analysis_text`에 기록
	- `3_bracket_dedup` - `special_column`이 비어 있고 `qrynewstype=SP`인 기사 중, 공백 정규화 후 `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며, 그 중복 구간의 `content_box2` 쪽 후방 경계 직후에 `〔`가 나타나는 경우(=괄호형 중복)에는 `analysis_text` 생성 시 `content_box2` 선두의 중복 구간을 제거
	- `4_bracket_dedup_and_delete_lv1_marker` - 괄호형 중복 개체에 `content_box2` 선두의 중복 구간을 제거 후 `content_box2` 선두가 `〔{lv1_div}〕`이면 그 표지 전체를 추가로 제거
	- `5_plain_merge` - 위 사례에 해당하지 않는 경우 별도의 수정 없이 `h1` `lv1_div` `content_box2`를 원문 그대로 이어 붙이기
3. stage3의 원본 열 `h1`, `lv1_div`, `content_box2`는 그대로 유지하고, 중복 제거와 표지 제거 등 수정은 **`analysis_text` 생성 과정에서만 적용**
	- 즉 `content_box2_clean`이라는 임시 개념으로만 처리하고, 별도 열로 저장하지는 않음
4. `era_year`는 원 열은 그대로 두고 분할해 생성한 것들을 위해 `chinese_era_year`, `japanese_era_year`를 따로 생성
5. `analysis_text` 병합 순서와 결측 처리 규칙
	- 병합 순서 고정: `h1` → `lv1_div` → `content_box2`
	- 각 규칙 적용 후 비어 있지 않은 구성요소만 이어붙임
	- 중간 구성요소가 비어 있어도 나머지는 그대로 병합
	- 정제 후 `content_box2`가 비면 남은 구성요소`h1` → `lv1_div`만 사용

---

### 답변 2-5-1
거의 정리됐습니다.  
다만 **구현 시 모호성이 남지 않게 하려면 4가지만 더 고정**하는 편이 좋습니다.

#### 1. `공백 정규화`의 뜻을 명확히 해야 합니다
지금 문안의 `공백 정규화`는 구현자가
- 연속 공백을 하나로 줄이는 것인지
- 앞뒤 공백만 제거하는 것인지
- 공백을 전부 제거하는 것인지
헷갈릴 수 있습니다.

현재까지의 검토에서 의도한 선별 결과를 재현한 것은:

- **중복 판정용 사본에서 모든 공백 문자를 제거**하는 방식

입니다.

권장 문구:
- `공백 정규화`는 **중복 판정에 한해** 문자열의 모든 공백 문자(반각/전각 공백, 탭, 줄바꿈 포함)를 제거하는 것으로 정의한다.

이걸 안 적으면 `〕...〔`형 선별 결과가 달라질 수 있습니다.

---

#### 2. `analysis_text_rule`의 우선순위를 고정해야 합니다
현재 항목만 보면 `lv1_div=本報訊`이면서 동시에 괄호형 중복인 행이 어떤 rule 값을 가져야 하는지가 불분명합니다.  
이 경우가 실제로 존재합니다.

권장 우선순위:
1. `2_box2_only`
2. `4_bracket_dedup_and_delete_lv1_marker`
3. `3_bracket_dedup`
4. `1_drop_benbaoxun`
5. `5_plain_merge`

즉:
- `special_column=分類廣告`면 무조건 `2`
- 그 외에 괄호형 중복이면 `3` 또는 `4`
- 그 외에 `lv1_div=本報訊`이면 `1`
- 나머지는 `5`

중요:
- `lv1_div=本報訊` 제외 규칙은 **병합 규칙**으로는 계속 적용하되,
- `analysis_text_rule` 값은 더 특수한 규칙(`3`/`4`)을 우선 기록하는 편이 맞습니다.

---

#### 3. `lv1` 표지 삭제 규칙은 `（...）`도 포함해야 합니다
현재 문안에는
- `〔{lv1_div}〕`
만 들어 있습니다.

그런데 실제 예외 사례에는
- `（未完）`
처럼 fullwidth 괄호형도 있습니다.

따라서 이 규칙은 아래처럼 쓰는 편이 맞습니다.

권장 문구:
- 중복 제거 직후 `content_box2` 선두가 `〔{lv1_div}〕` **또는** `（{lv1_div}）`이면 그 표지 전체를 제거한다.

---

#### 4. “정규화로 탐지된 중복 구간”을 raw `content_box2`에서 어떻게 지울지 적어야 합니다
이게 지금 가장 실무적으로 중요한 모호점입니다.

현재 문안은 “중복 구간을 삭제”라고만 되어 있는데,  
중복은 정규화된 문자열에서 찾고 실제 삭제는 raw 문자열에서 해야 하므로, 매핑 규칙이 필요합니다.

권장 문구:
- 중복 구간은 공백 정규화된 문자열에서 판정하되, 실제 삭제는 **그 정규화된 중복 구간과 대응하는 최소 raw 선두 구간**을 `content_box2`에서 제거하는 방식으로 수행한다.

이 한 줄이 있어야 구현자가 임의 처리하지 않습니다.

---

#### 따라서 현재 안은 이렇게 보면 됩니다

#### 이미 충분히 정리된 부분
1. 비결측 구성요소만 공백으로 이어붙이기
2. `analysis_text_rule` 열 추가
3. raw `h1`, `lv1_div`, `content_box2`는 유지
4. `era_year` 분할 생성
5. 병합 순서 `h1 -> lv1_div -> content_box2`

#### 추가로 고정해야 하는 부분
1. `공백 정규화 = 모든 공백 문자 제거`
2. `analysis_text_rule` 우선순위
3. `〔{lv1_div}〕`뿐 아니라 `（{lv1_div}）`도 제거
4. 정규화된 중복 구간을 raw `content_box2`에서 삭제하는 방식

---

#### 한 줄 결론
**개념적으로는 거의 끝났고, 코드로 옮기기 전에 위 4개만 문장으로 더 고정하면 됩니다.**

원하면 다음 단계로,  
지금 합의된 내용을 반영해서 `## 프롬프트 2-4`의 stage3 문단을 **중복 없이 바로 붙여 넣을 수 있는 최종 문안**으로 다시 써드리겠습니다.


---
### 프롬프트 2-5-2
`analysis_text_rule`에서 두 가지 룰을 다 적용하는 방식으로 하는 건 어떨까? 실제로 
1. `分類廣告` 열의 경우 엄밀히 말하면 lv1_div가 `本報訊` 또는 결측이기 때문에 지금까지는 box2_only로 가도 문제가 없는데 혹시 `本報訊` 또는 결측이 아닌 경우가 나중의 수집 데이터에 존재한다면 그것을 누락할 경우가 있고, 따라서 `本報訊` 삭제 규칙과 `分類廣告`인 경우 h1 제외 규칙을 이중으로 적용하는 게 맞는 것 같아.
2. 그리고 현재 데이터에서 단 1건에만 해당하는  `4_bracket_dedup_and_delete_lv1_marker` 사례는 bracket_dedup 규칙과 `content_box2` 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 전체를 제거하는 규칙을 함께 적용해야 하는 방식이라서

### 답변 2-5-2
네. **그 방식이 더 타당합니다.**  
지금 단계에서는 `analysis_text_rule`을 “상호배타적 분류값”으로 두기보다, **실제로 적용된 정제 규칙들의 목록**으로 두는 편이 맞습니다.

핵심 이유는 두 가지입니다.

1. `分類廣告`는 현재 데이터에서는 사실상 `content_box2`만 써도 결과가 같지만,  
   앞으로 `lv1_div`가 `本報訊`/결측이 아닌 경우가 나오면 지금의 `box2_only` 규칙은 정보를 잃을 수 있습니다.

2. `4_bracket_dedup_and_delete_lv1_marker`는 실제로 하나의 독립 규칙이 아니라  
   - `bracket_dedup`
   - `delete_lv1_marker`
   의 **연쇄 적용 결과**입니다.  
   따라서 합성 가능한 규칙으로 모델링하는 편이 더 정확합니다.

#### 권장 변경

##### 1. 열 이름
- `analysis_text_rule`보다 **`analysis_text_rules`**가 더 적절합니다.

이유:
- 한 행에 여러 규칙이 동시에 적용될 수 있기 때문입니다.

##### 2. 기록 방식
- 세미콜론 `;`으로 연결한 규칙 목록으로 기록

예:
- `1_drop_h1_for_classified;2_drop_benbaoxun`
- `3_bracket_dedup;4_delete_lv1_marker`
- `5_plain_merge`

#### 권장 규칙 체계

`analysis_text_rules` 값 후보:
- `1_drop_h1_for_classified`
- `2_drop_benbaoxun`
- `3_bracket_dedup`
- `4_delete_lv1_marker`
- `5_plain_merge`

여기서 중요한 점:
- `5_plain_merge`는 **다른 규칙이 하나도 적용되지 않을 때만** 사용

#### 실제 적용 순서
이 순서로 고정하는 것이 좋습니다.

1. `special_column=分類廣告`이면 `h1` 제외  
   → `1_drop_h1_for_adclassified`

2. `lv1_div=本報訊`이면 `lv1_div` 제외  
   → `2_drop_benbaoxun`

3. `special_column='' and qrynewstype=SP`이고, 공백 정규화 후  
   `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며  
   `content_box2` 쪽 후방 경계 직후가 `〔`이면  
   `content_box2` 선두의 중복 구간 제거  
   → `3_bracket_dedup`

4. 3 적용 후 `content_box2` 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면  
   그 표지 전체 제거  
   → `4_delete_lv1_marker`

5. 위 규칙이 아무것도 적용되지 않으면  
   → `5_plain_merge`

#### 이 방식으로 바뀌면 무엇이 달라지나

##### `分類廣告`
기존:
- 무조건 `content_box2`만 사용

수정 후:
- `h1`만 제외
- `lv1_div=本報訊`이면 그것도 제외
- 따라서 현재 데이터에서는 대부분 결과가 같음
- 하지만 미래 데이터에서 `lv1_div`가 의미 있는 값이면 보존 가능

즉, `分類廣告`의 병합 규칙은 이제:
- **`h1` 제외**
- **`本報訊`이면 `lv1_div` 제외**
- 나머지 비결측 문자열 병합

##### 괄호형 중복 2건
기존:
- `4_bracket_dedup_and_delete_lv1_marker`라는 별도 분류값

수정 후:
- `3_bracket_dedup;4_delete_lv1_marker`

이 편이 훨씬 정확합니다.

#### 따라서 지금 문안을 고치면 이렇게 됩니다

- `analysis_text_rule` → `analysis_text_rules`
- 규칙은 상호배타적 분류가 아니라 **누적 적용**
- 값은 세미콜론 연결
- `plain_merge`는 예외 없이 아무 규칙도 적용되지 않은 경우만 사용

#### 최종 판단
네, 이 정도면 현재 설계가 더 정밀해집니다.  
특히 아래 두 점이 해결됩니다.

- `分類廣告`의 미래 데이터 확장성
- `bracket_dedup + lv1_marker 삭제`의 합성 규칙 표현

원하면 다음 단계로, 이 방식을 반영해서 `## 프롬프트 2-4`의 stage3 문단을 **바로 붙여 넣을 수 있는 최종 문안**으로 다시 써드리겠습니다.


---
### 프롬프트 2-5-3
여기에 추가로 `공백 정규화`는 문자열의 앞 뒤 공백만 제거하는 것을 의미한다고 규정하고 싶어. 실제로 문자열 중간의 공백은 제거하지 않아도 동일하고, 탐색시에 문제가 되는 건 문자열 맨 앞과 맨 뒤의 공백 뿐이라서

### 답변 2-5-3
그렇게 정의하면 **지금까지 합의한 선별 결과와는 어긋납니다.**

핵심:
- `공백 정규화 = 문자열 전체의 앞뒤 공백만 제거`로 바꾸면,
- 이전에 재현했던 `〕...〔`형 `64건`이 유지되지 않습니다.
- 이 경우 **`62건`만 남고 2건이 빠집니다.**

빠지는 사례:
- `lixian, 4076, 1908-10-30`
- `xianfa, 8229, 1925-01-05`

이유:
- 이 두 행은 **문자열 전체의 맨 앞/맨 뒤 공백** 때문이 아니라,
- **중복 경계 근처에 끼어 있는 내부 공백** 때문에 raw 비교나 `strip`만으로는 중복이 성립하지 않습니다.

즉, 지금 사용자 의도대로
- “문자열 중간의 공백은 건드리고 싶지 않다”
는 점은 이해되지만,
- **탐색상 문제를 일으키는 공백이 항상 문자열 맨 앞/맨 뒤에만 있는 것은 아닙니다.**

#### 더 좋은 절충안

`공백 정규화`를 이렇게 정의하는 편이 맞습니다.

> 중복 판정 시에는 `h1`와 `content_box2` 전체에서 공백을 일괄 제거하지 않고, **중복 경계에 인접한 공백은 무시**한다.

하지만 이 문장은 구현이 조금 모호합니다.  
그래서 코드 규칙으로는 아래 둘 중 하나로 고정하는 것이 좋습니다.

##### 안 1. 가장 단순하고 재현성 높은 방식
- **중복 판정에 한해 모든 공백 문자를 제거**
- 실제 원문 저장과 병합은 raw 문자열 사용

장점:
- 이미 검증됨
- `64건` 정확히 재현됨

단점:
- 설명상 “공백 정규화”가 조금 넓음

##### 안 2. 더 보수적인 방식
- 문자열 전체를 바꾸지 않고,
- **중복 경계 양쪽에 붙은 공백만 무시**하도록 구현

장점:
- 사용자의 의도와 더 가까움
- 내부 일반 공백은 보존됨

단점:
- 규칙 설명과 구현이 더 복잡함
- 아직 이 방식으로 `64건` 재현을 다시 검증하지는 않았음

#### 실무적 권고

지금 stage3 규칙을 안정적으로 확정하려면 **안 1**이 더 낫습니다.

즉 문구는 이렇게 두는 편이 좋습니다.

> 중복 판정에 한해서는 `h1`와 `content_box2`의 공백 문자를 제거한 비교용 문자열을 사용한다. 다만 실제 `analysis_text` 생성과 원문 보존에는 raw 문자열을 사용한다.

이렇게 하면:
- 선별 재현성 유지
- 원문 손상 없음
- 규칙도 구현하기 쉬움

#### 결론
- **`공백 정규화 = 앞뒤 공백만 제거`로 정의하는 것은 권하지 않습니다.**
- 그렇게 바꾸면 기존 선별 결과가 달라집니다.
- 가장 안전한 선택은:
  - **판정용으로만 공백 전체 제거**
  - 저장/병합은 raw 유지

원하면 다음 단계로, 이 판단을 반영해서 stage3 규칙 문장을 다시 한 번 깔끔하게 정리해드리겠습니다.


---
### 프롬프트 2-5-4
1. lixian, 4076에서 공백 부분은 `電一` 이고 여기에서 공백은 h1에서는  `電一`의 앞, box2에서는  `電一`의 뒤에만 존재하는데 이게 왜 탐색이 안되는거야? 나로서는 잘 이해가 안 되는데?
2. xianfa, 8229에서도 마찬가지로, 공백은 h1에서 중복 문자열의 앞에 존재하는 게 전부인데, 왜 탐지가 안되는거야?

### 답변 2-5-4
두 사례에 대해서는 사용자의 지적이 맞습니다.  
제가 앞서 든 예시는 적절하지 않았습니다.

정확히 다시 보면:

#### 1. `lixian, 4076`
원문:
- `h1` 끝: `專電〕 電一`
- `content_box2` 시작: `電一 〔北京〕...`

`strip`만 적용하면:
- `h1`: `專電〕 電一`
- `content_box2`: `電一 〔北京〕...`

중복 구간:
- `電一`

중복 경계 주변:
- `h1` 쪽 경계 직전: `〕 `
- `content_box2` 쪽 경계 직후: ` 〔`

즉:
- 중복 구간 자체는 그대로 성립하고
- `〕`도 `h1` 경계 전방 2자 이내에 있고
- `〔`도 `content_box2` 경계 후방 2자 이내에 있습니다.

따라서 **이 사례는 `앞뒤 공백만 제거`하는 방식으로도 탐지됩니다.**  
여기서 공백이 문제를 만들지 않습니다.

#### 2. `xianfa, 8229`
원문:
- `h1` 끝부분은 `...直道〕 李根源復黎運動謁段衡突之趣劇 自曹錕...面談昨晚`
- `content_box2` 시작은 `李根源復黎運動謁段衡突之趣劇 自曹錕...面談昨晚〔二十七〕...`

`strip`만 적용해도:
- 중복 구간은 여전히 성립합니다.
- 실제 overlap 길이는 `416자`입니다.
- `h1` 경계 직전에는 `直道〕 `
- `content_box2` 경계 직후에는 `〔二十七〕`

즉:
- 사용자가 말한 것처럼, 이 사례에서 문제 되는 공백은 중복 문자열의 앞쪽에만 붙어 있고
- 중복 문자열 내부의 공백은 양쪽에 동일하게 존재합니다.
- 그래서 **`strip`만으로도 탐지됩니다.**

#### 정정
따라서 제가 앞서
- `lixian, 4076`
- `xianfa, 8229`
를 들어서 “앞뒤 공백만 제거하면 탐지가 안 된다”고 설명한 것은 **틀렸습니다.**

이 두 사례는 오히려 반대로,
- **`앞뒤 공백만 제거`해도 탐지되는 사례**입니다.

#### 추가로 다시 확인한 결과
이 부분까지 다시 계산해 보니:

- 엄격한 `〕...〔`형 그룹 1은  
  **`strip` 기준으로도 64건 그대로 유지**됩니다.
- 더 넓은 그룹 2는  
  **`strip` 기준에서는 65건**입니다.
- 즉 `공백 전체 제거`를 썼을 때의 66건보다 1건 줄어듭니다.

실무적 의미:
- **그룹 1 규칙만 놓고 보면**, 사용자가 새로 제안한
  - `공백 정규화 = 문자열 앞뒤 공백만 제거`
  라는 정의로도 문제 없습니다.
- 제가 이전에 이 정의에 반대한 근거는 부정확했습니다.

정리:
- `lixian, 4076`: `strip`만으로 탐지됨
- `xianfa, 8229`: `strip`만으로 탐지됨
- 따라서 이 두 건은 “공백 전체 제거가 꼭 필요하다”는 근거가 되지 않습니다.

원하면 다음 단계로,
1. `공백 정규화 = 앞뒤 공백만 제거`를 반영한 최종 stage3 규칙 문장을 다시 써드리거나
2. 그룹 2에서 `strip` 기준으로 빠지는 그 1건이 무엇인지도 바로 확인해드리겠습니다.


---
## 2-6. stage3 최종 작업 사양 정리
### 프롬프트 2-6-1
지금까지의 논의를 통해 `# 프롬프트 2-6` 이후에 변경된 사항들을 반영한 stage3 개선 규칙을 정리해줘

### 답변 2-6-1
아래처럼 정리하면 됩니다.  
이 버전은 `# 프롬프트 2-6` 이후 논의를 반영한 stage3 최종 개선 규칙입니다.

#### stage3 목적
- stage2까지는 데이터베이스에서 수집한 `publish_variant`부터 `theme`까지의 원 데이터를 유지한다.
- stage3의 목적은
  - 분석에 바로 사용할 수 있는 `analysis_text`를 생성하고
  - `era_year`처럼 분할이 필요한 필드를 추가 생성하며
  - 전체 행 순서를 분석용 기준으로 재정렬하는 것이다.
- 이 과정에서도 원본 수집 문자열 자체는 가능한 한 유지한다.

#### 1. 전체 행 재정렬
stage2 결과를 stage3로 넘길 때 전체 행을 아래 순서로 재정렬한다.

1. `date` 오름차순
2. `qrynewstype` 순서:
   - `SP`
   - `SP_AD`
   - `SP_FH`
   - `SP_HK`
3. `issue_page` 숫자 오름차순
   - `issue_page`가 비어 있거나 숫자 변환이 안 되면 같은 `qrynewstype` 집합 안에서 맨 뒤에 둔다
4. 최종 tie-breaker는 `article_id` 오름차순

#### 2. `dataset_index` 생성
- 재정렬이 끝난 뒤 최종 순서에 따라 `dataset_index`를 부여한다.
- `dataset_index`는 stage3 데이터셋 내부의 일련번호다.

#### 3. 열 유지 및 제거
- `detail_url`은 stage2에서 stage3로 가면서 제거한다.
- 원본 열 `h1`, `lv1_div`, `content_box2`, `era_year`는 그대로 유지한다.
- `h1`, `lv1_div`, `content_box2`에 대한 중복 제거·표지 제거는 원본 열을 수정하지 않고 `analysis_text` 생성 과정에서만 적용한다.
- 즉, `content_box2_clean` 같은 개념은 내부 처리용으로만 사용하고 별도 열로 저장하지 않는다.

#### 4. `era_year` 분할
- `era_year` 원열은 그대로 둔다.
- 추가 열로 아래 두 열을 생성한다.
  - `chinese_era_year`
  - `japanese_era_year`

#### 5. `analysis_text` 생성 원칙
- `analysis_text`는 `h1`, `lv1_div`, `content_box2`를 병합해 생성한다.
- 병합 시 문자열 사이에는 구분선 `|`을 넣지 않는다.
- 비결측 문자열만 공백 한 칸으로 이어붙인다.
- 병합 순서는 항상 다음과 같다.
  1. `h1`
  2. `lv1_div`
  3. `content_box2`
- 중간 구성요소가 비어 있어도 나머지는 그대로 이어붙인다.
- 정제 후 `content_box2`가 비면 남은 비결측 구성요소만 사용한다.

#### 6. `analysis_text_rules` 열 추가
- `analysis_text_rule`가 아니라 `analysis_text_rules`를 추가한다.
- 이 열은 상호배타적 분류값이 아니라, 실제로 적용된 정제 규칙들의 목록을 기록한다.
- 복수 규칙이 적용되면 `;`로 연결한다.
- 값 후보는 아래와 같다.

##### `1_drop_h1_for_classified`
- `special_column=分類廣告`인 경우 `h1`를 `analysis_text` 병합에서 제외한다.

##### `2_drop_benbaoxun`
- `lv1_div=本報訊`인 경우 `lv1_div`를 `analysis_text` 병합에서 제외한다.

##### `3_bracket_dedup`
- `special_column=''` and `qrynewstype=SP`인 기사 중,
- 공백 정규화 후 `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며,
- 그 중복 구간의 `content_box2` 쪽 후방 경계 직후에 `〔`가 나타나는 경우,
- `analysis_text` 생성 시 `content_box2` 선두의 중복 구간을 제거한다.

##### `4_delete_lv1_marker`
- `3_bracket_dedup` 적용 후 `content_box2` 선두가
  - `〔{lv1_div}〕`
  - 또는 `（{lv1_div}）`
  이면 그 표지 전체를 제거한다.

##### `5_plain_merge`
- 위 규칙이 하나도 적용되지 않은 경우,
- 별도 수정 없이 `h1`, `lv1_div`, `content_box2`를 원문 그대로 병합한다.

#### 7. `analysis_text_rules` 적용 방식
- `analysis_text_rules`는 누적 적용 방식으로 기록한다.
- `5_plain_merge`는 다른 규칙이 하나도 적용되지 않을 때만 사용한다.
- 따라서 실제로는 아래와 같은 조합이 가능하다.
  - `1_drop_h1_for_classified;2_drop_benbaoxun`
  - `3_bracket_dedup;4_delete_lv1_marker`
  - `2_drop_benbaoxun`
  - `5_plain_merge`

#### 8. 공백 정규화의 정의
- `공백 정규화`는 문자열의 앞뒤 공백만 제거하는 것을 의미한다.
- 즉 `strip` 수준으로 처리한다.
- 문자열 내부 공백은 제거하지 않는다.
- 이 규칙으로도 현재 확인된 그룹 1, 그룹 2 선별 결과는 유지된다.

#### 9. 괄호형 중복 판정과 실제 삭제의 관계
- 중복 판정은 공백 정규화 후 문자열에서 수행한다.
- 실제 삭제는 raw `content_box2`에서 수행한다.
- 즉, 정규화 후 탐지된 중복 구간에 대응하는 raw `content_box2` 선두 구간을 제거하는 방식으로 처리한다.
- 원본 `h1`, `lv1_div`, `content_box2` 열은 수정하지 않는다.

#### 10. 규칙 적용 순서
`analysis_text` 생성 시 규칙 적용 순서는 아래와 같이 고정한다.

1. `special_column=分類廣告`이면 `1_drop_h1_for_classified`
2. `lv1_div=本報訊`이면 `2_drop_benbaoxun`
3. `special_column=''` and `qrynewstype=SP`이고 괄호형 중복이면 `3_bracket_dedup`
4. 3 적용 후 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 `4_delete_lv1_marker`
5. 아무 규칙도 적용되지 않으면 `5_plain_merge`

#### 11. 요약
stage3의 핵심 변경점은 다음과 같다.

- 분석용 정렬 기준 도입
- `dataset_index` 추가
- `detail_url` 제거
- `era_year` 분할 열 추가
- 원본 `h1`, `lv1_div`, `content_box2`는 유지
- `analysis_text`를 별도 생성
- `analysis_text_rules`로 실제 적용 규칙 기록
- `分類廣告`, `本報訊`, 괄호형 중복에 대해서만 좁은 범위의 정제 수행
- 그 외 문자열 정제는 하지 않음

원하면 다음 단계로 이 내용을 `03_pipeline-revision_2...md`의 stage3 문단에 바로 붙여 넣을 수 있는 문체로 다시 압축해드리겠습니다.

---
### 프롬프트 2-6-2
압축해줘

### 답변 2-6-2
아래 버전으로 넣으면 됩니다.

```text
stage3
- stage2까지는 데이터베이스에서 수집한 `publish_variant`부터 `theme`까지의 원 데이터를 유지했으며, stage3의 목적은 분석에 바로 활용할 수 있는 `analysis_text`를 생성하고 `era_year`처럼 분할이 필요한 필드를 추가 생성하는 것이다.
- 작업에 앞서 전체 행 순서를 아래 규칙에 따라 재정렬한다.
  1. `date` 오름차순
  2. `qrynewstype` 순서: `SP` → `SP_AD` → `SP_FH` → `SP_HK`
  3. `issue_page` 숫자 오름차순. `issue_page`가 비어 있거나 숫자 변환이 불가능하면 같은 `qrynewstype` 집합 안에서 맨 뒤에 둔다.
  4. 최종 tie-breaker는 `article_id` 오름차순
- 재정렬 후 `dataset_index` 열을 생성하여 최종 순서에 따라 일련 번호를 부여한다.
- stage2에서 stage3로 가면서 `detail_url`은 제거한다.
- 원본 열 `h1`, `lv1_div`, `content_box2`, `era_year`는 그대로 유지한다.
- `era_year`는 원열을 유지한 채 `chinese_era_year`, `japanese_era_year`를 추가 생성한다.
- `analysis_text` 열을 추가한다.
  - `analysis_text`는 `h1` → `lv1_div` → `content_box2` 순서로 병합해 생성한다.
  - 병합 시 문자열 사이에는 구분선을 넣지 않고, 비결측 문자열만 공백으로 이어붙인다.
  - 중간 구성요소가 비어 있어도 나머지는 그대로 병합한다.
  - 정제 후 `content_box2`가 비면 남은 비결측 구성요소만 사용한다.
- `analysis_text_rules` 열을 추가한다.
  - 이 열은 상호배타적 분류값이 아니라 실제로 적용된 정제 규칙들의 목록을 기록하며, 복수 규칙이 적용되면 `;`로 연결한다.
  - 값은 아래와 같다.
    - `1_drop_h1_for_classified`: `special_column=分類廣告`인 경우 `h1`를 병합에서 제외
    - `2_drop_benbaoxun`: `lv1_div=本報訊`인 경우 `lv1_div`를 병합에서 제외
    - `3_bracket_dedup`: `special_column=''` and `qrynewstype=SP`인 기사 중, 공백 정규화 후 `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며 그 중복 구간의 `content_box2` 쪽 후방 경계 직후에 `〔`가 나타나는 경우 `content_box2` 선두의 중복 구간을 제거
    - `4_delete_lv1_marker`: `3_bracket_dedup` 적용 후 `content_box2` 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 전체를 제거
    - `5_plain_merge`: 위 규칙이 하나도 적용되지 않은 경우 원문 그대로 병합
  - `5_plain_merge`는 다른 규칙이 하나도 적용되지 않을 때만 사용한다.
- `analysis_text` 생성 시 정제는 원본 열을 수정하지 않고 내부 처리용 문자열에만 적용한다. 즉 `content_box2_clean` 같은 개념은 내부 처리에만 사용하고 별도 열로 저장하지 않는다.
- 여기서 `공백 정규화`는 문자열의 앞뒤 공백만 제거하는 것을 의미한다.
- 규칙 적용 순서는 아래와 같이 고정한다.
  1. `special_column=分類廣告`이면 `1_drop_h1_for_classified_ad`
  2. `lv1_div=本報訊`이면 `2_drop_benbaoxun`
  3. `special_column=''` and `qrynewstype=SP`이고 괄호형 중복이면 `3_bracket_dedup`
  4. 3 적용 후 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 `4_delete_lv1_marker`
  5. 아무 규칙도 적용되지 않으면 `5_plain_merge`
```

한 가지 표현만 보수적으로 더 다듬자면,
- `공백 정규화 후 h1 전체 또는 h1 끝과 content_box2 시작이 중복되며`
이 부분은 그대로 써도 되지만,
- 코드 구현을 더 명확히 하려면 `h1` 전체 prefix 포함과 suffix-prefix overlap을 명시적으로 분리해도 됩니다.

지금 버전으로도 문서에는 충분합니다.

---
# 3. 최종 지시서
shenbao_textdata_preprocess_combine.py 을 다음과 같은 규칙에 따라 작동하도록 개선하고 shenbao_textdata_preprocess_combine_ver2.py로 저장해줘

1. stage1
	- stage1은 네 건의 수집 데이터 간 단순 병합이 목적
	- 기존 스크립트에서 `preprocess_index`로 명명했던 열 헤더에 대해, 생성 시점을 명확히 밝히기 위해 `stage1_index`로 수정
	- Python/CSV 후속 처리 편의를 위해 하이픈이 있는 `content-box2`를 `content_box2`로 수정
	- 새 버전 수집 데이터는 메타데이터가 이미 모두 분리되어 있어 이후 통합 과정에서 원본열 자체에 대한 수정은 이루어지지 않으므로, `_raw` suffix 추가 로직은 삭제
	- 생성 파일명은 `shenbao_textdata_stage1_appended_rows_{dataset_label}.csv`로 설정
	- 헤더 구성: 17열
		```text
		stage1_index,
		label,
		page,
		item_index,
		list_title,
		detail_url,
		publish_variant,
		date,
		issue_page,
		special_column,
		h1,
		lv1_div,
		content_box2,
		era_year,
		category,
		theme,
		collect_error
		```

2. stage2
	- stage2는 `article_id` 기준 중복 항목 간 통합이 목적
	- `detail_url`로부터 `article_id`, `qrynewstype`를 분리하는 로직 유지
		- 이 데이터에서 같은 `article_id`는 같은 `qrynewstype`을 가지므로, 별도의 에러나 경고 로직은 불필요
	- 원본 파일이 제공하는 열 중 `label`, `page`, `item_index`, `list_title` 네 열은 그대로 남겨두더라도 stage2 결과물부터는 대표행의 값만 남게 되고 이후 분석에서 활용할 여지가 없으므로 삭제
	- 대표행 판정 기준 
		1. `collect_error`가 비어있는 행(즉, 에러 메시지가 등장하지 않은 행)
		2. `issue_page`가 비어있지 않은 행
		3. `theme` 길이가 긴 행
		4. `content_box2` 길이가 긴 행
		5. `h1` 길이가 긴 행
		6. `lv1_div` 길이가 긴 행
		7. `stage1_index`가 작은 행
	-  `select_reason`에 기록될 대표행 선택 사유
		1. `1_no_error`
		2. `2_page_exist`
		3. `3_long_theme`
		4. `4_long_box2`
		5. `5_long_h1`
		6. `6_long_lv1_div`
		7. `7_small_index`
	- `collision`은 병합 대상인 동일 `article_id` 개체 간에 `publish_variant`, `date`, `issue_page`, `special_column`, `h1`, `lv1_div`, `content_box2`, `era_year`, `category`, `theme`, `collect_error` 열의 정규화를 거치지 않은 원 데이터 사이에 하나의 사소한 차이라도 존재하는 모든 경우를  `T`로 판정. 하나는 채워져 있고 다른 하나는 결측인 경우도 역시 `collision=T`로 판정. 양쪽 모두 결측인 경우는 `collision=F`로 판정
	- 충돌 유형이 아닌, 충돌이 일어난 열을 기록하는 방식으로 수정. 열 헤더를 `collision_type`에서 `collision_columns`로 바꾸고, 비교 대상 열 중에서 충돌이 발생한 열 이름을 기록. 복수 열에서 충돌이 발생한 경우 값을 `;`로 연결하여 기록
		- `collision=F`일 때는 `collision_row`를 결측값으로 둘 것
	- 생성 파일명은 `shenbao_textdata_stage2_deduplicated_articles_{dataset_label}.csv`로 설정
	- 헤더 구성: 22열
		```text
		dataset_label,
		source_labels,
		stage1_indices,
		representative_label,
		representative_item_index,
		select_reason,
		article_id,
		qrynewstype,
		detail_url,
		publish_variant,
		date,
		issue_page,
		special_column,
		h1,
		lv1_div,
		content_box2,
		era_year,
		category,
		theme,
		collect_error,
		collision,
		collision_columns
		```

3. stage3
	- stage2까지는 데이터베이스에서 수집한 `publish_variant`부터 `theme`까지의 원 데이터를 유지했으며, stage3의 목적은 분석에 바로 활용할 수 있는 `analysis_text`를 생성하고 `era_year`처럼 분할이 필요한 필드를 추가 생성하는 것이다.
	- 작업에 앞서 전체 행 순서를 다음 규칙에 따라 재정렬
		1. `date` 오름차순
		2. `qrynewstype` 순서: SP → SP_AD → SP_FH → SP_HK
		3. `issue_page` 숫자 오름차순, `issue_page`가 비어 있거나 숫자 변환이 불가능하면 같은 `qrynewstype` 집합 안에서 맨 뒤에 배치
		4. 최종 tie-breaker는 `article_id` 오름차순
	- 재정렬 후 `dataset_index` 열을 생성하여 재정렬한 최종 순서에 따라 일련 번호를 부여
	- stage2에서 stage3로 가면서 `detail_url`은 제거
	- 원본 열 `h1`, `lv1_div`, `content_box2`, `era_year`는 그대로 유지
	- `era_year` 는 원래 열을 유지한 채 `chinese_era_year`, `japanese_era_year`를 추가 생성
	- `analysis_text` 열을 추가
		- `analysis_text`는 `h1` → `lv1_div` → `content_box2` 순서로 병합해 생성
		- 병합 시 문자열 사이에는 별도의 구분 인자를 넣지 않고, 비결측 문자열만 공백으로 이어 붙일 것
			- 중간 구성요소가 비어 있어도 나머지는 순서 그대로 병합할 것
			- 정제 후 `content_box2`가 비면 남은 비결측 구성요소만 사용
		- 생성에는 아래와 같은 정제 규칙을 적용하며, 정제 규칙 기록을 위해 `analysis_text_rules` 열을 추가
			- 이 열은 상호배타적 분류값이 아님. 실제로 적용된 정제 규칙들의 목록을 기록하며, 복수 규칙이 적용되면 `;`로 연결
			- `analysis_text_rules`의 적용 규칙과 순서는 아래와 같이 고정한다.
			  1. `1_drop_h1_for_classified_ad`: `special_column=分類廣告`인 경우 `h1`을 병합에서 제외
			  2. `2_drop_benbaoxun`: `lv1_div=本報訊`인 경우 `lv1_div`를 병합에서 제외
			  3. `3_bracket_dedup`: `special_column=''` and `qrynewstype=SP`인 기사 중, 공백 정규화 후 `h1` 전체 또는 `h1` 끝과 `content_box2` 시작이 중복되며 그 중복 구간의 `content_box2` 쪽 후방 경계 직후에 `〔`가 나타나는 경우 `content_box2` 선두의 중복 구간을 제거
			  4. `4_delete_lv1_marker`: `3_bracket_dedup` 적용 후 `content_box2` 선두가 `〔{lv1_div}〕` 또는 `（{lv1_div}）`이면 그 표지 전체를 제거
			  5. `5_plain_merge`: 위 규칙이 하나도 적용되지 않은 경우 원문 그대로 병합
			- 여기서 `공백 정규화`는 문자열의 앞뒤 공백만 제거하는 것을 의미함
			- `analysis_text` 생성 시 정제는 원본 열을 수정하지 않고 내부 처리용 문자열에만 적용한다. 즉 `content_box2_clean` 같은 개념은 내부 처리에만 사용하고 별도 열로 저장하지 않음

	- 생성 파일명은 `shenbao_textdata_stage3_preprocessed_articles_{dataset_label}.csv`로 설정
	- 헤더 구성: 26열
		```text
		dataset_label,
		dataset_index,
		source_labels,
		stage1_indices,
		representative_label,
		representative_item_index,
		select_reason,
		article_id,
		qrynewstype,
		publish_variant,
		date,
		issue_page,
		special_column,
		era_year,
		chinese_era_year,
		japanese_era_year,
		category,
		theme,
		collect_error,
		collision,
		collision_columns0,
		h1,
		lv1_div,
		content_box2,
		analysis_text,
		analysis_text_rules
		```
# 작업 메모
- 10_data-profile_11_전처리 결과물의 특성과 column별 분포 특징