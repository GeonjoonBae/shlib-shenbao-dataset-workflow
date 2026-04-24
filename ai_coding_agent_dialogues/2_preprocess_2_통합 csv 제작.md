---
주제: 통합 csv 제작
AI 플랫폼 및 모델:
  - GPT-5.4
날짜: 2026-04-10
---
# 1. 통합 전처리 워크플로우 설계

## 프롬프트 1-1
shenbao\shenbao_textdata\exceptions 안의 예외 사례, shlib-shenbao-dataset-workflow\copyright_rows.csv, shlib-shenbao-dataset-workflow\title_list_title_empty_rows.csv, shlib-shenbao-dataset-workflow\title_text_near_duplicate_rows.csv 파일, 그리고 지금까지 나눈 대화들을 바탕으로, 아래 요건을 충족하고, 시행 과정에서 작업이 꼬이지 않을 수 있는 textdata에 대한 전처리 워크플로우를 수립해줘.
- 최우선 목표: 네 csv 파일을 constitution이라는 라벨을 갖는 하나의 통합 텍스트 데이터로 통합
- 통합하더라도 해당 기사가 어떤 라벨을 가진 textdata csv로부터 왔는지를 통합 데이터에서 확인할 수 있어야 함
- publish 열 안에 들어있는 메타데이터를 분리하여 각 메타데이터 값을 별개 열로 정리
- title 열 또는 text 열 안에 들어있는 메타데이터(其他紀元： 類別： 主題：) 값을 별개 열로 정리
- 수집되어서는 안되는 데이터베이스 서비스/업체 관련 정보 삭제(예시: Copyright c 2012 得泓資訊. All Rights Reserved.)
- 그 밖에 정리가 필요한 사항 정리

## 답변 1-1
아래처럼 **원본 보존 → 예외 플래그 부여 → 메타데이터 분리 → 제목·본문 정리 → 중복 통합 → 분석용 데이터 산출** 순서로 잡는 것이 가장 안전합니다. 핵심은 정리 과정에서 원래 어느 검색 라벨 파일에서 온 행인지 잃지 않는 것입니다.

**기본 원칙**
1. 원본 CSV는 절대 수정하지 않는다.
2. 네 개의 검색 결과 파일은 먼저 행 단위로 단순 결합한 뒤, `detail_url`의 기사 ID를 기준으로 중복 통합한다.
3. 최종 통합 데이터의 대표 라벨은 `constitution`으로 두되, 원래 수집 라벨은 `source_labels` 또는 `source_label` 열에 보존한다.
4. 예외 행은 바로 삭제하지 않고 먼저 플래그를 붙인다.
5. 텍스트 정리는 항상 `raw` 값에서 파생한 `clean` 값으로 만든다.
6. 최종 산출물은 “검수 가능한 master 데이터”와 “분석용 corpus 데이터”를 분리한다.

**대상 파일**
통합 대상은 아래 네 파일로 한정합니다.

| source label | 입력 파일 |
|---|---|
| `xianfa` | `shenbao_textdata_xianfa_1to18648.csv` |
| `lixian` | `shenbao_textdata_lixian_1to7203.csv` |
| `xianzheng` | `shenbao_textdata_xianzheng_1to9906.csv` |
| `zhixian` | `shenbao_textdata_zhixian_1to4322.csv` |

현재 `shenbao\shenbao_textdata` 기준으로 네 파일은 총 40,079개 수집 행이며, `detail_url`의 기사 ID 기준으로는 33,513개의 고유 기사 ID가 확인됩니다. 즉, 단순 결합만 하면 중복 기사가 상당수 포함됩니다.

**권장 산출물**
최종적으로는 최소한 아래 세 파일을 만드는 것이 좋습니다.

| 파일                                             | 목적                                             |
| ---------------------------------------------- | ---------------------------------------------- |
| `shenbao_constitution_textdata_master.csv`     | 모든 고유 기사 단위 통합본. 예외 플래그와 원출처 추적 정보를 포함         |
| `shenbao_constitution_textdata_corpus.csv`     | 텍스트마이닝에 바로 사용할 분석용 본문 데이터. 오류·메타데이터 전용 행 등은 제외 |
| `shenbao_constitution_textdata_issue_rows.csv` | 삭제 또는 분석 제외된 행, 구조 예외 행, 검토 필요 행 목록            |

필요하면 중간 단계 파일도 남기는 것이 좋습니다.

| 중간 파일 | 목적 |
|---|---|
| `stage01_appended_source_rows.csv` | 네 파일을 그대로 결합한 행 단위 데이터 |
| `stage02_metadata_parsed_rows.csv` | `publish`, `title`, `text` 메타데이터를 분리한 상태 |
| `stage03_deduplicated_master.csv` | 기사 ID 기준 중복 통합 직후 데이터 |

---

#### 1. 원본 적재 단계

네 CSV를 읽어 하나의 행 단위 데이터로 결합합니다. 이 단계에서는 아무것도 삭제하지 않습니다.

추가할 열:

| 열 | 설명 |
|---|---|
| `dataset_label` | 최종 통합 데이터 라벨. 모든 행에 `constitution` 입력 |
| `source_label` | 원래 검색 라벨. `xianfa`, `lixian`, `xianzheng`, `zhixian` 중 하나 |
| `source_file` | 원래 CSV 파일명 |
| `source_page` | 원래 `page` 값 |
| `source_item_index` | 원래 `item_index` 값 |
| `article_id` | `detail_url`의 `id=` 값 |
| `qrynewstype` | `detail_url`의 `qrynewstype=` 값 |
| `list_title_raw` | 원래 `list_title` |
| `publish_raw` | 원래 `publish` |
| `title_raw` | 원래 `title` |
| `text_raw` | 원래 `text` |

이 단계에서 `csv.field_size_limit()`는 반드시 크게 설정해야 합니다. 현재 데이터에는 131,072자를 초과하는 `text` 필드가 3건 있으므로, 최소 1,000,000 이상이 안전합니다.

---

#### 2. `publish` 열 메타데이터 분리

`publish_raw`에서 신문명, 날짜, 판면, 부가 정보를 분리합니다.

권장 열:

| 열                          | 설명                                                   |
| -------------------------- | ---------------------------------------------------- |
| `newspaper`                | `申報`                                                 |
| `newspaper_variant`        | `main`, `hankou`, `hongkong`, `unknown`              |
| `publish_date`             | `YYYY-MM-DD`                                         |
| `page_issue`               | 예: `02 版`, `03 版`, `25 版`                            |
| `publish_tail`             | 판면 뒤에 붙은 통신사, 필자, `本報訊`, `分類廣告` 등                    |
| `publish_raw`              | 원문 보존                                                |
| `publish_exception`        | `T/F`                                                |
| `publish_exception_reason` | `topic_only`, `start_with_date`, `missing_publish` 등 |

처리 규칙:

| 원문 형식                 | 처리                                       |
| --------------------- | ---------------------------------------- |
| `申報 日期：... 版次/卷期：...` | 정상                                       |
| `申報_漢口版 日期：...`       | 정상. `newspaper_variant=hankou`           |
| `申報_香港版 日期：...`       | 정상. `newspaper_variant=hongkong`         |
| `日期：...`로 시작          | `publish_exception=T`, `start_with_date` |
| `主題：...`로 시작          | `publish_exception=T`, `topic_only`      |

`申報_漢口版`, `申報_香港版`은 예외로 분류하지 않는 것이 맞습니다. 이는 데이터 오류가 아니라 상하이 이외 지역판을 가리키는 출처 정보입니다.

---

#### 3. `detail_url` 기반 자료 유형 분리

`detail_url`에서 `qrynewstype`을 분리합니다.

권장 열:

| 열 | 설명 |
|---|---|
| `detail_url` | 원래 상세 URL |
| `article_id` | `id=` 값 |
| `qrygroup` | `qrygroup=` 값 |
| `qrynewstype` | `SP`, `SP_AD`, `SP_FH`, `SP_HK` 등 |
| `material_type` | `article`, `advertisement_or_special`, `hankou`, `hongkong`, `unknown` |
| `detail_url_exception` | `T/F` |
| `detail_url_exception_reason` | `sp_ad`, `no_detail_url` 등 |

처리 규칙:

| `qrynewstype` | 처리 |
|---|---|
| `SP` | 일반 기사 |
| `SP_FH` | 한구판. 예외 아님 |
| `SP_HK` | 홍콩판. 예외 아님 |
| `SP_AD` | 광고 또는 특수 지면 가능성이 높으므로 플래그 부여 |
| 빈 값 | `detail_url_exception=T`, `no_detail_url` |

`SP_AD`는 무조건 삭제하지 말고, 우선 `material_type=advertisement_or_special`로 표시하는 것이 좋습니다. 연구 목적에 따라 광고·공고성 자료를 제외할 수도 있고, 별도 분석 대상으로 둘 수도 있기 때문입니다.

---

#### 4. `title`·`text` 내부 메타데이터 분리

`title_raw` 또는 `text_raw` 안에 들어 있는 후행 메타데이터를 분리합니다.

대상 문자열:

```text
其他紀元：
類別：
主題：
```

권장 열:

| 열 | 설명 |
|---|---|
| `other_era_raw` | `其他紀元：` 뒤의 원문 |
| `minguo_year` | 가능하면 `民國37年` 등에서 숫자 추출 |
| `japanese_era_raw` | 예: `日昭和23年`, `日大正5年` |
| `category` | `類別：` 값 |
| `topic` | `主題：` 값 |
| `metadata_source` | `text`, `title`, `both`, `none` |
| `metadata_parse_status` | `ok`, `partial`, `none` |

처리 원칙:

1. 먼저 `text_raw`에서 메타데이터를 찾는다.
2. `text_raw`에 없고 `title_raw`에 있으면 `title_raw`에서 찾는다.
3. 둘 다 있으면 값이 같은지 확인하고, 다르면 `metadata_conflict=T`로 표시한다.
4. 메타데이터는 `text_clean`과 `title_clean`에서는 제거한다.
5. 단, `*_raw` 값은 별도 audit 파일 또는 source 파일에 남겨 추적 가능하게 한다.

---

#### 5. 서비스·업체 정보 제거

다음 문구는 데이터베이스 서비스 또는 업체 정보이므로 분석용 텍스트에서 제거합니다.

```text
Copyright c 2012 得泓資訊. All Rights Reserved.
```

현재 검토 결과:

| 항목 | 건수 |
|---|---:|
| copyright 문구 포함 행 | 19 |
| 포함 위치 | 전부 `title` 열 |
| `text` 전체가 `title` 안에 포함되는 행 | 동일한 19건 |

처리 규칙:

| 조건 | 처리 |
|---|---|
| `title_raw`에 copyright 포함 | `copyright_removed=T` |
| `title_raw`가 `text_raw` 전체를 포함 | `title_quality=h1_body_contamination` |
| 이 경우 `text_clean` | `text_raw`에서 메타데이터 제거 후 사용 |
| 이 경우 `title_clean` | 가능하면 `list_title_raw`에서 일련번호 제거한 값을 사용 |
| `list_title_raw`도 비정상 | `title_clean`은 빈 값 또는 `title_missing` 처리 |

즉, 이 19건은 `title`을 그대로 제목으로 쓰면 안 됩니다. `title`이 제목이 아니라 본문 전체와 후행 메타데이터를 포함한 오염 필드이기 때문입니다.

---

#### 6. 제목 정리 규칙

최종 제목은 `title_clean`으로 둡니다.

권장 우선순위:

| 우선순위 | 제목 후보 | 조건 |
|---:|---|---|
| 1 | 상세 페이지 `title_raw` 정리값 | 일반 구조이고, 본문 전체를 포함하지 않음 |
| 2 | `list_title_raw`에서 일련번호 제거한 값 | 상세 제목이 비어 있거나 오염된 경우 |
| 3 | 빈 값 | 둘 다 사용할 수 없는 경우 |

추가 플래그:

| 열 | 값 |
|---|---|
| `title_source` | `detail_title`, `list_title_fallback`, `missing` |
| `title_quality` | `ok`, `empty`, `body_contaminated`, `list_title_empty`, `both_empty` |

기존 비교 결과에 따르면 `list_title`와 `title`의 차이는 대부분 데이터 오류가 아니라 목록 페이지 표시 방식의 차이입니다.

| 유형 | 처리 |
|---|---|
| 말줄임표 생략형 | 상세 `title` 사용 |
| 후속 확장형 | 상세 `title` 사용 |
| 검색어 주변 문맥형 | 상세 `title` 사용 |
| `title_empty` | `list_title` fallback |
| `list_title_empty` | 상세 `title` 사용 |
| 둘 다 empty | 제목 결측 처리 |

---

#### 7. 본문 정리 규칙

최종 본문은 `text_clean`으로 둡니다.

처리 순서:

1. `text_raw`가 `[ERROR]`로 시작하면 본문 수집 실패로 표시한다.
2. `text_raw`가 `其他紀元：...` 메타데이터만 포함하면 본문 없음으로 표시한다.
3. `text_raw`에서 `其他紀元：`, `類別：`, `主題：` 이하 메타데이터를 분리한다.
4. copyright 문구가 있으면 제거한다.
5. 앞뒤 공백과 반복 공백을 정리한다.
6. 본문 길이가 극단적으로 짧으면 `short_text` 플래그를 유지한다.

권장 열:

| 열 | 설명 |
|---|---|
| `text_clean` | 분석에 사용할 정리 본문 |
| `text_length` | 정리 후 문자 수 |
| `text_exception` | `T/F` |
| `text_exception_reason` | `error_text`, `metadata_only`, `short_text` 등 |
| `text_quality` | `ok`, `error`, `metadata_only`, `short`, `empty` |

예외 처리:

| 유형 | 처리 |
|---|---|
| `[ERROR]` | `include_in_corpus=F` |
| `metadata_only` | `include_in_corpus=F` |
| `short_text` | 자동 삭제하지 말고 플래그만 부여 |
| 매우 긴 광고성 텍스트 | `material_type` 및 `text_length`로 관리 |

---

#### 8. `title`과 `text` 중복 구조 처리

검토 결과 두 가지 구조가 있습니다.

| 유형 | 건수 | 처리 |
|---|---:|---|
| `text` 전체가 `title` 안에 포함 | 19 | `title` 오염. `title_clean`은 `list_title` fallback, `text_clean`은 `text` 사용 |
| `title`이 `text` 안에 포함 | 295 | 본문 앞부분이 제목과 중복. 분석용 텍스트 생성 시 중복 주의 |

권장 열:

| 열 | 설명 |
|---|---|
| `title_text_relation` | `none`, `text_in_title`, `title_in_text` |
| `title_text_overlap_flag` | `T/F` |
| `analysis_text` | 텍스트마이닝에 사용할 최종 문자열 |

`analysis_text` 생성 규칙은 다음이 좋습니다.

| 조건 | `analysis_text` |
|---|---|
| `text_clean`이 충분히 있음 | `text_clean` |
| `text_clean`이 제목을 이미 포함 | `text_clean`만 사용 |
| `text_clean`이 제목을 포함하지 않음 | 필요 시 `title_clean + " " + text_clean` |
| `text_clean` 없음 | 빈 값 또는 제외 |

텍스트마이닝 목적이라면 `title_clean + text_clean`을 무조건 결합하면 안 됩니다. `title`이 이미 `text`에 들어 있는 295건에서 제목이 중복 계산될 수 있습니다.

---

#### 9. 중복 기사 통합

네 검색 결과 파일에는 같은 기사가 여러 라벨에 중복 수집된 경우가 많습니다. 따라서 최종 통합 데이터는 `article_id` 기준으로 1행 1기사 구조를 권장합니다.

현재 네 파일 기준:

| 항목                   |      값 |
| -------------------- | -----: |
| 원 수집 행               | 40,079 |
| 고유 기사 ID             | 33,513 |
| 2개 이상 라벨에서 중복된 기사 ID |  5,706 |
| 중복 그룹에 속한 원 수집 행     | 12,271 |

중복 통합 규칙:

| 열 | 처리 |
|---|---|
| `dataset_label` | `constitution` |
| `source_labels` | 해당 기사가 출현한 원 검색 라벨 전체. 예: `xianfa;zhixian` |
| `source_files` | 원 파일명 전체 |
| `source_refs` | `source_label:page:item_index` 형식으로 보존 |
| `search_keywords` | `憲法;制憲`처럼 원 검색어 병기 |
| `detail_url` | 대표 URL 1개 |
| `title_clean` | 가장 품질이 좋은 행에서 선택 |
| `text_clean` | 가장 품질이 좋은 행에서 선택 |
| `publish_*` | 대표 행에서 선택하되 충돌 시 플래그 |

대표 행 선택 기준:

| 우선순위 | 조건 |
|---:|---|
| 1 | `text_exception=F` |
| 2 | `metadata_only` 또는 `[ERROR]`가 아님 |
| 3 | `title_quality=ok` |
| 4 | copyright 오염이 없음 |
| 5 | `qrynewstype=SP` 우선 |
| 6 | 정리 후 본문 길이가 충분함 |
| 7 | 동일하면 가장 먼저 수집된 행 또는 가장 작은 `source_item_index` |

중복 통합 후에도 원래 어떤 파일에서 왔는지는 `source_labels`, `source_files`, `source_refs`로 확인할 수 있습니다.

---

#### 10. 최종 master 데이터 권장 스키마

`shenbao_constitution_textdata_master.csv`는 아래 열 구성을 권장합니다.

| 열 | 설명 |
|---|---|
| `dataset_label` | 항상 `constitution` |
| `article_id` | 상세 URL의 기사 ID |
| `source_labels` | 원 검색 라벨 목록 |
| `search_keywords` | 원 검색어 목록. 예: `憲法;立憲` |
| `source_files` | 원 CSV 파일명 목록 |
| `source_refs` | 원 위치. 예: `xianfa:1:1;zhixian:1:1` |
| `detail_url` | 대표 상세 URL |
| `qrynewstype` | `SP`, `SP_AD`, `SP_FH`, `SP_HK` 등 |
| `material_type` | `article`, `advertisement_or_special`, `hankou`, `hongkong` 등 |
| `newspaper` | `申報` |
| `newspaper_variant` | `main`, `hankou`, `hongkong`, `unknown` |
| `publish_date` | 발행일 |
| `page_issue` | 판면 또는 권호 |
| `publish_tail` | 통신사, 필자, `本報訊`, `分類廣告` 등 |
| `title_clean` | 정리된 제목 |
| `title_source` | `detail_title`, `list_title_fallback`, `missing` |
| `text_clean` | 정리된 본문 |
| `analysis_text` | 텍스트마이닝용 최종 문자열 |
| `other_era_raw` | `其他紀元` 값 |
| `minguo_year` | 민국 연도 |
| `japanese_era_raw` | 일본 연호 정보 |
| `category` | `類別` |
| `topic` | `主題` |
| `publish_exception` | `T/F` |
| `publish_exception_reason` | 사유 |
| `detail_url_exception` | `T/F` |
| `detail_url_exception_reason` | 사유 |
| `text_exception` | `T/F` |
| `text_exception_reason` | 사유 |
| `title_quality` | 제목 품질 |
| `text_quality` | 본문 품질 |
| `title_text_relation` | `none`, `title_in_text`, `text_in_title` |
| `copyright_removed` | `T/F` |
| `include_in_master` | 항상 `T` |
| `include_in_corpus` | 분석용 포함 여부 |
| `exclude_reason` | 분석 제외 사유 |

---

#### 11. 분석용 corpus 생성 규칙

`master`는 검수용이므로 가능한 한 많은 행을 보존합니다. 반면 `corpus`는 텍스트마이닝에 부적절한 행을 제외합니다.

기본 제외 조건:

| 조건 | 제외 사유 |
|---|---|
| `text_exception_reason=error_text` | 본문 수집 실패 |
| `text_exception_reason=metadata_only` | 본문 없음 |
| `text_clean` 빈 값 | 본문 없음 |
| `detail_url_exception_reason=no_detail_url` | 출처 추적 불가 |
| `text_quality=empty` | 분석 텍스트 없음 |

선택적 제외 조건:

| 조건 | 권장 처리 |
|---|---|
| `qrynewstype=SP_AD` | 연구 목적에 따라 제외 또는 별도 분석 |
| `short_text` | 자동 제외하지 말고 검토 후 결정 |
| `material_type=advertisement_or_special` | 기사 분석 corpus에서는 제외 가능 |
| `title_text_relation=title_in_text` | 제외하지 않음. `analysis_text` 중복만 방지 |

따라서 corpus는 두 버전으로 나눌 수도 있습니다.

| 파일 | 포함 기준 |
|---|---|
| `shenbao_constitution_textdata_corpus_all_valid.csv` | 본문이 정상 수집된 모든 텍스트 |
| `shenbao_constitution_textdata_corpus_articles_only.csv` | `SP_AD`와 광고성 자료를 제외한 기사 중심 corpus |

---

#### 12. 검증 단계

각 단계가 끝날 때 아래 검증을 반드시 실행하는 것이 좋습니다.

| 검증 항목 | 기준 |
|---|---|
| 입력 행 수 | 네 원본 파일 행 수 합계와 `stage01` 행 수 일치 |
| `article_id` 결측 | 0이어야 함 |
| 중복 통합 전후 | 원 행 수 > 고유 기사 수 |
| `source_labels` | 모든 최종 행에 1개 이상 존재 |
| `dataset_label` | 모든 최종 행이 `constitution` |
| copyright 문구 | `title_clean`, `text_clean`, `analysis_text`에는 없어야 함 |
| `[ERROR]` | `corpus`에는 없어야 함 |
| `其他紀元：` | `text_clean`, `analysis_text`에는 없어야 함 |
| `metadata_only` | `corpus`에는 없어야 함 |
| `source_refs` | 중복 통합된 행에서 원 위치 추적 가능해야 함 |

---

#### 13. 작업 순서 요약

실제 시행 순서는 아래처럼 고정하는 것이 좋습니다.

1. 네 원본 CSV를 읽어 `stage01_appended_source_rows.csv` 생성
2. `source_label`, `source_file`, `source_page`, `source_item_index`, `article_id`, `qrynewstype` 추가
3. `publish_raw`에서 발행 메타데이터 분리
4. `title_raw`, `text_raw`에서 `其他紀元`, `類別`, `主題` 분리
5. copyright 문구 제거
6. `title_clean`, `text_clean`, `analysis_text` 생성
7. 예외 플래그 부여
8. `article_id` 기준으로 중복 통합
9. `source_labels`, `source_files`, `source_refs` 병합
10. 대표 `title_clean`, `text_clean`, `publish_*` 선택
11. `master` 데이터 저장
12. 분석 제외 조건을 적용해 `corpus` 데이터 저장
13. 제외·검토 대상 행을 `issue_rows`로 저장
14. 행 수, 중복 수, 예외 수, copyright 제거 여부 검증

이 방식이면 통합 후에도 원래 수집 출처를 잃지 않고, 메타데이터 분리와 텍스트 정리를 재현 가능한 순서로 수행할 수 있습니다.

---

## 프롬프트 1-2
shenbao_constitution_textdata_corpus_articles_only.csv를 생성할 때, SP_AD 쿼리로 표시되지 않은 광고성 자료는 어떻게 식별해 제외시킬 수 있지?

## 답변 1-2
`SP_AD`만으로 광고성 자료를 모두 걸러내기는 어렵습니다. `qrynewstype=SP` 안에도 실제로는 광고, 고지, 가격표, 극장 프로그램, 서적 광고, 은행·회사 공고 같은 자료가 섞여 있을 수 있습니다. 따라서 `shenbao_constitution_textdata_corpus_articles_only.csv`를 만들 때는 **단일 기준이 아니라 다단계 필터**를 쓰는 것이 안전합니다.

가장 현실적인 방식은 아래입니다.

#### 1. 1차 제외: 구조 기반 필터

먼저 확실한 것부터 제외합니다.

| 기준 | 처리 |
|---|---|
| `qrynewstype=SP_AD` | 제외 |
| `publish`에 `分類廣告` 포함 | 제외 후보 |
| `publish_exception_reason=start_with_date`이면서 `qrynewstype=SP_AD` | 제외 |
| `text_exception_reason=metadata_only` | 제외 |
| `text_exception_reason=error_text` | 제외 |
| `text_clean`이 지나치게 짧음 | 제외 후보 |

여기서 중요한 것은 `publish`에 `分類廣告`가 포함된 경우입니다. 실제 검토 결과에서 `SP`인데도 `publish`가 다음처럼 표시되는 행들이 있었습니다.

```text
申報 日期：1947-03-13 版次/卷期：07 版 分類廣告 本報訊
```

이런 행은 `qrynewstype=SP`라 하더라도 광고·분류광고 지면에서 온 자료일 가능성이 큽니다. 따라서 `articles_only`에서는 기본적으로 제외하는 편이 안전합니다.

다만 “분류광고 지면에 실린 텍스트도 연구 대상에 포함할 것인가”라는 연구 판단이 필요합니다. 헌정 논의 기사 corpus라면 제외하는 것이 더 적절합니다.

#### 2. 2차 제외: 제목·본문 키워드 기반 필터

`SP_AD`도 아니고 `分類廣告`도 없지만 광고성 자료일 수 있는 경우는 제목과 본문에 반복적으로 나타나는 광고 표지를 이용해 걸러냅니다.

예상 광고성 키워드:

| 범주 | 예시 |
|---|---|
| 가격·판매 | `售`, `每册`, `每冊`, `定價`, `價目`, `大廉價`, `一角`, `五角`, `每部`, `郵費`, `發售`, `出售` |
| 업체·상점 | `商務印書館`, `中華書局`, `洋行`, `公司`, `股份有限公司`, `書局`, `藥房`, `藥室`, `銀行`, `信託公司` |
| 광고 문구 | `廣告`, `啟`, `謹啟`, `敬告`, `特此布告`, `聲明`, `通告`, `告白` |
| 약품·의료 광고 | `包治`, `包愈`, `不靈`, `加倍受罰`, `秘方`, `丸`, `丹`, `膏`, `藥水` |
| 극장·공연 | `戲院`, `大戲院`, `日場`, `夜場`, `主演`, `公演`, `開映`, `電影`, `票價` |
| 경매·판매 | `拍賣`, `不限價`, `貨`, `疋頭`, `木器`, `地產` |

하지만 키워드 필터는 과잉 제외 위험이 있습니다. 예를 들어 `公司`, `銀行`, `通告`는 일반 기사에도 나올 수 있습니다. 따라서 단어 하나만으로 제외하지 말고 **점수화 방식**이 좋습니다.

예:

```text
광고성 점수 = 광고 키워드 출현 수 + publish 신호 + 제목 신호 + 형식 신호
```

점수 기준 예시:

| 조건 | 점수 |
|---|---:|
| `publish`에 `分類廣告` | +5 |
| `title_clean`에 `廣告`, `拍賣`, `發售`, `價目`, `啟`, `告白` 포함 | +3 |
| `text_clean` 앞 300자 안에 가격 표현 포함 | +2 |
| `text_clean` 앞 300자 안에 업체명·상점명 2개 이상 | +2 |
| `text_clean`에 `包治`, `包愈`, `不靈加倍` 등 의료 광고 표현 포함 | +3 |
| `text_clean`이 쉼표 없는 품목 나열·가격표 형태 | +2 |

그리고 예를 들어 `ad_score >= 5`이면 광고성 자료로 제외합니다.

#### 3. 3차 제외: 형식 기반 필터

광고성 자료는 문체보다 형식에서 드러나는 경우가 많습니다.

확인할 수 있는 형식적 특징:

| 특징 | 설명 |
|---|---|
| 가격 표현 반복 | `一角`, `二角`, `五角`, `一元`, `二元`, `每册`, `每部`, `定價` |
| 업체명 반복 | `公司`, `洋行`, `書局`, `藥房`, `銀行` 등이 짧은 간격으로 반복 |
| 상품명 나열 | 문장보다 품목·상호·가격의 열거가 많음 |
| 기사 문장 구조 부족 | `某地電`, `本報訊`, `社論`, `專電` 같은 기사 표지가 없고 상업 문구 중심 |
| `text` 시작부가 광고 표제 | `某某公司廣告`, `某某藥房`, `某某書局發售` 등 |

특히 `text_clean` 앞부분 300-500자를 기준으로 보는 것이 좋습니다. 광고 여부는 대개 앞부분에서 드러납니다.

#### 4. 4차: rule-based 결과를 사람이 검수

완전 자동 제외는 위험합니다. 특히 신문 데이터에서는 광고와 기사, 공고와 뉴스, 출판 광고와 지식 담론의 경계가 흐릴 수 있습니다.

따라서 자동 필터 결과를 아래처럼 나누는 것을 권합니다.

| 판정 | 처리 |
|---|---|
| `ad_certain` | corpus에서 제외 |
| `ad_likely` | 별도 검수 후 제외 여부 결정 |
| `not_ad` | corpus 포함 |
| `unknown` | 보수적으로 corpus 포함 또는 검수 대상으로 분리 |

`articles_only`를 엄격하게 만들고 싶다면 `ad_likely`까지 제외할 수 있습니다. 다만 논문에서는 이 기준을 명시해야 합니다.

#### 권장 열 구성

`master`에 아래 열을 추가해 두면 좋습니다.

| 열 | 설명 |
|---|---|
| `ad_candidate` | `T/F` |
| `ad_score` | 광고성 점수 |
| `ad_reason` | 감지된 사유. 예: `publish_classified;price_terms;company_terms` |
| `corpus_type` | `article`, `advertisement`, `classified`, `notice`, `unknown` |
| `include_in_articles_only` | `T/F` |
| `articles_only_exclude_reason` | 제외 사유 |

예:

```text
ad_candidate=T
ad_score=8
ad_reason=publish_classified;price_terms;company_terms
corpus_type=advertisement
include_in_articles_only=F
articles_only_exclude_reason=advertisement_or_classified
```

#### 실무적으로 가장 안전한 워크플로우

`articles_only` 생성은 아래 순서가 좋습니다.

1. `SP_AD` 제외
2. `publish`에 `分類廣告` 포함된 행 제외
3. 광고성 점수 계산
4. `ad_score >= 5`는 제외
5. `ad_score 3-4`는 `ad_likely_review.csv`로 별도 저장
6. 검수 후 제외 규칙 확정
7. 최종 `shenbao_constitution_textdata_corpus_articles_only.csv` 생성

요약하면, `SP_AD`는 **확실한 제외 기준**이지만 **충분한 제외 기준은 아닙니다**. `publish`의 `分類廣告`, 광고성 키워드, 가격·상호·판매 형식, 그리고 검수용 점수화를 함께 써야 합니다.

---

## 프롬프트 1-3
앞에서 이야기했던 전처리 작업 절차 중에서, 일단 당장은 통합 데이터 생성을 위한 가장 기본적이고 필수적으로 해야 하는 것들만 골라서 해보고 싶어. C:\Users\class\Documents\Obsidian Vault\5_Project\중국 근현대 헌정 논의 텍스트마이닝\2_preprocess_2_통합 csv 제작.md에 네가 이야기했던 내용을 정리해놨으니 이걸 참고하면서, 아래 절차 중 필수-권장-추가 같은 방식으로 우선순위를 매겨줘

1. 네 원본 CSV를 읽어 `stage01_appended_source_rows.csv` 생성
2. `source_label`, `source_file`, `source_page`, `source_item_index`, `article_id`, `qrynewstype` 추가
3. `publish_raw`에서 발행 메타데이터 분리
4. `title_raw`, `text_raw`에서 `其他紀元`, `類別`, `主題` 분리
5. copyright 문구 제거
6. `title_clean`, `text_clean`, `analysis_text` 생성
7. 예외 플래그 부여
8. `article_id` 기준으로 중복 통합
9. `source_labels`, `source_files`, `source_refs` 병합
10. 대표 `title_clean`, `text_clean`, `publish_*` 선택
11. `master` 데이터 저장
12. 분석 제외 조건을 적용해 `corpus` 데이터 저장
13. 제외·검토 대상 행을 `issue_rows`로 저장
14. 행 수, 중복 수, 예외 수, copyright 제거 여부 검증

## 답변 1-3
기준을 먼저 나누는 것이 좋습니다.

- `필수`: 네 CSV를 하나의 통합 데이터로 만들기 위해 반드시 필요한 단계
- `권장`: 통합 데이터의 품질과 추적 가능성을 높이기 위해 가급적 같이 하는 단계
- `추가`: 분석용 corpus를 더 정교하게 만들 때 시행해도 되는 단계

지금 목표가 **“당장 가장 기본적인 통합 master CSV를 만드는 것”**이라면, 우선순위는 아래처럼 잡는 것이 적절합니다.

|  번호 | 절차                                                                                                | 우선순위       | 이유                                                                                                                                            |
| --: | ------------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
|   1 | 네 원본 CSV를 읽어 `stage01_appended_source_rows.csv` 생성                                                | 필수         | 통합 작업의 출발점입니다. 원본을 수정하지 않고 단순 병합본을 남겨야 이후 검증이 가능합니다.                                                                                          |
|   2 | `source_label`, `source_file`, `source_page`, `source_item_index`, `article_id`, `qrynewstype` 추가 | 필수         | 통합 후에도 원래 어느 검색어·파일·위치에서 온 행인지 추적하려면 반드시 필요합니다. 특히 `article_id`는 중복 통합의 기준입니다.                                                                |
|   3 | `publish_raw`에서 발행 메타데이터 분리                                                                       | 권장         | 통합 자체에는 필수는 아니지만, 발행일·판면·지역판 구분은 이후 분석에서 중요하므로 초기에 분리하는 편이 좋습니다.                                                                              |
|   4 | `title_raw`, `text_raw`에서 `其他紀元`, `類別`, `主題` 분리                                                   | 권장         | 통합 자체에는 필수는 아니지만, 본문에 후행 메타데이터가 섞여 있으므로 분석용 데이터까지 염두에 두면 이 단계에서 처리하는 것이 좋습니다.                                                                 |
|   5 | copyright 문구 제거                                                                                   | 권장         | 통합 자체에는 필수는 아니지만, 이미 19건에서 오염이 확인되었으므로 `title_clean`, `analysis_text` 생성 전 처리하는 것이 좋습니다.                                                      |
|   6 | `title_clean`, `text_clean`, `analysis_text` 생성                                                   | 권장         | master만 만들면 필수는 아니지만, 바로 분석 가능한 통합 데이터를 만들려면 사실상 필요합니다.                                                                                       |
|   7 | 예외 플래그 부여                                                                                         | 필수에 가까운 권장 | 단순 통합만 한다면 권장이지만, 대표 행 선택과 corpus 제외 기준을 정하려면 필요합니다. 최소한 `[ERROR]`, `metadata_only`, `empty_text`, `copyright_contaminated` 정도는 부여하는 것이 좋습니다. |
|   8 | `article_id` 기준으로 중복 통합                                                                           | 필수         | 네 검색어 결과에 중복 기사가 많으므로, 하나의 constitution 데이터로 만들려면 반드시 필요합니다.                                                                                  |
|   9 | `source_labels`, `source_files`, `source_refs` 병합                                                 | 필수         | 중복 통합 후 원 수집 출처를 잃지 않기 위한 핵심 단계입니다.                                                                                                           |
|  10 | 대표 `title_clean`, `text_clean`, `publish_*` 선택                                                    | 필수         | `article_id` 기준으로 여러 행이 묶일 때 최종 1행에 어떤 값을 남길지 정해야 합니다.                                                                                        |
|  11 | `master` 데이터 저장                                                                                   | 필수         | 최종 통합본입니다. 당장 목표가 통합 데이터 생성이라면 여기까지가 최소 완성선입니다.                                                                                               |
|  12 | 분석 제외 조건을 적용해 `corpus` 데이터 저장                                                                     | 권장         | master와 별도로 분석용 데이터를 만들 때 필요합니다. 당장 master만 만든다면 다음 단계로 미뤄도 됩니다.                                                                              |
|  13 | 제외·검토 대상 행을 `issue_rows`로 저장                                                                      | 권장         | 재현성과 검수를 위해 중요합니다. 특히 논문에 전처리 기준을 설명하려면 생성하는 편이 좋습니다.                                                                                         |
|  14 | 행 수, 중복 수, 예외 수, copyright 제거 여부 검증                                                               | 필수         | 통합 작업이 제대로 되었는지 확인하는 최소 검증입니다. 논문에 수치를 제시하려면 반드시 필요합니다.                                                                                       |

정리하면, **최소 필수 절차**는 다음입니다.

```text
1 → 2 → 8 → 9 → 10 → 11 → 14
```

다만 실제로는 10번의 “대표값 선택”을 안정적으로 하려면 7번의 일부가 필요합니다. 따라서 실무적으로 안전한 최소 절차는 아래입니다.

```text
1 → 2 → 7(최소 예외 플래그) → 8 → 9 → 10 → 11 → 14
```

여기서 7번은 전체 예외 체계를 다 만들 필요는 없고, 우선 다음 정도만 있으면 됩니다.

| 최소 예외 플래그 | 목적 |
|---|---|
| `text_is_error` | `[ERROR]` 행을 대표 본문으로 선택하지 않기 위해 |
| `text_is_empty` | 빈 본문을 대표값으로 선택하지 않기 위해 |
| `text_is_metadata_only` | `其他紀元：...`만 있는 행을 본문으로 선택하지 않기 위해 |
| `title_is_empty` | 상세 제목 결측 여부 확인 |
| `copyright_contaminated` | title 오염 행을 대표 제목으로 선택하지 않기 위해 |

**권장 절차까지 포함한 1차 실행안**
당장 한 번 실행해서 논문에 쓸 수 있는 안정적인 통합 데이터를 만들려면, 저는 아래 순서를 추천합니다.

```text
1. 네 원본 CSV 적재 및 단순 병합
2. source_label, source_file, source_page, source_item_index, article_id, qrynewstype 추가
3. 최소 예외 플래그 부여
4. copyright 문구 제거
5. title_clean, text_clean 생성
6. article_id 기준 중복 통합
7. source_labels, source_files, source_refs 병합
8. 대표 title_clean, text_clean, publish_raw 선택
9. master 저장
10. 검증 통계 출력
```

이 경우 원래 목록 번호로는 다음에 해당합니다.

```text
1 → 2 → 7 → 5 → 6 → 8 → 9 → 10 → 11 → 14
```

이 순서가 좋은 이유는, `publish`와 후행 메타데이터를 아직 완전히 분리하지 않더라도 **중복 통합과 원 출처 보존이라는 핵심 목표**는 달성할 수 있기 때문입니다.

**뒤로 미뤄도 되는 단계**
아래는 통합 master를 만든 뒤, 다음 단계에서 해도 됩니다.

| 번호 | 절차 | 뒤로 미뤄도 되는 이유 |
|---:|---|---|
| 3 | `publish_raw` 메타데이터 분리 | 발행일·판면 분석을 본격화할 때 해도 됩니다. 단, `publish_raw`는 반드시 보존해야 합니다. |
| 4 | `其他紀元`, `類別`, `主題` 분리 | 분석용 본문 정제를 할 때 처리해도 됩니다. 단, `text_clean`을 만들 때 메타데이터 제거 여부는 결정해야 합니다. |
| 12 | `corpus` 저장 | master가 먼저 있어야 corpus 기준을 안정적으로 적용할 수 있습니다. |
| 13 | `issue_rows` 저장 | 예외 플래그가 안정화된 뒤 생성해도 됩니다. |

**추가 단계로 두는 것이 좋은 것**
아래는 당장 통합 master를 만드는 데는 필요하지 않고, `articles_only` corpus를 만들 때 추가하면 됩니다.

| 절차 | 이유 |
|---|---|
| 광고성 자료 점수화 | `SP_AD`만으로 광고를 모두 잡을 수 없지만, 처음부터 넣으면 규칙 설계가 복잡해집니다. |
| `corpus_articles_only` 생성 | 연구 목적에 따라 제외 기준이 달라질 수 있으므로 master 생성 후 별도 단계로 두는 것이 안전합니다. |
| `ad_likely_review.csv` 생성 | 자동 제외 기준을 검수할 때 필요합니다. |
| `short_text` 자동 제외 여부 결정 | 단신 자료가 중요한 연구에서는 짧은 본문도 분석 대상일 수 있으므로 나중에 결정하는 편이 좋습니다. |

**최종 권장**
지금 당장 해볼 1차 작업은 아래 범위가 가장 적절합니다.

```text
필수 1차 목표:
shenbao_constitution_textdata_master.csv 생성

포함할 작업:
1, 2, 5, 6, 7, 8, 9, 10, 11, 14

보류할 작업:
3, 4, 12, 13

추가 작업:
광고성 자료 점수화, articles_only corpus 생성, issue_rows 세분화
```

단, `3`과 `4`를 완전히 하지 않더라도 `publish_raw`, `title_raw`, `text_raw`는 반드시 보존해야 합니다. 그래야 나중에 메타데이터 분리 규칙을 바꾸더라도 원본을 다시 읽지 않고 재처리할 수 있습니다.

---
# 2. 전처리 코드 작성 전략과 중복 통합 순서 결정

## 프롬프트 2-1
아래 지침에 따라 shenbao_textdata 폴더 (경로로 설정, 실제로 현재 shenbao_textdata 안에 있는 csv 파일들을 의미하는 것이 아니라, 코드 실행 시 shenbao_textdata 폴더 안에 있는 파일들을 가져와서 시행하라는 의미) 안의 csv 파일을 가져와 통합 텍스트 데이터를 만드는 전처리 코드를 작성하고, shenbao_preprocess_combine.py와 같은 이름으로 저장하고 싶어. 그런데 이 코드를 모든 절차를 포함하는 하나의 긴 코드로 만드는 게 좋을지, 아니면 단계별로 구분하는 게 좋을지 잘 모르겠어. 일단 이 문제에 대해 판단하고, 아래 지침 중에서 모호하거나 문제될 만한 부분이 있는지 검토해줘

지침
① 수집된 네 건의 원본 CSV를 단순 병합하여 1단계 통합 데이터를 생성하고, 모든 열 제목에 `“_raw”` 를 추가해, 이후 전처리 작업을 통해 생성할 정제 데이터들과 구분할 수 있도록 한다. 추가로 ‘preprocess_index’ 열을 생성하여, 1단계 통합 데이터 내의 일련 번호를 부여한다. 생성한 파일은 shenbao_textdata_preprocess_1_simple_combined_rows.csv로 저장한다.

② ‘detail_url_raw’ 열에 기록된 해당 기사 url 내의 “id=”와 “qrynewstype=” 값을 추출해 각각의 열로 분리한다. 이를 위해 ‘article_id’, ‘qrynewstype’ 열을 생성한다. “id=” 값은 데이터베이스 내 기사 개체가 갖는 고유 id로, 여러 수집 단위에서 중복 수집된 기사 개체를 식별해, 하나의 행으로 만드는 데 결정적인 인자로 사용된다. “qrynewstype=”은 “SP”, “SP_AD”, “SP_FH”, “SP_HK” 등의 값을 갖는데, 각각 “SP”는 《신보》 일반 기사, “SP_AD”는 광고 기사, “SP_FH”는 《신보》한커우판 기사, “SP_HK”는 《신보》홍콩판 기사임을 지칭하며, 가장 기본적인 유형 분류에 활용할 수 있다. 다만 “SP_AD”로 표기되지 않은 광고 기사도 다수 존재하는 점은 유의할 필요가 있다.

③ ‘publish_raw’ 문자열에 포함된 발행 관련 메타데이터를 추출해 각각의 열로 분리한다. 이를 위해 ‘publish_variant’, ‘publish_date’, ‘page_issue’, ‘publish_tail’, ‘publish_exception’, ‘publish_exception_reason’, ‘topic’ 열을 생성한다. 일반적으로 나타나는 “申報 日期：YYYY-MM-DD 版次/卷期：NN 版 …” 형식을 가진 행에 대해서는, ‘publish_exception’ 열에 “F”를 기록하고, “申報 {지역명}”(지역명 없을 경우 “申報”만 추출), “YYYY-MM-DD”, “NN”, 그리고 그 뒤에 부기 정보(통신사, 필자, “本報訊”, “分類廣告” 등)의 문자열을 추출하여 각각 ‘publish_variant’, ‘publish_date’, ‘page_issue’, ‘publish_tail’ 열에 기록한다. “日期：...” 또는 “主題：…”와 같이 예외 형식을 갖는 행들은 ‘publish_exception’ 열에 “T”를 기입하고, ‘publish_exception_reason’ 열에 각각 “start_with_date” 또는 “topic_only”를 기록한다. 단, 이 중 날짜, 판면, 부기 정보 추출이 가능한 “日期：...” 형식 행은 ‘publish_variant’만 결측값으로 두고 나머지 정보는 일반 형식과 동일하게 값을 추출해 해당 열에 기록한다. 또한 ‘publish_raw’에서 기대되는 정보를 포함하고 있지 않은 “主題：…” 형식 행은 ‘publish_variant’, ‘publish_date’, ‘page_issue’, ‘publish_tail’ 열을 모두 결측값으로 두고, 주제 정보를 ‘topic’ 행에 기록한다. 

④ ‘title_raw’와 ‘text_raw’ 두 열 중 한쪽 또는 양쪽 모두에 포함된 메타데이터를 추출해 각각의 열로 분리한다. 이를 위해 ‘chinese_era_year’, ‘japanese_era_year’, ‘category’, ‘metadata_source’ 열을 생성한다. 기년을 나타내는 “其他紀元：” 뒤의 원문 중 “淸...年” 또는 “民國...年” 문자열은 ‘chinese_era_year’에 기록하고, “日... 年” 문자열은 ‘japanese_era_year’에 기록한다. 유형을 나타내는 “類別：” 뒤의 원문은 ‘category’에,  주제를 나타내는 “主題：” 뒤의 원문은 ③ ‘publish_raw’ 데이터 처리 중 생성한 ‘topic’에 기록한다. ‘metadata_source’에는 해당 메타데이터 원문이 ‘title_raw’와 ‘text_raw’ 중 어느 쪽에서 추출되었는지를 확인해 “title”, “text”, “both”, “none” 중 하나를 기입한다.

⑤ ‘title_raw’ 문자열을 정제하여 연구에 사용 가능한 문자열로 만든다. 이를 위해 ‘title_clean’, ‘title_exist’, ‘title_source’ 열을 생성한다. 우선 ‘list_title_raw’에서 일련번호 부분을 제거한 값과 ‘title_raw’에 대해 문자열 존재 유무를 확인하고, 그 결과를 ‘title_exist’에 기록한다. 둘 다 존재할 경우 “both_exist”, 일련번호 제외한 ‘list_title_raw’ 값에 유효 문자열이 없을 경우 “list_title_empty”, ‘title_raw’가 비어 있을 경우 “title_empty”, 둘 다 비어 있을 경우 “both_empty”를 기입한다. 이를 바탕으로 ‘title_exist’가 “both_exist”, list_title_empty”일 행은 ‘title_raw’ 값을, “title_empty”인 행은 ‘list_title_raw’ 값을 ‘title_clean’에 붙여 넣고, “both_empty”인 행은 ‘title_clean’을 결측값으로 처리한다. ‘title_source’ 역시 이 처리 결과에 따라 “title_raw”, “list_title_raw”, “missing” 중 하나를 표기한다. 그 다음 ‘title_clean’ 안에 “其他紀元：…” 문자열 또는 오수집된 데이터베이스 업체 정보를 나타내는 “Copyright c 2012 得泓資訊. All Rights Reserved.” 문자열이 존재할 경우, 해당 부분을 제거한다. 

⑥ ‘text_raw’ 열을 정제하여 연구에 사용 가능한 데이터로 만든다. 이를 위해 ‘text_clean’, ‘text_exception’, ‘text_exception_reason’ 열을 생성한다. 우선 ‘text_raw’를 검토해 예외 사례를 확인한다. 문자열에 “[ERROR]”가 포함된 경우, “其他紀元：...” 형식의 메타데이터만 포함하는 경우, 문자열이 5자 이하인 경우를 예외 사례로 규정한다. ‘text_exception’은 예외 사례가 탐지되지 않은 열은 “F”, 탐지된 열은 “T”를 기록하고, ‘text_exception_reason’는 각각 사유에 따라 “error_text”, “metadata_only”, “short_text”를 기록한다. 이후 ‘text_exception’이 “F”인 행은 ‘text_raw’ 값이 “其他紀元：…” 문자열을 포함할 경우, 해당 부분을 제거한 나머지 문자열을 ‘text_clean’에 기록하고, “其他紀元：…” 포함하지 않을 경우 ‘text_raw’ 값을 그대로 ‘text_clean’에 복제한다. ‘text_exception’이 “T”인 행은 ‘text_exception_reason’ 값에 따라, “metadata_only”인 행은 ‘text_clean’을 결측값으로, “short_text”인 행은 ‘text_raw’ 값을 그대로 ‘text_clean’에 복제하고, “error_text”인 행에는 데이터베이스 원문을 찾아 수동 보완한다.

⑦ ①부터 ⑥에 걸쳐 만들어진 CSV 데이터를 shenbao_textdata_preprocess_2_preprocessed_rows.csv로 저장한다. 이 CSV 데이터는 다음과 같이 27개 열을 갖는다.


```
label_raw, page_raw, item_index_raw, list_title_raw, publish_raw, detail_url_raw, title_raw, text_raw, preprocess_index, article_id, qrynewstype, publish_variant, publish_date, page_issue, publish_tail, publish_exception, publish_exception_reason, topic, chinese_era_year, japanese_era_year, category, metadata_source, title_clean, title_exist, title_source, text_clean, text_exception, text_exception_reason
```


⑧ shenbao_textdata_preprocess_2_preprocessed_rows.csv에 정리된 중복 기사를 통합하여 ‘article_id’ 기준 1행 1기사 구조의 통합 데이터를 구축한다. 이를 위해 ‘dataset_label’, ‘source_labels’, ‘preprocess_indeces’, ‘collision’ 열 를 생성한다. ‘dataset_label’은 통합 데이터셋 전체에 공통 레이블을 부여하는 열로, 해당 수집 데이터의 특징을 나타낼 수 있는 문자열을 사용한다. ‘source_labels’에는 중복 기사를 한 기사로 합치면서, 해당 기사를 포함한 데이터의 레이블을 함께 표시한다. 예를 들어 ‘article_id’가 같은 두 행이 각각 “lixian”, “xianfa”의 ‘label_raw’ 값을 가진다면, ‘source_labels’는 “lixian;xianfa”로 표기한다. ‘preprocess_indeces’ 역시 마찬가지로 중복된 기사들의 ‘preprocess_index’ 값을 참조해 “{숫자1};{숫자2};…”의 형식으로 기입한다. 중복 행 통합시 대표 행은 ‘text_exception’이 “F”인 행을 우선으로 하고, 충돌이 발생할 경우 ‘collision’ 열에 “T”를 표시한다. 별도의 충돌이 없을 경우 ‘collision’ 값은 “F”로 표시한다. 최종적으로 생성한 통합 데이터는 shenbao_textdata_combind_{dataset_label 값}.csv로 저장하며, 다음과 같이 23개 열을 갖는다.


```
dataset_label, source_labels, preprocess_indeces, article_id, qrynewstype, publish_variant, publish_date, page_issue, publish_tail, publish_exception, publish_exception_reason, topic, chinese_era_year, japanese_era_year, category, metadata_source, title_clean, title_exist, title_source, text_clean, text_exception, text_exception_reason, collision
```

## 답변 2-1
**판단**
`shenbao_preprocess_combine.py` 하나의 스크립트로 작성하되, 내부는 단계별 함수로 분리하는 방식이 가장 적절합니다.

즉, 파일은 하나로 두고 내부 구조는 다음처럼 나누는 방식입니다.

```text
shenbao_preprocess_combine.py
- 원본 CSV 탐색
- 1단계 단순 병합 생성
- 2단계 행 단위 전처리 생성
- article_id 기준 중복 통합
- 검증 통계 출력
```

이 방식이 좋은 이유는 다음과 같습니다.

- 논문에서 “하나의 전처리 스크립트를 실행해 통합 데이터를 생성했다”고 설명하기 쉽습니다.
- 중간 산출물은 `stage 1`, `stage 2`, `final`로 분리 저장할 수 있어 절차 검증이 가능합니다.
- 코드는 함수 단위로 나뉘므로 너무 긴 덩어리 코드가 되는 문제를 피할 수 있습니다.
- 단계별 별도 스크립트로 나누면 파일명, 인코딩, 컬럼 순서, 중간 산출물 버전이 어긋날 위험이 커집니다.
- 향후 특정 단계만 다시 실행할 필요가 있으면 `--stage all`, `--stage preprocess`, `--stage combine` 같은 옵션을 추가할 수 있습니다.

따라서 구현 방향은 **“단일 실행 파일 + 단계별 함수 + 중간 CSV 저장”**이 가장 안정적입니다.

**입력 파일 선택**
가장 먼저 확정해야 할 부분은 `shenbao_textdata` 폴더 안의 어떤 CSV를 원본으로 볼 것인지입니다.

현재 지침대로 “폴더 안의 CSV 파일”을 모두 읽으면 문제가 생길 수 있습니다. 전처리 스크립트를 한 번 실행하면 같은 폴더 안에 다음 파일들이 생기기 때문입니다.

```text
shenbao_textdata_preprocess_1_simple_combined_rows.csv
shenbao_textdata_preprocess_2_preprocessed_rows.csv
shenbao_textdata_combined_constitution.csv
```

이 파일들을 다음 실행 때 다시 원본 CSV로 읽으면 데이터가 중복·오염됩니다.

따라서 코드는 원본 수집 파일만 읽도록 제한해야 합니다. 예를 들면 다음 패턴을 사용하는 방식이 안전합니다.

```text
shenbao_textdata_*_1to*.csv
```

그리고 다음 파일들은 제외해야 합니다.

```text
*preprocess*
*combined*
*exception*
*exceptions*
```

즉, `shenbao_textdata` 폴더를 입력 경로로 받되, 실제 입력 파일은 **수집 원본 형식에 맞는 CSV만 자동 선택**하도록 해야 합니다.

**지침에서 수정이 필요한 부분**
가장 명확한 오류는 ⑦의 열 개수입니다.

지침에는 “27개 열”이라고 되어 있지만, 실제로 나열된 열은 `28개`입니다.

```text
label_raw
page_raw
item_index_raw
list_title_raw
publish_raw
detail_url_raw
title_raw
text_raw
preprocess_index
article_id
qrynewstype
publish_variant
publish_date
page_issue
publish_tail
publish_exception
publish_exception_reason
topic
chinese_era_year
japanese_era_year
category
metadata_source
title_clean
title_exist
title_source
text_clean
text_exception
text_exception_reason
```

따라서 ⑦은 다음처럼 고쳐야 합니다.

```text
이 CSV 데이터는 다음과 같이 28개 열을 갖는다.
```

또 ⑧의 `preprocess_indeces`는 영어 표기로는 부정확합니다. 코드와 논문 모두에서 다음 표현을 쓰는 편이 좋습니다.

```text
preprocess_indices
```

파일명 `shenbao_textdata_combind_{dataset_label 값}.csv`도 오타로 보입니다. 가능하면 다음으로 수정하는 편이 좋습니다.

```text
shenbao_textdata_combined_{dataset_label}.csv
```

다만 이미 논문 초고나 작업 파일에서 `combind`를 사용했다면, 지금 수정할 수 있는 시점인지 확인한 뒤 통일해야 합니다.

**수동 보완 부분**
⑥의 마지막 문장에는 자동 코드로 처리하기 어려운 내용이 있습니다. ^377a6d

```text
“error_text”인 행에는 데이터베이스 원문을 찾아 수동 보완한다.
```

이 동작은 전처리 코드가 자동으로 수행할 수 없습니다. 스크립트가 원 데이터베이스에 접속해 수동 보완까지 하도록 만들지 않는 이상, 별도의 입력 파일이 필요합니다.

따라서 구현 방식은 둘 중 하나로 정해야 합니다.

| 방식       | 설명                                                      |
| -------- | ------------------------------------------------------- |
| 보수적 방식   | `error_text` 행은 그대로 예외로 표시하고 `text_clean`은 비워 둠         |
| 보완 파일 방식 | 사용자가 직접 보완한 CSV를 별도로 제공하면, 스크립트가 이를 읽어 `text_clean`에 반영 |

논문 재현성을 생각하면 두 번째 방식이 더 좋습니다. 예를 들어 다음 파일을 둘 수 있습니다.

```text
shenbao_textdata_manual_corrections.csv
```

구성은 다음 정도면 충분합니다.

```text
article_id,label_raw,item_index_raw,title_clean,text_clean,note
```

다만 지금 당장 기본 통합 데이터를 만드는 목적이라면, 우선은 `error_text`를 예외로 남기고 `issue_rows` 또는 로그로 따로 출력하는 방식이 더 단순합니다.

**topic 열의 모호성**
현재 지침에서는 `topic` 열이 두 경로에서 채워집니다.

```text
publish_raw가 “主題：...” 형식인 경우
title_raw 또는 text_raw 안의 “主題：...” 메타데이터에서 추출한 경우
```

이 둘은 성격이 약간 다릅니다.

- `publish_raw`의 `主題：...`는 발행 정보 대신 잘못 들어온 데이터베이스 주제 경로입니다.
- `title_raw` 또는 `text_raw` 뒤쪽의 `主題：...`는 상세 페이지 하단 메타데이터입니다.

현재 데이터에서는 충돌이 많지 않을 가능성이 크지만, 구조상 같은 `topic` 열에 넣을 경우 출처가 불분명해질 수 있습니다.

해결 방법은 두 가지입니다.

| 방식                | 판단                   |
| ----------------- | -------------------- |
| `topic` 하나만 유지    | 지침이 단순하고 최종 스키마가 간결함 |
| `topic_source` 추가 | 더 엄밀하지만 스키마가 늘어남     |

지금 지침을 크게 바꾸지 않으려면 `topic` 하나만 유지하되, 코드 내부에서는 출처가 다른 topic 값이 동시에 존재하고 서로 다르면 `;`로 병합하는 편이 안전합니다.

예:

```text
topic = "政治/憲政;分類廣告"
```

다만 논문에서 엄밀하게 설명하려면 `topic`은 “데이터베이스 또는 상세 페이지에서 추출된 주제 관련 문자열”이라고 넓게 정의해야 합니다.

**metadata_source 처리**
④에서 `metadata_source`를 `title`, `text`, `both`, `none`으로 기입하는 것은 좋습니다. 다만 실제 추출값이 `title_raw`와 `text_raw` 양쪽에 모두 있고 서로 다른 경우를 어떻게 처리할지 정해야 합니다.

권장 방식은 다음과 같습니다.

```text
둘 다 있고 값이 같으면 그대로 사용
둘 다 있고 값이 다르면 서로 다른 값을 ; 로 병합
metadata_source는 both로 기록
```

예:

```text
chinese_era_year = "民國37年;民國38年"
metadata_source = "both"
```

물론 실제 데이터에서는 이런 충돌이 드물 가능성이 큽니다.

**title_clean 규칙**
⑤의 기본 규칙은 타당합니다. 다만 다음 부분은 문장에 따옴표가 빠져 있습니다.

현재 문장:

```text
‘title_exist’가 “both_exist”, list_title_empty”일 행은 ...
```

수정:

```text
‘title_exist’가 “both_exist” 또는 “list_title_empty”인 행은 ...
```

그리고 `list_title_raw`에서 일련번호를 제거하는 규칙도 명시하는 편이 좋습니다.

예:

```text
^\s*\d+\.\s*
```

즉, 앞쪽의 `숫자. ` 형식만 제거하고, 제목 내부의 숫자나 마침표는 건드리지 않는 방식입니다.

**text_exception 우선순위**
⑥에서 예외 사유가 여러 개 동시에 해당될 수 있습니다.

예를 들어 `[ERROR]`가 들어 있으면서 문자열 길이가 5자 이하인 경우, 또는 메타데이터만 남아 있으면서 짧은 문자열인 경우가 있을 수 있습니다.

따라서 `text_exception_reason`의 우선순위를 정해야 합니다.

권장 우선순위는 다음입니다.

```text
error_text > metadata_only > short_text
```

이유는 다음과 같습니다.

- `[ERROR]`는 수집 실패를 의미하므로 가장 강한 예외입니다.
- `metadata_only`는 본문이 아니라 메타데이터만 수집된 구조적 예외입니다.
- `short_text`는 실제 단문 기사일 가능성도 있으므로 가장 약한 예외입니다.

문자열 길이 판단은 원문 그대로가 아니라 양끝 공백을 제거한 뒤 수행하는 것이 좋습니다.

```text
len(text_raw.strip()) <= 5
```

**metadata_only 정의**
`metadata_only`의 판정 기준도 명확히 해야 합니다.

권장 기준은 다음입니다.

```text
text_raw에서 공백을 제거한 값이 “其他紀元：”로 시작하고, 그 앞에 본문 문자열이 없는 경우
```

즉, `text_raw` 안에 `其他紀元：`이 포함되어 있다는 사실만으로는 `metadata_only`로 보면 안 됩니다. 일반 기사도 본문 뒤에 메타데이터가 붙어 있기 때문입니다.

정확한 판정은 다음처럼 해야 합니다.

```text
text_raw에서 “其他紀元：” 앞부분을 잘라 보았을 때,
그 앞부분에 유효한 본문 문자열이 없으면 metadata_only
```

**중복 통합 규칙**
⑧은 가장 중요한 단계인데, 현재 지침만으로는 대표 행 선택과 충돌 판정이 다소 모호합니다.

현재 지침:

```text
중복 행 통합시 대표 행은 ‘text_exception’이 “F”인 행을 우선으로 하고, 충돌이 발생할 경우 ‘collision’ 열에 “T”를 표시한다.
```

여기서 “충돌”이 무엇인지 정의해야 합니다.

권장 정의는 다음입니다.

```text
동일 article_id를 가진 여러 행 사이에서,
정제 대상 핵심 열의 비어 있지 않은 값이 서로 다를 경우 collision = T
```

핵심 비교 대상은 다음 정도가 적절합니다.

```text
qrynewstype
publish_variant
publish_date
page_issue
publish_tail
topic
chinese_era_year
japanese_era_year
category
title_clean
text_clean
```

단, `source_labels`, `preprocess_indices`는 중복 출처를 기록하는 열이므로 충돌 판정 대상이 아닙니다.

대표 행 선택 기준도 더 구체적으로 정해야 합니다. 권장 순서는 다음입니다.

```text
1. text_exception = F 인 행 우선
2. text_clean 길이가 긴 행 우선
3. title_clean이 존재하는 행 우선
4. publish_date가 존재하는 행 우선
5. preprocess_index가 가장 작은 행 우선
```

이렇게 하면 같은 데이터를 여러 번 실행해도 항상 같은 대표 행이 선택됩니다.

**article_id 결측 처리**
현재까지 검토한 데이터에서는 `article_id` 결측 행이 없었지만, 코드에서는 대비해야 합니다.

선택지는 두 가지입니다.

| 방식 | 설명 |
|---|---|
| 즉시 오류 | `article_id`가 없는 행이 있으면 중단하고 문제 행을 출력 |
| 임시 ID 부여 | `missing_article_id_{preprocess_index}` 같은 값을 부여하고 계속 진행 |

논문용 데이터 생성이라면 첫 번째가 더 엄밀합니다. `article_id`는 중복 통합의 핵심 기준이므로, 결측이 있으면 조용히 넘어가지 않는 편이 좋습니다.

**최종 데이터 열**
⑧의 최종 데이터 열은 현재 23개가 맞습니다. 다만 앞서 말한 것처럼 `preprocess_indeces`는 `preprocess_indices`로 고치는 편이 좋습니다.

수정 후 최종 열은 다음이 적절합니다.

```text
dataset_label
source_labels
preprocess_indices
article_id
qrynewstype
publish_variant
publish_date
page_issue
publish_tail
publish_exception
publish_exception_reason
topic
chinese_era_year
japanese_era_year
category
metadata_source
title_clean
title_exist
title_source
text_clean
text_exception
text_exception_reason
collision
```

**추가하면 좋은 출력**
지침에는 없지만, 실제 작업 안정성을 위해 코드 실행 후 요약 통계를 터미널에 출력하는 것이 좋습니다.

예:

```text
Input files: 4
Stage 1 rows: 40079
Stage 2 rows: 40079
Unique article_id: 33513
Duplicated source rows: 12273
Final combined rows: 33513
Text exception rows: ...
Collision rows: ...
Output:
- shenbao_textdata_preprocess_1_simple_combined_rows.csv
- shenbao_textdata_preprocess_2_preprocessed_rows.csv
- shenbao_textdata_combined_constitution.csv
```

이 통계는 논문에 들어갈 절차 검증 수치로도 사용할 수 있습니다.

**정리**
현재 지침은 전체 방향은 타당합니다. 다만 코드를 작성하기 전에 아래 사항은 수정하거나 확정하는 것이 좋습니다.

| 항목 | 판단 |
|---|---|
| 코드 구조 | 하나의 스크립트로 작성하되 내부 함수는 단계별 분리 |
| 입력 파일 | `shenbao_textdata_*_1to*.csv`만 읽도록 제한 |
| ⑦ 열 개수 | 27개가 아니라 28개 |
| `preprocess_indeces` | `preprocess_indices`로 수정 권장 |
| `combind` | `combined`로 수정 권장 |
| `error_text` 수동 보완 | 자동 처리 불가, 별도 보완 파일 또는 예외 유지 필요 |
| `topic` | publish와 metadata 양쪽에서 들어올 수 있어 병합 규칙 필요 |
| `text_exception_reason` | `error_text > metadata_only > short_text` 우선순위 필요 |
| `collision` | 어떤 열의 값 차이를 충돌로 볼지 명시 필요 |
| 대표 행 선택 | 결정적 우선순위 필요 |
| `article_id` 결측 | 발생 시 중단하고 문제 행 출력 권장 |

이 기준으로 확정하면 `shenbao_preprocess_combine.py`는 재현 가능한 전처리 스크립트로 만들 수 있습니다.

---

## 프롬프트 2-2
그런데 이 작업은 크게 보면 title과 text 문자열에 섞여 들어간 정보를 분리해서 열로 생성하는 작업 하나, 그리고 중복 행을 한 행으로 통합하는 작업 하나, 이렇게 두 단계로 구성되어 있는데, 내가 처음 제시한 순서를 무시하고, 각 단계의 처리 로직과 실제 데이터 구조를 고려했을 때, 둘 중 어떤 걸 먼저 하는 게 낫다고 생각해?

## 답변 2-2
먼저 해야 할 작업은 **title/text에 섞여 들어간 정보와 메타데이터를 분리·정제하는 작업**입니다. 그다음에 **`article_id` 기준 중복 행을 통합**하는 순서가 더 안전합니다.

즉 권장 순서는 다음입니다.

```text
1. 원본 4개 CSV 단순 병합
2. 행 단위 전처리
   - detail_url에서 article_id, qrynewstype 추출
   - publish_raw 분해
   - title_raw, text_raw에서 후행 메타데이터 분리
   - title_clean, text_clean 생성
   - 예외 플래그 부여
3. article_id 기준 중복 통합
```

이 순서가 더 나은 이유는 명확합니다.

첫째, **중복 행 통합의 판단 기준 자체가 전처리 결과에 의존**합니다.  
어떤 행을 대표 행으로 삼을지 결정하려면 최소한 다음 정보가 필요합니다.

```text
text_exception
text_exception_reason
title_clean
text_clean
publish_date
qrynewstype
metadata_source
```

이 값들은 모두 title/text/publish를 먼저 분해·정제해야 생깁니다. 전처리 전에 중복 통합을 해버리면, 나중에 알고 보니 대표 행으로 고른 행이 `metadata_only`, `error_text`, `short_text`였다는 문제가 생길 수 있습니다.

둘째, **같은 `article_id`라도 라벨별 수집 결과의 품질이 다를 수 있습니다.**  
예를 들어 동일한 기사 개체가 `xianfa`와 `xianzheng` 양쪽에서 수집되었을 때, 한쪽은 정상 본문이고 다른 쪽은 `[ERROR] TimeoutError`일 수 있습니다. 이 경우 중복 통합 전에 `text_exception`을 판정해두어야 정상 본문을 가진 행을 대표 행으로 선택할 수 있습니다.

셋째, **충돌 여부를 판단하려면 정제된 값을 비교해야 합니다.**  
원본 `title_raw`, `text_raw`에는 다음 요소들이 섞여 있을 수 있습니다.

```text
其他紀元：
類別：
主題：
Copyright c 2012 得泓資訊. All Rights Reserved.
목록 제목의 일련번호
본문 뒤 후행 메타데이터
```

이 상태에서 중복 행끼리 비교하면 실제 내용 차이가 아니라, 메타데이터 혼입 여부나 수집 구조 차이 때문에 충돌처럼 보일 수 있습니다. 따라서 `title_clean`, `text_clean`, `publish_*`를 만든 뒤 비교해야 더 의미 있는 `collision` 판정이 가능합니다.

넷째, **전처리 전 통합은 원본 행 단위의 문제를 가릴 수 있습니다.**  
중복 통합을 먼저 하면 특정 라벨에서 발생한 수집 오류, 예외 구조, 메타데이터 혼입이 대표 행 선택 과정에서 사라질 수 있습니다. 그러면 나중에 “어떤 수집 라벨에서 어떤 문제가 있었는지” 추적하기 어려워집니다. 반대로 행 단위 전처리를 먼저 하면 각 원본 행의 상태를 보존한 채, 마지막 단계에서만 통합할 수 있습니다.

따라서 구조적으로는 다음이 가장 적절합니다.

```text
Stage 1: append
원본 행을 모두 보존한 단순 병합 데이터 생성

Stage 2: preprocess rows
각 원본 행에 대해 article_id 추출, 메타데이터 분리, title/text 정제, 예외 플래그 부여

Stage 3: combine articles
article_id 기준으로 중복 행을 통합하고 source_labels, preprocess_indices, collision 기록
```

반대로 **중복 통합을 먼저 하는 방식**은 다음 경우에만 적합합니다.

```text
- 동일 article_id의 여러 행이 완전히 동일하다고 확신할 수 있을 때
- title/text/publish의 예외 처리가 거의 필요 없을 때
- 대표 행 선택 기준이 단순히 “첫 번째 행”이어도 무방할 때
```

하지만 지금 데이터는 그렇지 않습니다. 실제로 이 데이터에는 `error_text`, `metadata_only`, `short_text`, `title/text 오염`, `publish 예외`, `SP_AD`, `SP_FH`, `SP_HK`, 라벨 간 중복이 함께 존재합니다. 그러므로 먼저 행 단위 전처리를 하고, 그 결과를 바탕으로 중복 통합하는 것이 맞습니다.

정리하면, 사용자가 처음 제시한 순서인 **①-⑦ 행 단위 전처리 후 ⑧ 중복 통합**은 실제 데이터 구조를 고려해도 타당합니다. 다만 논리적으로는 다음처럼 이름을 붙여 설명하는 것이 더 명확합니다.

```text
1단계: 원본 행 보존 병합
2단계: 원본 행 단위 정제 및 예외 판정
3단계: article_id 기준 기사 단위 통합
```

이렇게 정리하면 논문에서도 “전처리”와 “통합”의 관계가 분명해집니다.

---

## 프롬프트 2-3
네 csv 파일에서 article_id가 같은 행 사이에 publish,title,text 세 열의 값을 기준으로 차이가 있는 경우가 얼마나 되는지 검토해줘. 완전 일치 경우, 공백만 다른 경우, 서로 다른 경우 등의 비중이 얼마나 되는지 알고 싶어. 불일치인 경우에도 [ERROR] 때문인 경우를 제외하고 또 어떤 경우가 얼마나 비중을 차지하는지 알고 싶어

## 답변 2-3
`shlib-shenbao-dataset-workflow\shenbao_textdata`의 네 CSV, 총 `40,079행`을 기준으로 다시 검토했습니다. 기준은 `detail_url`에서 추출한 `article_id`이며, 같은 `article_id`를 가진 중복 그룹 `5,707개`만 비교했습니다.

**요약**
같은 `article_id`를 가진 행들 사이에서 `publish`, `title`, `text` 세 열은 거의 모두 동일합니다.  
`publish`, `title`, `text` 세 열을 함께 비교했을 때:

| 비교 유형 | article_id 그룹 수 | 비율 |
|---|---:|---:|
| 완전 일치 | 5,698 | 99.84% |
| 공백만 다름 | 1 | 0.02% |
| 서로 다름 | 8 | 0.14% |
| 합계 | 5,707 | 100.00% |

행 기준으로 보면, 중복 출현한 전체 행 `12,273행` 중 `12,253행`은 같은 `article_id`의 다른 행과 `publish`, `title`, `text`가 완전히 같은 그룹에 속합니다.

| 비교 유형 | 행 수 | 비율 |
|---|---:|---:|
| 완전 일치 그룹 소속 행 | 12,253 | 99.84% |
| 공백 차이 그룹 소속 행 | 2 | 0.02% |
| 불일치 그룹 소속 행 | 18 | 0.15% |
| 합계 | 12,273 | 100.00% |

**열별 비교**
각 열을 따로 비교하면 다음과 같습니다.

| 열 | 완전 일치 | 공백만 다름 | 서로 다름 | 합계 |
|---|---:|---:|---:|---:|
| `publish` | 5,706 | 1 | 0 | 5,707 |
| `title` | 5,703 | 0 | 4 | 5,707 |
| `text` | 5,699 | 1 | 7 | 5,707 |

비율로 보면 다음과 같습니다.

| 열 | 완전 일치 비율 | 공백 차이 비율 | 내용 차이 비율 |
|---|---:|---:|---:|
| `publish` | 99.98% | 0.02% | 0.00% |
| `title` | 99.93% | 0.00% | 0.07% |
| `text` | 99.86% | 0.02% | 0.12% |

따라서 중복 통합 과정에서 `publish`는 사실상 안정적입니다. 차이가 난 1건도 실질 내용 차이가 아니라 공백 차이입니다.

**공백만 다른 사례**
공백만 다른 그룹은 1건입니다.

| article_id | 라벨 | item_index | 차이 |
|---|---|---:|---|
| `A2013061067526` | `xianfa`, `zhixian` | 9122, 1082 | `publish`와 `text`에서 전각 공백 또는 일반 공백 위치만 다름 |

이 경우는 내용상 동일하므로, 전처리에서 공백 정규화를 적용하면 충돌로 볼 필요는 없습니다.

**서로 다른 8개 그룹의 원인**
`publish`, `title`, `text` 세 열 중 하나라도 실질적으로 다른 그룹은 8개입니다.

| 원인 유형 | article_id 그룹 수 | 불일치 그룹 내 비율 | 전체 중복 그룹 내 비율 |
|---|---:|---:|---:|
| `[ERROR]` 수집 실패 문자열 때문에 다름 | 7 | 87.50% | 0.12% |
| `[ERROR]`가 아닌 title 결측 차이 | 1 | 12.50% | 0.02% |
| 합계 | 8 | 100.00% | 0.14% |

즉, 불일치 8건 중 대부분은 실제 기사 내용이 서로 다른 것이 아니라, 어느 한 라벨에서 같은 기사를 수집할 때 본문 로드 실패가 발생해 `text`에 `[ERROR] TimeoutError...`가 들어간 사례입니다.

**[ERROR] 관련 불일치의 세부 유형**
`[ERROR]`가 포함된 7개 그룹은 다시 두 가지로 나눌 수 있습니다.

| 세부 유형 | 그룹 수 | 설명 |
|---|---:|---|
| 모든 중복 행이 `[ERROR]`이나 에러 문자열의 URL 일부가 달라 완전일치하지 않음 | 4 | 실제 본문은 모두 수집 실패 |
| 일부 라벨에서는 정상 수집, 일부 라벨에서는 `[ERROR]` | 3 | 정상 수집 행을 대표 행으로 선택하면 복구 가능 |

예를 들어 다음과 같은 경우입니다.

| article_id | 라벨 / item_index | 상황 |
|---|---|---|
| `A2013061161883` | `lixian` 261, `xianzheng` 1658 | 둘 다 `[ERROR]`, 에러 문자열 내부 URL 일부가 달라 text 완전일치 아님 |
| `A2013060139748` | `lixian` 655, `xianfa` 6996, `zhixian` 834 | 모두 `[ERROR]`, 에러 문자열 내부 URL 일부가 달라 text 완전일치 아님 |
| `A2013010176307` | `lixian` 4293, `xianfa` 16603, `xianzheng` 8494 | 앞의 두 행은 정상, `xianzheng`만 `[ERROR]` |
| `A2013060789732` | `xianfa` 1883, `xianzheng` 921 | `xianzheng`은 정상, `xianfa`는 `[ERROR]` |
| `A2013040078400` | `xianfa` 13447, `zhixian` 2907 | `xianfa`는 정상, `zhixian`은 `[ERROR]` |

따라서 중복 통합 시에는 `text_exception = F`인 행을 우선 선택하면 이 중 일부는 자동으로 해결됩니다.

**[ERROR]가 아닌 불일치**
`[ERROR]`와 무관한 불일치는 1건입니다.

| article_id | 라벨 / item_index | 차이 |
|---|---|---|
| `A2015100134302` | `xianfa` 726, `xianzheng` 249 | `publish`와 `text`는 완전히 같지만, `xianfa` 행의 `title`이 비어 있고 `xianzheng` 행에는 title이 존재 |

이 사례는 본문 길이가 매우 긴 광고성 자료입니다. `xianfa` 쪽에서는 `title` 추출이 누락되었지만, `text`는 정상 수집되어 있고, 같은 `article_id`의 `xianzheng` 행에는 title이 들어 있습니다. 따라서 중복 통합 단계에서 `title_clean`이 존재하는 행을 우선 선택하면 보완 가능합니다.

**해석**
결론적으로, 같은 `article_id`를 가진 중복 행들 사이에서 `publish`, `title`, `text`의 내용 차이는 거의 없습니다. 불일치로 분류된 `8개 article_id` 중 `7개`는 `[ERROR] TimeoutError` 같은 수집 실패 문자열 때문에 발생한 것이고, `[ERROR]`와 무관한 실제 차이는 `title` 결측 1건뿐입니다.

따라서 중복 통합 로직은 다음 원칙으로 두면 충분합니다.

```text
1. 같은 article_id 그룹 안에서는 text_exception = F인 행을 우선 선택
2. title_clean이 비어 있지 않은 행을 우선 선택
3. text_clean 길이가 긴 행을 우선 선택
4. 그래도 동일하면 preprocess_index가 가장 작은 행 선택
```

이 기준을 적용하면, 중복 행 간의 실질 내용 차이 때문에 문제가 생길 가능성은 매우 낮습니다. 논문에서는 “동일 `article_id`를 갖는 중복 행의 99.84%는 `publish`, `title`, `text` 세 열이 완전히 일치했으며, 불일치 사례 대부분은 수집 실패 문자열(`[ERROR]`)에 기인했다”고 정리할 수 있습니다.

---

## 프롬프트 2-4
만약에 이처럼 동일 article_id를 가진 여러 개체가 실제로는 데이터베이스 내의 같은 페이지를 불러오는 것이어서, 에러가 발생하지만 않는다면 확실히 서로 같다는 점이 확인된다면, 중복 행을 먼저 합친 후에 메타데이터를 분리해도 되지 않을까

## 답변 2-4
가능합니다. 그리고 지금 확인한 데이터 특성만 놓고 보면, **중복 행을 먼저 통합한 뒤 메타데이터를 분리하는 방식도 충분히 방어 가능**합니다.

다만 조건이 있습니다. “그냥 첫 행을 남기고 합친다”가 아니라, **중복 그룹 안에서 가장 좋은 원본 행을 먼저 고르는 통합**이어야 합니다.

즉 순서는 이렇게 바뀔 수 있습니다.

```text
1. 원본 4개 CSV 단순 병합
2. detail_url에서 article_id, qrynewstype 추출
3. article_id 기준 중복 행 통합
   - [ERROR] 없는 행 우선
   - title/text가 비어 있지 않은 행 우선
   - text 길이가 긴 행 우선
   - source_labels, source_indices 보존
4. 통합된 1행 1기사 데이터에서 publish/title/text 메타데이터 분리
5. title_clean, text_clean, 예외 플래그 생성
```

이 방식이 가능한 이유는 방금 확인한 결과 때문입니다.

- 중복 `article_id` 그룹 `5,707개` 중 `5,698개`, 즉 `99.84%`는 `publish`, `title`, `text`가 완전히 같았습니다.
- 공백만 다른 경우는 `1개`뿐이었습니다.
- 서로 다른 경우는 `8개`뿐이었고, 그중 `7개`는 `[ERROR] TimeoutError` 때문이었습니다.
- `[ERROR]`가 아닌 실질 차이는 `title` 결측 1건뿐이었습니다.
- 따라서 같은 `article_id`는 에러만 없으면 사실상 동일한 데이터베이스 개체를 가리킨다고 볼 수 있습니다.

이 조건에서는 **중복 통합을 먼저 하는 편이 오히려 더 단순**합니다.

**장점**
중복 통합을 먼저 하면 다음 장점이 있습니다.

```text
1. 이후 메타데이터 분리와 예외 판정을 40,079행이 아니라 33,513행에 대해서만 수행하면 됨
2. 같은 기사에 대해 동일한 전처리를 여러 번 반복하지 않아도 됨
3. 최종 연구용 데이터의 단위인 article_id 기준 1행 1기사 구조가 먼저 확정됨
4. 논문 설명이 단순해짐
```

특히 연구용 통합 데이터가 최종 목표라면, “먼저 기사 개체 단위를 확정한 뒤, 그 개체의 필드를 정제했다”고 설명하는 것이 더 자연스러울 수 있습니다.

**주의점**
다만 중복 통합을 먼저 하려면, 통합 전에 최소한의 판정은 필요합니다.

메타데이터 분리는 뒤로 미뤄도 되지만, 대표 행 선택을 위해 다음 정도는 먼저 계산해야 합니다.

```text
article_id
qrynewstype
source_labels
preprocess_indices
has_error_text
title_is_empty
text_is_empty
text_length
```

즉 “완전한 전처리”는 나중에 하더라도, “대표 행 선택을 위한 최소 품질 점수”는 먼저 만들어야 합니다.

예를 들어 대표 행 선택 기준은 다음처럼 둘 수 있습니다.

```text
1. text가 [ERROR]로 시작하지 않는 행 우선
2. title이 비어 있지 않은 행 우선
3. text가 비어 있지 않은 행 우선
4. text 길이가 긴 행 우선
5. preprocess_index가 작은 행 우선
```

이렇게 하면 다음 사례들이 자연스럽게 처리됩니다.

- 한 라벨에서는 `[ERROR]`, 다른 라벨에서는 정상 수집된 경우 → 정상 수집 행 선택
- 한 라벨에서는 `title` 결측, 다른 라벨에서는 `title` 존재 → title 존재 행 선택
- 둘 다 정상이고 내용이 같음 → 아무 행을 선택해도 동일
- 둘 다 `[ERROR]` → 어쩔 수 없이 하나를 선택하되, 최종 전처리 단계에서 `text_exception = T`

**논문상 설명 가능성**
논문에서는 이 순서가 더 간결하게 설명될 수 있습니다.

예를 들면 다음처럼 쓸 수 있습니다.

```text
동일 article_id를 가진 행들은 데이터베이스 내 동일 기사 개체를 가리키므로, 먼저 article_id를 기준으로 중복 행을 통합하였다. 실제 검토 결과, 중복 article_id 5,707개 가운데 5,698개(99.84%)는 publish, title, text 세 열이 완전히 일치했으며, 불일치 8건 중 7건은 수집 실패 문자열([ERROR])에 따른 차이였다. 따라서 중복 통합 단계에서는 [ERROR]가 없는 행, title과 text가 결측되지 않은 행, text 길이가 긴 행을 우선하여 대표 행으로 선택하고, 해당 기사 개체가 어떤 검색 라벨에서 수집되었는지는 source_labels와 preprocess_indices에 보존하였다. 이후 통합된 1행 1기사 데이터에 대해 발행 정보, 후행 메타데이터, 제목 및 본문 정제 작업을 수행하였다.
```

이 설명은 데이터 구조에 근거가 있기 때문에 충분히 설득력 있습니다.

**두 방식 비교**
정리하면 두 방식은 다음 차이가 있습니다.

| 순서 | 장점 | 단점 |
|---|---|---|
| 행 단위 전처리 후 중복 통합 | 원본 행별 예외를 세밀하게 기록 가능 | 절차가 길고 중복 기사에 같은 전처리를 반복 |
| 중복 통합 후 전처리 | 구조가 단순하고 최종 데이터 단위가 먼저 확정됨 | 대표 행 선택 전 최소 품질 판정이 필요 |

현재 데이터의 실제 검토 결과를 고려하면, **중복 통합 후 전처리 방식이 더 실용적이고 논문 설명도 간결합니다.**

다만 원본 행별 오류 분석을 완전히 포기하면 안 됩니다. 따라서 가장 좋은 구조는 다음입니다.

```text
Stage 1. 원본 행 단순 병합
- 40,079행 보존
- 모든 원본 열에 _raw 부여
- preprocess_index 부여

Stage 2. article_id 기준 중복 통합
- 33,513행 생성
- source_labels, preprocess_indices 기록
- 대표 원본 행 선택
- duplicate_collision 또는 source_row_status 기록

Stage 3. 통합 데이터 전처리
- publish_raw 분리
- title_raw/text_raw 후행 메타데이터 분리
- title_clean/text_clean 생성
- 예외 플래그 부여
```

이렇게 하면 두 목표를 모두 만족합니다.

- 원본 40,079행의 출처와 중복 관계는 보존
- 실제 연구용 데이터는 33,513개 기사 개체 기준으로 정리
- 메타데이터 분리와 본문 정제는 중복 제거 후 한 번만 수행

따라서 질문에 대한 답은 다음입니다.

**네, 동일 `article_id`가 실제로 같은 데이터베이스 개체를 가리키며, 에러가 없을 때 `publish`, `title`, `text`가 사실상 동일하다는 점이 확인되었으므로, 중복 행을 먼저 통합한 뒤 메타데이터를 분리해도 됩니다. 오히려 현재 데이터 구조에서는 그 방식이 더 단순하고 실용적입니다. 단, 통합 전에는 `[ERROR]`, title/text 결측, text 길이 등을 기준으로 대표 행을 고르는 최소 품질 판정 로직을 반드시 넣어야 합니다.**

---

## 프롬프트 2-5
- "duplicate_collision 또는 source_row_status 기록"는 어떻게 하라는거야?
- 만약 지금 바로 "중복 통합 후 전처리" 방식으로 진행하는 코드를 만들어야 한다면, 모호한 부분, 즉 내가 미리 결정해줘야 할 부분이 있을까?

## 답변 2-5
**`duplicate_collision` / `source_row_status`의 의미**
둘은 “중복 통합 과정에서 어떤 일이 있었는지”를 남기는 진단용 열입니다. 필수는 아니지만, 논문용 데이터라면 남겨두는 편이 좋습니다.

`duplicate_collision`은 같은 `article_id`를 가진 여러 행 사이에 `publish`, `title`, `text` 값이 서로 달랐는지를 표시하는 열입니다.

예:

```text
duplicate_collision = F
```

같은 `article_id`의 모든 행이 완전 일치하거나 공백 차이만 있는 경우입니다.

```text
duplicate_collision = T
```

같은 `article_id`의 여러 행 사이에 실제 차이가 있는 경우입니다. 예를 들어 한쪽은 정상 본문이고 다른 쪽은 `[ERROR] TimeoutError...`인 경우입니다.

`source_row_status`는 같은 `article_id`로 묶인 원본 행들이 어떤 상태였는지를 요약하는 열입니다.

예:

```text
all_exact
```

중복 행들이 모두 완전히 같음.

```text
whitespace_only
```

공백 차이만 있음.

```text
error_vs_normal
```

어떤 라벨에서는 정상 수집되었고, 어떤 라벨에서는 `[ERROR]`가 들어 있음.

```text
all_error
```

중복 행들이 모두 `[ERROR]` 상태임.

```text
title_missing_vs_present
```

한쪽은 `title`이 비어 있고, 다른 쪽은 `title`이 있음.

```text
other_difference
```

위 유형으로 설명되지 않는 차이.

즉, 두 열의 차이는 다음과 같습니다.

| 열                     | 역할                   |
| --------------------- | -------------------- |
| `duplicate_collision` | 차이가 있었는지 T/F로 간단히 표시 |
| `source_row_status`   | 차이가 어떤 종류였는지 설명      |

둘 다 넣으면 가장 명확하지만, 열 수를 줄이고 싶다면 `source_row_status` 하나만으로도 충분합니다. 예를 들어 `all_exact`, `whitespace_only`는 충돌 없음으로 해석하고, 나머지는 충돌 있음으로 해석할 수 있습니다.

**바로 코드를 만든다면 미리 결정해야 할 부분**
지금 바로 “중복 통합 후 전처리” 방식으로 코드를 만들 수 있습니다. 다만 아래 항목들은 결정해두는 편이 좋습니다.

**1. 최종 파일명**
현재 지침에는 다음 파일명이 있었습니다.

```text
shenbao_textdata_combind_{dataset_label 값}.csv
```

이건 `combind`가 오타로 보입니다. 지금부터 새 코드로 만들 거라면 다음을 권장합니다.

```text
shenbao_textdata_combined_{dataset_label}.csv
```

예:

```text
shenbao_textdata_combined_constitution.csv
```

결정 필요:

```text
combind를 유지할지, combined로 고칠지
```

제 판단은 `combined`로 고치는 편이 맞습니다.

**2. `preprocess_indeces` vs `preprocess_indices`**
이것도 영어 표기 문제입니다.

현재 지침:

```text
preprocess_indeces
```

권장:

```text
preprocess_indices
```

결정 필요:

```text
기존 지침 표기를 유지할지, 영어 문법에 맞게 preprocess_indices로 고칠지
```

제 판단은 `preprocess_indices`가 맞습니다.

**3. 최종 데이터에 원본 대표 행의 기본 정보도 남길지**
최종 통합 데이터에는 `source_labels`, `preprocess_indices`가 들어갑니다. 그런데 대표 행이 어느 라벨에서 왔는지도 별도로 알 수 있으면 검수에 유리합니다.

추가 후보 열:

```text
representative_label
representative_preprocess_index
representative_item_index
```

다만 열이 늘어납니다.

결정 필요:

```text
최종 스키마를 간결하게 유지할지,
대표 행 추적 열을 추가할지
```

제 판단은 논문용 재현성을 고려해 최소한 `representative_preprocess_index`는 있으면 좋습니다. 하지만 사용자가 제시한 23개 열 구조를 유지하려면 생략해도 됩니다. `preprocess_indices`의 첫 번째 값을 대표 행으로 규정하면 되기 때문입니다.

**4. `duplicate_collision`, `source_row_status`를 최종 열에 포함할지**
기존 최종 스키마에는 `collision`만 있었습니다.

```text
collision
```

이를 다음처럼 유지할 수 있습니다.

```text
collision
```

또는 더 명확하게 바꿀 수 있습니다.

```text
duplicate_collision
source_row_status
```

결정 필요:

```text
기존 collision 열 하나만 둘지,
duplicate_collision과 source_row_status를 둘 다 둘지
```

제 판단은 다음입니다.

- 논문 설명과 검수에는 `source_row_status`가 유용합니다.
- 최종 분석용 데이터에는 `collision` 하나면 충분합니다.

절충안:

```text
collision
source_row_status
```

이렇게 두 열을 두는 것이 좋습니다.

**5. 대표 행 선택 기준**
이건 반드시 확정해야 합니다. 권장 기준은 다음입니다.

```text
1. text_raw가 [ERROR]로 시작하지 않는 행 우선
2. text_raw가 비어 있지 않은 행 우선
3. title_raw가 비어 있지 않은 행 우선
4. text_raw 길이가 긴 행 우선
5. preprocess_index가 작은 행 우선
```

주의할 점은 2번과 3번의 순서입니다.  
본문 데이터가 더 중요하면 `text_raw` 우선, 제목 데이터가 더 중요하면 `title_raw` 우선입니다.

제 판단은 **본문 우선**이 맞습니다.

```text
text 정상 여부 > title 존재 여부
```

다만 앞에서 확인한 `A2015100134302` 같은 경우는 두 행의 text가 같고 한쪽 title만 비어 있으므로, 위 기준에서도 title이 있는 행이 선택됩니다.

**6. `[ERROR]` 행을 최종 데이터에 어떻게 남길지**
중복 그룹 안에 정상 행이 있으면 정상 행을 대표로 선택하면 됩니다.  
문제는 같은 `article_id`의 모든 행이 `[ERROR]`인 경우입니다.

선택지는 두 가지입니다.

| 방식 | 설명 |
|---|---|
| 보수적 유지 | 대표 행으로 하나를 남기고 `text_exception=T`, `text_clean` 결측 |
| 수동 보완 전제 | 별도 보완 파일을 읽어 `text_clean`을 채움 |

지금 바로 자동 코드를 만든다면 첫 번째 방식이 현실적입니다.

```text
all_error인 경우 그대로 남기고 text_exception = T
```

**7. `short_text` 기준**
기존 지침은 5자 이하입니다.

```text
len(text_clean.strip()) <= 5
```

결정 필요:

```text
5자 이하 기준 유지 여부
```

제 판단은 유지해도 됩니다. 다만 논문에는 “본문이 극히 짧은 경우를 검토 대상으로 표시하기 위한 보수적 기준”이라고 설명하는 것이 좋습니다. 짧다고 무조건 삭제해서는 안 됩니다.

**8. `SP_AD` 광고 자료를 최종 통합 데이터에서 제외할지**
현재 지침은 “통합 데이터 생성”입니다. 분석용 corpus를 만드는 단계는 별도입니다.

따라서 지금 코드에서는 `SP_AD`도 삭제하지 않고 보존하는 것이 맞습니다.

결정 필요:

```text
combined 데이터에 SP_AD를 포함할지 제외할지
```

제 판단은 포함입니다.  
제외는 나중에 `corpus_articles_only` 같은 분석용 파생 데이터에서 해야 합니다.

**9. `publish_exception=T` 행을 최종 데이터에서 제외할지**
마찬가지로 제외하면 안 됩니다.  
`publish_exception`은 검수 플래그이지 삭제 조건이 아닙니다.

권장:

```text
최종 combined 데이터에는 모두 포함
분석용 corpus 생성 시 제외 여부 판단
```

**10. `topic` 열 병합 규칙**
`topic`은 `publish_raw`의 `主題：...` 또는 `title/text` 후행 메타데이터에서 나올 수 있습니다.

결정 필요:

```text
둘 다 존재하고 값이 다르면 어떻게 할지
```

권장:

```text
서로 다르면 ; 로 병합
같으면 하나만 기록
없으면 빈칸
```

**11. 메타데이터 제거 범위**
`text_clean`을 만들 때 `其他紀元：` 이후를 제거하는 것은 명확합니다.

다만 `title_clean`에서도 `其他紀元：` 이후와 copyright를 제거할지 결정해야 합니다. 기존 지침은 제거입니다.

권장:

```text
title_clean: 其他紀元： 이후 제거, copyright 제거
text_clean: 其他紀元： 이후 제거, copyright 제거
```

**12. 저장 위치**
코드 파일은 작업 디렉토리에 저장하고, 결과물은 `shenbao_textdata` 폴더 안에 저장하는 것이 자연스럽습니다.

예:

```text
C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_preprocess_combine.py
C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\shenbao_textdata_preprocess_1_simple_combined_rows.csv
C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\shenbao_textdata_combined_constitution.csv
```

다만 중간 산출물이 원본 입력으로 다시 읽히지 않도록, 입력 파일 패턴 제한은 반드시 넣어야 합니다.

**내가 권장하는 확정안**
지금 바로 구현한다면 저는 아래 기준으로 만들겠습니다.

```text
코드 파일명:
shenbao_preprocess_combine.py

입력 경로:
기본값 = ./shenbao_textdata

입력 파일:
shenbao_textdata_*_1to*.csv 만 사용

출력:
1. shenbao_textdata_preprocess_1_simple_combined_rows.csv
2. shenbao_textdata_combined_constitution.csv

최종 파일명:
shenbao_textdata_combined_constitution.csv

dataset_label:
constitution

중복 통합 순서:
article_id 기준 먼저 통합 후 전처리

대표 행 선택:
1. [ERROR] 없는 행
2. text_raw 비어 있지 않은 행
3. title_raw 비어 있지 않은 행
4. text_raw 길이 긴 행
5. preprocess_index 작은 행

최종 열:
dataset_label
source_labels
preprocess_indices
article_id
qrynewstype
publish_variant
publish_date
page_issue
publish_tail
publish_exception
publish_exception_reason
topic
chinese_era_year
japanese_era_year
category
metadata_source
title_clean
title_exist
title_source
text_clean
text_exception
text_exception_reason
collision
source_row_status
```

기존 23개 열에 `source_row_status` 하나가 추가되어 총 24개 열이 됩니다.  
만약 논문에서 반드시 23개 열로 고정하고 싶다면 `source_row_status`는 빼고 `collision`만 남기면 됩니다.

**최종적으로 사용자 결정이 필요한 것**
정말로 결정이 필요한 것은 아래 4개입니다.

1. 최종 파일명을 `combined`로 고칠지, 기존 오타형 `combind`를 유지할지
2. 최종 열에 `source_row_status`를 추가할지
3. 최종 열에 대표 행 추적용 `representative_preprocess_index`를 추가할지
4. `[ERROR]만 있는 article_id`를 그대로 남길지, 별도 수동 보완 파일을 적용할지

제 권장 선택은 다음입니다.

```text
1. combined 사용
2. source_row_status 추가
3. representative_preprocess_index는 생략
4. [ERROR]만 있는 article_id는 그대로 남기고 text_exception=T로 표시
```

이 선택이면 코드가 단순하고, 논문에서도 설명하기 쉽고, 원본 추적성도 충분히 확보됩니다.

---

## 프롬프트 2-6
- 메타데이터 등을 분리해 낸 최종 combined 파일하고 simple_combine_rows 사이에, 중복열 제거까지만 시행된 단계의 파일을 하나 더 만들어야 하는거 아닌가?
- 파일명에서 `simple_combine_rows`가 좀 전문적이지 않게 느껴져서, 좀더 일반적인 표현 형식을 추천해줘

## 답변 2-6
네, **중복열 제거까지만 시행된 단계의 파일을 하나 더 만드는 편이 좋습니다.**  
특히 지금처럼 “중복 통합 후 전처리” 방식으로 간다면, 단계 산출물을 다음처럼 분리하는 것이 논리적으로 더 깔끔합니다.

```text
1단계: 원본 행 병합
2단계: article_id 기준 중복 통합
3단계: 메타데이터 분리 및 정제
```

이렇게 하면 각 파일이 서로 다른 역할을 갖습니다.

| 단계 | 역할 | 행 단위 |
|---|---|---|
| 1단계 | 네 원본 CSV를 그대로 이어 붙임 | 원본 수집 행 단위 |
| 2단계 | 같은 `article_id`를 가진 중복 행을 1행으로 통합 | 기사 개체 단위 |
| 3단계 | `publish`, `title`, `text`에서 메타데이터 분리 및 정제 | 정제된 기사 개체 단위 |

이 구조가 좋은 이유는 다음입니다.

- `1단계`는 원 수집 결과 전체를 보존합니다.
- `2단계`는 중복 제거 이후의 “기사 개체 기준 원자료”입니다.
- `3단계`는 연구에 사용할 수 있도록 열을 분해하고 정제한 최종 데이터입니다.
- 문제가 생겼을 때 어느 단계에서 값이 바뀌었는지 추적하기 쉽습니다.
- 논문에서 “원본 병합 → 중복 통합 → 정제”라는 절차를 명확히 설명할 수 있습니다.

따라서 중간 파일은 만드는 편이 맞습니다.

다만 표현은 “중복열 제거”보다는 **“중복 행 통합”**이 정확합니다.  
여기서 제거하는 것은 열(column)이 아니라, 동일 `article_id`를 가진 행(row)이기 때문입니다.

**추천 파일명**
현재 `simple_combine_rows`는 의미는 전달되지만 다소 구어적이고, `combine`과 `rows`가 함께 쓰여 어색합니다. 일반적으로는 다음 표현들이 더 자연스럽습니다.

| 용도 | 추천 파일명 |
|---|---|
| 1단계 원본 행 병합 | `shenbao_textdata_stage1_appended_rows.csv` |
| 2단계 중복 행 통합 | `shenbao_textdata_stage2_deduplicated_articles.csv` |
| 3단계 메타데이터 분리·정제 | `shenbao_textdata_stage3_preprocessed_articles.csv` |

가장 추천하는 전체 구성은 다음입니다.

```text
shenbao_textdata_stage1_appended_rows.csv
shenbao_textdata_stage2_deduplicated_articles.csv
shenbao_textdata_stage3_preprocessed_articles.csv
```

이 명명 방식의 장점은 다음입니다.

- `stage1`, `stage2`, `stage3`로 처리 순서가 명확합니다.
- `appended_rows`는 네 원본 CSV를 단순히 이어 붙였다는 의미입니다.
- `deduplicated_articles`는 `article_id` 기준으로 중복 제거된 기사 단위 데이터라는 뜻입니다.
- `preprocessed_articles`는 메타데이터 분리와 정제가 완료된 기사 단위 데이터라는 뜻입니다.
- `rows`와 `articles`를 구분해, 1단계는 원본 행 단위이고 2단계 이후는 기사 개체 단위라는 점을 드러낼 수 있습니다.

논문에 쓰기에도 이 표현이 가장 안정적입니다.

**대안**
조금 더 설명적인 파일명을 원하면 다음도 가능합니다.

```text
shenbao_textdata_1_appended_source_rows.csv
shenbao_textdata_2_deduplicated_article_rows.csv
shenbao_textdata_3_preprocessed_article_rows.csv
```

이 방식은 `stage`라는 표현을 쓰지 않고도 순서가 드러납니다. 다만 저는 `stage1`, `stage2`, `stage3`가 더 명확하다고 봅니다.

**최종 추천안**
코드 산출물은 다음 3개로 정리하는 것을 권장합니다.

```text
shenbao_textdata_stage1_appended_rows.csv
shenbao_textdata_stage2_deduplicated_articles.csv
shenbao_textdata_stage3_preprocessed_articles.csv
```

그리고 최종 통합 연구 데이터라는 의미를 더 강조하고 싶다면, 3단계 파일을 다음처럼 해도 됩니다.

```text
shenbao_textdata_stage3_constitution_articles.csv
```

하지만 전처리 절차 전체를 설명하는 논문이라면, 기능 중심 명칭인 `preprocessed_articles`가 더 일반적입니다.

**수정된 처리 흐름**
현재 작업의 전체 흐름은 이렇게 정리하는 것이 가장 좋습니다.

```text
Stage 1. Append source rows
- 네 원본 CSV를 단순 병합
- 원본 열 이름에 _raw 추가
- preprocess_index 부여
- 출력: shenbao_textdata_stage1_appended_rows.csv

Stage 2. Deduplicate articles
- detail_url_raw에서 article_id, qrynewstype 추출
- article_id 기준으로 중복 행 통합
- source_labels, preprocess_indices 기록
- 대표 행 선택
- collision, source_row_status 기록
- 출력: shenbao_textdata_stage2_deduplicated_articles.csv

Stage 3. Preprocess articles
- publish_raw 분해
- title_raw/text_raw 후행 메타데이터 분리
- title_clean, text_clean 생성
- 예외 플래그 부여
- 출력: shenbao_textdata_stage3_preprocessed_articles.csv
```

이 방식이면 중간 산출물의 기능이 명확하고, 논문에서도 재현 가능한 전처리 절차로 설명하기 쉽습니다.

---

## 프롬프트 2-7
`바로 코드를 만든다면 미리 결정해야 할 부분`에 대한 나의 지침은 다음과 같아. 
1. 파일명: shenbao_textdata_combined_{dataset_label}.csv
2. preprocess_indices
3. 최종 데이터에 원본 대표 행의 기본 정보: representative_label, representative_item_index 만 추가
4. `source_row_status`로 설명한 내용을 `collision_type`이라는 열 제목으로 추가 구현. 네가 말한 `duplicate_collision` 기능이 내 지침에서 `collision`의 역할(T/F 판정)이었으므로, `duplicate_collision`은 추가 구현할 필요 없음
5. 대표 행 선택 기준: 제안대로 text_raw를 우선.
	5-1. 대표행 선택 사유를 나타내는 select_reason 열을 추가하고, 해당 열의 값을 각 선택 사유별로 "1_no_error", "2_text_exists", "3_title_exists", "4_long_text", "5_small_index"로 표시
6. [ERROR] 행을 최종 데이터에: 보수적 유지
7. `short_text` 기준 기존 지침에서 더 줄여서 3자 이하로 설정 
8. `SP_AD` 유지
9. `publish_exception=T` 행 제외하지 말 것
10. `topic` 열 병합 규칙은 권장안대로 (서로 다르면 ; 로 병합 / 같으면 하나만 기록 / 없으면 빈칸)
11. 메타데이터 제거: 권장안대로 (title_clean과 text_clean 모두에서 其他紀元： 이후 제거, copyright 제거)
12. 저장 위치
  - 코드 파일은 작업 디렉토리
  - 결과물 파일은 shenbao_textdata\preprocess 경로에 저장. 해당 폴더가 없으면 생성

이를 고려하면서, 중복열 제거까지만 시행된 단계의 파일을 하나 더 만드는 방식으로 진행해줘. 각 단계의 파일명은 아래 형식으로 해줘
`shenbao_{dataset_label}_text_stage1_appended_rows.csv`
`shenbao_{dataset_label}_text_stage2_deduplicated_articles.csv`
`shenbao_{dataset_label}_text_stage3_preprocessed_articles.csv`

혹시 더 내가 결정해야 할 부분이 있을까?

## 답변 2-7
**구현 결과**
추가로 반드시 결정해야 할 부분은 없다고 보고, 제시한 지침대로 전처리 코드를 작성하고 실행까지 완료했습니다.

작성한 코드:

[shenbao_preprocess_combine.py](C:/Users/class/Documents/coding/shenbao_preprocess_combine.py)

기본 실행 명령어:

```powershell
python .\shenbao_preprocess_combine.py
```

현재 실행에서는 입력 폴더를 자동 탐색하여 아래 경로의 네 CSV를 사용했습니다.

```text
C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata
```

결과물은 요청대로 아래 경로에 저장했습니다.

```text
C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\preprocess
```

**생성 파일**
세 단계 산출물을 모두 생성했습니다.

| 단계 | 파일 | 행 수 |
|---|---|---:|
| Stage 1 | [shenbao_constitution_text_stage1_appended_rows.csv](C:/Users/class/Documents/coding/shlib-shenbao-dataset-workflow/shenbao_textdata/preprocess/shenbao_constitution_text_stage1_appended_rows.csv) | 40,079 |
| Stage 2 | [shenbao_constitution_text_stage2_deduplicated_articles.csv](C:/Users/class/Documents/coding/shlib-shenbao-dataset-workflow/shenbao_textdata/preprocess/shenbao_constitution_text_stage2_deduplicated_articles.csv) | 33,513 |
| Stage 3 | [shenbao_constitution_text_stage3_preprocessed_articles.csv](C:/Users/class/Documents/coding/shlib-shenbao-dataset-workflow/shenbao_textdata/preprocess/shenbao_constitution_text_stage3_preprocessed_articles.csv) | 33,513 |

`dataset_label` 기본값은 `constitution`으로 설정했습니다. 다른 라벨로 만들고 싶으면 다음처럼 실행하면 됩니다.

```powershell
python .\shenbao_preprocess_combine.py --dataset-label constitution
```

입력 폴더를 명시하려면 다음처럼 실행할 수 있습니다.

```powershell
python .\shenbao_preprocess_combine.py --input-dir C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata
```

**반영한 지침**
요청한 사항은 다음과 같이 반영했습니다.

| 지침 | 반영 내용 |
|---|---|
| 파일명 | `shenbao_{dataset_label}_text_stage*.csv` 형식 사용 |
| `preprocess_indices` | `preprocess_indeces`가 아니라 `preprocess_indices`로 구현 |
| 대표 행 정보 | `representative_label`, `representative_item_index` 추가 |
| 충돌 유형 | `collision_type` 추가 |
| T/F 충돌 판정 | 기존 `collision` 열로 구현 |
| 대표 행 선택 | `text_raw` 정상 여부 우선 |
| 선택 사유 | `select_reason` 열 추가 |
| 선택 사유 값 | `1_no_error`, `2_text_exists`, `3_title_exists`, `4_long_text`, `5_small_index` |
| `[ERROR]` 행 | 삭제하지 않고 보수적으로 유지 |
| `short_text` 기준 | 3자 이하로 설정 |
| `SP_AD` | 제외하지 않고 유지 |
| `publish_exception=T` | 제외하지 않고 유지 |
| `topic` 병합 | 서로 다르면 `;`로 병합 |
| 메타데이터 제거 | `title_clean`, `text_clean` 모두에서 `其他紀元：` 이후 제거 |
| copyright 제거 | `title_clean`, `text_clean`에서 제거 |
| 저장 위치 | `shenbao_textdata\preprocess` 생성 후 저장 |

**검증 통계**
실행 결과는 다음과 같습니다.

| 항목 | 값 |
|---|---:|
| Stage 1 원본 병합 행 수 | 40,079 |
| Stage 2 중복 통합 후 기사 수 | 33,513 |
| Stage 3 전처리 후 기사 수 | 33,513 |
| `article_id` 기준 제거된 중복 행 수 | 6,566 |
| Stage 2 `article_id` 중복 | 0 |
| Stage 3 `article_id` 중복 | 0 |

`collision_type` 분포는 다음과 같습니다.

| collision_type | 건수 |
|---|---:|
| `single_source` | 27,806 |
| `all_exact` | 5,698 |
| `all_error` | 4 |
| `error_vs_normal` | 3 |
| `title_missing_vs_present` | 1 |
| `whitespace_only` | 1 |

`select_reason` 분포는 다음과 같습니다.

| select_reason | 건수 |
|---|---:|
| `1_no_error` | 3 |
| `3_title_exists` | 1 |
| `4_long_text` | 2 |
| `5_small_index` | 33,507 |

`text_exception_reason` 분포는 다음과 같습니다.

| text_exception_reason | 건수 |
|---|---:|
| 없음 | 31,383 |
| `metadata_only` | 2,061 |
| `short_text` | 49 |
| `error_text` | 20 |

`publish_exception_reason` 분포는 다음과 같습니다.

| publish_exception_reason | 건수 |
|---|---:|
| 없음 | 29,961 |
| `start_with_date` | 3,532 |
| `topic_only` | 20 |

**남은 선택사항**
필수적으로 더 결정해야 할 부분은 없습니다. 다만 후속 단계에서 선택할 수 있는 사항은 있습니다.

| 선택사항                   | 현재 처리                                                |
| ---------------------- | ---------------------------------------------------- |
| `error_text` 20건 수동 보완 | 현재는 삭제하지 않고 `text_exception=T`, `text_clean` 빈칸으로 유지 |
| `SP_AD` 제외 여부          | 현재는 유지, 분석용 corpus 생성 단계에서 제외 권장                     |
| `metadata_only` 제외 여부  | 현재는 유지, `text_clean` 빈칸 처리                           |
| `short_text` 제외 여부     | 현재는 유지, `text_exception=T`로 표시                       |
| 최종 분석용 corpus 생성       | 아직 별도 생성하지 않음                                        |

현재 산출물은 “통합 전처리 데이터”로는 사용할 수 있습니다. 다만 실제 텍스트마이닝용 corpus를 만들 때는 Stage 3 파일에서 `text_exception`, `qrynewstype`, `publish_exception_reason`, `collision_type` 등을 기준으로 분석 제외 조건을 별도로 적용하는 편이 안전합니다.