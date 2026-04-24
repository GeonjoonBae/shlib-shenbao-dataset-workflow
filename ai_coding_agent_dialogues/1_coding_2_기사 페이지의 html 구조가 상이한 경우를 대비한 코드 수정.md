---
주제: 기사 페이지의 html 구조가 상이한 경우를 대비한 코드 수정
AI 플랫폼 및 모델:
  - GPT-5.4
날짜: 2026-04-13
---
# 1. 상세 페이지 HTML 구조 차이에 따른 본문 추출 오류 진단

## 프롬프트 1-1
shenbao_textdata 폴더 내(하위 폴더 제외) 네 파일에 대해 title 열의 내용에서 일련번호가 표시 `숫자. ` 부분을 제외한 순제목이 띄어쓰기와 무관하게 text의 문자열과 일치하는 경우가 각 파일별로 몇 건이나 되는지 확인해줘. 추측컨대 이 경우에 text 컬럼의 문자열에는 `其他紀元：...`로 시작하는 메타데이터 부분이 빠져있을거야.

## 답변 1-1
확인했습니다.

비교 기준:
- `title`에서 앞의 `숫자. ` 제거
- `title`과 `text` 모두 **모든 공백 문자 제거 후** 비교
- 즉 띄어쓰기, 줄바꿈 차이는 무시

결과:
- [shenbao_textdata_xianfa_1to18648.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_xianfa_1to18648.csv): `891건`
- [shenbao_textdata_lixian_1to7203.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_lixian_1to7203.csv): `406건`
- [shenbao_textdata_xianzheng_1to9906.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_xianzheng_1to9906.csv): `557건`
- [shenbao_textdata_zhixian_1to4322.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_zhixian_1to4322.csv): `175건`

추가 확인:
- 위 일치 행들 중 `text`에 `其他紀元：`가 포함된 경우는 **4개 파일 모두 0건**이었습니다.
- 즉 당신의 추측대로, 이런 일치 사례에서는 `text` 컬럼에 `其他紀元：...` 메타데이터가 붙어 있지 않았습니다.

원하면 다음으로는 각 파일별 **해당 item_index 전체 목록**을 CSV나 TXT로 뽑아드릴 수 있습니다.

---

## 프롬프트 1-2
수집한 원본 데이터를 보니 text 컬럼에 들어온 데이터가 원래 내가 원했던 기사 본문이 아니라 제목 부분만 들어온 경우가 있어. 아마도 탑재 방식이 달라서 그런 것 같아. 내가 이런 문제가 발생한 페이지의 해당 부분 outerHTML 정보를 예시로 줄테니 crawl_shenbao_chrome.py 파일에서 text 컬럼에 저장할 텍스트를 가져오는 라인을 함께 검토해서 문제가 발생한 이유와 해결 방안을 알려줘. 참고로 나는 text 컬럼에 `今年五月二十日行憲政府之正副總統就職，...`로 시작하는 내용이 들어오길 원했는데, 실제로 들어온 건 `專論 對於立法院之期望` 뿐이었어. 물론 이런 경우가 아주 많지는 않고 전체 수량 중의 4~5% 정도여서, 일반적인 구조인 페이지에는 기존의 수집 방식을 유지하는 한편 아래와 같은 구조가 등장했을 때는 이 구조에 맞춰서 수집을 할 수 있으면 좋겠어. 

<div id="content-box_contentwrapper" class="contentwrapper" style="position: relative; top: 0px; width: 100%; display: block; padding: 0px; left: 0px;"><div class="img-pdf"><a href="tm_show.php?id=A2013060878635&amp;fullversion=1&amp;qrygroup=1&amp;qrynewstype=SP" target="_blank" title="原始圖檔" fullversion="1"><img src="SP/images/pdf.png" border="0"></a></div><span id="left-title">申報 </span><span><b>日期：</b>1948-06-09 <b>版次/卷期：</b>02 版　<b>專欄：</b></span><h1><span style="color:yellow;background-color:green">專</span><span style="color:yellow;background-color:green">論</span>

<span style="color:yellow;background-color:green">對</span><span style="color:yellow;background-color:green">於</span><span style="color:yellow;background-color:green">立</span><span style="color:yellow;background-color:green">法</span><span style="color:yellow;background-color:green">院</span><span style="color:yellow;background-color:green">之</span><span style="color:yellow;background-color:green">期</span><span style="color:yellow;background-color:green">望</span> </h1><div>胡先驌<div><div class="content-box2">　<br>

　　今年五月二十日行憲政府之正副總統就職，十七日立法院正副院長選出，孫科先生以得五百五十八票當選為正院長，陳立夫先生以得三百四十三票當選為副院長，廿四日立法院正式通過翁文灝先生為行政院長，此為憲政實施以後最重要之三件大事。蔣總統在就任演說中鄭重聲明行憲政府必當恪守　法所規定的範圍，執行憲法所賦予的職責；必須整頓軍事，加强軍事，在短期內戡平叛亂；必須整肅吏治，樹立紀網，起用賢能，刷新人事，厲行老核，嚴明賞罰，勸求民隱，减除地方民衆所受法外之苛擾，更必須簡化法令，　訂權責，統一執行之機構，芟除繁複不切實際之法規；在經濟措施方面，必須貫澈三民主義的實施；治標則必須以有效的方法穩定幣値，平衛收支，管理金融，改善交通，使物價趨於安定，人民得無窮困，治本則必須推行士地改革，保護佃農利益，推廣農地貸款以平均地權；必須用異進稅率，徽收過分利得，取締投機暴利，以節制資本；尤必須推行合作事業，獎進農工生產，保護合法貿易，歡迎國際投資。蔣總統所摽舉新政府之施政方針，實為全國人民所企望者。然在新憲法所規定之條文下，立法院有絕大之權，不但一切重要法規皆須由立法院立法，且立法之後，行政院必須見諸實施，否則行政院長必須辭職。故在今日立法院之權，乃遠在訓政時期之上。勝來國家政治之休明與否，立法院所負之音，反較行政院為大。故人民所期望於立法院者，尤超乎所期望於行政院者之上也。<br>

　　當前最重要最迫切之事為戡亂。然而經濟戡亂之重要更在軍事戡亂與政治戡亂之上。我國在八年抗戰之後，又經過兩年剿匪，民生凋敝日極。老弱死於　壑，少壯不服兵役，便為共匪參軍，或聚嘯山林成為股匪。田野荒蕪，災民遍野，而以戡亂需款，於是　購徵實，誅求無藝，適以為　敲雀，徒增亂源。而豪門奸商，投機囤積，富者益富，　者益貧。過去徵稅，皆不及於富豪，政府始終不敢徵收財產捐，取締投機囤積亦無有效方法，故立法院第一要務，即在通過嚴密徵收財產稅與徽用國人在國外存款之法規，以平民憤而裕財源，庶以平衡收支，穩定幣値，此期望於立法院者一也。<br>

　　土地改革為當前之急務。耕者有其田，尤為民生主義所標榜。同時匪黨正以土地改革方案為其政治資本。即在地方政府如廣西山西河北福建亦有其單行之土地法規。處此情形，立法院之訂定土地法，尤刻不容緩。或者澈底使耕者有其田、或訂立限田法，或採用地政學會所提方案，使佃農在十四年後取得所佃之田之所有權，或發行土地公債，購買地主之土地以分配於佃農，或廣行土地貸欵，使佃農可有資金購買地主之土地，或限定地主所有之田不能超過某一限度。超額之田，無價收歸國有，轉而分與貧農。此皆須徽集專家之意見，寨愼討論，訂定法規。法規訂定之後，即須普遍實施，同時取消地方政府所訂之單行法，以謀法令之統一。尤有要者，即共匪與各地方政府所定限田之額，皆嫌過低，此農學家經濟學家人人所能言者。今日立法委員中農業專家甚多，甚盼彼等能擬訂通過適合國情適合農業經濟之士地法也。<br>

　　復次。為人民謀福利尙有與耕者有其田同樣重要者，即蔣總統所標舉之推行合作事業獎進農工生產是也。農業有季節性，故在農產品宋收割以前則穀價騰踊。貧農存儲不足，每須高價購責食糧。及至新殺登塲則榖價　落。又每每在脅黃不接之際，農民被迫而接受高利貸，甚或忍痛豫賣靑苗。此種剝削必須澈底取締，則信用貸款與抵押貸款實為市要。今日農民銀行雖亦此方發展，惜貸款之規模過小，不足以應農民廣大之需要。經濟學家每謂合作制度為實現社會主義最優良之方式。盼立法院在此方面從速訂立完善之法規，並擴大農貸，使農民得以免除高利貸之剝削，與收　時　賤之損失。則增進農民之利益，即所以解除革命之危機也。<br>

　　復次農民占全國人口百分之八十以上，而在工業不發遠之情况之下，國家之歲入，大部利賴農民所　之租稅。近年烟葉之價格　漲，政府所徵收之烟草稅在上海一埠竟占消費稅百分之六十以上。即此一端可概其餘。然而政府為謀農民之福利，曾費幾何經費？過去行政院不設農林部。今日農林部之經費占全國歲出預算之最小額。中央農業試驗所夙有成績，而經費極少，不能慶開其事業為農民興利徐害。姑舉一例：據估計江南某省每縣每年耕牛死於生疫者約一萬頭。以今日之物價計之，全國死亡耕牛之損失，必為極大之天文數字。而今日美國已有終身免疫之血淸，法國又發明ROX之聖藥，茍能使全國農業改進所有充足之經費，擴大其機構，即制止默疫一項·每年减少國家與農民之損失者將不可億計。至於興修水利，改良種子，增加肥料，農產加工，種種農業科學上之措施，可以增加國富而裕民生者，其數殆不在工業化之下，而所費之經費必較小，今憲法上規定敎育文化科學經費，須占全國歲出預算百分之十五。則為最大多數之民衆謀羅利計，農林事業經費應占全國歲出之若干乎？故立法院必須在各方面增加農林事業經費以謀增進農民之福利。此期望於立法院者二也。<br>

　　今日之在官者，固多賢能，然　冗無能貪污執法之惡吏，亦不在少數。而　貴與高級將領之貪污其數量之巨尤駭人聽聞。賞罰不明，紀綱不立，久為巾外所騰笑。而冗員益多，行政效舉　低下。政府日日言裁員，而戡亂建國委員會以厚　　養坐食之冗當竟至數千人之多。又自新縣制施行以來，縣級官吏驟加數倍，而縣政之不舉猶如往普。如何確立人事制度簡化機構　汰冗員以節經費，如何簡化行政手續，及芟除繁複不切實際之法規，以增加行政效率，皆有賴於賢　之立法。此期望於立法院者三也。<br>

　　敎育為立國之大本，而我國之敎育制度不能配合人民之實際需要；義務敎育尤以缺乏經費不能普遍認眞辦理，至無以掃除文實，提高一般人民之知繼水準；高等敎育亦以經費不足，有名無實。因之全國敎育之水準日見低落，無以配合建國之需要。雖憲法規定敎育文化科學經費占全國歲出預算百分之十五，然尙未見諸實施。又科學為近代立國之基礎，科學不能迎頭趕上，即無以自存於今日之世界。蘇聯有鑒於此，故不惜以龐大經費以擴充科學研究事業。故能在短期間，使其科學發達　駸可以追蹤英美，一躍而為兩大强國之一。我國在戰前十年科學研究尙有規模。至今日則以經費缺乏，科學研究十九陷於停頓狀態。前年國防最高委員會曾通過一決議案規定以歲出總預算百分之一列為舉辦科學研究專款。然而主計處竟不將此項經費列入預算，荏苒兩年，終未見諸實施。遂使國內科學研究不能進展。今後如何澈底改革敎育制度，如何將憲法所規定國家總預算中百分之十五敎育經費照數又付，以及如何實施國防最高會議籌撥總預算百分之一之科學研究專款，皆有賴於立法。此期望於立法院者四也。<br>

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

## 답변 1-2
원인은 현재 본문 추출 selector의 fallback 설계입니다.

**문제 지점**
- [crawl_shenbao_chrome.py:31](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:31)
- [crawl_shenbao_chrome.py:32](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:32)
- [crawl_shenbao_chrome.py:437](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:437)

현재 코드:
- `DETAIL_TEXT_XPATH = //*[@id="content-box_contentwrapper"]/div[2]/div`
- fallback selector:
  - `#content-box_contentwrapper > div:nth-child(4) > div`
  - `#content-box_contentwrapper > h1`
- `extract_detail_text()`는 이 selector들을 순서대로 돌면서 **처음으로 비어 있지 않은 텍스트를 바로 반환**합니다.

**왜 이 사례에서 제목만 저장됐나**
사용자가 준 HTML 구조에서는 실제 본문이 여기 있습니다.
- `#content-box_contentwrapper .content-box2`

반면 현재 fallback은 이 구조와 맞지 않습니다.
- `#content-box_contentwrapper > div:nth-child(4) > div`
  - 이 HTML에서는 `nth-child(4)`가 `h1`입니다
  - 즉 구조상 본문을 가리킬 수 없습니다
- `#content-box_contentwrapper > h1`
  - 이건 명시적으로 제목입니다
  - 앞 selector가 실패하면 제목만 `text`로 저장됩니다

즉 이번 사례는:
1. 1순위 XPath가 이 변형 구조에서 기대대로 본문을 못 잡았고
2. 2순위 CSS도 잘못된 `nth-child`를 가리켰고
3. 3순위 `h1`이 발동해서 제목만 저장된 것입니다

그래서 사용자가 원한:
- `今年五月二十日行憲政府之正副總統就職，...`

대신 실제 저장된:
- `專論 對於立法院之期望`

이 나온 겁니다.

**추가로 보이는 문제**
현재 구조에서는 본문 뒤에 메타도 같이 붙습니다.
- `其他紀元：...`

즉 이 변형 페이지를 제대로 처리하려면
- 본문 selector를 `.content-box2` 중심으로 바꾸고
- 추출 후 `其他紀元：` 이후를 잘라내야 합니다

**해결 방안**
가장 안전한 수정은 이겁니다.

1. 본문 selector 1순위를 `.content-box2`로 추가
- 예:
  - `#content-box_contentwrapper .content-box2`
- 이 구조가 지금 보여준 예시에는 정확히 맞습니다

2. `#content-box_contentwrapper > h1` fallback 제거
- 제목을 본문 fallback으로 쓰는 건 잘못입니다
- 이 fallback 때문에 조용히 오수집이 발생합니다

3. 추출 후 `其他紀元：` 이후 제거
- 본문 + 메타가 같이 잡히는 구조가 있으므로 필요합니다

4. 방어 로직 추가
- 추출한 텍스트가 상세 페이지 `h1`와 동일하면 본문으로 인정하지 말고 다음 selector로 넘어가야 합니다

**권장 수정 방향**
`DETAIL_TEXT_SELECTORS`는 최소한 이렇게 바꾸는 게 맞습니다.

```python
DETAIL_TEXT_SELECTORS = [
    ("css", "#content-box_contentwrapper .content-box2"),
    ("xpath", '//*[@id="content-box_contentwrapper"]/div[2]/div'),
]
```

그리고 `extract_detail_text()` 안에서:
- 추출 텍스트에서 `其他紀元：` 이후 제거
- 결과가 비었거나 `h1` 제목과 같으면 버리기

**판단**
- 일반 구조는 기존 방식이 어느 정도 맞았지만
- 지금처럼 4~5% 정도 존재하는 변형 구조에서는
- `h1` fallback 때문에 제목 오수집이 발생할 수 있습니다

즉 해결의 핵심은:
- **본문용 selector를 `.content-box2` 중심으로 추가**
- **제목 fallback 제거**
- **메타 잘라내기**

원하면 이 기준으로 [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)를 바로 수정하겠습니다.

---

## 프롬프트 1-3
텍스트 뒤에 붙는 메타데이터는 수집 이후에 추가 전처리를 통해 새 컬럼으로 분리할 예정이니 메타데이터 잘라내기는 하지 않아도 돼. 나머지 문제들만 해결하는 방식으로 코드를 수정하고 싶어. 단, 그 전에 한 가지 확인할 게 있어. 아래는 기존 코드에서 정상적으로 수집된 페이지의 outerHTML이야. 과연 네가 수정하려는 방향대로 수정하더라도 일반적인 사례에서의 수집도 문제 없이 이루어질지 검토해줘.

사례 1(정상 수집)
- HTML:
<div id="content-box_contentwrapper" class="contentwrapper" style="position: relative; top: 0px; width: 100%; display: block; padding: 0px; left: 0px;"><div class="img-pdf"><a href="tm_show.php?id=A2013060903335&amp;fullversion=1&amp;qrygroup=1&amp;qrynewstype=SP" target="_blank" title="原始圖檔" fullversion="1"><img src="SP/images/pdf.png" border="0"></a></div><span id="left-title">申報 </span><span><b>日期：</b>1948-11-17 <b>版次/卷期：</b>03 版　<b>專欄：</b></span><h1>吉田將宣布解散國會　圖恢復日皇政權　盟總認爲現內閣無權解散國會
　　</h1><div>合衆社東京十六日電<div><div class="content-box2"><span style="color:yellow;background-color:green">日</span><span style="color:yellow;background-color:green">首</span><span style="color:yellow;background-color:green">相</span><span style="color:yellow;background-color:green">吉</span><span style="color:yellow;background-color:green">田</span><span style="color:yellow;background-color:green">蔑</span><span style="color:yellow;background-color:green">視</span><span style="color:yellow;background-color:green">衆</span><span style="color:yellow;background-color:green">所</span><span style="color:yellow;background-color:green">周</span><span style="color:yellow;background-color:green">知</span><span style="color:yellow;background-color:green">盟</span><span style="color:yellow;background-color:green">總</span><span style="color:yellow;background-color:green">願</span><span style="color:yellow;background-color:green">望</span>，十六日對國會宣佈：在國會通過勞工法修正法案以後，渠將解散國會，重行普選·盟總政府處官員認爲：吉田之措施顯圖破壤憲法及重行恢復天　之政治權力，但渠等尚不願對國會解散問題展開憲法辯論·渠等希望，在可能範圍內，日本人民能解決本身之問題，而母需盟總干涉。<br>
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

- 수집 결과(csv): 3,293,293. 吉田將宣布解散國會 圖恢復日皇政權 盟總認爲現內閣無權解散國會,申報 日期：1948-11-17 版次/卷期：03 版 合衆社東京十六日電,https://z.library.sh.cn/http/80/10.1.30.77/yitlink/tm/tm_shownews.php?id=A2013060903335&qrygroup=1&qrynewstype=SP&n=293,日首相吉田蔑視衆所周知盟總願望，十六日對國會宣佈：在國會通過勞工法修正法案以後，渠將解散國會，重行普選·盟總政府處官員認爲：吉田之措施顯圖破壤憲法及重行恢復天 之政治權力，但渠等尚不願對國會解散問題展開憲法辯論·渠等希望，在可能範圍內，日本人民能解決本身之問題，而母需盟總干涉。 其他紀元：民國37年 日昭和23年 類別： 主題：

사례 2(정상 수집)
HTML:
<div id="content-box_contentwrapper" class="contentwrapper" style="position: relative; top: 0px; width: 100%; display: block; padding: 0px; left: 0px;"><div class="img-pdf"><a href="tm_show.php?id=A2013040052905&amp;fullversion=1&amp;qrygroup=1&amp;qrynewstype=SP" target="_blank" title="原始圖檔" fullversion="1"><img src="SP/images/pdf.png" border="0"></a></div><span id="left-title">申報 </span><span><b>日期：</b>1916-08-10 <b>版次/卷期：</b>06 版　<b>專欄：</b></span><h1>憲法起草委員會將開會
　　制定憲法爲此次國會中第一重要職務聞憲法起草委員會委員長湯漪君約集呼委員定今日</h1><div>七號<div><div class="content-box2"><span style="color:yellow;background-color:green">午</span><span style="color:yellow;background-color:green">前</span><span style="color:yellow;background-color:green">十</span><span style="color:yellow;background-color:green">時</span><span style="color:yellow;background-color:green">假</span><span style="color:yellow;background-color:green">衆</span><span style="color:yellow;background-color:green">議</span><span style="color:yellow;background-color:green">院</span><span style="color:yellow;background-color:green">小</span><span style="color:yellow;background-color:green">會</span><span style="color:yellow;background-color:green">場</span><span style="color:yellow;background-color:green">開</span><span style="color:yellow;background-color:green">談</span>話會大致因二年草定之案即俗稱天壇憲法草案者當時雖已草具理由咨交兩院合組之憲法會議但時隔三載似應撤回重加研究俟兩院正式開會將次議及憲法之時再行咨還大約撤回之後或將發生修正問題出頗聞有人主張擬將憲法起草委員會加以改組如參議員劉成禺君即其一人其意以爲起草民國憲法實最神聖莊嚴之職務斷不可任附逆分子混跡其中如李某孫某輩均非排除不可但多數意見以爲此屬議員資格問題聽兩院處置並非委員會内之問題且憲法起草委員會實與兩院鼎足而立兩院亦不能任意提議墏其改組因之不甚贊同說其<br>
</div><div>
			<b>其他紀元：</b>民國5年 日大正5年 <br>
			<b>類別：</b><br>
			<b>主題：</b>
			</div>
</div>
		<!--end content-box --></div>
<!--end content -->


<div id="footer">Copyright c 2012 得泓資訊. All Rights Reserved.</div>
 <!--end footer-->
</div>

수집 결과(csv): 144,14303,14303. 憲法起草委員會將開會 制定憲法爲此次國會中第一重要職務聞憲法起草委員會委員長湯漪君約集呼委員定今日,申報 日期：1916-08-10 版次/卷期：06 版 七號,https://z.library.sh.cn/http/80/10.1.30.77/yitlink/tm/tm_shownews.php?id=A2013040052905&qrygroup=1&qrynewstype=SP&n=14303,午前十時假衆議院小會場開談話會大致因二年草定之案即俗稱天壇憲法草案者當時雖已草具理由咨交兩院合組之憲法會議但時隔三載似應撤回重加研究俟兩院正式開會將次議及憲法之時再行咨還大約撤回之後或將發生修正問題出頗聞有人主張擬將憲法起草委員會加以改組如參議員劉成禺君即其一人其意以爲起草民國憲法實最神聖莊嚴之職務斷不可任附逆分子混跡其中如李某孫某輩均非排除不可但多數意見以爲此屬議員資格問題聽兩院處置並非委員會内之問題且憲法起草委員會實與兩院鼎足而立兩院亦不能任意提議墏其改組因之不甚贊同說其 其他紀元：民國5年 日大正5年 類別： 主題：

## 답변 1-3
문제 없이 갈 가능성이 높습니다.  
제시한 두 정상 사례를 보면, 내가 제안한 수정 방향은 **일반 구조를 깨지 않고 문제 사례만 보완하는 방향**입니다.

**핵심 판단**
지금 세 사례 모두 공통으로 가진 구조는 이것입니다.

- `#content-box_contentwrapper`
- 그 아래 제목 `h1`
- 그 아래 본문이 들어 있는 `.content-box2`

즉 정상 사례 1, 정상 사례 2, 문제 사례 모두 **실제 본문은 `.content-box2` 안에 있습니다.**  
반면 `h1`는 세 경우 모두 제목입니다.

그래서 현재 문제의 핵심은:
- 본문 selector가 실패했을 때
- fallback이 `h1`까지 내려가 있어서
- 제목을 본문으로 잘못 저장할 수 있다는 점입니다.

**왜 수정 방향이 일반 사례를 해치지 않나**
정상 사례 1:
- 본문: `#content-box_contentwrapper .content-box2`
- 실제 수집 결과도 이 영역 텍스트와 일치

정상 사례 2:
- 본문: `#content-box_contentwrapper .content-box2`
- 실제 수집 결과도 이 영역 텍스트와 일치

즉 두 정상 사례 모두 `.content-box2` selector로 그대로 잡힙니다.  
따라서 아래 변경은 일반 사례에도 부합합니다.

1. 본문 추출 1순위를 `.content-box2`로 둔다
2. `h1` fallback을 제거한다

이건 “일반 구조 변경”이 아니라, **실제 본문 컨테이너를 더 직접적으로 잡는 쪽으로 정밀화**하는 것입니다.

**지금 코드의 위험**
현재 [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)에서:
- [line 32](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:32)
- [line 35](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:35)

```python
DETAIL_TEXT_SELECTORS = [
    ("xpath", DETAIL_TEXT_XPATH),
    ("css", "#content-box_contentwrapper > div:nth-child(4) > div"),
    ("css", "#content-box_contentwrapper > h1"),
]
```

여기서 제일 위험한 건 마지막 줄입니다.
- `#content-box_contentwrapper > h1`

이건 본문이 아니라 제목이라서,
- 실패를 조용히 “제목 수집 성공”으로 바꿔버립니다.
- 이게 지금 같은 4~5% 오수집의 직접 원인입니다.

**권장 수정**
메타 절단은 하지 않는 전제로, 이 정도가 맞습니다.

```python
DETAIL_TEXT_SELECTORS = [
    ("css", "#content-box_contentwrapper .content-box2"),
    ("xpath", DETAIL_TEXT_XPATH),
]
```

그리고 `h1` fallback은 제거.

이렇게 하면:
- 정상 사례 1, 2: `.content-box2`로 정상 수집
- 문제 사례: `.content-box2`로 제목이 아닌 본문 수집
- 기존 XPath가 필요한 구조가 있으면 2순위로 계속 보완

**추가 방어 하나**
더 안전하게 하려면 `extract_detail_text()`에서
- 추출된 텍스트가 상세 페이지 `h1`와 동일하면 버리기
를 넣을 수 있습니다.

즉:
- selector가 실수로 제목을 잡아도
- 제목만 들어온 텍스트는 본문으로 인정하지 않음

이건 일반 사례를 거의 해치지 않는 안전장치입니다.

**결론**
- 제시한 정상 사례 둘을 보면, `.content-box2` 우선 + `h1` fallback 제거는 **일반 사례 수집에도 문제를 만들 가능성이 낮습니다**
- 오히려 현재보다 더 정확합니다
- 가장 합리적인 수정은:
  1. `.content-box2`를 1순위로 추가
  2. 기존 XPath는 보조 fallback으로 유지
  3. `h1` fallback 제거
  4. 제목과 동일한 텍스트는 본문으로 채택하지 않는 방어 로직 추가

원하면 이 기준으로 [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)를 바로 수정하겠습니다.

---

## 프롬프트 1-4
만약 추출된 텍스트가 상세 페이지 h1와 동일하면 버리기
를 할 경우, text에는 어떤 내용이 저장되지?

## 답변 1-4
그 조건만 **단독으로** 넣으면, 경우에 따라 두 가지입니다.

1. 뒤에 다른 본문 selector가 남아 있으면
- `h1`에서 얻은 텍스트를 버리고
- **다음 selector를 계속 시도**합니다
- 다음 selector가 성공하면 그 본문이 `text`에 저장됩니다

2. 뒤에 유효한 selector가 더 없으면
- 끝까지 본문을 못 찾은 것으로 처리됩니다
- 지금 코드 구조에서는 결국 예외가 나고,
- 최종 CSV에는 `text`에 `[ERROR] ...`가 들어가게 됩니다

즉 중요한 건:
- **“h1와 같으면 버리기”만 넣는다고 제목 대신 빈 문자열이 저장되는 건 아닙니다**
- 현재 구조에선 보통
  - 다음 selector로 넘어가거나
  - 전부 실패하면 `[ERROR] ...`
가 됩니다

이번 경우에 내가 권한 수정은 사실 이 둘을 같이 하는 것입니다.
1. `.content-box2`를 1순위로 올리기
2. `h1` fallback 제거
3. 추가 방어로 “제목과 같은 텍스트는 본문으로 인정하지 않기”

이렇게 하면, 제목만 저장되는 문제를 막으면서도 정상 본문은 계속 수집할 수 있습니다.

---

## 프롬프트 1-5
일단 그럼 위에 제시해준 수정 방안대로 코드를 수정해줘

## 답변 1-5
수정했습니다.

변경 파일:
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

반영 내용:
- 본문 추출 selector 우선순위 변경
  - `#content-box_contentwrapper .content-box2`를 1순위로 사용
  - 기존 XPath `//*[@id="content-box_contentwrapper"]/div[2]/div`는 보조 fallback으로 유지
- 제목 fallback 제거
  - `#content-box_contentwrapper > h1`는 더 이상 `text` 추출 selector로 사용하지 않음
- 방어 로직 추가
  - 추출된 텍스트가 상세 페이지 `h1` 제목과 완전히 같으면 본문으로 채택하지 않고 다음 selector를 계속 시도

의도:
- 일반적인 페이지에서는 기존처럼 `.content-box2` 본문이 수집됨
- 문제 사례처럼 구조가 약간 다른 페이지에서도 제목만 `text`에 들어가는 오수집을 막음
- `其他紀元：...` 메타는 요청대로 그대로 유지

검증:
- `py_compile` 통과
- `pyright` 통과: `0 errors, 0 warnings`

---
# 2. 수집 스키마 개선 및 구버전 호환 로직 정리

## 프롬프트 2-1
아래 지침에 따라 코드를 수정해줘.

1. item_index와 title 열을 기입하던 로직을 그대로 유지하되, 목록 페이지에서 가져오는 제목은 title 열이 아닌 list_title 이라는 열에 입력하고, title 열에는 이후 상세페이지 진입 후에 h1 부분을 가져와서 저장하도록 하는거야. 차라리 이렇게 하는게 데이터를 모두 가져와서 문제나 예외 발생을 점검하는 데 더 좋을 것 같아.

2. 추가로 결과 csv에 수집 키워드 label을 표시하는 열을 추가하고 싶어.(현재 생성된 파일들을 예로 들면, lixian, xianfa, xianzheng, zhixian 등을 가리킴)
결과적으로 이 코드를 통해 수집되는 csv는 다음과 같은 열 구성을 가져야 해.

label,page,item_index,list_title,publish,detail_url,title,text
zhixian,1,1,1. 波恩憲法分裂德國 德共產黨代表拒絕簽字,申報 日期：1949-05-26 版次/卷期：02 版 新華社北平廿五日電,https://z.library.sh.cn/http/80/10.1.30.77/yitlink/tm/tm_shownews.php?id=A2013040227679&qrygroup=1&qrynewstype=SP&n=1,波恩憲法分裂德國 德共產黨代表拒絕簽字,美英法集團一手製造的分裂主義的「憲法」，已於廿三日在波恩製憲議會的末次會議上宣佈生效。 ...

## 답변 2-1
수정했습니다.

변경 파일:
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

반영 내용:
1. `item_index` 추출 로직 유지
- 여전히 목록 페이지 제목에서 앞의 `숫자.`를 읽어 `item_index`를 계산합니다.

2. 목록 페이지 제목은 `list_title`로 저장
- 기존 `title`에 들어가던 목록 제목은 이제 `list_title` 열로 갑니다.

3. 상세 페이지 `h1`는 `title`로 저장
- 상세 진입 후 `#content-box_contentwrapper > h1`를 읽어 `title` 열에 넣습니다.

4. 결과 CSV에 `label` 열 추가
- `run_label` 값을 저장합니다.
- 열 순서는 아래처럼 바뀌었습니다.

```text
label,page,item_index,list_title,publish,detail_url,title,text
```

5. 재개 호환
- 예전 CSV를 다시 읽을 때 `list_title` 열이 없으면 기존 `title` 값을 `list_title`로 받아들이도록 처리했습니다.
- `label` 열이 없던 예전 CSV도 읽을 수 있습니다.

현재 저장 형식:
```text
label,page,item_index,list_title,publish,detail_url,title,text
zhixian,1,1,1. 波恩憲法分裂德國 德共產黨代表拒絕簽字,申報 日期：1949-05-26 版次/卷期：02 版 新華社北平廿五日電,https://...,波恩憲法分裂德國 德共產黨代表拒絕簽字,美英法集團一手製造的分裂主義的「憲法」...
```

검증:
- `py_compile` 통과
- `pyright` 통과: `0 errors, 0 warnings`

주의:
- 예전에 생성된 CSV에서 재개하는 경우, 이미 저장돼 있던 과거 행들은 당시 형식 그대로 남습니다.
- 즉 **새로 수집되는 행부터** `label/list_title/title` 분리 형식이 정확히 적용됩니다.

---

## 프롬프트 2-2
재개 호환 기능이 꼭 필요할까? 나는 지금 완성된 코드를 만들어서 그 코드의 기능을 학술 논문에서 설명해야 하는 상황인데, 그냥 완성된 코드로 새로 자료를 수집하는 게 더 적합하지 않을까?

## 답변 2-2
그렇습니다. 구분해서 봐야 합니다.

- **재개 기능 자체**
  - 유지하는 게 좋습니다
  - 이유: 이 크롤러는 로그인 만료, 페이지 오류, 장시간 실행 중단이 실제로 발생합니다
  - 학술적으로도 “중단 후 동일 형식의 출력 파일에서 재개 가능”은 설명 가능한 기능입니다

- **구버전 CSV와의 호환 기능**
  - 굳이 필요 없습니다
  - 이건 과거 작업물을 살리기 위한 운영 편의 기능일 뿐입니다
  - 논문에서 설명할 “완성된 수집기” 관점에서는 오히려 불필요한 복잡성입니다

즉 더 적합한 방향은:

1. **새 형식으로 처음부터 다시 수집**
2. **재개는 허용**
3. **단, 재개 대상은 현재 스키마의 CSV만 허용**
   - `label,page,item_index,list_title,publish,detail_url,title,text`

이렇게 가면 코드도 더 깔끔합니다.

현재 코드에서 제거 가능한 “구버전 호환” 부분은 주로 이것입니다.
- `load_resume_rows()`에서
  - `row.get("list_title", row.get("title", ""))`
  - `row.get("label", "")`

이런 fallback은 과거 스키마를 읽기 위한 장치입니다.  
완성본이라면 차라리:
- `list_title`와 `label`이 없으면 에러
로 두는 게 더 명확합니다.

내 권고:
- **재개 기능은 유지**
- **구버전 호환은 제거**
- **새 코드로 새로 수집**
- **기존 구형 CSV는 archive로 분리**

이게 논문 설명에도 가장 적합합니다.
- 구현 설명이 단순해짐
- 출력 스키마가 일관됨
- 예외 처리 논리가 덜 지저분해짐

원하면 바로 다음 단계로:
- `crawl_shenbao_chrome.py`에서 **구버전 CSV 호환 fallback만 제거**해서
- “최종 논문용 코드” 형태로 정리해드리겠습니다.

---

## 프롬프트 2-3
좋아. 구버전 csv 호환 fallback 부분을 제거해줘

## 답변 2-3
수정했습니다.

변경 파일:
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

변경 내용:
- `load_resume_rows()`에서 구버전 CSV 호환 fallback 제거
- 이제 재개 입력 CSV는 아래 현재 스키마를 **반드시** 가져야 합니다.

```text
label,page,item_index,list_title,publish,detail_url,title,text
```

구체적으로:
- 제거된 fallback
  - `row.get("label", "")`
  - `row.get("list_title", row.get("title", ""))`
  - `row.get("title", "")`
- 추가된 동작
  - 재개 파일 헤더를 먼저 검사
  - 위 필수 컬럼 중 하나라도 없으면 즉시 에러
  - 에러 메시지에 누락 컬럼명을 출력

의미:
- 이제 이 코드는 **현재 완성 스키마로 생성된 CSV만 재개 대상으로 인정**합니다
- 구버전 CSV를 억지로 읽어 맞추는 운영용 fallback은 제거됐습니다

검증:
- `py_compile` 통과
- `pyright` 통과: `0 errors, 0 warnings`

---

## 프롬프트 2-4
위 필수 컬럼 중 하나라도 없으면 즉시 에러  이 동작은 꼭 필요한걸까

## 답변 2-4
꼭 필요한 건 아닙니다.  
하지만 **지금 목표가 “완성된 코드의 명확한 동작 정의”라면 넣어두는 편이 더 낫습니다.**

이유는 간단합니다.

**왜 넣는 게 좋은가**
1. **재개 입력 스키마를 고정할 수 있음**
- 논문에서 설명할 때
- “이 스크립트는 이 스키마의 CSV를 출력하고, 같은 스키마의 CSV에서 재개한다”
라고 명확하게 말할 수 있습니다.

2. **조용한 오동작을 막음**
- 컬럼이 빠진 CSV를 억지로 읽으면
- 잘못된 열 매핑으로 재개가 틀어질 수 있습니다
- 이건 실패보다 더 안 좋습니다

3. **운영상 디버깅이 쉬움**
- 즉시 에러가 나면 원인을 바로 알 수 있습니다
- 반대로 느슨하게 읽으면 나중에 페이지나 item 재개가 어긋날 수 있습니다

**왜 없어도 되나**
현재 코드 맥락상 정말 중요한 재개 필드는 사실 몇 개뿐입니다.
- `page`
- `item_index`

엄격히 말하면 재개 자체만 생각하면:
- `label`
- `list_title`
- `publish`
- `detail_url`
- `title`
- `text`
전부가 꼭 있어야 하는 건 아닙니다.

즉 “마지막 어디까지 갔는지”만 계산하려면 최소 스키마로도 가능합니다.

**그래서 더 균형 잡힌 대안**
가장 좋은 타협은 이겁니다.

1. **재개에 필수인 최소 컬럼만 강제**
- `page`
- `item_index`

2. **나머지 출력 컬럼은 있으면 읽고, 없으면 빈 문자열**
- 단, 현재 저장은 항상 완성 스키마로 유지

이렇게 하면:
- 재개는 유연해지고
- 출력 스키마는 여전히 고정됩니다

**내 판단**
- 논문용 “완성 코드”라는 관점에서는 지금의 엄격 체크가 충분히 defensible 합니다
- 하지만 실용성까지 생각하면 **최소 필수 컬럼만 검사하는 쪽이 더 합리적**입니다

즉 답은:
- **꼭 필요한 것은 아니다**
- **엄격성 때문에 넣은 것**
- 더 실용적으로 하려면 `page`, `item_index`만 필수로 검사하면 충분합니다

원하면 바로 그 방향으로 완화해드리겠습니다.

---

## 프롬프트 2-5
기존 버전 코드에서는 어떤 필드를 기준으로 재개를 진행했었는지 현재 버전과 비교해서 알려줘

## 답변 2-5
비교 결과, **재개 지점 자체는 기존 버전과 현재 버전 모두 사실상 같은 필드로 계산합니다.**  
핵심은 `page`와 `item_index`입니다.

대상 파일:
- 기존 버전: [shlib-shenbao-dataset-workflow\crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\crawl_shenbao_chrome.py)
- 현재 버전: [coding\crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

**1. 기존 버전에서 재개 기준**
기존 버전은 재개 파일을 읽을 때 아래 필드를 사용했습니다.
- `page`
- `item_index`
- 보조 저장용: `title`, `publish`, `detail_url`, `text`

관련 위치:
- 재개 파일 읽기: [기존 load_resume_rows](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\crawl_shenbao_chrome.py:593)
- 재개 지점 계산: [기존 get_resume_target](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\crawl_shenbao_chrome.py:618)

동작:
- 마지막 행의 `page` 읽음
- 마지막 행의 `item_index` 읽음
- `item_index > 100`이면 전역 번호로 보고 현재 페이지 내 local offset으로 환산
- 마지막 행을 메모리에서 제거한 뒤, **그 마지막 기록 행부터 다시 재수집**

즉 기존 버전의 실제 재개 기준은:
- **`page`**
- **`item_index`**

입니다.

**2. 현재 버전에서 재개 기준**
현재 버전도 재개 지점 계산 자체는 동일합니다.

관련 위치:
- 재개 파일 읽기: [현재 load_resume_rows](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:605)
- 재개 지점 계산: [현재 get_resume_target](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:649)

현재도:
- 마지막 행의 `page`
- 마지막 행의 `item_index`
를 읽어서 재개 지점을 계산합니다.

즉 **현재 버전도 재개 위치 계산은 `page + item_index` 기준**입니다.

**3. 달라진 점**
달라진 것은 “재개 위치 계산 기준”이 아니라 **재개 입력 CSV의 스키마와 보조 필드**입니다.

기존 버전의 출력/재개 스키마:
- `page,item_index,title,publish,detail_url,text`

현재 버전의 출력/재개 스키마:
- `label,page,item_index,list_title,publish,detail_url,title,text`

그리고 현재 버전은:
- `label`로 재개 파일 선택을 더 명확하게 할 수 있음
- `list_title`와 `title`를 분리함
- 구버전 CSV fallback을 제거해서 **현재 스키마만 재개 허용**

하지만 재개 지점 계산 로직 자체는 여전히:
- **`page`**
- **`item_index`**
입니다.

**4. 보조적으로 파일 선택에 쓰는 필드**
재개가 시작되기 전에 “어느 파일을 재개할지”를 고를 때는 `label`이 영향을 줍니다.
- 현재: [find_latest_resume_file](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:571)
- 기존: [find_latest_resume_file](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\crawl_shenbao_chrome.py:563)

즉 정리하면:
- **재개 파일 선택**: `label`이 관여할 수 있음
- **재개 행 위치 계산**: `page`와 `item_index`만 사용

**결론**
- 기존 버전과 현재 버전 모두, **재개 지점은 `page`와 `item_index`를 기준으로 계산**합니다.
- 현재 버전은 여기에
  - `label` 추가
  - `list_title/title` 분리
  - 현재 스키마만 허용
이 붙은 것입니다.
- 따라서 “재개 기준 필드” 자체는 **기존과 현재가 본질적으로 동일**합니다.

---

## 프롬프트 2-6
내가 어차피 기존 파일을 별도의 archive 폴더로 옮겨 놓을거라면, `현재 스키마만 허용` 관련 라인은 필요하지 않을 것 같아

## 답변 2-6
제거했습니다.

변경 파일:
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

변경 내용:
- `load_resume_rows()` 안의 명시적 “현재 스키마만 허용” 검사 블록 삭제
- 이제 재개 파일은 별도 사전 검증 없이 바로 읽습니다

의미:
- `archive`로 구버전 파일을 분리해 둘 전제라면 이 편이 더 단순합니다
- 현재 스키마를 만족하지 않는 파일이 실수로 재개 대상으로 들어오면, 그때는 필요한 필드 접근 시점에 일반적인 `KeyError`/파싱 오류가 납니다

검증:
- `py_compile` 통과
- `pyright` 통과: `0 errors, 0 warnings`

---
# 3. 상세 페이지 제목 수집 오류와 CSV 필드 제한 처리

## 프롬프트 3-1
현재 코드에서 h1을 title로 가져오는 동작이 제대로 시행되지 않고 있는 것 같아. 해당 라인이 모두 비어있어. 뭐가 문제인지 검토해봐

## 답변 3-1
원인은 **시점 문제**입니다.  
`h1` selector가 틀렸다기보다, **너무 이른 시점에 한 번만 읽고 끝내고 있기 때문**입니다.

확인한 사실:
- 최신 출력 파일 [shenbao_textdata_xianfa_1to80.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_xianfa_1to80.csv) 에서
  - `list_title`은 정상
  - `title`은 초반 행들이 전부 빈 문자열
- 즉 `detail_title`이 실제로 저장되지 않고 있습니다.

**문제 지점**
1. 상세 `title` 읽기 함수
- [crawl_shenbao_chrome.py:437](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:437)

```python
def extract_detail_title(scope: Page | Frame) -> str:
    try:
        title_locator = scope.locator("css=#content-box_contentwrapper > h1").first
        if title_locator.count():
            return normalize_text(title_locator.inner_text())
    except PlaywrightError:
        pass
    return ""
```

2. 이 함수가 호출되는 시점
- [crawl_shenbao_chrome.py:796](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:796)

```python
detail_title = extract_detail_title(detail_active.scope)
detail_text = extract_detail_text(...)
```

즉 현재는:
- 상세 페이지 진입 직후
- `h1`를 **딱 한 번만** 읽습니다.

반면 `text`는 다릅니다.
- [crawl_shenbao_chrome.py:446](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:446)

`extract_detail_text()`는 최대 60초까지 반복 대기하면서 본문을 찾습니다.  
그래서:
- `title`은 너무 빨리 읽어서 빈 문자열
- `text`는 나중에 로드가 끝난 뒤 정상 추출

이 상황이 생깁니다.

**왜 이런 일이 생기나**
`wait_for_detail_scope()`는 상세 페이지가 “완전히 다 로드된 상태”를 보장하지 않습니다.  
현재는 대략 이런 조건만 만족하면 반환합니다.
- 상세 URL로 이동했거나
- 특정 본문 selector가 보이기 시작했거나

그 직후엔:
- `h1`가 아직 렌더링 전일 수 있습니다
- 그래서 `extract_detail_title()`는 빈 문자열 반환
- 이후 본문은 조금 늦게 로드되어 `extract_detail_text()`에서는 성공

**결론**
- 문제는 `h1` selector 자체보다
- **`title`만 재시도/대기 없이 한 번 읽는 구조**입니다.

**해결 방향**
가장 맞는 수정은 둘 중 하나입니다.

1. `extract_detail_title()`도 `extract_detail_text()`처럼 **폴링**하게 만들기
- 최대 60초까지 기다리되
- `h1`가 생기면 즉시 반환

2. 더 깔끔한 방법:
- `detail_text` 추출 성공 후에
- 같은 scope에서 `h1`를 다시 읽기

내 판단:
- **1번이 가장 자연스럽습니다.**
- 현재 구조를 크게 안 바꾸고 바로 해결됩니다.

즉 요약하면:
- `title`이 비는 이유는 **상세 `h1`를 너무 빨리, 한 번만 읽기 때문**
- `text`는 재시도 로직이 있어서 성공하고, `title`은 없어서 실패하는 구조입니다

원하면 바로 이 부분까지 수정하겠습니다.

---

## 프롬프트 3-2
그럼 1번 제안대로, title 추출을 text 추출과 마찬가지 로직으로 시도하도록 수정해줘

## 답변 3-2
수정했습니다.

변경 파일:
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

변경 내용:
- `extract_detail_title()`를 단발성 조회에서 **조건부 장기 대기 방식**으로 변경
- 이제 `text` 추출과 같은 철학으로 동작합니다.
  - `h1`가 바로 없으면 실패하지 않음
  - 최대 `MAX_RESULT_WAIT_MS` 범위에서 계속 폴링
  - `h1` 텍스트가 생기면 즉시 반환

문제 원인과 수정 효과:
- 기존에는 상세 페이지 진입 직후 `h1`를 한 번만 읽어서 `title`이 빈 문자열로 남을 수 있었습니다
- 이제는 `h1` 렌더링이 늦어도 기다렸다가 채워집니다

검증:
- `py_compile` 통과
- `pyright` 통과: `0 errors, 0 warnings`

---

## 프롬프트 3-3
아래와 같은 에러 메시지가 나왔어. 뭐가 문제일까

```powershell
Found existing file for label 'xianfa': C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_xianfa_1to1884.csv
Traceback (most recent call last):
  File "C:\Users\class\Documents\coding\crawl_shenbao_chrome.py", line 909, in <module>
    main()
  File "C:\Users\class\Documents\coding\crawl_shenbao_chrome.py", line 712, in main
    rows = load_resume_rows(resume_path)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\class\Documents\coding\crawl_shenbao_chrome.py", line 617, in load_resume_rows
    for row in reader:
  File "C:\Python311\Lib\csv.py", line 111, in __next__        
    row = next(self.reader)
          ^^^^^^^^^^^^^^^^^
_csv.Error: field larger than field limit (131072)
```

## 답변 3-3
문제는 CSV 구조가 아니라 **파이썬 `csv` 모듈의 기본 필드 길이 제한**입니다.

에러 의미:
- 재개 파일 [shenbao_textdata_xianfa_1to1884.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_xianfa_1to1884.csv) 를 읽는 중
- 어떤 행의 한 컬럼 값, 거의 확실히 `text`, 가
- 기본 허용 크기 `131072` 문자를 넘었습니다

즉:
- 크롤링이 잘못된 게 아니라
- **본문이 긴 기사**가 하나 이상 있어서
- `csv.DictReader`가 읽다가 멈춘 겁니다

현재 실패 지점:
- [crawl_shenbao_chrome.py:617](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py:617)
- `for row in reader:`

**원인**
Python의 `csv` 모듈은 기본적으로 필드 최대 길이가 작습니다.  
신문 본문을 통째로 넣는 지금 구조에서는 긴 기사 하나만 있어도 충분히 걸립니다.

**해결**
코드 시작 부분에서 `csv.field_size_limit(...)`를 크게 올리면 됩니다.

보통 이렇게 처리합니다.
```python
csv.field_size_limit(10_000_000)
```

또는 더 보수적으로:
```python
csv.field_size_limit(sys.maxsize)
```

다만 Windows/Python 환경에 따라 `sys.maxsize`는 너무 클 수 있으니, 보통은 적당히 큰 값으로 잡는 게 안전합니다.

**결론**
- 문제는 재개 파일의 `text` 필드가 너무 길어서 발생한 것
- 해결은 `csv.field_size_limit` 상향
- 이건 재개 읽기뿐 아니라 앞으로 긴 기사 처리에도 필요한 수정입니다

원하면 바로 [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)에 반영하겠습니다.

---

### 프롬프트 3-3-1
일단 해당 파일 안에서 어떤 행 때문에 길이 문제가 발생했는지 확인해줘

### 답변 3-3-1
문제 행은 하나입니다.

대상 파일:
- [shenbao_textdata_xianfa_1to1884.csv](C:\Users\class\Documents\coding\shenbao\shenbao_textdata\shenbao_textdata_xianfa_1to1884.csv)

확인 결과:
- 초과 필드 수: `1건`
- 문제 행:
  - CSV 물리 행 번호: `727`행
  - `item_index`: `726`
  - 문제 컬럼: `text`
  - 길이: `322522`자

즉 재개가 실패한 직접 원인은:
- `item_index=726` 행의 `text` 필드가 너무 길어서
- Python `csv` 기본 한도 `131072`를 넘은 것입니다

최대값도 동일합니다.
- 최대 필드 = `item_index=726`, `text`, `322522`

다음 단계로 필요한 건 명확합니다.
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)에 `csv.field_size_limit(...)`를 추가해야 합니다

원하면 바로 반영하겠습니다.

---

### 프롬프트 3-3-2
그럼 csv.field_size_limit을 1000000자로 올려 시행하도록 코드를 수정해줘

### 답변 3-3-2
수정했습니다.

변경 파일:
- [crawl_shenbao_chrome.py](C:\Users\class\Documents\coding\crawl_shenbao_chrome.py)

변경 내용:
- 파일 상단에 아래 설정 추가
```python
csv.field_size_limit(1_000_000)
```

효과:
- `csv.DictReader`가 기본 한도 `131072` 대신 최대 `1000000`자까지 한 필드를 읽을 수 있습니다
- 앞서 문제였던 `text` 길이 `322522`짜리 행도 이제 재개 시 읽을 수 있습니다

검증:
- `py_compile` 통과
- `pyright` 통과: `0 errors, 0 warnings`

---
# 4. 목록 제목과 상세 제목의 대응 관계 검토

## 프롬프트 4-1
shlib-shenbao-dataset-workflow\shenbao_textdata 내 csv 내용 중에서, list_title열과 title 열 사이에 어떤 차이가 있는지 검토해줘. 단, 둘 사이의 비교에서 list_title 값 전방에 포함된 일련번호("{숫자}. ")는 고려하지 않아도 돼. 일련번호 부분을 제외하고 두 열 값이 완전히 일치하는 사례가 어느 정도 비중을 차지하는지, 두 열의 내용이 다른 행이 존재한다면, 주로 어떤 지점에서 차이가 발생하는지 등을 검토하고, 유형별 카운트도 해줘

## 답변 4-1
검토 대상:
- [shenbao_textdata_lixian_1to7203.csv](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\shenbao_textdata_lixian_1to7203.csv)
- [shenbao_textdata_xianfa_1to18648.csv](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\shenbao_textdata_xianfa_1to18648.csv)
- [shenbao_textdata_xianzheng_1to9906.csv](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\shenbao_textdata_xianzheng_1to9906.csv)
- [shenbao_textdata_zhixian_1to4322.csv](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\shenbao_textdata\shenbao_textdata_zhixian_1to4322.csv)

비교 방식:
- `list_title` 앞의 `숫자. ` 부분은 제거했습니다.
- 그 뒤의 `list_title` 값과 `title` 값을 비교했습니다.
- “완전 일치”는 공백 차이까지 포함해 문자열이 정확히 같은 경우로 계산했습니다.
- 별도로 공백 차이만 있는 경우도 따로 집계했습니다.

**전체 결과**
총 `40,078`행 중:
- 완전 일치: `25,971건` / `64.80%`
- 공백 차이만 존재: `5,006건` / `12.49%`
- 구두점·공백 차이만 존재: `25건` / `0.06%`
- 실질적 차이 존재: `9,076건` / `22.65%`
- `title` 빈 값: `7건`
- `list_title` 빈 값: `1건`

공백·구두점 차이까지 사실상 동일한 제목으로 보면:
- `31,002건` / `77.35%`

즉, 엄격한 완전 일치 기준으로는 약 `65%`, 공백·구두점 차이를 무시하면 약 `77%`가 사실상 같은 제목입니다.

**파일별 일치율**

| 파일          |   전체 행 |  완전 일치 | 완전 일치 비율 | 공백·구두점 차이까지 허용한 일치 |
| ----------- | -----: | -----: | -------: | -----------------: |
| `lixian`    |  7,203 |  4,402 |   61.11% |     5,681 / 78.87% |
| `xianfa`    | 18,648 | 12,196 |   65.40% |    14,036 / 75.27% |
| `xianzheng` |  9,906 |  6,170 |   62.29% |     7,779 / 78.53% |
| `zhixian`   |  4,322 |  3,203 |   74.11% |     3,506 / 81.12% |

**차이 유형별 집계**

| 유형                                | 전체 건수 | 의미                                      |
| --------------------------------- | ----: | --------------------------------------- |
| `whitespace_only`                 | 5,006 | 내용은 같지만 띄어쓰기만 다름                        |
| `different_content`               | 4,115 | 목록 제목에 생략부호 `...`가 들어가거나, 상세 제목과 상당히 다름 |
| `list_title_inside_detail_title`  | 2,869 | 목록 제목이 상세 제목의 일부 구간으로 포함됨               |
| `detail_title_extends_list_title` | 2,085 | 상세 제목이 목록 제목으로 시작하지만 더 길게 이어짐           |
| `punct_or_spacing_only`           |    25 | 구두점·생략부호·공백 차이만 있음                      |
| `title_empty`                     |     7 | 상세 페이지 제목 추출 실패 또는 오류 행                 |
| `list_title_empty`                |     1 | 목록 제목이 비어 있음                            |

**주요 차이 양상**
1. 공백 삽입 차이
- 가장 단순한 차이입니다.
- 목록 제목은 붙어 있고, 상세 제목은 단어 사이에 공백이 들어간 경우가 많습니다.
- 예:
  - `list_title`: `社評比王投降與歐戰展望`
  - `title`: `社評 比王投降與歐戰展望`
- 이런 경우는 실질적으로 같은 제목으로 보아도 무방합니다.

2. 목록 제목의 생략부호
- `different_content`로 분류된 `4,115건`은 모두 목록 제목 쪽에 `...` 또는 유사한 생략부호가 포함되어 있었습니다.
- 즉 목록 페이지에서는 긴 제목이나 긴 제목+본문 일부를 축약해 보여 주고, 상세 페이지의 `h1`에는 더 긴 문자열이 들어 있는 경우입니다.
- 예:
  - `list_title`: `社論越南走向分裂之路 紛擾已久的越南問題，現巳進入新的分裂階段了。據中央社消息...`
  - `title`: `社論 越南走向分裂之路 紛擾已久的越南問題，現巳進入新的分裂階段了。據中央社消息。越南新中央臨時政府...`

3. 상세 제목이 목록 제목보다 긴 경우
- `detail_title_extends_list_title`가 `2,085건`입니다.
- 목록 제목은 상세 제목의 앞부분만 담고 있고, 상세 페이지 `h1`에는 더 긴 제목 또는 제목과 기사 도입부가 이어지는 경우입니다.
- 예:
  - `list_title`: `希望深長考慮 奠立憲政初基 ... 我認爲`
  - `title`: `希望深長考慮 奠立憲政初基 ... 我認爲五五憲草，在今天是不適用的...`

4. 목록 제목이 상세 제목 내부의 일부 구간인 경우
- `list_title_inside_detail_title`가 `2,869건`입니다.
- 이는 목록 페이지가 상세 제목의 시작 부분이 아니라, 검색어가 포함된 중간 구간을 보여 주는 경우로 보입니다.
- 특히 검색 결과 목록이 “제목”이라기보다 검색어 주변 문맥 일부를 함께 보여 주는 방식일 때 이런 현상이 나타납니다.

5. 상세 제목 추출 실패
- `title_empty`는 `7건`뿐입니다.
- 대체로 본문 추출 오류 행과 연결되어 있습니다.
- 즉 구조적 다수 현상이 아니라 예외적 실패 사례입니다.

**해석**
`list_title`과 `title`은 같은 정보를 가리키는 경우가 많지만, 완전히 동일한 필드는 아닙니다.

- `list_title`은 검색 결과 목록에서 보이는 제목 또는 검색어 주변 요약 문자열입니다.
- `title`은 기사 상세 페이지의 `#content-box_contentwrapper > h1`에서 추출한 제목입니다.
- 따라서 `list_title`에는 검색 결과 일련번호, 축약부호, 검색어 주변 문맥, 제목 일부가 섞일 수 있습니다.
- 반면 `title`은 상세 페이지 기준의 제목이므로, 더 길거나 더 정돈된 형태인 경우가 많습니다.

---

## 프롬프트 4-2
반대로 목록 제목이 상세 제목보다 더 긴 경우도 있나?

## 답변 4-2
검토 기준은 다음처럼 잡았습니다.

- `list_title` 앞의 `숫자. `는 제거
- 공백 차이는 무시
- 구두점과 생략부호 자체는 비교에서 제외
- `list_title`에는 있지만 `title`에는 없는 실질 문자열 조각이 같은 행의 `text`에 포함되는지 확인

**결론**
`list_title`에 생략부호가 있는 경우는 거의 모두 상세 페이지의 `title`이 길어서 목록 화면에서 앞부분만 생략 표시와 함께 보여준 사례였습니다. 즉, `list_title`에만 있고 `title`에는 없는 별도 내용이 `text`에 들어 있는 구조는 거의 확인되지 않았습니다.

**1. 목록 제목에 생략부호가 포함된 경우**

| 파일 | 생략부호 포함 행 | 생략부호 제거 후 목록 제목이 `title`에 포함 | `title`에는 없지만 `text`에 포함 | 기타/확인 불가 |
|---|---:|---:|---:|---:|
| `lixian` | 556 | 556 | 0 | 0 |
| `xianfa` | 2,313 | 2,311 | 1 | 1 |
| `xianzheng` | 839 | 839 | 0 | 0 |
| `zhixian` | 438 | 437 | 0 | 1 |
| 합계 | 4,146 | 4,143 | 1 | 2 |

해석하면, 생략부호 포함 행 4,146건 중 4,143건은 `list_title`의 실질 내용이 이미 `title` 안에 포함되어 있었습니다. 따라서 이 경우는 대체로 “목록 제목이 상세 제목보다 별도 정보를 더 갖고 있는 경우”가 아니라, “상세 제목이 너무 길어 목록 페이지에서 축약 표시된 경우”로 보는 것이 맞습니다.

예외는 다음과 같습니다.

- `xianfa`, `item_index=726`
  - `list_title`: `Detamore, World Traveller and Bible Lecturer pres...`
  - `title`: 비어 있음
  - `text`: 같은 문자열이 포함됨
  - 해석: 상세 제목 추출은 실패했지만, 목록 제목의 내용은 본문 텍스트 안에서 확인됨

- `zhixian`, `item_index=2907`
  - `list_title`: `參議院議决常會會期案 ...`
  - `title`: 비어 있음
  - `text`: `[ERROR] TimeoutError ...`
  - 해석: 상세 페이지 본문 수집 자체가 실패했기 때문에, `text` 포함 여부를 확인할 수 없음

- `xianfa`, `item_index=6907`
  - `list_title`와 `title`이 모두 `?`로 되어 있어 실질 비교 대상이 없음
  - 이 행은 의미 있는 제목 비교 사례라기보다 원천 데이터 또는 문자 인식상의 예외로 보는 편이 적절합니다.

**2. 목록 제목이 긴 요약 문자열처럼 보이는 경우**

단순 글자 수 기준으로는 `list_title`이 `title`보다 긴 행이 100건 있었습니다.

| 파일 | 단순 글자 수 기준 `list_title`이 더 긴 행 |
|---|---:|
| `lixian` | 10 |
| `xianfa` | 57 |
| `xianzheng` | 21 |
| `zhixian` | 12 |
| 합계 | 100 |

하지만 이 100건 대부분은 공백, 구두점, 표기 차이 때문에 길이가 달라진 경우였습니다. 공백·구두점·생략부호를 제거하고 실질 문자열 기준으로 다시 보면, 실제로 `list_title`에만 있는 내용이 확인되는 행은 7건뿐이었습니다.

| 파일 | 실질적으로 `list_title`에만 있는 문자열이 있는 행 | 그 문자열이 `text`에 포함 | `text`에서 확인 안 됨 |
|---|---:|---:|---:|
| `lixian` | 1 | 0 | 1 |
| `xianfa` | 3 | 1 | 2 |
| `xianzheng` | 2 | 0 | 2 |
| `zhixian` | 1 | 0 | 1 |
| 합계 | 7 | 1 | 6 |

중요한 점은 이 7건 모두 `title`이 비어 있는 행이었다는 것입니다. 즉, 정상적으로 상세 페이지 `h1`이 수집된 행에서 `list_title`이 `title`보다 더 많은 실질 정보를 담고 있는 사례는 확인되지 않았습니다.

`text`에서 확인되지 않은 6건은 대부분 본문 수집 실패 행이었습니다. 예를 들면 다음과 같습니다.

- `lixian`, `item_index=3816`
  - `list_title`: `擬辦四鄉巡警杭州`
  - `title`: 비어 있음
  - `text`: `[ERROR] TimeoutError ...`

- `xianzheng`, `item_index=8494`
  - `list_title`: `論說 再論于式枚奏陳立憲之謬 ...`
  - `title`: 비어 있음
  - `text`: `[ERROR] TimeoutError ...`

따라서 “목록 제목이 긴 요약 문자열처럼 보이는 경우”도 실제로는 독립적인 요약문이 `text`에 들어 있는 경우라기보다, 상세 제목 또는 본문 수집이 실패한 예외 행에서 `list_title`만 남아 있는 경우로 보는 것이 더 타당합니다.

---

## 프롬프트 4-3
목록 제목과 상세 제목 간 차이 유형 중 `different_content`로 분류된 `4,115건`을 더 상세하게 분류해줘

## 답변 4-3
`different_content` 4,115건을 다시 세분화해 보니, 실제로는 서로 다른 내용이 섞인 유형이 아니라 **전부 목록 제목의 말줄임표 생략형**이었습니다.

즉, 이전 분류의 `different_content`는 이름이 다소 부정확합니다. 더 정확한 명칭은 다음 중 하나가 적절합니다.

- `목록 제목 생략형`
- `목록 제목 절단형`
- `상세 제목 접두부 축약형`

**1. 라벨별 분포**

| 라벨 | `different_content` | 세부 판정 |
|---|---:|---|
| lixian | 556 | 전부 목록 제목 생략형 |
| xianfa | 2,290 | 전부 목록 제목 생략형 |
| xianzheng | 835 | 전부 목록 제목 생략형 |
| zhixian | 434 | 전부 목록 제목 생략형 |
| 합계 | 4,115 | 전부 목록 제목 생략형 |

**2. 세부 유형**

| 세부 유형 | 건수 | 비율 |
|---|---:|---:|
| 생략부호 제거 후, 목록 제목이 상세 제목의 앞부분과 일치 | 4,113 | 99.95% |
| 생략부호·공백·구두점 제거 후, 목록 제목이 상세 제목의 앞부분과 일치 | 2 | 0.05% |
| 목록 제목이 상세 제목이 아니라 본문에만 대응 | 0 | 0.00% |
| 목록 제목과 상세 제목·본문이 모두 불일치 | 0 | 0.00% |
| 합계 | 4,115 | 100.00% |

따라서 `different_content` 4,115건은 실질적으로 다음 구조입니다.

```text
list_title: 상세 제목의 앞부분 + ...
title:      상세 제목 전체
```

예를 들면 다음과 같은 방식입니다.

```text
list_title:
社論越南走向分裂之路 紛擾已久的越南問題，現巳進入新的分裂階段了。據中央社消息。越南新中央臨時政府...

title:
社論 越南走向分裂之路 紛擾已久的越南問題，現巳進入新的分裂階段了。據中央社消息。越南新中央臨時政府，於本月二十日在西貢宣吿成立，...
```

이 경우 `list_title`이 `title`과 다른 내용을 갖는 것이 아니라, `title`의 앞부분만 목록 페이지에서 표시된 것입니다.

**3. 생략부호 위치**

| 항목 | 건수 |
|---|---:|
| 생략부호가 `list_title` 끝에 위치 | 4,115 |
| 생략부호가 중간 또는 앞쪽에 위치 | 0 |

즉, 모두 목록 제목 말미의 생략부호입니다.

**4. 생략된 상세 제목 길이**

생략부호 뒤에 상세 제목에서 추가로 이어지는 문자열 길이를 계산하면 다음과 같습니다. 여기서는 공백·구두점·생략부호를 제외한 문자 수 기준입니다.

| 생략된 후속 문자열 길이 | 건수 |
|---|---:|
| 1-50자 | 1,311 |
| 51-100자 | 714 |
| 101-200자 | 769 |
| 201-500자 | 796 |
| 501-1000자 | 339 |
| 1001자 이상 | 186 |
| 합계 | 4,115 |

요약 통계는 다음과 같습니다.

| 항목 | 값 |
|---|---:|
| 최소 | 1자 |
| 중앙값 | 104자 |
| 평균 | 254.69자 |
| 최대 | 9,947자 |

이 결과는 일부 상세 페이지의 `h1`이 일반적인 짧은 제목이 아니라, 제목과 기사 앞부분 또는 긴 요약성 문자열을 함께 포함하고 있음을 보여줍니다.

**해석**

이전에 `different_content`로 분류된 4,115건은 실제로 “목록 제목과 상세 제목의 내용이 서로 다른 경우”라기보다, **목록 페이지에서 상세 제목의 앞부분만 보여주고 말줄임표로 생략한 경우**입니다. 따라서 논문에서는 `different_content`라는 표현을 그대로 쓰기보다는 다음처럼 수정하는 것이 좋습니다.

> 목록 제목 생략형

또는 표의 열 제목으로는 더 짧게:

> 생략형 제목

---

## 프롬프트 4-4
`list_title_inside_detail_title`, `detail_title_extends_list_title` 유형에 대해서도 마찬가지로 더 상세하게 분류해줘

## 답변 4-4
두 유형을 세분화한 결과, 둘 다 실제로는 “내용 불일치”라기보다 **상세 페이지 `h1`이 매우 길고, 목록 페이지가 그중 일부만 표시한 경우**로 해석하는 것이 적절합니다.

##### 1. `list_title_inside_detail_title`

이 유형은 총 **2,869건**입니다.

의미는 다음과 같습니다.

```text
title:      [앞부분] + list_title + [뒷부분]
list_title:            [상세 제목 내부의 일부]
```

즉, 목록 제목이 상세 제목의 처음부터 시작하지 않고, 상세 제목 내부의 한 구간으로 나타난 경우입니다.

##### 세부 분류

| 세부 유형 | 건수 | 비율 | 설명 |
|---|---:|---:|---|
| 상세 제목 중간부 표시 | 2,439 | 85.01% | `list_title` 앞뒤로 상세 제목의 다른 문자열이 모두 존재 |
| 상세 제목 말미 표시 | 430 | 14.99% | `list_title` 앞에는 상세 제목의 다른 문자열이 있고, 뒤에는 없음 |
| 합계 | 2,869 | 100.00% |  |

라벨별로 보면 다음과 같습니다.

| 라벨 | 합계 | 상세 제목 중간부 표시 | 상세 제목 말미 표시 |
|---|---:|---:|---:|
| lixian | 551 | 473 | 78 |
| xianfa | 1,378 | 1,165 | 213 |
| xianzheng | 722 | 617 | 105 |
| zhixian | 218 | 184 | 34 |
| 합계 | 2,869 | 2,439 | 430 |

##### 상세 제목 안에서 생략된 앞뒤 문자열 길이

이 유형에서는 `list_title`이 상세 제목의 중간 또는 끝부분에 해당하므로, 상세 제목 안에서 `list_title` 앞에 빠진 문자열이 존재합니다.

| 항목 | 최소 | 중앙값 | 평균 | 최대 |
|---|---:|---:|---:|---:|
| `list_title` 앞쪽에 있는 상세 제목 문자열 | 80자 | 197자 | 373.96자 | 4,539자 |
| `list_title` 뒤쪽에 있는 상세 제목 문자열 | 0자 | 212자 | 372.86자 | 4,309자 |

여기서 중요한 점은 `list_title` 앞쪽에 생략된 문자열의 최소값도 80자라는 것입니다. 따라서 이 유형은 단순히 “짧은 말머리”가 붙은 정도가 아니라, 상세 제목 또는 상세 페이지 `h1`의 상당히 긴 앞부분이 목록 제목에서 빠진 경우입니다.

##### 검색어 위치

`list_title_inside_detail_title` 유형에서 검색어가 `list_title` 안에 나타나는 위치를 보면 다음과 같습니다.

| 검색어 위치 | 건수 |
|---|---:|
| 목록 제목 앞쪽 | 607 |
| 목록 제목 중간 | 1,697 |
| 목록 제목 뒤쪽 | 529 |
| 목록 제목에 검색어 없음 | 36 |
| 합계 | 2,869 |

검색어가 목록 제목 중간에 위치한 경우가 가장 많습니다. 따라서 이 유형은 목록 페이지가 상세 제목 전체를 보여준 것이 아니라, 검색어 주변의 문맥 일부를 잘라 보여준 **검색어 중심 문맥 표시형**으로 해석할 수 있습니다.

논문용 명칭으로는 다음이 적절합니다.

> 검색어 주변 문맥형

또는 조금 더 기술적으로:

> 상세 제목 내부 문맥형

##### 2. `detail_title_extends_list_title`

이 유형은 총 **2,085건**입니다.

의미는 다음과 같습니다.

```text
list_title: [상세 제목의 앞부분]
title:      [상세 제목의 앞부분] + [추가 문자열]
```

즉, 목록 제목이 상세 제목의 시작부와 일치하고, 상세 제목이 그 뒤로 더 길게 이어지는 경우입니다.

##### 세부 분류

이 유형은 모두 같은 구조였습니다.

| 세부 유형 | 건수 | 비율 | 설명 |
|---|---:|---:|---|
| 상세 제목 후속 확장 | 2,085 | 100.00% | `title`이 `list_title`으로 시작하고 뒤에 추가 문자열이 이어짐 |

라벨별로 보면 다음과 같습니다.

| 라벨 | 상세 제목 후속 확장 |
|---|---:|
| lixian | 414 |
| xianfa | 940 |
| xianzheng | 568 |
| zhixian | 163 |
| 합계 | 2,085 |

##### 추가된 후속 문자열 길이

| 후속 문자열 길이 | 건수 |
|---|---:|
| 1-5자 | 52 |
| 6-20자 | 160 |
| 21-50자 | 261 |
| 51-100자 | 296 |
| 101-500자 | 835 |
| 501자 이상 | 481 |
| 합계 | 2,085 |

요약 통계는 다음과 같습니다.

| 항목 | 값 |
|---|---:|
| 최소 | 1자 |
| 중앙값 | 169자 |
| 평균 | 372.43자 |
| 최대 | 6,870자 |

즉, 이 유형도 단순히 한두 글자가 누락된 경우가 아닙니다. 상당수는 상세 페이지 `h1`이 목록 제목보다 훨씬 길게 이어지는 구조입니다.

##### 짧은 확장과 긴 확장

| 세부 유형 | 기준 | 건수 | 비율 |
|---|---|---:|---:|
| 짧은 후속 확장 | 추가 문자열 20자 이하 | 212 | 10.17% |
| 긴 후속 확장 | 추가 문자열 21자 이상 | 1,873 | 89.83% |
| 합계 |  | 2,085 | 100.00% |

대부분은 긴 후속 확장입니다.

검색어 위치도 확인하면 다음과 같습니다.

| 검색어 위치 | 건수 |
|---|---:|
| 목록 제목 앞쪽 | 769 |
| 목록 제목 중간 | 1,012 |
| 목록 제목 뒤쪽 | 267 |
| 목록 제목에 검색어 없음 | 37 |
| 합계 | 2,085 |

이 유형 역시 목록 제목이 단순한 기사 제목 전체라기보다, 상세 페이지 `h1`의 앞부분만 제한적으로 표시한 경우가 많습니다.

논문용 명칭으로는 다음이 적절합니다.

> 상세 제목 후속 확장형

또는 더 짧게:

> 후속 확장형

#### 종합 해석

세 유형을 함께 보면 다음처럼 정리할 수 있습니다.

| 기존 분류명 | 건수 | 재해석 |
|---|---:|---|
| `different_content` | 4,115 | 목록 제목 생략형: `list_title`이 상세 제목의 앞부분이고 말줄임표로 끝남 |
| `list_title_inside_detail_title` | 2,869 | 검색어 주변 문맥형: `list_title`이 상세 제목 내부의 일부 구간 |
| `detail_title_extends_list_title` | 2,085 | 후속 확장형: `list_title`은 상세 제목의 시작부이고 `title`이 뒤로 더 이어짐 |

따라서 세 유형 모두 목록 제목과 상세 제목이 서로 다른 출처의 문자열을 담고 있다기보다는, **목록 페이지가 상세 페이지 `h1`의 일부만 선택적으로 표시한 결과**로 보는 것이 타당합니다.

---

## 프롬프트 4-5
그럼 말줄임표로 생략된 유형과 후속 확장형은 말줄임표의 유무만 다르고 구조적으로는 같다고 할 수 있겠네?

## 답변 4-5
대체로는 그렇게 볼 수 있습니다. 다만 **완전히 동일한 유형**이라기보다는, 구조적으로 매우 가까운 두 하위 유형이라고 설명하는 편이 안전합니다.

두 유형의 공통 구조는 다음입니다.

```text
list_title = 상세 페이지 title의 앞부분
title      = list_title + 뒤에 이어지는 추가 문자열
```

차이는 목록 페이지가 “뒤에 더 있음”을 어떻게 표시했는가입니다.

| 유형 | 구조 | 목록 페이지 표시 방식 |
|---|---|---|
| 말줄임표 생략형 | `list_title`이 `title`의 앞부분 | 목록 제목 끝에 `...`가 붙음 |
| 후속 확장형 | `list_title`이 `title`의 앞부분 | 말줄임표 없이 그냥 끊김 |

따라서 두 유형은 모두 **상세 제목 시작부 표시형**으로 묶을 수 있습니다.

단, 아주 엄밀하게는 앞서 계산에서 말줄임표 생략형 4,115건 중 2건은 공백·구두점 정규화까지 해야 시작부 일치가 확인되었습니다. 하지만 전체의 0.05%에 불과하므로, 본문에서는 큰 흐름으로 “구조적으로 같은 계열”이라고 설명해도 무리는 없습니다.

---

## 프롬프트 4-6
xianfa 726의 원 데이터베이스 내 수집 대상 필드의 outerHTML은 아래와 같아. 내가 보기에는 여기에서 title이 h1에 잘 들어 있고, 수집 되지 않을 이유가 없어보이는데, 이 html 구조를 살펴보고 왜 title이 수집되지 않았을지 검토해줘. 단 이 개체는 본문 부분이 아주 길다는 점도 함께 유념해.

<div id="content-box_contentwrapper" class="contentwrapper" style="position: relative; top: 0px; width: 100%; display: block; padding: 0px; left: 0px;"><div class="img-pdf"><a href="tm_show.php?id=A2015100134302&amp;fullversion=1&amp;qrygroup=1&amp;qrynewstype=SP" target="_blank" title="原始圖檔" fullversion="1"><img src="SP/images/pdf.png" border="0"></a></div><span id="left-title">申報 </span><span><b>日期：</b>1948-04-10 <b>版次/卷期：</b>05 版　<b>專欄：</b>分類廣告</span><h1>　Detamore,　World　Traveller　and　Bible　Lecturer　presents　his　widely-discussed　address　on　the　ATOMIC　BOMB.</h1><div>本報訊<div><div class="content-box2">　Detamore,　World　Traveller　and　Bible　Lecturer　presents　his　widely-discussed　address　on　the　ATOMIC　BOMB.<br>
Will　our　world　commit　ATOMIC　SUICIDE　Bccording　to　Bible　predic-tlon?　An　address　of　titanic　importanco　this　tense　hour.<br>
Every　person　in　shanghai　ought　to　heal　this　messagel<br>
The　Auditorfum　waspacked　last　week　and　hundreds　could　not　zet　in　.The　ATOMIC　BOMB　address　will　be　given　twleel<br>
Every　X12:00　O　Noon<br>
Sunday　R＆<br>
A　10:00　P.m<br>
THE　ATOMIC.5：30　＆7：30　P.　　　SUNDAY　April　11　FREE<br>
BOMB　AND　THE　DOVE　OF　PEACE<br>
Other　Leetures:　7:30　P.in<br>
Wed;　Thme,　Frtday　Nights-Every　night　tmportant<br>
ＮＥＷ　BIBLE　AUDITORIUM　　105　Rt.　say　zoong　常熟路（善鐘路）一０五號<br>
四明銀行<br>
舉辦星期定期存欵　每單位國幣一百萬元<br>
...(생략)...
<br>
西門路２２９弄念三號洽新屋數幢内有亭子樓統樓店客堂廚房水電全共售七億二８０６９３</p<br></div><div>
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

## 답변 4-6
HTML 구조만 놓고 보면 `xianfa` 726의 `title`이 수집되지 않을 이유는 거의 없습니다.

제시한 상세 페이지에는 제목이 명확하게 들어 있습니다.

```html
<h1>　Detamore,　World　Traveller　and　Bible　Lecturer　presents　his　widely-discussed　address　on　the　ATOMIC　BOMB.</h1>
```

그리고 현재 크롤러도 상세 제목을 다음 선택자로 가져오도록 되어 있습니다.

```python
#content-box_contentwrapper > h1
```

즉, 이 HTML은 현재 코드의 제목 선택자와 정확히 맞습니다. 따라서 이 사례는 **원 데이터베이스의 HTML 구조 때문에 `title`이 비어 있는 사례**라기보다는, **수집 당시 크롤러 동작 과정에서 `title` 추출만 실패했지만 `text` 추출은 성공한 사례**로 보는 것이 맞습니다.

가능성이 큰 원인은 세 가지입니다.

1. **긴 본문으로 인한 Playwright 처리 지연**
   
   이 개체의 `text`는 322,522자로 매우 깁니다. 본문이 비정상적으로 긴 광고 묶음 페이지이기 때문에, 상세 페이지 로드 직후 DOM 접근이나 `inner_text()` 호출이 지연되었을 가능성이 있습니다. 현재 코드에서 제목 추출은 [crawl_shenbao_text_chrome.py](C:\Users\class\Documents\coding\shlib-shenbao-dataset-workflow\crawl_shenbao_text_chrome.py):439의 `extract_detail_title()`에서 이루어지는데, 내부적으로 `h1.inner_text()`를 호출합니다. `inner_text()`는 화면에 표시되는 텍스트를 계산하는 방식이라, 매우 긴 페이지에서는 `textContent`보다 브라우저 처리 부담이 큽니다.

2. **`title` 추출과 `text` 추출이 서로 독립적으로 저장됨**
   
   현재 코드 흐름은 다음과 같습니다.

   ```python
   detail_title = extract_detail_title(detail_active.scope)
   detail_text = extract_detail_text(...)
   ```

   즉, 먼저 `title`을 추출하고, 그 다음에 `text`를 추출합니다. 문제는 첫 번째 `extract_detail_title()` 호출이 실패해 `""`을 반환하더라도, 이후 `extract_detail_text()`가 성공하면 해당 행은 정상 수집처럼 저장될 수 있다는 점입니다. 더구나 `extract_detail_text()` 내부에서도 다시 `extract_detail_title()`을 호출하지만, 그 값은 `text == title` 여부를 확인하는 데만 쓰이고, 바깥의 `detail_title` 값을 갱신하지 않습니다. 따라서 수집 시점에 `title` 추출이 일시적으로 실패하고, 직후 `text` 추출은 성공하면 지금처럼 **`title`은 비어 있고 `text`는 정상적으로 들어간 행**이 생길 수 있습니다.

3. **이 개체는 기사라기보다 광고 묶음에 가까운 특수 자료**
   
   `publish`에 `分類廣告`가 들어 있고, 본문도 `NEW BIBLE AUDITORIUM`, 은행, 부동산, 판매 광고 등이 이어지는 형태입니다. 따라서 자료 성격상 일반 기사와 다른 구조적·분량적 특성을 가지고 있습니다. 다만 이 점은 `title`이 비어야 하는 이유는 아닙니다. 정확히 말하면, **광고성 장문 자료이기 때문에 브라우저 자동화 처리 과정에서 제목 추출 타이밍 문제가 발생했을 가능성이 높다**고 보는 편이 적절합니다.

코드 측면에서 재발을 줄이려면 두 가지 수정이 적절합니다.

1. `detail_text`를 추출한 뒤에도 `detail_title`이 비어 있으면 `extract_detail_title()`을 한 번 더 시도합니다.
2. `h1` 제목 추출에는 `inner_text()`보다 `text_content()` 또는 JavaScript `textContent` 기반 추출을 우선 사용합니다. 긴 본문이 있는 페이지에서는 이 방식이 더 가볍습니다.

즉, 이 사례는 **HTML 구조상 제목이 없는 경우가 아니라, 장문 광고성 상세 페이지에서 발생한 수집 아티팩트**로 분류하는 것이 가장 정확합니다.
