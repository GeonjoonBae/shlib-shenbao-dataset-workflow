# 상하이도서관 《申報》 텍스트 데이터와 그 수집-전처리 절차
## Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing

<details> <summary><h3>데이터 인용 예시</h3></summary>
- Bae, Geonjoon. “Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing.” GitHub repository. https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow

- Bae, G., 2026. “Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing.” GitHub repository. Available at: https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow [Accessed XX April 20XX(방문 일자)].

- Bae, G. (2026). Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing. https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow

- 배건준, 「상하이도서관 《申報》 텍스트 데이터와 그 수집-전처리 절차」, GitHub 저장소, https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow (검색일 기입)

</details>

## README 목차
- [저장소 개요](#저장소-개요)
- [실행 환경](#실행-환경)
- [저장소 구성](#저장소-구성)
- [코드 소개](#코드-소개)
- [자료 소개](#자료-소개)
- [수집 절차](#수집-절차)
- [전처리 절차](#전처리-절차)
- [사용 방법](#사용-방법)
- [산출물 구조](#산출물-구조)
- [유의사항](#유의사항)

## 저장소 개요
`《申報》`는 1872년부터 1949년까지 발행된 중국 근현대사의 대표적 일간지이며, 정치사·사회사·문화사·경제사 연구 전반에서 중요한 사료로 활용된다. 이 저장소는 상하이도서관 `《申報》` 데이터베이스에서 특정 검색어 또는 특정 기간에 해당하는 기사 텍스트를 수집하고, 이를 하나의 연구용 기사 단위 데이터셋으로 전처리하는 전체 절차를 재현할 수 있도록 설계되었다.

이 워크플로우는 다음 두 단계로 이루어진다.

1. `crawl_shenbao_text_chrome.py`
   - 상하이도서관 로그인 이후 사용자가 직접 검색 결과 목록을 준비하면, 크롬 브라우저를 제어해 기사 목록과 상세 페이지를 순차적으로 순회하며 텍스트 데이터를 수집한다.
2. `shenbao_textdata_preprocess_combine.py`
   - 여러 수집 기준별 원본 CSV를 병합하고, `detail_url`의 기사 식별자(`article_id`)를 기준으로 중복 행을 통합한 뒤, 발행 정보와 후행 메타데이터를 분리하고 제목/본문 문자열을 정제한다.

본 작업의 코드 작성과 수정 과정에는 OpenAI Codex 기반 GPT-5.4 코딩 에이전트를 활용했으며, 사용자가 요구사항·오류 메시지·HTML 구조 예시를 제시하고 이에 따라 코드를 반복 수정하는 Human-in-the-Loop 방식으로 진행되었다. 저장소는 AI Coding Agent 대화 기록, 스크립트, 수집 및 전처리 데이터 샘플을 제공한다.

## 실행 환경
- 운영체제: Windows 로컬 환경
- 편집 도구: Visual Studio Code 1.115.0
- 구현 언어: Python 3.11.9
- 실행 및 검증: PowerShell
- 브라우저 자동화: Playwright for Python 1.58.0
- 브라우저: Google Chrome

## 저장소 구성 
```text
shlib-shenbao-dataset-workflow/
├─ README.md
├─ crawl_shenbao_text_chrome.py
├─ shenbao_textdata_exceptions.py
├─ shenbao_textdata_preprocess_combine.py
├─ ai_coding_agent_dialogues/
│  ├─ 1_coding_1_상하이도서관 신보 데이터 크롤링 코드 작성.md
│  ├─ 1_coding_2_기사 페이지의 html 구조가 상이한 경우를 대비한 코드 수정.md
│  ├─ 2_preprocess_1_예외 데이터 식별.md
│  └─ 2_preprocess_2_통합 csv 제작.md
└─ shenbao_textdata/
   ├─ (sample)shenbao_textdata_lixian_1to7203.csv
   ├─ (sample)shenbao_textdata_xianfa_1to18648.csv
   ├─ (sample)shenbao_textdata_xianzheng_1to9906.csv
   ├─ (sample)shenbao_textdata_zhixian_1to4322.csv
   └─ preprocess/
      ├─ (sample)shenbao_textdata_stage1_appended_rows_constitution.csv
      ├─ (sample)shenbao_textdata_stage2_deduplicated_articles_constitution.csv
      └─ (sample)shenbao_textdata_stage3_preprocessed_articles_constitution.csv
```

## 코드 소개
### 1. `crawl_shenbao_text_chrome.py`
상하이도서관 `《申報》` 데이터베이스 검색 결과를 대상으로 기사 텍스트를 수집하는 스크립트다.

주요 기능:
- 수동 로그인 이후 자동 수집
- 수집 기준 레이블(`label`) 기반 파일 저장
- 중간 저장(`--save-every`)
- 작업 재개(`--label`, `--resume-latest`, `--resume-file`)
- 최대 수집 페이지 제한(`--max-pages`)
- CSV 필드 길이 제한 확장(`csv.field_size_limit(1_000_000)`)

출력 파일 형식:
```text
shenbao_textdata_{label}_{start_index}to{end_index}.csv
```

### 2. `shenbao_textdata_exceptions.py`
원본 수집 CSV에서 예외 행을 식별해 별도 CSV로 정리하는 보조 스크립트다. `publish`, `detail_url`, `text` 세 열을 기준으로 예외 여부와 사유를 판정한다. 이 스크립트는 `2_preprocess_1_예외 데이터 식별.md`의 대화 내용을 바탕으로 작성되었다. 해당 코드로 작성된 예외 데이터는 3. `shenbao_textdata_preprocess_combine.py`의 전처리 규칙을 구체화하는 참고 자료로 활용되었다. 실제 워크플로우에서는 사용하지 않는다.

주요 기능:
- 네 원본 CSV 자동 탐색
- `publish` 예외 판정(`topic_only`, `start_with_date`)
- `detail_url` 예외 판정(`sp_ad`, `no_detail_url`)
- `text` 예외 판정(`error_text`, `metadata_only`, `short_text`)
- 예외 행만 별도 CSV로 저장

출력 파일 형식:
```text
shenbao_textdata_{label}_exception_rows.csv
```

### 3. `shenbao_textdata_preprocess_combine.py`
여러 원본 CSV를 하나의 통합 데이터셋으로 정리하는 전처리 스크립트다.

주요 기능:
- 여러 수집 결과 파일 단순 병합
- `detail_url`에서 `article_id`, `qrynewstype` 추출
- `article_id` 기준 중복 기사 통합
- 대표행 선택 사유 기록
- 발행 정보, 기년, 주제, 범주 등 메타데이터 분리
- 제목/본문 정제
- 연구용 기사 단위 CSV 3종 산출

출력 파일 형식:
```text
shenbao_textdata_stage1_appended_rows_{dataset_label}.csv
shenbao_textdata_stage2_deduplicated_articles_{dataset_label}.csv
shenbao_textdata_stage3_preprocessed_articles_{dataset_label}.csv
```

## 자료 소개
### 1. 원본 수집 데이터
원고에서 실제 수집한 전체 결과는 다음 네 묶음이다.

- `shenbao_textdata_lixian_1to7203.csv`
- `shenbao_textdata_xianfa_1to18648.csv`
- `shenbao_textdata_xianzheng_1to9906.csv`
- `shenbao_textdata_zhixian_1to4322.csv`

이 네 파일은 각각 `立憲`, `憲法`, `憲政`, `制憲` 검색 결과를 수집한 데이터이며, 전체 행 수는 40,079건이다. 저장소에는 재배포 및 용량 문제를 고려해 전체 원본 대신 `(sample)` 접두부가 붙은 샘플 CSV만 포함했다.

원본 CSV의 기본 열 구조는 다음과 같다.

```text
label, page, item_index, list_title, publish, detail_url, title, text
```

각 열의 의미:
- `label`: 검색어별 수집 단위 식별값
- `page`: 검색 결과 목록 페이지 번호
- `item_index`: 검색 결과 전체에서의 기사 일련번호
- `list_title`: 목록 페이지에 표시된 기사 제목
- `publish`: 상세 페이지 상단의 발행 정보 문자열
- `detail_url`: 상세 페이지 URL
- `title`: 상세 페이지 `h1`에서 확보한 제목
- `text`: 상세 페이지 본문 문자열

### 2. 전처리 결과 데이터
저장소에는 `constitution` 데이터셋에 대한 단계별 샘플 결과도 포함되어 있다.

- `stage1`: 여러 원본 CSV를 단순 병합한 행 단위 데이터
- `stage2`: `article_id` 기준으로 중복 통합한 기사 단위 데이터
- `stage3`: 메타데이터 분리와 문자열 정제를 수행한 최종 연구용 데이터

### 3. AI 코딩 에이전트 대화 기록
`ai_coding_agent_dialogues/` 폴더에는 이 저장소의 주요 스크립트가 작성·수정되는 과정에서 AI 코딩 에이전트와 주고받은 마크다운 대화 기록 4종을 수록했다.

- `1_coding_1_상하이도서관 신보 데이터 크롤링 코드 작성.md`: 수집 스크립트의 초기 설계와 반자동 크롤링 흐름 정리
- `1_coding_2_기사 페이지의 html 구조가 상이한 경우를 대비한 코드 수정.md`: 상세 페이지 HTML 구조 예외 대응, 필드 구조 조정, 재개 로직 및 수집 안정화
- `2_preprocess_1_예외 데이터 식별.md`: 원본 CSV의 예외 행 검토와 `shenbao_textdata_exceptions.py` 작성
- `2_preprocess_2_통합 csv 제작.md`: 예외 검토 결과를 전제로 한 통합 전처리 스크립트 설계와 `stage1`-`stage2`-`stage3` 산출물 구조 확정

이 문서들은 코드와 데이터가 만들어진 과정을 보여주는 작업 기록이다. 관련 내용을 한 문서에 정리하는 것을 원칙으로 했기 때문에, 문서 번호가 대화 순서를 의미하지는 않는다. 실제 대화 순서는 대체로 `1_coding_1`->`2_preprocess_1`->`1_coding_2`->`2_preprocess_2`이며, 이는 `2_preprocess_1` 대화를 통해 예외 데이터 추출 스크립트를 작성하던 중 기존 수집 스크립트의 오류 발생율이 다소 높아 수동 보완 부담이 커지는 것을 개선하고자 `1_coding_2` 대화가 시작되었기 때문이다. 단, 문서 내 동일 최상위 헤더(#)내의 순서(`프롬프트 1-1` -> `프롬프트 1-2` -> ...)는 실제 대화 순서와 동일하다. 

## 수집 절차
수집 스크립트의 기본 흐름은 다음과 같다.

1. 사용자가 터미널에서 `crawl_shenbao_text_chrome.py`를 실행한다.
2. 스크립트가 레이블 입력을 요구하거나, 명령어로 전달된 레이블을 사용한다.
3. 스크립트가 Chrome을 열고 상하이도서관 `《申報》` 데이터베이스 로그인 페이지로 이동한다.
4. 사용자가 직접 로그인한 뒤, 원하는 검색어 또는 기간 조건으로 결과 목록 첫 페이지를 연다.
5. 사용자가 한 페이지당 결과 수를 `100`으로 설정한다.
6. 터미널로 돌아와 Enter 키를 입력하면, 스크립트가 목록 페이지와 상세 페이지를 순차적으로 이동하며 기사 정보를 수집한다.
7. 일정 건수마다 CSV를 저장하고, 오류나 세션 종료가 발생하면 현재까지의 결과를 저장한 뒤 종료한다.
8. 필요하면 기존 CSV를 기준으로 작업을 재개한다.

이 워크플로우는 사이트가 OAuth 로그인, CAPTCHA, 동적 프레임 전환을 사용하기 때문에 완전 자동 방식이 아니라 반자동 방식으로 설계되었다.

## 전처리 절차
전처리 스크립트는 3단계로 구성된다.

### 1단계. 원본 CSV 병합
- 여러 원본 `shenbao_textdata_*.csv` 파일을 하나로 합친다.
- 원본 열 이름 뒤에 `_raw`를 붙여 보존한다.
- `preprocess_index`를 추가한다.

생성 파일:
```text
shenbao_textdata_stage1_appended_rows_{dataset_label}.csv
```

### 2단계. 중복 기사 통합
- `detail_url_raw`에서 `article_id`와 `qrynewstype`를 추출한다.
- `article_id` 기준으로 중복 행을 묶는다.
- 대표행은 다음 우선순위에 따라 선택한다.
  - `[ERROR]`가 아닌 `text_raw`
  - `text_raw` 존재
  - `title_raw` 존재
  - 더 긴 `text_raw`
  - 더 작은 `preprocess_index`
- 선택 사유는 `select_reason`에 기록한다.
- 중복 충돌 여부와 유형을 `collision`, `collision_type`에 기록한다.

생성 파일:
```text
shenbao_textdata_stage2_deduplicated_articles_{dataset_label}.csv
```

### 3단계. 메타데이터 분리와 문자열 정제
- `publish_raw`에서 발행 정보 분리
  - `publish_variant`
  - `publish_date`
  - `page_issue`
  - `publish_tail`
- 제목/본문 후행 메타데이터 분리
  - `topic`
  - `chinese_era_year`
  - `japanese_era_year`
  - `category`
  - `metadata_source`
- 제목 정제
  - `title_clean`
  - `title_exist`
  - `title_source`
- 본문 정제
  - `text_clean`
  - `text_exception`
  - `text_exception_reason`

생성 파일:
```text
shenbao_textdata_stage3_preprocessed_articles_{dataset_label}.csv
```

## 사용 방법
### 1. 저장소 복제
```powershell
git clone https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow.git
cd shlib-shenbao-dataset-workflow
```

### 2. 필수 패키지 설치
수집 스크립트에는 Playwright가 필요하다.

```powershell
pip install playwright
```

전처리 스크립트는 Python 표준 라이브러리만 사용한다.

### 3. 수집 스크립트 실행
```powershell
python crawl_shenbao_text_chrome.py --label xianfa --save-every 20 --output-dir .\shenbao_textdata
```

작업 재개 예시:
```powershell
python crawl_shenbao_text_chrome.py --label xianfa --resume-latest --save-every 20 --output-dir .\shenbao_textdata
python crawl_shenbao_text_chrome.py --resume-file .\shenbao_textdata\shenbao_textdata_xianfa_1to18648.csv --output-dir .\shenbao_textdata
```

`crawl_shenbao_text_chrome.py`의 기본 출력 경로는 스크립트 기준 `.\shenbao\shenbao_textdata`이지만, 이 저장소에 포함된 샘플 데이터 폴더 구조에 맞추려면 위 예시처럼 `--output-dir .\shenbao_textdata`를 명시하는 편이 편리하다.

### 4. 전처리 스크립트 실행
```powershell
python shenbao_textdata_preprocess_combine.py --input-dir .\shenbao_textdata --dataset-label constitution
```

`--dataset-label`을 생략하면 터미널에서 값을 입력받는다.

## 산출물 구조
### 1. 원본 수집 CSV
```text
label,page,item_index,list_title,publish,detail_url,title,text
```

예시:
```text
lixian,1,1,1. 制憲議會批準憲草 西德設雛型政府 為德國統一政府樹立基礎,申報 日期：1949-05-08 版次/卷期：02 版 路透社西德波恩城六日電,https://...,制憲議會批準憲草 西德設雛型政府 為德國統一政府樹立基礎,德國政治家已於今日...
```

### 2. Stage 1
```text
preprocess_index,label_raw,page_raw,item_index_raw,list_title_raw,publish_raw,detail_url_raw,title_raw,text_raw
```

### 3. Stage 2
```text
dataset_label,source_labels,preprocess_indices,representative_label,representative_item_index,select_reason,article_id,qrynewstype,label_raw,page_raw,item_index_raw,list_title_raw,publish_raw,detail_url_raw,title_raw,text_raw,collision,collision_type
```

### 4. Stage 3
```text
dataset_label,source_labels,preprocess_indices,representative_label,representative_item_index,select_reason,article_id,qrynewstype,publish_variant,publish_date,page_issue,publish_tail,publish_exception,publish_exception_reason,topic,chinese_era_year,japanese_era_year,category,metadata_source,title_clean,title_exist,title_source,text_clean,text_exception,text_exception_reason,collision,collision_type
```

## 유의사항
- 상하이도서관 `《申報》` 데이터베이스 접근에는 상하이도서관 계정 로그인이 필요하다.
- 로그인 이후에도 CAPTCHA와 동적 프레임 전환이 존재하므로, 수집 스크립트는 반자동 방식으로 동작한다.
- 검색어는 번체 중문으로 입력해야 한다. 간체 중문으로는 결과가 나오지 않는다.
- 로그인 세션은 실제 운용 시 약 2시간 내외로 유지되었으며, 1회 실행으로 수집 가능한 기사 수는 대체로 2,000건 안팎이었다.
- 데이터베이스 내 기사 개체 분할 기준이 항상 일관된 것은 아니므로, 한 행이 반드시 하나의 완결된 기사와 정확히 대응한다고 가정할 수는 없다.
- `qrynewstype=SP_AD`는 광고성 자료 식별에 유용하지만, 광고 전체를 완전히 포괄하지는 않는다.
- 저장소에는 전체 데이터가 아니라 샘플 데이터만 포함되어 있다.
- `《申報》` 텍스트는 번체 중문이며, 시대별 문체 차이도 크므로 후속 자연어처리 적용 시 별도의 언어학적 검토가 필요하다.
