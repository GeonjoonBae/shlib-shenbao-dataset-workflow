---
주제: 전처리 결과물의 특성과 column별 분포 특징
AI 플랫폼 및 모델:
  - GPT-5.4
날짜: 2026-05-04
---

# 프롬프트
shenbao\shenbao_textdata\preprocess 경로 내 각 stage의 파일들이 규칙에 맞게 잘 만들어졌는지 검토하고, 각 데이터의 특성, 각 열 데이터의 대체적인 분포 특징을 상세히 정리해줘
# 답변
검토 대상:
- stage1
- stage2
- stage3

기준:
- 현재 `shenbao_textdata_preprocess_combine_ver2.py` 규칙
- UTF-8 기준 실제 산출 파일 재검토
- 헤더, 행 수, 인덱스, 정렬, 규칙 적용 결과, 주요 열 분포 확인

**총평**
- 세 파일 모두 현재 규칙에 맞게 잘 생성되어 있습니다.
- stage1 `17열`, stage2 `22열`, stage3 `26열` 모두 정확합니다.
- stage3는 현재 의도대로 `collision_columns` 헤더를 사용하고 있습니다.
- 구조적 오류는 보이지 않았습니다.
- 현재 데이터 특성상 `collision`, `select_reason` 등 일부 진단 열은 거의 변별력이 없는데, 이는 스크립트 문제가 아니라 원본 데이터가 매우 일관적이기 때문입니다.

**전체 규모**
- stage1: `40,079행`
- stage2: `33,513행`
- stage3: `33,513행`

중복 제거 결과:
- stage1 `40,079` -> stage2/3 `33,513`
- 제거된 중복 행: `6,566`
- 복수 source에서 수집된 고유 기사: `5,707건`

---

**stage1**
규칙 적합성:
- 헤더 17열 정확
- `stage1_index`가 `1..40079`로 연속 생성됨
- `content-box2`가 `content_box2`로 정규화됨
- `_raw` suffix 없음
- 4개 원본 CSV 단순 병합 목적에 부합

레이블 분포:
- `lixian`: `7,203`
- `xianfa`: `18,648`
- `xianzheng`: `9,906`
- `zhixian`: `4,322`

`qrynewstype` 분포:
- `SP`: `35,748`
- `SP_AD`: `4,158`
- `SP_FH`: `39`
- `SP_HK`: `134`

열별 분포 특징:
- `detail_url`: 전부 비결측
- `date`: 전부 비결측
- `issue_page`: 전부 비결측
- `special_column`: 비결측 `3,479` (`8.68%`)
  - 값은 사실상 `分類廣告`만 존재
- `h1`: 비결측 `39,945` (`99.67%`)
- `lv1_div`: 비결측 `40,038` (`99.90%`)
- `content_box2`: 비결측 `37,512` (`93.60%`)
- `era_year`: 전부 비결측
- `theme`: 비결측 `877` (`2.19%`)
- `category`: 전부 공란
- `collect_error`: 전부 공란
- `h1`와 `content_box2` 동시 결측: `0`

길이 분포:
- `list_title`: 중앙값 `19`, 3사분위수 `49`, 최대 `112`
- `publish_variant`: 중앙값 `2`, 사실상 매우 짧은 열
- `h1`: 중앙값 `14`, 3사분위수 `45`, 최대 `10,095`
- `lv1_div`: 중앙값 `3`, 3사분위수 `3`, 최대 `56`
- `content_box2`: 중앙값 `799`, 3사분위수 `1,795`, 최대 `322,522`

대표 값:
- `publish_variant`
	- `申報` `35,748`
	- `申報_香港版` `134`
	- `申報_漢口版` `39`
- `special_column`
	- `分類廣告` `3,479`
- `lv1_div`
	- `本報訊` `21,663`
	- `一` `936`
	- `續` `578`
	- `北京` `406`
	- `未完` `403`
	- `南京` `394`

해석:
- stage1은 원본 4개 수집 파일의 구조와 예외를 거의 그대로 보존한 병합본입니다.
- `SP`가 압도적 다수이고, `SP_AD`, `SP_FH`, `SP_HK`는 소수층입니다.
- `special_column`, `theme`, `category`는 희소 메타데이터입니다.
- 본문은 대체로 `content_box2`에 있지만, `h1`에 긴 텍스트가 말려 올라간 예외도 일부 존재합니다.

---

**stage2**
규칙 적합성:
- 헤더 22열 정확
- `article_id` 기준 dedup 정상
- `article_id` 전부 유일
- 원본 `label`, `page`, `item_index`, `list_title`는 제거되고 대표행 정보만 유지됨
- `collision_columns` 헤더 정상 생성

중복 그룹 크기:
- 1개 source만: `27,806`
- 2개 source: `4,887`
- 3개 source: `781`
- 4개 source: `39`

즉, 복수 source 기사 수는 `5,707건`입니다.

주요 분포:
- `qrynewstype`
	- `SP` `29,819`
	- `SP_AD` `3,532`
	- `SP_FH` `38`
	- `SP_HK` `124`
- `special_column` 비결측: `3,094` (`9.23%`)
- `theme` 비결측: `661` (`1.97%`)
- `category`: 전부 공란
- `collect_error`: 전부 공란

대표행 선택 결과:
- `select_reason`: 전부 `7_small_index`

이 의미:
- 현재 데이터에서는 동일 `article_id` 기사끼리
  - `collect_error`
  - `issue_page`
  - `theme`
  - `content_box2`
  - `h1`
  - `lv1_div`
기준에서 차이가 없어, 결국 가장 작은 `stage1_index`가 항상 대표행이 되었습니다.

collision 결과:
- `collision=F`: `33,513`
- `collision=T`: `0`
- `collision_columns` 비결측: `0`

이 의미:
- 동일 `article_id`끼리
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
  - `collect_error`
값 차이가 전혀 없었습니다.

대표 `source_labels` 조합:
- `xianfa` `14,379`
- `xianzheng` `6,454`
- `lixian` `4,394`
- `zhixian` `2,579`
- `xianfa;zhixian` `1,391`
- `lixian;xianzheng` `1,360`
- `xianfa;xianzheng` `1,258`

해석:
- stage2는 현재 데이터에서 사실상 “중복 제거 + provenance 유지” 역할을 수행합니다.
- collision이 전부 `F`인 것은 현재 원본 상태와 일치합니다.
- 따라서 통합 손실이나 비정상 대표행 선택은 보이지 않습니다.

---

**stage3**
규칙 적합성:
- 헤더 26열 정확
- `dataset_index`가 `1..33513`으로 연속 생성됨
- `detail_url` 제거 정상
- `era_year` 유지 + `chinese_era_year`, `japanese_era_year` 생성됨
- `analysis_text`, `analysis_text_rules` 생성 정상
- 정렬 위반 `0건`

정렬:
- `date` 오름차순
- `qrynewstype` 순서
- `issue_page` 숫자 오름차순
- 최종 tie-breaker `article_id`

실제 시작:
- `1872-08-20`, `SP`, `05`
실제 마지막:
- `1949-05-26`, `SP`, `02`

주요 분포:
- `publish_variant` 비결측: `29,981`
- `date`: 전부 비결측
- `issue_page`: 전부 비결측
- `special_column` 비결측: `3,094`
- `era_year`: 전부 비결측
- `chinese_era_year`: 전부 비결측
1

해석:
- 가장 흔한 경우는 `lv1_div=本報訊`만 제외하고 병합하는 유형
- 그다음은 아무 정제 없이 그대로 병합하는 유형
- `分類廣告`는 대부분 `h1`와 `本報訊`이 제외되어 사실상 `content_box2` 중심으로 `analysis_text`가 생성됨
- 괄호형 중복 정제는 총 `52건`으로 매우 희귀한 구조 예외 처리입니다

`era_year` 분할:
- 샘플 확인 결과 형식은 일관됩니다.
  - 예: `清同治11年 日明治5年`
  - `chinese_era_year = 清同治11年`
  - `japanese_era_year = 日明治5年`

---

**issue_page 결측 여부**
- 현재 `preprocess` 산출물 기준으로는 stage1, stage2, stage3 모두 `issue_page` 결측 행이 없습니다.
- 즉 현재 작업 디렉터리에 있는 실제 산출물에서는 `issue_page`가 전부 채워져 있습니다.

이 점은 중요합니다.
- 과거 원본 상태나 별도 점검 시점과는 다를 수 있지만,
- 지금 `preprocess` 폴더의 실제 파일 기준으로는 `0건`입니다.

---

**최종 판단**
- stage1: 병합본으로 정상
- stage2: dedup 및 provenance 유지 정상
- stage3: 분석용 최종본으로 정상
- 현재 산출물은 규칙 적합성과 데이터 일관성 모두 양호합니다.

핵심 데이터 특성만 다시 요약하면:
- 전체 `40,079`행이 `33,513`개의 고유 기사로 정리됨
- 동일 `article_id` 간 충돌은 현재 코퍼스에서 사실상 없음
- `SP`가 코퍼스의 중심층
- `分類廣告`는 약 `9%` 규모의 뚜렷한 하위 구조
- `theme`, `category`, `collect_error`는 매우 희소하거나 비어 있음
- `analysis_text`는 전 기사에 대해 안정적으로 생성됨
- 괄호형 중복 정제는 예외 처리 수준으로만 작동

원하면 다음 단계로
1. 이 결과를 문서용 서술 문단으로 압축하거나
2. `analysis_text_rules` 각 유형별 실제 기사 사례를 2-3건씩 뽑아 보여드리겠습니다.


# 작업 메모
- 

# 연결 문서 및 연결 이유
## 내부 연결
- 
## 외부 연결
- 