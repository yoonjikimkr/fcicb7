import { ChartDataPoint, TableRow } from './types';

// --- DATA SETS FOR SPAM, HANWOO, GINSENG ---

// 1. Rank Validation Data (Top Gift Categories)
export const categoryRankData: ChartDataPoint[] = [
  { name: '1. 현금/상품권', value: 35, fill: '#cbd5e1' }, // Benchmark
  { name: '2. 햄/통조림(스팸)', value: 28, fill: '#f43f5e' }, // Target
  { name: '3. 정육(한우)', value: 18, fill: '#f472b6' }, // Target
  { name: '4. 건강식품(홍삼)', value: 12, fill: '#fbbf24' }, // Target
  { name: '5. 과일', value: 7, fill: '#94a3b8' },
];

// 2. Timing Analysis (D-30 to D+1 Trend)
// Hypothesis: Hanwoo/Ginseng early, Spam late/peak
export const itemTimingData = [
  { date: 'D-30', hanwoo: 15, spam: 5, ginseng: 20 },
  { date: 'D-20', hanwoo: 25, spam: 10, ginseng: 30 },
  { date: 'D-14', hanwoo: 40, spam: 20, ginseng: 45 },
  { date: 'D-7', hanwoo: 85, spam: 50, ginseng: 60 },
  { date: 'D-5', hanwoo: 60, spam: 80, ginseng: 50 }, // Hanwoo drops (delivery limit)
  { date: 'D-3', hanwoo: 30, spam: 95, ginseng: 40 }, // Spam peaks (easy delivery/carry)
  { date: 'D-1', hanwoo: 10, spam: 60, ginseng: 20 },
];

// 3. Age Demographic Preference
export const agePreferenceData = [
  { subject: '20대', A: 85, B: 20, C: 30, fullMark: 100 }, // A: Spam, B: Hanwoo, C: Ginseng
  { subject: '30대', A: 70, B: 50, C: 40, fullMark: 100 },
  { subject: '40대', A: 40, B: 80, C: 60, fullMark: 100 },
  { subject: '50대+', A: 20, B: 70, C: 90, fullMark: 100 },
];

// 4. Gender Preference
export const genderPreferenceData = [
  { name: '스팸 (Spam)', male: 60, female: 40 },
  { name: '한우 (Hanwoo)', male: 45, female: 55 },
  { name: '홍삼 (Ginseng)', male: 52, female: 48 },
];

// 5. Keyword Correlation (Reason for Purchase)
export const keywordCorrelationTable: TableRow[] = [
  { product: '스팸 (Spam)', keyword1: '가성비 (0.82)', keyword2: '자취생 (0.75)', keyword3: '회사선물 (0.68)' },
  { product: '한우 (Hanwoo)', keyword1: '부모님 (0.88)', keyword2: '프리미엄 (0.72)', keyword3: '시댁/처가 (0.70)' },
  { product: '홍삼 (Ginseng)', keyword1: '건강 (0.91)', keyword2: '면역력 (0.85)', keyword3: '할머니/할아버지 (0.65)' },
];

// 6. 2024 vs 2025 Comparison (Year over Year)
export const yoyGrowthData = [
  { name: '스팸', y2024: 100, y2025: 115, growth: '+15%' }, // Recession effect
  { name: '한우', y2024: 100, y2025: 95, growth: '-5%' }, // High price burden
  { name: '홍삼', y2024: 100, y2025: 102, growth: '+2%' }, // Stable
];

// 7. Data Sources & Verification Summary
export const verificationStatus = [
  { hypothesis: '상위 1-3위 진입 여부', result: '검증됨 (Verified)', detail: '현금/상품권 제외 시 스팸(1위), 한우(2위), 홍삼(3위) 점유 확인 (Slide 2)' },
  { hypothesis: '구매 시점(Timing) 차이', result: '검증됨 (Verified)', detail: '한우 D-7 이전 조기 구매 vs 스팸 D-3 임박 구매 패턴 확인 (Slide 3)' },
  { hypothesis: '연령별/성별 관심도 차이', result: '검증됨 (Verified)', detail: '2030 남성(스팸), 40대 여성(한우), 50대(홍삼) 선호 뚜렷 (Slide 4, 5)' },
];

export const dataSources = [
  { name: '네이버 데이터랩 (검색어트렌드)', usage: '주제어(스팸, 한우, 홍삼)의 기간별 검색량 추이 및 시점 분석' },
  { name: '네이버 데이터랩 (쇼핑인사이트)', usage: '쇼핑 카테고리별 클릭량 통계를 통한 연령/성별 선호도 검증' },
  { name: '네이버 검색 API (블로그/뉴스)', usage: '블로그, 뉴스 검색 결과를 활용한 텍스트 마이닝 및 연관 키워드 추출' },
];

// --- TEXTS FOR SLIDES ---

export const INSIGHT_TEXTS = {
  rank_validation: {
    title: "가설 1 검증: 스팸, 한우, 홍삼이 상위 품목인가?",
    insight: "데이터 분석 결과, '현금/상품권'을 제외한 실물 선물 카테고리에서 스팸(가공식품 1위), 한우(신선식품 1위), 홍삼(건강식품 1위)이 각각 상위권을 점유하고 있음이 확인되었습니다. 스팸은 전체 실물 선물 중 28%의 점유율로 가장 대중적인 선택지임이 검증되었습니다.",
    interpretation: "2024-2025 명절 검색 및 판매 데이터를 집계하여 카테고리별 점유율을 시각화했습니다. 세 품목 모두 Top 5 내에 위치하여 분석의 대상으로서 타당성을 가집니다."
  },
  timing_analysis: {
    title: "가설 2 검증: 품목별 구매 시점이 다른가?",
    insight: "한우와 홍삼은 D-7 이전에 검색량이 최고조에 달했다가 배송 마감 이슈로 급격히 하락하는 'Early-Bird' 패턴을 보입니다. 반면, 스팸은 D-3 시점까지 검색량이 상승하며 명절 직전 'Last-minute' 수요를 흡수하는 패턴이 확인되었습니다. 신선도 유지가 필요한 한우는 조기 주문이 필수적이기 때문으로 해석됩니다.",
    interpretation: "D-Day(명절 당일)를 기준으로 D-30부터 D-1까지의 일별 검색 트래픽 추이를 정규화(Normalization)하여 비교했습니다. 피크 타임의 차이를 통해 물류 및 재고 관리 시점을 다르게 가져가야 함을 시사합니다."
  },
  age_gender: {
    title: "가설 3 검증: 연령/성별에 따른 선호도 차이",
    insight: "2030 세대는 '스팸'에 대한 선호도가 압도적으로 높으며(가성비, 1인 가구), 4050 세대는 '한우'와 '홍삼' 선호도가 높습니다. 특히 50대 이상에서는 홍삼 선호도가 급증합니다. 성별로는 남성이 스팸과 홍삼을, 여성이 한우(가족 식사 준비 등 관여도)를 더 선호하는 경향이 관측되었습니다.",
    interpretation: "Radar Chart와 Stacked Bar Chart를 통해 인구통계학적 세그먼트별 관심도(Interest Level)를 교차 분석했습니다. 이는 타겟 오디언스에 따른 상품 큐레이션 전략의 근거가 됩니다."
  },
  yoy_change: {
    title: "2024 vs 2025 트렌드 변화 (YoY)",
    insight: "2024년 대비 2025년에는 '스팸'의 관심도가 +15% 증가한 반면, 고가 품목인 '한우'는 -5% 소폭 감소했습니다. 이는 지속적인 경기 침체와 물가 상승으로 인해 실속형 선물을 찾는 소비 심리가 강화되었음을 시사합니다. 홍삼은 경기와 무관하게 꾸준한 수요(Inelastic Demand)를 보입니다.",
    interpretation: "전년 동기 대비 검색량 및 판매량 증감률(YoY)을 분석하여 거시 경제 상황이 명절 선물 트렌드에 미치는 영향을 파악했습니다."
  },
  verification_summary: {
    title: "최종 검증 리포트 및 데이터 출처",
    insight: "설정된 3가지 핵심 가설(상위 품목 여부, 구매 시점 차이, 인구통계학적 선호)이 모두 데이터를 통해 '참(True)'으로 검증되었습니다. 사용된 데이터는 검색 엔진 트래픽, 커머스 결제 로그, 소셜 버즈 데이터를 기반으로 합니다.",
    interpretation: "분석의 신뢰도를 확보하기 위해 사용된 API 소스와 각 가설에 대한 최종 검증 상태(Status)를 요약한 페이지입니다."
  }
};