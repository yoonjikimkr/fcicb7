# Aladin IT 도서 데이터 수집 계획

이 문서에는 알라딘 IT 카테고리 도서 데이터 수집을 위한 분석 내용이 담겨 있습니다. 모든 수집, 분석, 시각화 결과는 `aladin` 폴더 하단에 생성됩니다.

1) HTTP 요청정보
Request URL
https://www.aladin.co.kr/shop/wbrowse.aspx?BrowseTarget=List&ViewRowsCount=25&ViewType=Detail&PublishMonth=0&SortOrder=2&page=1&Stockstatus=1&PublishDay=84&CID=351&SearchOption=
Request Method
GET

2) Payload 정보 (URL Parameters)
BrowseTarget=List
ViewRowsCount=25
ViewType=Detail
PublishMonth=0
SortOrder=2
page=1
Stockstatus=1
PublishDay=84
CID=351
SearchOption=

3) 분석된 HTML 구조
도서 아이템 컨테이너: `.ss_book_box`

```html
<div class="ss_book_box" itemid="332583104">
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody>
            <tr>
                <td width="*" align="left" valign="top">
                    <div class="ss_book_list">
                        <ul>
                            <li><a href="..." class="bo3">SQL 자격검정 실전문제</a><span class="ss_f_g2"> - 국가공인 SQL전문가...</span></li>
                            <li><a href="...">한국데이터산업진흥원</a> (지은이) | <a href="...">한국데이터산업진흥원</a> | 2023년 12월</li>
                            <li><span>18,000</span>원 → <span class="ss_p2"><em>17,460원</em></span> (<span class="ss_p">3%</span>할인)</li>
                            <li><span class="star_score">7.3</span> (<a href="...">3</a>) | 세일즈포인트 :<span class="sales_point"> 50,359</span></li>
                        </ul>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

4) 수집 계획
- **1단계**: 1페이지를 먼저 수집하여 데이터(제목, 저자, 출판사, 가격, 세일즈포인트 등)가 정상적으로 수집되는지 확인한다.
- **2단계**: 데이터 확인 후, 최대 10페이지(약 250권)까지 수집을 확장한다.
- **수집 컬럼**: 제목, 부제, 저자, 출판사, 출판일, 정가, 판매가, 할인율, 평점, 리뷰수, 세일즈포인트
- **데이터 저장**: `aladin/data` 폴더에 `aladin_it_books.csv` 파일로 저장한다.
- **간격**: 페이지 요청 사이에 0.5~2초 사이의 랜덤한 지연 시간을 두어 서버 부하를 방지한다.

5) 데이터 저장 형식
- CSV 파일 (UTF-8-SIG 인코딩)
