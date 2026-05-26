# 상하이도서관 《申報》 텍스트 데이터와 그 수집·전처리 절차
## Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collection and Preprocessing

<details> <summary><h3>데이터 인용 예시</h3></summary>
- Bae, Geonjoon. “Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing.” GitHub repository. https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow

- Bae, G., 2026. “Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing.” GitHub repository. Available at: https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow [Accessed XX April 20XX(방문 일자)].

- Bae, G. (2026). Text Data from the Shanghai Library *Shun Pao* Database and the Workflow for Collecting and Preprocessing. https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow

- 배건준, 「상하이도서관 《申報》 텍스트 데이터와 그 수집-전처리 절차」, GitHub 저장소, https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow (검색일 기입)

</details>

## README 목차
- [저장소 개요](#저장소-개요)
- [기준 스크립트](#기준-스크립트)
- [실행 환경](#실행-환경)
- [수집 스크립트 개요](#수집-스크립트-개요)
- [전처리 스크립트 개요](#전처리-스크립트-개요)
- [예시 데이터와 산출물 규모](#예시-데이터와-산출물-규모)
- [사용 방법](#사용-방법)
- [산출물 구조](#산출물-구조)
- [유의사항](#유의사항)

## 저장소 개요
`《申報》`는 1872년부터 1949년까지 발행된 중국 근현대사의 대표적 일간지이며, 정치사·사회사·문화사·경제사 연구 전반에서 중요한 사료로 활용된다. 이 저장소는 상하이도서관 `《申報》` 데이터베이스에서 특정 검색어 또는 특정 기간에 해당하는 기사 텍스트를 수집하고, 이를 하나의 연구용 기사 단위 데이터셋으로 전처리하는 전체 절차를 재현할 수 있도록 설계되었다.

## 기준 스크립트
현재 워크플로우의 주 스크립트는 아래 두 개다.

1. `collect_shenbao_textdata_chrome_ver3_1.py`
- 최신 수집 스크립트
- Google Chrome을 직접 열고, 로그인 완료 후 결과 목록 프레임을 탐지해 수집한다.
- 수집 결과는 16열 CSV로 저장된다.

2. `shenbao_textdata_preprocess_combine_ver2.py`
- 최신 전처리·통합 스크립트
- 여러 원본 수집 CSV를 병합하고, `article_id` 기준 대표 기사 행을 고른 뒤, 분석용 텍스트 `analysis_text`를 생성한다.

이전 버전 스크립트와 보조 스크립트는 참고용이다.

- 이전 버전 수집 스크립트: `collect_shenbao_textdata_chrome_ver2.py`, `collect_shenbao_textdata_chrome_ver3.py`: 
- 이전 버전 전처리 스크립트: `shenbao_textdata_preprocess_combine.py`
- 예외 행 식별 실험을 위한 보조 스크립트: `shenbao_textdata_exceptions.py`

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
├─ collect_shenbao_textdata_chrome_ver2.py
├─ collect_shenbao_textdata_chrome_ver3.py
├─ collect_shenbao_textdata_chrome_ver3_1.py
├─ shenbao_textdata_exceptions.py
├─ shenbao_textdata_preprocess_combine.py
├─ shenbao_textdata_preprocess_combine_ver2.py
├─ ai_coding_agent_dialogues/
│  ├─ 01_coding_1_상하이도서관 신보 데이터 크롤링 코드 작성.md
│  ├─ 01_coding_2_기사 페이지의 html 구조가 상이한 경우를 대비한 코드 수정.md
│  ├─ 02_preprocess_1_예외 데이터 식별.md
│  ├─ 02_preprocess_2_통합 csv 제작.md
│  ├─ 03_pipeline-revision_1_기존 코드의 fallback 기능으로 인한 오수집 개선.md
│  ├─ 03_pipeline-revision_2_lv1_div의 수집 로직 개선.md
│  ├─ 03_pipeline-revision_3_수집 구조 개선에 따른 전처리-통합 코드 수정.md
│  ├─ 10_data-profile_1_데이터 구조 및 필드별 충실도 검토.md
│  ├─ 10_data-profile_2_중복 개체 간 데이터 일치.md
│  ├─ ...
│  ├─ 10_data-profile_11_전처리 결과물의 특성과 column별 분포 특징.md
│  └─ 10_data-profile_12_분석용 constitutional 데이터셋의 시간 정보 관련 통계.md
└─ shenbao_textdata/
   ├─ (sample)shenbao_textdata_lixian_1to7203.csv
   ├─ (sample)shenbao_textdata_xianfa_1to18648.csv
   ├─ (sample)shenbao_textdata_xianzheng_1to9906.csv
   ├─ (sample)shenbao_textdata_zhixian_1to4322.csv
   └─ preprocess/
      ├─ (sample)shenbao_textdata_stage1_appended_rows_constitutional.csv
      ├─ (sample)shenbao_textdata_stage2_deduplicated_articles_constitutional.csv
      └─ (sample)shenbao_textdata_stage3_preprocessed_articles_constitutional.csv
```

## 수집 스크립트 개요
#### `collect_shenbao_textdata_chrome_ver3_1.py`
상하이도서관 `《申報》` 데이터베이스 검색 결과를 대상으로 기사 텍스트를 수집하는 스크립트다.

- 시작 URL 기본값: `https://z.library.sh.cn/http/80/77/30/1/10/yitlink/`
- 기본 출력 경로: 스크립트 기준 `./shenbao/shenbao_textdata`
- Chrome 기본 탐색 경로:
  - `C:\Program Files\Google\Chrome\Application\chrome.exe`
  - `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
- 결과 목록과 상세 페이지는 프레임을 포함한 현재 브라우저 컨텍스트 전체에서 탐지한다.
- 로그인 세션이 `passport.library.sh.cn`로 되돌아가면 `SessionExpiredError`로 감지하고 즉시 저장 후 종료한다.

수집 CSV의 열 구조는 아래 16개다.

```text
label
page
item_index
list_title
detail_url
publish_variant
date
issue_page
special_column
h1
lv1_div
content-box2
era_year
category
theme
collect_error
```

각 열의 의미는 다음과 같다.

- `label`: 검색어 또는 수집 단위를 식별하는 사용자 레이블
- `page`: 결과 목록 페이지 번호
- `item_index`: 전체 결과에서의 기사 번호
- `list_title`: 목록 화면 제목
- `detail_url`: 기사 상세 URL
- `publish_variant`: 상세 페이지 좌측 상단 발행 정보 문자열
- `date`: 상세 페이지에서 추출한 날짜
- `issue_page`: 판차 또는 면수 정보
- `special_column`: 특집면 또는 분류 광고 등 별도 표지 정보
- `h1`: 기사 제목 영역
- `lv1_div`: 제목 직후 보조 표지 영역
- `content-box2`: 본문 영역
- `era_year`: 후행 메타데이터에 포함된 연호 문자열
- `category`: 후행 메타데이터의 범주 정보
- `theme`: 후행 메타데이터의 주제 정보
- `collect_error`: 수집 실패 시 오류 원인과 URL 정보를 기록하는 열

### 수집 절차
1. 터미널에서 스크립트를 실행한다.
2. `--label`, `--resume-file`, `--resume-latest`가 없으면 레이블을 직접 입력한다.
3. 스크립트가 Chrome을 열고 시작 URL로 이동한다.
4. 사용자가 상하이도서관 계정으로 로그인한다.
5. 사용자가 원하는 검색어 또는 기간 조건으로 결과 목록 첫 페이지를 준비한다.
6. 사용자가 한 페이지 표시 건수를 `100`으로 바꾼다.
7. 터미널에서 Enter를 누르면 스크립트가 결과 프레임을 탐지하고 자동 순회를 시작한다.
8. 각 기사마다 목록 제목을 읽고, 링크를 클릭하고, 상세 페이지 필드를 추출한 뒤, 목록으로 복귀한다.
9. `--save-every` 간격마다 중간 저장한다.
10. 세션 만료, 페이지 전환 실패, 또는 마지막 페이지 도달 시 현재까지 결과를 저장하고 종료한다.

### 수집 스크립트 주요 옵션(CLI)
```text
--start-url                시작 URL 지정
--chrome-path              Chrome 실행 파일 경로 직접 지정
--output-dir               출력 디렉터리 지정
--label                    수집 레이블 지정
--start-page               현재 열려 있는 결과 화면의 페이지 번호 지정
--max-pages                최대 수집 페이지 수 제한
--wait-seconds             기본 대기 시간
--extended-wait-seconds    확장 대기 시간
--detail-timeout-seconds   이전 버전 호환용 옵션
--save-every               N건마다 중간 저장
--resume-file              특정 결과 파일에서 재개
--resume-latest            최신 결과 파일에서 재개
```

#### 재개 옵션
- `--label`만 주더라도 동일 레이블의 기존 결과 파일이 있으면 자동 재개 대상으로 삼을 수 있다.
- `--resume-latest`는 출력 경로에서 가장 최근 수정된 파일을 찾는다.
- `--resume-file`은 특정 파일을 직접 지정한다.
- 재개 시에는 마지막으로 저장된 행을 다시 한 번 재생하면서 이어서 수집하므로, 직전 저장 지점의 마지막 항목은 중복 없이 안정적으로 이어지는 구조다.

## 전처리 스크립트 개요
### `shenbao_textdata_preprocess_combine_ver2.py`
여러 원본 CSV를 하나의 통합 데이터셋으로 정리하는 3단계 전처리 스크립트다.

1. Stage 1: 원본 수집 CSV 단순 병합
2. Stage 2: `article_id` 기준 대표 기사 선정 및 중복 정보 통합
3. Stage 3: 정렬, 연호 분리, 분석용 텍스트 생성

입력 파일 탐색 규칙은 아래와 같다.

- 파일 패턴: `shenbao_textdata_*_1to*.csv`
- 아래 문자열이 파일명에 포함된 경우 원본 후보에서 제외한다.
  - `stage1`, `stage2`, `stage3`
  - `preprocess`, `deduplicated`, `preprocessed`, `appended`
  - `combined`, `exception`, `marker`, `inpageordertest`
- 입력 디렉터리를 주지 않으면 `shenbao/shenbao_textdata`, `shenbao_textdata`, 저장소 하위 `shenbao_textdata` 등 여러 후보를 순서대로 탐색한다.

전처리 스크립트는 큰 CSV 필드를 안전하게 읽기 위해 Windows 환경을 고려한 `csv.field_size_limit` fallback 루프를 포함한다. 또한 UTF-8을 기본으로 사용하고, 헤더 BOM이 감지되면 `utf-8-sig`로 다시 읽는다.

### Stage 1: 단순 병합
Stage 1 출력 열은 아래 17개다.

```text
stage1_index
label
page
item_index
list_title
detail_url
publish_variant
date
issue_page
special_column
h1
lv1_div
content_box2
era_year
category
theme
collect_error
```

설명:

- Stage 1은 여러 원본 CSV를 행 단위로 이어 붙인다.
- 원본 수집 CSV의 `content-box2` 열은 Stage 1부터 `content_box2`로 정규화된다.
- 각 행에는 병합 순서를 나타내는 `stage1_index`가 새로 추가된다.

### Stage 2: `article_id` 기준 대표 기사 선정 후 중복 제거
Stage 2 출력 열은 아래 22개다.

```text
dataset_label
source_labels
stage1_indices
representative_label
representative_item_index
select_reason
article_id
qrynewstype
detail_url
publish_variant
date
issue_page
special_column
h1
lv1_div
content_box2
era_year
category
theme
collect_error
collision
collision_columns
```

Stage 2의 핵심 규칙은 다음과 같다.

- `detail_url`에서 `article_id`와 `qrynewstype`를 추출한다.
- `article_id`가 없는 행은 중복 제거를 수행할 수 없으므로 예외로 처리한다.
- 같은 `article_id`를 가진 행들 중 대표행은 다음 우선순위로 선정한다.
  1. `collect_error`가 비어 있는 행 우선
  2. `issue_page`가 있는 행 우선
  3. `theme`가 더 긴 행 우선
  4. `content_box2`가 더 긴 행 우선
  5. `h1`이 더 긴 행 우선
  6. `lv1_div`가 더 긴 행 우선
  7. 위 기준으로도 동률이면 `stage1_index`가 가장 작은 행 선택
- 실제로 대표행을 좁힌 최초 기준은 `select_reason`에 기록한다.
- 중복 묶음 안에서 차이가 난 열이 있으면 `collision=T`, 차이가 난 열 이름은 `collision_columns`에 세미콜론으로 기록한다.

### Stage 3: 정렬, 연호 분리, 분석용 텍스트 생성
Stage 3 출력 열은 아래 26개다.

```text
dataset_label
dataset_index
source_labels
stage1_indices
representative_label
representative_item_index
select_reason
article_id
qrynewstype
publish_variant
date
issue_page
special_column
era_year
chinese_era_year
japanese_era_year
category
theme
collect_error
collision
collision_columns
h1
lv1_div
content_box2
analysis_text
analysis_text_rules
```

Stage 3의 처리 내용은 아래와 같다.

- 정렬 우선순위:
  1. `date` 오름차순
  2. `qrynewstype` 우선순위 `SP -> SP_AD -> SP_FH -> SP_HK`
  3. `issue_page` 오름차순
  4. `article_id` 오름차순
- 정렬 결과에 따라 `dataset_index`를 새로 부여한다.
- `era_year`에서 중국 연호와 일본 연호를 분리해 `chinese_era_year`, `japanese_era_year`를 생성한다.
- `h1`, `lv1_div`, `content_box2`를 바탕으로 분석용 본문 `analysis_text`를 생성한다.
- 각 행에서 어떤 결합 규칙을 적용했는지는 `analysis_text_rules`에 기록한다.

#### `analysis_text` 생성 규칙

1. `1_drop_h1_for_classified_ad`
- `special_column`이 `分類廣告`일 때 `h1`을 제외한다.

2. `2_drop_benbaoxun`
- `lv1_div`가 `本報訊`일 때 `lv1_div`를 제외한다.

3. `3_bracket_dedup`
- `h1`과 `content_box2` 선두에 중복 구간이 있고, 그 경계 주변에 `〔`가 나타나는 경우 `content_box2`의 중복 선두를 제거한다.

4. `4_delete_lv1_marker`
- `3_bracket_dedup` 이후 `content_box2`가 `〔{lv1_div}〕` 또는 `（{lv1_div}）` 형태로 시작하면 해당 표지를 제거한다.

5. `5_plain_merge`
- 위 조건에 해당하지 않으면 `h1`, `lv1_div`, `content_box2`를 공백으로 이어 붙인다.

## 예시 데이터와 산출물 규모
예시 데이터의 실제 수집·전처리 규모는 아래와 같다.

| 구분 | 파일명 | 데이터 성격 | 행 수 | 열 수 | 시기 범위 |
| --- | --- | --- | ---: | ---: | --- |
| 원 수집 데이터 | `shenbao_textdata_zhixian_1to4322.csv` | 검색어 `制憲` | 4,322 | 16 | 1872-08-20 - 1949-05-26 |
| 원 수집 데이터 | `shenbao_textdata_xianzheng_1to9906.csv` | 검색어 `憲政` | 9,906 | 16 | 1875-08-31 - 1949-05-23 |
| 원 수집 데이터 | `shenbao_textdata_xianfa_1to18648.csv` | 검색어 `憲法` | 18,648 | 16 | 1873-09-02 - 1949-05-26 |
| 원 수집 데이터 | `shenbao_textdata_lixian_1to7203.csv` | 검색어 `立憲` | 7,203 | 16 | 1877-06-06 - 1949-05-08 |
| 전처리 1단계 | `shenbao_textdata_stage1_appended_rows_constitutional.csv` | 단순 병합 | 40,079 | 17 | 1872-08-20 - 1949-05-26 |
| 전처리 2단계 | `shenbao_textdata_stage2_deduplicated_articles_constitutional.csv` | 중복 제거 | 33,513 | 22 | 1872-08-20 - 1949-05-26 |
| 전처리 3단계 | `shenbao_textdata_stage3_preprocessed_articles_constitutional.csv` | 분석용 데이터 | 33,513 | 26 | 1872-08-20 - 1949-05-26 |

※ 저장소는 수집 및 전처리 데이터 전체가 아닌  `(sample)` 접두부가 붙은 샘플 데이터만을 제공한다.

## 사용 방법
### 1. 저장소 복제
```powershell
git clone https://github.com/GeonjoonBae/shlib-shenbao-dataset-workflow.git
cd shlib-shenbao-dataset-workflow
```

### 2. 필수 패키지 설치
```powershell
pip install playwright
```

Google Chrome이 기본 경로가 아닌 곳에 설치되어 있으면 `--chrome-path`를 직접 지정해야 한다.

### 3. 수집 스크립트 실행
```powershell
python .\collect_shenbao_textdata_chrome_ver3_1.py --label xianfa --save-every 20 --output-dir .\shenbao_textdata
```

부분 수집 예시:
```powershell
python .\collect_shenbao_textdata_chrome_ver3_1.py --label xianfa --max-pages 3 --output-dir .\shenbao_textdata
```

작업 재개 예시:
```powershell
python .\collect_shenbao_textdata_chrome_ver3_1.py --label xianfa --resume-latest --save-every 20 --output-dir .\shenbao_textdata
python .\collect_shenbao_textdata_chrome_ver3_1.py --resume-file .\shenbao_textdata\shenbao_textdata_xianfa_1to18648.csv --output-dir .\shenbao_textdata
```

### 4. 전처리 스크립트 실행
```powershell
python .\shenbao_textdata_preprocess_combine_ver2.py --input-dir .\shenbao_textdata --dataset-label constitutional
```

`--dataset-label`을 생략하면 터미널에서 값을 직접 입력받는다.

### 5. 산출물 확인
전처리 완료 후 기본적으로 아래 세 파일이 만들어진다.

```text
shenbao_textdata_stage1_appended_rows_{dataset_label}.csv
shenbao_textdata_stage2_deduplicated_articles_{dataset_label}.csv
shenbao_textdata_stage3_preprocessed_articles_{dataset_label}.csv
```

## 유의사항
- 상하이도서관 `《申報》` 데이터베이스 접근에는 상하이도서관 계정 로그인이 필요하다.
- 로그인 이후에도 CAPTCHA, OAuth, 동적 프레임 전환이 존재하므로, 완전 자동 수집이 아니라 반자동 수집을 시행한다.
- 로그인 세션은 대체로 2시간 내외로 유지된다.
- 1회 실행으로 수집 가능한 규모는 대체로 2,000건 안팎이다.
- 검색어는 번체 중문 입력을 요구한다. 간체 중문 입력 시 결과가 출력되지 않는다.
- 데이터베이스의 기사 개체 분할 기준이 일관적이지 않으므로, 한 행이 반드시 하나의 완결된 기사와 정확히 대응한다고 가정할 수는 없다.
- `qrynewstype=SP_AD`는 광고성 자료 식별에 유용하지만 광고 전체를 완전히 포괄하지는 않는다.
- `analysis_text`는 구조적 예외를 줄이기 위한 규칙 기반 결합 결과이며, 원문 영인 이미지 상의 텍스트와 1:1 완전 일치를 보장하지는 않는다.
- `《申報》` 텍스트는 번체 중문이며 시기별 문체 차이도 크므로, 후속 자연어처리나 계량 분석에는 별도의 언어학적 검토가 필요하다.
