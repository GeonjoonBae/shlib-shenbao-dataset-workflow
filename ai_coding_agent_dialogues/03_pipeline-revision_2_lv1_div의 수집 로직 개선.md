---
주제: lv1_div의 수집 로직 개선
AI 플랫폼 및 모델:
  - GPT-5.4
날짜: 2026-04-30
---
# 작업 메모
- 10_data-profile_2_중복 개체 간 데이터 일치 검토 과정에서 일부 동일 기사 간의 lv1_div에 차이가 있는 것을 발견, 검색어 문자열이 빠져 발생한 것으로 추정하여 이를 개선하였음. 개선 결과는 `crawl_shenbao_text_chrome_ver3_1.py` 로 저장
# 프롬프트 1
현재 `..._ver3`코드에서 문제가 하나 발견됐어. 다른 부분은 그대로 두고 이 문제만 수정해서 `..._ver3_1.py`로 저장해줘.

lv1_div를 수집할 때, h1 아래 첫번째 div에 있는 문자열을 가지고 오도록 했는데, 검색 결과에서 검색어를 노란색과 초록색으로 표시하는 span style이 적용된 문자열은 가지고 오지 않는 사례가 발견되었어. 예를 들면 立憲의 검색결과로 나온 한 기사의 lv1_div가 `中華民國憲法芻議`인데, 憲法의 검색결과로 나온 같은 id를 갖는 기사의 해당 부분에 대해 스크립트는 `中華民國 芻議`로만 수집했어. 데이터베이스에서 확인해보니 원 소스에서는  `中華民國憲法芻議`가 문제 없이 출력되고 있어. 아래 html 요소를 보면, 이것은 한 div 구획 내에서 span style 적용 문자열까지 가지고 오도록 설정되어 있지 않아 생긴 문제로 보여. 우선 이러한 문제를 해결하기 위한 방안을 설명해줘

```html
  <div>中華民國
  <span style="color:yellow;background-color:green">憲</span>
  <span style="color:yellow;background-color:green">法</span>
  芻議
  <div>
```

# 답변 1
원인은 명확합니다.

현재 `ver3` 코드에서 `lv1_div`는 crawl_shenbao_text_chrome_ver3.py:470 부근의 `directText()`로 읽고 있고, 실제 적용은 crawl_shenbao_text_chrome_ver3.py:511~518에서 이뤄집니다.

현재 방식:
- `h1` 다음 첫 번째 `div`를 찾음
- 그 `div`의 `childNodes` 중 `TEXT_NODE`만 이어붙임
- 따라서 `span` 안에 들어간 글자는 버림

그래서 아래 구조에서

```html
<div>
  中華民國
  <span style="color:yellow;background-color:green">憲</span>
  <span style="color:yellow;background-color:green">法</span>
  芻議
  <div>...</div>
</div>
```

현재 로직은
- `中華民國`
- `芻議`

만 읽고,
- `span` 안의 `憲`, `法`
는 빠뜨립니다.

그래서 `中華民國憲法芻議`가 아니라 `中華民國 芻議`로 수집된 것입니다.

중요한 점은, 이 문제를 고치려고 **그냥 `sibling.textContent`나 `sibling.innerText`로 바꾸면 안 된다**는 것입니다.  
그렇게 하면 같은 `div` 아래에 있는
- 본문 `content-box2`
- 뒤쪽 메타데이터 `div`
까지 같이 빨려 들어와 `lv1_div`가 과수집될 수 있습니다.

가장 안전한 수정 방향은 두 가지입니다.

1. `h1` 아래 첫 번째 `div`의 **직계 자식들만** 보되,
- `TEXT_NODE`는 그대로 포함
- `span` 같은 **inline element의 textContent도 포함**
- 대신 그 아래의 **중첩 `div`는 포함하지 않음**

이 방식이면
- 일반 텍스트
- 하이라이트 `span`
은 가져오고
- 본문/메타데이터는 제외할 수 있습니다.

2. 더 구현이 깔끔한 방식은
- 해당 `div`를 복제한 뒤
- 그 안의 하위 `div`들을 제거하고
- 남은 `textContent`를 읽는 방식입니다

개념적으로는:
- 원본: `中華民國 [span 憲][span 法] 芻議 <div>본문...</div>`
- 하위 `div` 제거 후: `中華民國 [span 憲][span 法] 芻議`
- 여기서 `textContent`를 읽으면 `中華民國憲法芻議`

이 방법의 장점:
- 현재 코드 구조를 거의 유지
- `span` 하이라이트 문제만 해결
- 일반적인 사례에서는 기존 동작을 거의 그대로 보존

정리하면, 수정 원칙은 이겁니다.

- `lv1_div` 추출은 계속 `h1` 다음 첫 번째 `div`를 대상으로 한다
- 하지만 “직접 텍스트 노드만 읽기”를 버리고
- **inline 요소(`span`)의 텍스트까지 포함**
- **중첩된 하위 `div`의 텍스트는 제외**
하는 방식으로 바꾼다

이렇게 하면 지금 지적한
- `中華民國憲法芻議` / `中華民國 芻議`
같은 불일치를 해결할 수 있고,
동시에 기존의 정상 사례에서 `content-box2`가 `lv1_div`로 섞여 들어가는 부작용도 피할 수 있습니다.

원하면 다음 단계로 이 원칙만 반영해서 `crawl_shenbao_text_chrome_ver3_1.py`로 실제 수정하겠습니다.

# 프롬프트 2
혹시 ‘lv1_div’ 외에 ‘publish_variant’, ‘date’, ‘issue_page’, ‘special_column’, ‘h1’, ‘content-box2’, ‘era_year’, ‘category’, ‘theme’를 가져오는 과정에는 이런 문제가 없나? 일단 내가 확인한 바로는 이것들은 다 문제 없이 들어와 있긴 한데, 단순히 해당 영역에 검색어가 안 걸려서 문제되지 않은 건지, 아니면 코드 로직 자체가 ‘lv1_div’와는 다르게 짜여 있는 건지 확인해줘. 당장 내가 보기에는 ‘h1’, ‘content-box2’은 문제가 없을 것 같아. 이 영역안에는 거의 확실히 검색어 문자열이 들어 있고, 해당 문자열에 span style이 적용되어 있음에도 누락 문자열 없이 들어왔거든. 다른 요소로부터 가져오는 로직은 어떤지도 함께 봐줘

# 답변 2
결론부터 말하면, **현재 확인된 문제는 `lv1_div` 추출 로직에 특이하게 들어 있는 `directText()` 때문에 생긴 것이고, 질문하신 다른 필드들은 같은 종류의 span 누락 문제에 걸리지 않도록 이미 다른 방식으로 짜여 있습니다.**

핵심 차이:
- `lv1_div`만 crawl_shenbao_text_chrome_ver3.py:472의 `directText()`를 씁니다.
- 이 함수는 `childNodes` 중 `TEXT_NODE`만 이어붙입니다.
- 그래서 `<span>憲</span><span>法</span>` 같은 **inline 요소 안의 텍스트를 버립니다**.
- 실제 적용 위치는 crawl_shenbao_text_chrome_ver3.py:511 부근입니다.

반면 다른 필드들은 대부분 **`.textContent` 기반**입니다.  
`textContent`는 하위 `span` 안의 글자도 포함하므로, 같은 유형의 누락이 생기지 않습니다.

**필드별 확인**

- `publish_variant`
  - crawl_shenbao_text_chrome_ver3.py:495
  - `leftTitle?.textContent`
  - span 하이라이트가 있어도 포함됩니다.

- `date`
  - crawl_shenbao_text_chrome_ver3.py:501
  - `headerSpan?.textContent`를 먼저 문자열로 받고, 그 위에서 날짜를 정규식으로 추출합니다.
  - 즉 span 누락 문제는 없습니다.
  - 다만 이 필드는 **header 형식이 달라지면 regex가 실패할 수 있는 별도 위험**은 있습니다.

- `issue_page`
  - `date`와 같은 `headerText`에서 regex로 추출
  - span 하이라이트 때문에 글자가 빠질 구조는 아닙니다.
  - 역시 형식 변화에는 민감할 수 있습니다.

- `special_column`
  - crawl_shenbao_text_chrome_ver3.py:536
  - `headerText`에서 정규식으로 뒷부분을 잘라 저장
  - headerSpan 내부에 하이라이트 `span`이 있어도 `textContent`에 포함되므로 누락 문제는 없습니다.

- `h1`
  - crawl_shenbao_text_chrome_ver3.py:508
  - `h1El?.textContent`
  - 사용자가 이미 확인한 대로, span 하이라이트가 있어도 정상적으로 들어옵니다.

- `content-box2`
  - crawl_shenbao_text_chrome_ver3.py:523
  - `contentEl?.textContent`
  - 이것도 span 누락 문제는 없습니다.

- `era_year`, `category`, `theme`
  - 먼저 crawl_shenbao_text_chrome_ver3.py:525, crawl_shenbao_text_chrome_ver3.py:529에서 `metadataText`를 `textContent`로 만듭니다.
  - 그다음 crawl_shenbao_text_chrome_ver3.py:540~542에서 라벨 사이 문자열을 잘라냅니다.
  - 따라서 검색어 하이라이트 span 때문에 값이 빠질 구조는 아닙니다.
  - 다만 이쪽은 **`其他紀元：`, `類別：`, `主題：` 라벨 구조가 무너지면** 다른 종류의 추출 오류가 생길 수 있습니다.

**정리**
- 이번 문제는 **검색어가 우연히 다른 필드에 덜 걸려서 안 드러난 것이 아니라**, **`lv1_div`만 유독 `TEXT_NODE`만 읽는 특수 로직**을 써서 생긴 문제입니다.
- `h1`, `content-box2`, `publish_variant`, `date`, `issue_page`, `special_column`, `era_year`, `category`, `theme`는 모두 `.textContent` 또는 그 파생 문자열 처리라서, **같은 종류의 span 누락 문제에는 걸리지 않습니다.**
- 따라서 이번 수정은 **`lv1_div` 추출 방식만 고치면 되는 문제**로 보는 것이 맞습니다.

주의할 점 하나:
- `lv1_div`를 단순히 `sibling.textContent`로 바꾸면 span 문제는 해결되지만, 아래쪽 `div`의 본문/메타데이터까지 같이 빨아들일 수 있습니다.
- 그래서 수정은 **span은 포함하되, 하위 `div`는 제외**하는 방식으로 해야 안전합니다.

원하면 바로 그 방식으로만 수정해서 crawl_shenbao_text_chrome_ver3_1.py로 저장하겠습니다.

