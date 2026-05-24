---
주제: 기사 페이지의 html 구조가 상이한 경우 수집 코드 수정 2
AI 플랫폼 및 모델:
  - GPT-5.4
날짜: 2026-04-22
---
# 작업 메모
- 기존 스크립트(crawl_shenbao_text_chrome_ver2.py)의 fallback 기능이 잘못된 요소를 저장하도록 만드는 경우가 있어, fallback 대신 각 요소가 있으면 있는 대로, 없으면 없는 대로 그 요소 이름대로 저장하도록 수정.
- h1 요소만 있고 content-box2가 없는 기사(일반적으로 별도 제목이 없고 본문 자체가 h1에 들어 있는 경우)도 그것을 title로 가져오는 것이 아니라 원래 출처의 표기 그대로 h1 요소로 저장하여 이후 정리에서 혼동을 덜기 위함.
- 기존 코드(crawl_shenbao_text_chrome_ver2.py)가 `1_coding_2_기사 페이지의 html 구조가 상이한 경우를 대비한 코드 수정.md`의 대화를 거쳐 개선된 두 번째 버전이었음을 고려해 이번 스크립트 개선을 ver3로 명명함.

# 프롬프트 1
기존 `coding\crawl_shenbao_text_chrome_ver2.py` 코드에 구현된 fallback 기능으로 인해, html 구조가 일반적이지 않은 상세 페이지에서 불필요한 정보가 딸려 들어오거나 맞지 않는 항목 이름을 부여 받는 경우가 있어서 이를 수정하고 싶어. 가장 중요한 수정 사항은 상세 페이지 내의 정보들을 파싱해서 수집 후 전처리 단계에서 문자열 분리를 최소화 하는 방향으로 가는 거야. 단 기존 코드에서 label, page, item_index, list_title, detail_url을 수집하는 방식은 그대로 유지하고 싶어. 아래 제시한 HTML 구조별 수집 지침을 바탕으로 수집 스크립트를 수정하고, 같은 경로에 crawl_shenbao_text_chrome_ver3.py로 저장해줘

1. 아래 outerHTML 구조를 예로 들면, 
	- span id="left-title"에 들어 있는 申報를 publish_variant 열에 기입
	- 日期：다음에 오는 1949-05-08를 date 열에 기입 
	- 版次/卷期：다음에 오는 02를 page 열에 기입, 版은 삭제
	- 專欄：다음에 오는 문자열이 있다면 special_column 열에 기입. 없다면 결측값으로
	- h1 에 들어 있는 문자열을 h1 열에 기입. 없다면 결측값으로
	- h1 다음에 위치한 div 안에 바로 위치한  路透社西德波恩城六日電 를 lv1_div 열에 기입. 없다면 결측값으로
	- div class="content-box2" 에 들어 있는 문자열을 content-box2 열에 기입. 없다면 결측값으로
	- 其他紀元：다음에 오는 民國38年 日昭和24年를 era_year 열에 기입. 없다면 결측값으로
	- 類別：다음에 오는 문자열이 있다면 category 열에 기입. 없다면 결측값으로
	- 主題：다음에 오는 문자열이 있다면 theme 열에 기입. 없다면 결측값으로
	- div id="footer" 에 들어있는 문자열 Copyright c 2012 得泓資訊. All Rights Reserved.은 수집하지 않음

<div id="content-box_contentwrapper" class="contentwrapper" style="position: relative; top: 0px; width: 100%; display: block; padding: 0px; left: 0px;"><div class="img-pdf"><a href="tm_show.php?id=A2013040226056&amp;fullversion=1&amp;qrygroup=1&amp;qrynewstype=SP" target="_blank" title="原始圖檔" fullversion="1"><img src="SP/images/pdf.png" border="0"></a></div><span id="left-title">申報 </span><span><b>日期：</b>1949-05-08 <b>版次/卷期：</b>02 版　<b>專欄：</b></span><h1>制憲議會批準憲草　西德設雛型政府　為德國統一政府樹立基礎
　　</h1><div>路透社西德波恩城六日電<div><div class="content-box2">德國政治家已於今日在此設立西德之雛型政府，西德制憲議會今日決定設立一臨時委員會，以執行聯邦政府成立前之政府任務。該案前動議人自由民主黨領袖薛費，謂該過渡委員會之目的，在收集並研究資料，以準備統一的立法，同時並草具設立各政府部門之法令，俾聯邦政府成立後即可立時展開工作。<br>
　　〔聯合社德國波恩六日電〕制憲議會今二讀通過西德政府憲章，僅共黨議員兩名投反對票。憲草將於作日舉行三讀，其中有兩條特別富於與味：〔一〕要求將西柏林併入西德，此議早由美英法軍政府總督表示反對；〔三〕規定取消西德罪犯之死刑，此乃共黨所贊成之唯一條文。此外，西德首都所在將於八日會議中決定之，西德共和國成立蜞暫定七月十五日。<br>
　　〔合眾社波恩六日電〕德制憲議會今日選出一十八人之執行委員會暫為政府，此一西德政府將在盟國監督下行政，正式之政府將在七月下旬舉行普選後正式成立。盟國方面已準備將德境佔領區移交文官管制，對德國之行政將儘少過問。西德臨時政府係自議員中選出共七名，計社會黨一人，基督民主黨一人，自由民主黨二人，及其他各黨各一人。據柏林方面透露，西方盟國軍事長官業已賦權予西德政府，一俟該政府正式成立後將可設立聯邦警察隊。西德領袖於四強同意解除柏林封鎖及舉行四強外長會議之際，倉卒成<span style="color:yellow;background-color:green">立</span><span style="color:yellow;background-color:green">憲</span>法及決定成立政府，蓋德人希望若西方盟國與蘇聯獲致協定，則德國統一政府可能以波恩憲法為基礎。<br>
</div><div>
			<b>其他紀元：</b>民國38年 日昭和24年 <br>
			<b>類別：</b><br>
			<b>主題：</b>台灣文化精髓-台灣文化協會/大正民主
			</div>
</div>
		<!--end content-box --></div>
<!--end content -->


<div id="footer">Copyright c 2012 得泓資訊. All Rights Reserved.</div>
 <!--end footer-->
</div>

2. 아래 outerHTML 구조를 예로 들면, 
	- span id="left-title"에 들어 있는 申報를 publish_variant 열에 기입
	- 日期：다음에 오는 1948-06-10를 date 열에 기입 
	- 版次/卷期：다음에 오는 02를 page 열에 기입, 版은 삭제
	- 專欄：다음에 오는 문자열이 있다면 special_column 열에 기입. 없다면 결측값으로
	- h1 에 들어 있는 문자열을 h1 열에 기입. 없다면 결측값으로
	- h1 다음에 위치한 div 안에 바로 위치한  行政院新聞局攝 를 lv1_div 열에 기입. 없다면 결측값으로
	- div class="content-box2" 에 들어 있는 문자열을 content-box2 열에 기입해야 하지만, 아래 경우에는 해당 요소 안에 문자열이 없고 `<br>`만 있으므로, 이런 경우 결측값으로
	- 其他紀元：다음에 오는 民國37年 日昭和23年를 era_year 열에 기입. 없다면 결측값으로
	- 類別：다음에 오는 문자열이 있다면 category 열에 기입. 없다면 결측값으로
	- 主題：다음에 오는 문자열이 있다면 theme 열에 기입. 없다면 결측값으로
	- div id="footer" 에 들어있는 문자열 Copyright c 2012 得泓資訊. All Rights Reserved.은 수집하지 않음
	
<div id="content-box_contentwrapper" class="contentwrapper" style="position: relative; top: 0px; width: 100%; display: block; padding: 0px; left: 0px;"><div class="img-pdf"><a href="tm_show.php?id=A2013060878797&amp;fullversion=1&amp;qrygroup=1&amp;qrynewstype=SP" target="_blank" title="原始圖檔" fullversion="1"><img src="SP/images/pdf.png" border="0"></a></div><span id="left-title">申報 </span><span><b>日期：</b>1948-06-10 <b>版次/卷期：</b>02 版　<b>專欄：</b></span><h1>社論
救濟特捐與財產稅
　　自從救濟特捐具體化後，財產稅這問題，本已無形消滅，因為籌備期間，幾經蛻化，最後纔歸結到所謂特捐，這原是財產稅的化身。
　　由於王雲五財長的開游政策，復　目於這項稅源，而立法院也有人提議舉辦、認為這是平衡社會財富，不流血的經濟革命方法，於是這個問題，復引起了各方面的熱烈討論。
　　不管提議人的動機如何，現在財政的收不數支，與通貨膨脹過於嚴重，這是大衆公認的事實。所以另關稅源，增加稅收，以勉求預算的平衡，同時即避免通貨的繼續膨脹，亦幾為人同此心，心同此理的要求。不過現值行憲伊始，庶政公開，人民有納稅的義務，同時透過議會，亦有審核財政的權利。現在國家出支的實况究竟如何？逐月增發的法幣究有幾何？固有的各項收入，還有沒有增加之餘地？可以節省的浮濫支出，和可以挹注的其他收入又有若干？這篇細帳，財政部長似應先行廠實公佈出來，使大家共見共聞，瞭然於癥結之所在。只須收支適當；確須另籌抵補，那麼，開辦財產稅也可，另籌其他的收入也無不可。這是<span style="color:yellow;background-color:green">立</span><span style="color:yellow;background-color:green">憲</span>國家的常軌，並不是我們故唱高調。
　　我們也很知道，現在並不是沒有國家預算，而且卅七年度下半年的預算，還正在財部編製之中，所有收支兩項數字，當然先應有個交代。不過我們所要求的，是各項準確的數字，和財政上實際的狀况，決不是膚泛的輪廓，也決不是紙面上勉强凑合的結論，更不是吞吞吐吐，隱隱約約，搪塞籠統的數字。觀於過去各年度財政方面的官樣文章，和發行數目迄未按期公佈，我們相信，這個起碼的要求，是十分合理，也是十分切要，新任的財長似乎不能漠然置之吧。
　　至於平衡財富云云，其意自在豪富鉅室，與一般利用時機攫取暴利的人，這是當前一致的輿論，誰也不會替他們故意廻護的。但眞正的問題是：在財產稅徵收之時，其對象會不會走了樣？換句話說，眞正的豪富鉅室與一般暴利發跡的人，有沒有逃避的可能？這項負擔，是否仍會落到一般中下級人民的身上去？試觀逃避在海外的國人存款，已經各方面熱烈地要求了幾年，到如今當局還是一籌莫展，又救濟特捐的重擔，也好像依舊要向同業公會方面去費神攤募，可知我們這項過慮，也並不是毫無根據。
　　大家知道，由於長期抗戰，和通貨膨賬的結果，一般中下階級已經焦頭爛額，再也經不住過分的剝削，而工商業亦俱在苛捐雜稅與形形式式的攤派之下，拚命掙扎，日趨崩潰。黃台之瓜，其實不堪再摘。所以這項財產稅如果確定開徵，那麼，其徵課的對象，必須依照原案，明確規定，不許以增加收入為唯一的理由，而不擺手段，任意地瓜蔓開去。須知豪富鉅室與暴利發跡，其範圍並不甚廣，除了他們這班人以外，其餘大多數久民鉤在飢餓綫上掙扎，其僅有的財富，用不着重行分配，而如果再予分配的結果，除加速了他們的沒落以外，亦並沒有大量的貢獻，可以補充國庫。這是當局籌擬財產稅的時候所必須慎重注意的。
　　上文說過，救濟特捐原是財產稅的變相，假如王財長對於財產稅的舉辦，確具決心，那麼，救濟特捐應否依然照案執行，似又值得重行研討。一物兩稅，或重複課徵，在理倫上，都是不許可的。個或有了一個名目，便可以開徽一道，則在財產稅蛻變為救濟特捐的過程中，還有財產捐，臨時財產稅，和建國特捐等等名稱，是不是現在或將來，還可以在某種某種名義之下，依次地搬演出來重徽幾次？默察時人心理，凡是贊成舉辦財產稅的，其口號不外乎有錢出錢，其對象也不外乎豪富鉅室與暴利發跡的人，其理由更不外乎平衡社會財富。可知這項目標如果可以達到，那麼，只須一次已足，用不着重複舉辦，否則疊訶架屋，一再重微，與原來的宗旨依舊不相干涉，反而顯涉苛擾！所以我們主張；救濟特捐的名稱不妨加以修正，其內容亦僅可予以加强與充實，但不宜與財陸競分道並進，致造成一稅兩徵的現象。好得時經數月，所謂救濟特捐，事實上幾乎還沒右辦通，及時修改，並不算太晚。
（上）楊妹譯晨寫字，右王小姐，左郭偑琪（下）楊妹在美國新聞虞看電影</h1><div>行政院新聞局攝<div><div class="content-box2"><br>
</div><div>
			<b>其他紀元：</b>民國37年 日昭和23年 <br>
			<b>類別：</b><br>
			<b>主題：</b>
			</div>
</div>
		<!--end content-box --></div>
<!--end content -->


<div id="footer">Copyright c 2012 得泓資訊. All Rights Reserved.</div>
 <!--end footer-->
</div>

# 답변 1

수정 완료했습니다.

새 파일:
crawl_shenbao_text_chrome_ver3.py

핵심 변경 사항:
- 기존 `crawl_shenbao_text_chrome_ver2.py`는 그대로 두고, 같은 경로에 `crawl_shenbao_text_chrome_ver3.py`를 새로 생성했습니다.
- 기존 `label`, `page`, `item_index`, `list_title`, `detail_url` 수집 방식은 유지했습니다.
- 상세 페이지에서는 fallback으로 다른 요소를 대신 저장하지 않고, 실제 DOM 요소별로 다음 열에 분리 저장하도록 바꿨습니다.
- `span#left-title` → `publish_variant`
- `日期：...` → `date`
- `版次/卷期：...` → `issue_page`
- `專欄：...` → `special_column`
- `h1` → `h1`
- `h1` 다음의 1단계 `div` 직접 텍스트 → `lv1_div`
- `.content-box2` → `content-box2`
- `其他紀元：...` → `era_year`
- `類別：...` → `category`
- `主題：...` → `theme`
- `div#footer`의 `Copyright c 2012 得泓資訊. All Rights Reserved.`는 수집하지 않습니다.
- `.content-box2`가 없거나 `<br>`만 있는 경우에도 에러로 처리하지 않고 빈 값으로 저장합니다.
- `h1`만 있고 `.content-box2`가 없는 구조는 `h1` 값만 `h1` 열에 저장하고, `content-box2`는 빈 값으로 둡니다.
- 상세 페이지 수집 실패 메시지는 본문 열에 섞지 않고 `crawl_error` 열에만 기록하도록 했습니다.

주의할 점:
- 기존 `page` 열은 검색 결과 목록의 페이지 번호로 유지했습니다.
- 상세 페이지의 `版次/卷期` 값은 기존 `page` 열과 충돌하므로 `issue_page` 열에 저장하도록 했습니다.
- 새 스키마가 기존 CSV와 섞이지 않도록 출력 파일명 prefix를 `shenbao_textdata_ver3_...csv`로 설정했습니다.

새 CSV 열 구성:
```text
label,page,item_index,list_title,detail_url,publish_variant,date,issue_page,special_column,h1,lv1_div,content-box2,era_year,category,theme,crawl_error
```

검증:
- `python -m py_compile` 문법 검사 통과.
- 로컬 정적 HTML 예시를 브라우저 DOM에 넣어 `publish_variant`, `date`, `issue_page`, `h1`, `lv1_div`, `content-box2`, `era_year`, `category`, `theme` 파싱이 정상 동작하는 것을 확인했습니다.

실행 예:
```powershell
python C:\Users\class\Documents\coding\crawl_shenbao_text_chrome_ver3.py --label zhixian --save-every 20
```

이 경우 결과 파일은 기본적으로 다음 경로에 생성됩니다.
```text
C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_ver3_zhixian_1to{마지막번호}.csv
```

# 프롬프트 2
이 코드의 출력 파일명 형식을 `shenbao_textdata_ver3_{label}_{start_index}to{end_index}.csv`에서 `shenbao_textdata_{label}_{start_index}to{end_index}_ver3.csv`로 바꾸고 싶어. 코드 내에서 관련 라인을 수정해줘. 특히 작업 재개 관련 라인이 기존 파일명을 불러오게 되어 있으니, 그 부분도 이전 작업 파일명을 `shenbao_textdata_{label}_{start_index}to{end_index}_ver3.csv`로 하여 불러오도록 수정하고, 그 외에 영향이 있는 라인들을 함께 수정해줘.

# 답변 2
수정했습니다.

변경 파일:
crawl_shenbao_text_chrome_ver3.py

변경 내용:
- 출력 파일명 형식을 기존
  `shenbao_textdata_ver3_{label}_{start_index}to{end_index}.csv`
  에서
  `shenbao_textdata_{label}_{start_index}to{end_index}_ver3.csv`
  로 변경했습니다.
- `--label` 또는 `--resume-latest` 사용 시 재개 대상 파일 탐색도 새 형식만 찾도록 수정했습니다.
- `infer_label_from_path()`도 새 파일명 형식에서 label을 추출하도록 수정했습니다.
- `parse_end_index()`도 `to{end_index}_ver3` 형식에서 마지막 index를 읽도록 정규식 기반으로 수정했습니다.
- `--help` 메시지에 표시되는 파일명 설명도 새 형식으로 바꿨습니다.

검증:
- `python -m py_compile` 문법 검사 통과.
- 테스트 결과 `build_output_path()`가 `shenbao_textdata_xianfa_1to200_ver3.csv` 형식으로 생성됨을 확인했습니다.
- `find_latest_resume_file(..., "xianfa")`가 새 형식의 파일을 정상 탐색하는 것도 확인했습니다.
- 기존 형식인 `shenbao_textdata_ver3_xianfa_1to999.csv`는 더 이상 재개 대상으로 잡히지 않습니다.