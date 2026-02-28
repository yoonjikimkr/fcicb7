# 건강기능식품 기능성 원료 인정 현황 수집 Plan Prompt

본 문서는 `nutrient/plan.md`의 수집 우선순위 1위인 **"건강기능식품 기능성 원료 인정 현황"** 데이터를 공공데이터 API를 통해 수집하기 위한 상세 가이드입니다.

## 1. API 개요
- **API 명칭**: 건강기능식품 기능성 원료 인정 현황
- **제공 기관**: 식품의약품안전처 (식품안전나라)
- **데이터 ID**: `I2710`
- **조회 목적**: 민간 데이터(iHerb, 네이버 쇼핑)의 원료명을 키로 공인된 기능성(면역, 수면 등)을 매핑하여 신뢰성 있는 분석 수행.

## 2. 수집 인터페이스 (HTTP 요청 정보)
- **Base URL**: `http://openapi.foodsafetykorea.go.kr/api/{SERVICE_KEY}/I2710/{TYPE}/{START_IDX}/{END_IDX}`
- **요청 인자**:
    - `SERVICE_KEY`: 인증키 (data.go.kr 또는 식품안전나라에서 발급)
    - `TYPE`: `json` (권장) 또는 `xml`
    - `START_IDX`: 시작 인덱스 (예: 1)
    - `END_IDX`: 종료 인덱스 (예: 100)
- **선택 파라미터**:
    - `APLC_RAWMTRL_NM`: 신청원료명 (특정 원료 검색 시 사용)

## 3. 주요 응답 항목 (Response Mapping)
| 필드명 | 설명 | 비즈니스 가치 |
| :--- | :--- | :--- |
| `HF_FNCLTY_MTRAL_RCOGN_NO` | 인정번호 | 데이터 고유 식별자 |
| `APLC_RAWMTRL_NM` | **신정원료명** | 민간 데이터와 조인할 핵심 키 (예: 비타민D) |
| `FNCLTY_CN` | **기능성 내용** | 실제 효능 분석 (면역력 증진, 피로개선 등) |
| `DAY_INTK_CN` | 1일 섭취량 | 가이드라인 준수 여부 확인 |
| `IFTKN_ATNT_MATR_CN` | 섭취 시 주의사항 | 이상사례 데이터와 교차 분석용 |
| `PRMS_DT` | 인정일자 | 최신 트렌드 원료 파악 |
| `BSSH_NM` | 업체명 | 제조사/수입사 분석 |

## 4. 수집 및 저장 시나리오
1. **전체 데이터 수집**: `I2710` API를 페이징 처리(1-1000, 1001-2000 ...)하여 전체 마스터 데이터를 수집합니다.
2. **데이터 클렌징**: 원료명(`APLC_RAWMTRL_NM`)에서 불필요한 공백이나 특수문자를 제거하여 민간 데이터와 매칭률을 높입니다.
3. **DB 저장**: `SQLite`를 사용하여 `functional_ingredients` 테이블을 생성하고 데이터를 저장합니다.

## 5. 실행 코드 템플릿 (Python)
```python
import requests
import pandas as pd

def fetch_functional_ingredients(api_key, start=1, end=100):
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/I2710/json/{start}/{end}"
    response = requests.get(url)
    data = response.json()
    
    if 'I2710' in data:
        items = data['I2710']['row']
        return pd.DataFrame(items)
    else:
        print("Error or No Data:", data)
        return pd.DataFrame()

# 전체 수집 예시 (루프 사용)
# all_data = []
# for i in range(1, 5000, 1000):
#     df = fetch_functional_ingredients(MY_KEY, i, i+999)
#     all_data.append(df)
```

## 6. 예상 분석 인사이트
- "네이버 쇼핑 상위 100개 제품 중 식약처 공인 기능성 원료가 포함된 비율은?"
- "최근 3년간 가장 인기있는 성분 변화 추이는?"
- "특정 원료의 식약처 권장 섭취량 대비 해외 직구 제품의 함량 과다 여부."
